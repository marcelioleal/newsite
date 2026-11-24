# Writing posts — quick reference

The one-page cheatsheet. For the long story, see [README.md](../README.md).

## 1. Create the post

```bash
hugo new content/pt-br/posts/meu-slug/index.md
# or for EN:
hugo new content/en/posts/my-slug/index.md
```

Front-matter template (Hugo fills most via archetype):

```yaml
---
title: "Título do post"
date: 2026-11-24T15:30:00-03:00
draft: false
tags: ["kitesurf", "viagem"]
translationKey: "my-slug"   # same value in PT+EN files to pair them
summary: "1-2 frases que aparecem no RSS + meta description + preview da home."
---
```

## 2. Add images to the post

### Via GitHub Action (default — zero setup local)

1. Dropa o arquivo em `static/images-source/2026/11/minha-foto.jpg`
   - Estrutura de pastas por ano/mês (mesmo padrão do WordPress)
   - A pasta `static/images-source/` é **gitignored** — a imagem crua nunca entra no commit.
2. `git add` do post + `git commit` + `git push`.
3. O workflow **Upload new images to R2** detecta a nova imagem e sobe pra R2.
4. Abre a execução em https://github.com/marcelioleal/newsite/actions, clica no job, scrolla até o **Step summary** — ele lista a URL pública de cada imagem subida.
5. Cola a URL no post:

   ```markdown
   ![Pôr do sol na Preá](https://images.marcelioleal.com/2026/11/minha-foto.jpg)
   ```

6. Commit a referência da URL + push. Netlify rebuilda em ~1min. A imagem crua local em `static/images-source/` pode ficar lá ou você apaga — tanto faz.

### Localmente (sem round-trip CI)

```bash
# Primeiro: credentials em ~/.env.r2 ou exportadas no shell
# (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT, R2_PUBLIC_URL)

./scripts/upload-image.sh static/images-source/2026/11/minha-foto.jpg
# Output: https://images.marcelioleal.com/2026/11/minha-foto.jpg
```

Depois cola a URL no markdown como acima.

## 3. Preview local

```bash
hugo server
```

Abre http://localhost:1313/. Sem imagens locais — mas as URLs do CDN carregam normal no browser porque são públicas.

## 4. Imagens otimizadas?

Imagens enormes (10MB+ screenshots) degradam o carregamento mesmo com CDN. Não precisa otimizar manualmente — Phase 2.5 do roadmap ([roadmap.json](../.aimi/tasks/wordpress-to-hugo-migration/roadmap.json)) tem a tarefa de rodar um otimizador em batch sobre o R2 todo.

Se for uma foto específica que você quer deixar leve na hora, antes de uploadar:

```bash
magick input.jpg -strip -interlace Plane -quality 82 -resize '2000x2000>' output.jpg
# OU PNG:
magick input.png -strip -resize '2000x2000>' -colors 256 PNG8:output.png
```

## 5. Publicar

```bash
git add content/<lang>/posts/<slug>/
git commit -m "post: <título curto>"
git push origin main
```

Netlify deploya em ~1-2min. Produção em https://new.marcelioleal.com até Phase 3 cutover; depois será https://marcelioleal.com.

## Dicas

- **Idiomas emparelhados**: PT e EN do mesmo post devem ter o mesmo valor em `translationKey` pro language switcher pairá-los. Se um idioma não existir, o switcher mostra "apenas em PT" / "only in EN".
- **Tags**: usa o mesmo nome em ambos idiomas se quiser que a taxonomia liste ambos os posts.
- **URL amigável**: por padrão Hugo usa o nome da pasta como slug (ex: `meu-slug/`). Pra override, usa `slug: "outra-coisa"` no front-matter.
- **Front-matter summary**: aparece no RSS, meta description, e preview da home — vale a pena escrever uma frase matadora de 1-2 linhas.
