# Guia — cada emprego e cada projeto

No Overleaf você edita **um arquivo por experiência**. Assim fica claro o que é emprego, o que é projeto e o que é formação.

## Mapa dos arquivos

| Arquivo | O que é | Empresa / tema |
|---------|---------|----------------|
| `content/jobs/01-engeletra.tex` | **Emprego atual** | Engeletra — ERP |
| `content/jobs/02-empetur.tex` | **Emprego atual** | Empetur (governo PE) |
| `content/jobs/03-campello-siqueira.tex` | Emprego anterior | Campello & Siqueira — dados |
| `content/jobs/04-softex.tex` | Residência | Softex — robótica |
| `content/jobs/05-freelance.tex` | Autônomo | Freelance |
| `content/projects/01-chatbot-ia.tex` | Projeto | Chatbot IA |
| `content/projects/02-mestrado-saeb.tex` | Pesquisa | Mestrado SAEB |

## O que editar em cada job

Abra o `.tex` do emprego. No topo tem comentário com cargo e período. No corpo:

- **Linha 1 do `\cventry`**: nome da empresa  
- **Linha 2**: seu cargo  
- **Linha 3**: período (`Mai 2026 -- Presente`)  
- **Linha 4**: cidade  
- **`\item ...`**: cada conquista (bullet)

## Remover um emprego do CV (sem apagar o arquivo)

Em `content/experience.tex`, comente a linha:

```latex
% \input{content/jobs/04-softex}
```

## Mudar a ordem (mais recente primeiro)

Reordene as linhas `\input{...}` em `content/experience.tex`.

## Adicionar emprego novo

1. Copie `content/jobs/05-freelance.tex` → `content/jobs/06-nova-empresa.tex`  
2. Edite o conteúdo  
3. Em `content/experience.tex`, adicione no topo:  
   `\input{content/jobs/06-nova-empresa}`

## Emprego vs projeto

| Pasta | Use para |
|-------|----------|
| `content/jobs/` | CLT, PJ longo, residência, estágio com vínculo |
| `content/projects/` | Freelance pontual, pesquisa, side project, hackathon |

## Outros arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `content/sidebar.tex` | Foto, contato, skills, idiomas |
| `content/profile.tex` | Parágrafo de resumo |
| `content/education.tex` | Formação acadêmica |
| `main.tex` | Só monta o documento — quase não precisa mexer |
