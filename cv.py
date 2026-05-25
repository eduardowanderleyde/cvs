#!/usr/bin/env python3
"""
cv.py — Gera currículo HTML/PDF a partir de cv.yaml

Uso:
  python cv.py build          # gera dist/<slug>.html
  python cv.py pdf            # gera dist/<slug>.pdf (Chrome/Edge)
  python cv.py all            # build + pdf
  python cv.py open           # abre o HTML no navegador
  python cv.py watch          # recompila ao salvar cv.yaml
  python cv.py init           # cria cv.yaml de exemplo (se não existir)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("\n  Dependências faltando. Rode:\n")
    print("    pip install -r requirements.txt\n")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"
TEMPLATES = {
    "modern": "modern.html.j2",
    "professional": "professional.html.j2",
}
DEFAULT_TEMPLATE = "modern"
DIST = ROOT / "dist"
DEFAULT_CONFIG = ROOT / "cv.yaml"

# ANSI cores (funciona no Windows 10+ terminal)
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"


def enable_ansi_windows() -> None:
    if platform.system() == "Windows":
        os.system("")  # habilita VT no console


def ok(msg: str) -> None:
    print(f"  {C.GREEN}[ok]{C.RESET} {msg}")


def info(msg: str) -> None:
    print(f"  {C.CYAN}>{C.RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {C.YELLOW}[!]{C.RESET} {msg}")


def err(msg: str) -> None:
    print(f"  {C.RED}[x]{C.RESET} {msg}", file=sys.stderr)


def banner() -> None:
    print(f"\n{C.BOLD}{C.MAGENTA}  +----------------------------------+{C.RESET}")
    print(f"{C.BOLD}{C.MAGENTA}  |  CV BUILDER  -  yaml -> html/pdf |{C.RESET}")
    print(f"{C.BOLD}{C.MAGENTA}  +----------------------------------+{C.RESET}\n")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def load_config(path: Path) -> dict:
    if not path.exists():
        err(f"Arquivo não encontrado: {path}")
        err("Rode: python cv.py init")
        sys.exit(1)

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        err("cv.yaml inválido: raiz deve ser um objeto.")
        sys.exit(1)

    _validate(data)
    return data


def _validate(data: dict) -> None:
    if "personal" not in data or "name" not in data.get("personal", {}):
        err("cv.yaml: falta personal.name")
        sys.exit(1)

    output = data.setdefault("output", {})
    if "slug" not in output:
        output["slug"] = slugify(data["personal"]["name"])

    data.setdefault("meta", {})
    data["meta"].setdefault("lang", "pt-BR")
    data["meta"].setdefault("template", DEFAULT_TEMPLATE)
    data["meta"].setdefault(
        "title",
        f"{data['personal']['name']} - Currículo",
    )
    tpl = data["meta"]["template"]
    if tpl not in TEMPLATES:
        err(f"Template '{tpl}' invalido. Opcoes: {', '.join(TEMPLATES)}")
        sys.exit(1)

    data["personal"].setdefault("headline", "")


def render_html(data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl_key = data["meta"].get("template", DEFAULT_TEMPLATE)
    template = env.get_template(TEMPLATES[tpl_key])
    return template.render(**data)


def output_paths(data: dict) -> tuple[Path, Path]:
    slug = data["output"]["slug"]
    html_path = DIST / f"{slug}.html"
    pdf_path = DIST / f"{slug}.pdf"
    return html_path, pdf_path


def cmd_build(config_path: Path) -> Path:
    data = load_config(config_path)
    html = render_html(data)
    html_path, _ = output_paths(data)

    DIST.mkdir(exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    tpl = data["meta"].get("template", DEFAULT_TEMPLATE)
    ok(f"HTML -> {html_path.relative_to(ROOT)}  [{tpl}]")
    return html_path


def find_browser() -> list[str] | None:
    """Retorna comando base do Chrome ou Edge para headless PDF."""
    candidates: list[list[str]] = []

    if platform.system() == "Windows":
        pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        pf86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")

        for exe in [
            Path(pf) / "Google/Chrome/Application/chrome.exe",
            Path(pf86) / "Google/Chrome/Application/chrome.exe",
            Path(local) / "Google/Chrome/Application/chrome.exe",
            Path(pf) / "Microsoft/Edge/Application/msedge.exe",
            Path(pf86) / "Microsoft/Edge/Application/msedge.exe",
        ]:
            if exe.exists():
                candidates.append([str(exe)])
    elif platform.system() == "Darwin":
        for exe in [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            Path.home() / "Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]:
            if exe.exists():
                candidates.append([str(exe)])
    else:
        for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
            found = shutil.which(name)
            if found:
                candidates.append([found])

    return candidates[0] if candidates else None


def cmd_pdf(config_path: Path, html_path: Path | None = None) -> Path | None:
    data = load_config(config_path)
    if html_path is None:
        html_path, pdf_path = output_paths(data)
        if not html_path.exists():
            info("HTML não existe, gerando antes...")
            html_path = cmd_build(config_path)
    else:
        _, pdf_path = output_paths(data)

    browser = find_browser()
    if not browser:
        warn("Chrome/Edge não encontrado para PDF automático.")
        warn(f"Abra {html_path.name} no navegador → Ctrl+P → Salvar como PDF")
        return None

    file_url = html_path.resolve().as_uri()
    _, pdf_path = output_paths(data)

    cmd = [
        *browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        file_url,
    ]

    info("Gerando PDF via navegador headless...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
    except subprocess.CalledProcessError as e:
        err("Falha ao gerar PDF.")
        if e.stderr:
            print(e.stderr.decode(errors="replace")[:500])
        warn("Tente: python cv.py open  →  Ctrl+P  →  Salvar como PDF")
        return None
    except subprocess.TimeoutExpired:
        err("Timeout ao gerar PDF.")
        return None

    if pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        ok(f"PDF  -> {pdf_path.relative_to(ROOT)} ({size_kb:.0f} KB)")
        return pdf_path

    warn("PDF não foi criado. Use impressão manual do HTML.")
    return None


def cmd_open(config_path: Path) -> None:
    data = load_config(config_path)
    html_path, _ = output_paths(data)
    if not html_path.exists():
        html_path = cmd_build(config_path)
    webbrowser.open(html_path.resolve().as_uri())
    ok("Abrindo no navegador...")


def cmd_watch(config_path: Path) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        err("watchdog não instalado. Rode: pip install -r requirements.txt")
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if Path(event.src_path).resolve() == config_path.resolve():
                print(f"\n{C.DIM}  -- alteracao detectada --{C.RESET}")
                try:
                    cmd_build(config_path)
                except SystemExit:
                    pass

    info(f"Observando {config_path.name}  (Ctrl+C para sair)")
    cmd_build(config_path)
    observer = Observer()
    observer.schedule(Handler(), str(config_path.parent), recursive=False)
    observer.start()
    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n  {C.DIM}encerrado.{C.RESET}\n")


def cmd_init(config_path: Path) -> None:
    if config_path.exists():
        warn(f"{config_path.name} já existe — nada feito.")
        return
    sample = ROOT / "cv.yaml"
    if sample.exists() and sample != config_path:
        warn("Use o cv.yaml já presente como base.")
        return
    err("Template init não disponível separado; edite cv.yaml diretamente.")


def cmd_export_json(config_path: Path) -> None:
    data = load_config(config_path)
    out = DIST / f"{data['output']['slug']}.json"
    DIST.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    ok(f"JSON -> {out.relative_to(ROOT)}")


def main() -> None:
    enable_ansi_windows()
    parser = argparse.ArgumentParser(
        description="Gera CV profissional a partir de cv.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="build",
        choices=["build", "pdf", "all", "open", "watch", "init", "json"],
        help="comando (padrão: build)",
    )
    parser.add_argument(
        "-c", "--config",
        default=str(DEFAULT_CONFIG),
        help="caminho do arquivo YAML (padrão: cv.yaml)",
    )
    args = parser.parse_args()
    config_path = Path(args.config).resolve()

    banner()

    if args.command == "init":
        cmd_init(config_path)
        return

    if args.command == "build":
        cmd_build(config_path)
    elif args.command == "pdf":
        cmd_pdf(config_path)
    elif args.command == "all":
        html_path = cmd_build(config_path)
        cmd_pdf(config_path, html_path)
    elif args.command == "open":
        cmd_build(config_path)
        cmd_open(config_path)
    elif args.command == "watch":
        cmd_watch(config_path)
    elif args.command == "json":
        cmd_export_json(config_path)

    print()


if __name__ == "__main__":
    main()
