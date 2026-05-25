# CV LaTeX — zip para Overleaf

## Subir no Overleaf (passo a passo)

1. No Explorer, entre na pasta **`latex`** (esta pasta).
2. Selecione **tudo** dentro dela (`main.tex`, `cv.sty`, `content/`, `assets/`…).
3. Botão direito → **Enviar para** → **Pasta compactada (zip)**.
4. Overleaf → **New Project** → **Upload Project** → escolha o zip.
5. Menu esquerdo → **Compiler** → **XeLaTeX**.
6. **Recompile**.

O `main.tex` precisa ficar na **raiz do zip**, não dentro de uma subpasta extra.

```
zip correto:
  main.tex
  cv.sty
  content/...
  assets/...

zip errado:
  latex/latex/main.tex   ← evite pasta duplicada
```

## Estrutura

```
latex/
  main.tex                 ← raiz do projeto Overleaf
  cv.sty                   ← visual (cores, fontes, comandos)
  GUIA-JOBS.md             ← mapa de cada emprego/projeto
  content/
    sidebar.tex            ← foto + contato + skills
    profile.tex            ← resumo
    experience.tex         ← lista quais jobs entram no PDF
    projects.tex
    education.tex
    jobs/
      01-engeletra.tex     ← 1 arquivo = 1 emprego
      02-empetur.tex
      ...
    projects/
      01-chatbot-ia.tex    ← 1 arquivo = 1 projeto
      02-mestrado-saeb.tex
  assets/
    images/profile.jpg     ← troque pela sua foto
    images/sidebar-accent.jpg
    fonts/                 ← Roboto + Oswald (já inclusas)
```

## Dia a dia

- Mudou **um emprego** → edite só `content/jobs/XX-nome.tex`
- Quer **esconder** um job → comente `\input{...}` em `content/experience.tex`
- Nova **foto** → substitua `assets/images/profile.jpg` (quadrada, ~400px+)

Detalhes: leia **`GUIA-JOBS.md`**.

## Fontes e imagens

- **Fontes**: `assets/fonts/` (Roboto corpo, Oswald no nome)
- **Ícones**: Font Awesome (já no Overleaf, via `cv.sty`)
- **Foto**: placeholder Unsplash — troque antes de enviar candidaturas
