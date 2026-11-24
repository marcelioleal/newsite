# Vague anchor text — review

Scan date: 2026-11-24. Total findings: **15** across 13 posts.

## How to use this file

Each finding shows: file + line number, current anchor text, the URL, and a context-aware suggestion. **Mark each finding** by changing the leading `[ ]` to `[x]` once applied.

To apply all approved changes in one go, after reviewing run:
```bash
python3 scripts/review_vague_links.py --apply   # not yet implemented; ask Claude to produce it once marks are done
```

## Breakdown by anchor text

- **aqui**: 13
- **clique aqui**: 1
- **here**: 1

## Findings by file

### `content/en/posts/hiring-a-hard-thing-about-hard-things/index.md`

- [ ] L164 (HTML) — current: **here** → `https://handbook.gitlab.com/handbook/hiring/`
  - **Suggest:** `see at handbook.gitlab.com`
  - **Context:** `- GitLab has an amazing material for hiring. Take a look <a href="https://handbook.gitlab.com/handbook/hiring/" target="_blank" rel="noopene…`

### `content/pt-br/posts/a-vida-e-boa-suas-lembrancas-nao-te-deixam-mentir/index.md`

- [ ] L60 (HTML) — current: **aqui** → `https://sprudge.com/the-sprudge-guide-to-sao-paulos-vila-madalena-neighborhood-127584.html`
  - **Suggest:** `ver em sprudge.com`
  - **Context:** `Eles tem um lugar especial no meu coração. Dá pra listar: Ekoa, Le pain quotidien, Cupping, Tastemade, Santo Grão, etc. Dá uma olhada <a hre…`

### `content/pt-br/posts/aprenda-a-programar-livrosite/index.md`

- [ ] L13 (MD) — current: **aqui** → `http://aprendaaprogramar.rubyonrails.pro.br/introducao`
  - **Suggest:** `ver em aprendaaprogramar.rubyonrails.pro.br`
  - **Context:** `Quem tá iniciando, vale dar uma lida [aqui](http://aprendaaprogramar.rubyonrails.pro.br/introducao).`

### `content/pt-br/posts/como-se-conectar-na-comunidade-de-startups/index.md`

- [ ] L36 (HTML) — current: **Aqui** → `https://www.startupdigest.com/digests/brazil`
  - **Suggest:** `ver em startupdigest.com`
  - **Context:** `O <a href="https://www.startupdigest.com/" target="_blank" rel="noopener noreferrer">Startup Digest</a> reune os principais eventos relacion…`

### `content/pt-br/posts/concurso-do-serpro/index.md`

- [ ] L17 (HTML) — current: **aqui** → `http://www.cespe.unb.br/concursos/SERPRO2008/arquivos/SERPRO_CARGO_05.pdf`
  - **Suggest:** `baixar o PDF`
  - **Context:** `A prova do SERPRO para o cargo de Especialização em Desenvolvimento de Sistemas pode ser baixada <a href="http://www.cespe.unb.br/concursos/…`

### `content/pt-br/posts/desenvolvimento-de-um-sistema-de-autenticacao-simples-e-funcional-em-php/index.md`

- [ ] L33 (MD) — current: **aqui** → `http://2.download-1.files-upload.com/50/2007/11/15/22-40/0/model.xml`
  - **Suggest:** `ver em 2.download-1.files-upload.com`
  - **Context:** `Para baixar o modelo de dados desenvolvido no [DBDesigner](http://fabforce.net/dbdesigner4/) é só clicar [aqui](http://2.download-1.files-up…`

- [ ] L103 (MD) — current: **clique aqui** → `http://www.php.net/manual/pt_BR/keyword.paamayim-nekudotayim.php`
  - **Suggest:** `ver em php.net`
  - **Context:** `Na linha 25 chamamos o método *loginUser* da classe *Fachada*, que a interface única com o BD. Esse método recebe como parâmetros o login e …`

### `content/pt-br/posts/duro-de-errar-50/index.md`

- [ ] L319 (MD) — current: **aqui** → `http://rapidshare.com/files/109601562/teste.zip.html`
  - **Suggest:** `ver em rapidshare.com`
  - **Context:** `Os códigos-fonte utilizados estão disponíveis [aqui](http://rapidshare.com/files/109601562/teste.zip.html).`

### `content/pt-br/posts/festival-do-sul-rock-do-norte/index.md`

- [ ] L177 (MD) — current: **aqui** → `https://marcelioleal.com/2025/09/28/o-perigo-da-musica-reflexiva-e-a-relacao-austro-paraense/`
  - **Suggest:** `ver em marcelioleal.com`
  - **Context:** `PS.2: Eu já falei de eletrônico e música paraense [aqui](https://marcelioleal.com/2025/09/28/o-perigo-da-musica-reflexiva-e-a-relacao-austro…`

### `content/pt-br/posts/organizando-a-busca-do-seu-proximo-emprego/index.md`

- [ ] L39 (HTML) — current: **aqui** → `https://medium.com/@marcelioleal/preparando-a-sua-documenta%C3%A7%C3%A3o-para-aplicar-para-as-vagas-de-emprego-spoiler-n%C3%A3o-%C3%A9-s%C3%B3-o-curr%C3%ADculo-545bd0fc2f79`
  - **Suggest:** `ler no Medium`
  - **Context:** `Pronto, utilize essa planilha como motivador nesse período difícil. Pense positivo e se prepare. O próximo passo é organizar a documentação …`

### `content/pt-br/posts/preparando-a-sua-documentacao-para-aplicar-para-as-vagas-de-emprego-spoiler-nao-e-so-o-curriculo/index.md`

- [ ] L62 (HTML) — current: **Aqui** → `https://docs.google.com/document/d/1T3NSkY7yhQRxDCjw6ABapt3ChxwJyKage6N3hf4393M/edit?usp=sharing`
  - **Suggest:** `ver no Google Docs`
  - **Context:** `<a href="https://docs.google.com/document/d/1T3NSkY7yhQRxDCjw6ABapt3ChxwJyKage6N3hf4393M/edit?usp=sharing" target="_blank" rel="noopener nor…`

- [ ] L101 (HTML) — current: **aqui** → `https://www.hongkiat.com/blog/online-portfolios-for-designers/`
  - **Suggest:** `ver em hongkiat.com`
  - **Context:** `Para outros papéis, como Designers, há outras plataformas como o <a href="https://www.behance.net/" target="_blank" rel="noopener noreferrer…`

### `content/pt-br/posts/proatividade-sem-maestria-nao-serve/index.md`

- [ ] L38 (HTML) — current: **aqui** → `http://g1.globo.com/planeta-bizarro/noticia/2012/08/idosa-tenta-restaurar-pintura-mas-distorce-obra-do-sec-xix-na-espanha.html`
  - **Suggest:** `ver em g1.globo.com`
  - **Context:** `Em 2012, uma senhora espanhola, como uma boa cidadã, decidiu ser proativa e restaurar uma obra de Elías García Martínez. Como ela não tinha …`

### `content/pt-br/posts/startup-lifestyle/index.md`

- [ ] L106 (HTML) — current: **aqui** → `https://medium.com/@ev/formula-for-entrepreneurial-success-ea0b02c504cd`
  - **Suggest:** `ler no Medium`
  - **Context:** `- Equilibre seu dia-a-dia, não deixe sua ocupação principal tomar sua vida de você. O Ev Williams resume algumas coisas bem legais <a href="…`

### `content/pt-br/posts/to-sempre-online-como-marcelioleal-em-alguma-rede-as-que-mais-uso-sao/index.md`

- [ ] L17 (HTML) — current: **aqui** → `https://about.me/marcelioleal`
  - **Suggest:** `ver em about.me`
  - **Context:** `Mas, tem algumas outras <a href="https://about.me/marcelioleal" target="_blank" rel="noopener noreferrer">aqui</a>.`
