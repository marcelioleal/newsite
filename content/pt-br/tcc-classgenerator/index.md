---
title: 'TCC — ClassGenerator: Um Gerador de Artefatos Multiplataforma'
date: '2026-11-21T01:38:26'
slug: tcc-classgenerator
wp_id: 1591
translationKey: tcc-classgenerator
---

Em fevereiro de 2005 eu defendi meu Trabalho de Conclusão de Curso em Ciência da Computação na Universidade Federal do Pará, em Belém, orientado pelo Prof. Dr. Eloi Luiz Favero. O tema era o ClassGenerator, uma ferramenta que eu vinha usando desde 2001 pra gerar boa parte de um sistema de informação a partir do esquema do banco de dados.

Aqui eu deixo um resumo do trabalho, o PDF pra quem quiser ler inteiro e um pouco do porquê eu acho que esse assunto, que parecia coisa dos anos 2000, voltou com tudo agora que a IA escreve código.

- [TCC original em português (PDF, 76 páginas)](/images/2008/08/tccfinal.pdf)
- [Tradução em inglês (PDF, 73 páginas)](/images/2026/11/ClassGenerator-Thesis-EN.pdf)

## O que é o ClassGenerator

O ClassGenerator junta três coisas numa ferramenta só: um gerador de código, um gerador de artefatos e um framework. Ele foi escrito em PHP com MySQL, roda no navegador, e o processo começa num esquema de banco de dados. A partir daí ele gera:

- as classes básicas (uma por tabela, com get e set);
- as classes de negócio, numa arquitetura em três camadas com o padrão Facade (Fachada, Cad e CadBD), que deixam o mapeamento objeto-relacional transparente pra quem programa a regra de negócio;
- as interfaces web de cadastro, edição, exclusão, administração e detalhe, em XHTML com CSS (tableless) e validação em JavaScript separada do HTML;
- a documentação do código.

As classes podiam sair em PHP, Java ou Python. O resultado da primeira geração já é um protótipo que funciona, e que pode virar a base do sistema ou servir só pra refinar requisito com o cliente. Quem usa não fica preso: dá pra continuar mantendo os artefatos pela ferramenta (cadastrando novos métodos com o SQL, os parâmetros e o tipo de retorno) ou pegar o código gerado e seguir a vida.

## As ideias por trás

O trabalho parte do "No Silver Bullet" do Fred Brooks, que divide o desenvolvimento de software em atividades essenciais (criar o modelo conceitual do sistema) e acidentais (implementar esse modelo num programa). O objetivo do ClassGenerator era melhorar diretamente as acidentais e, com isso, sobrar tempo e cabeça pras essenciais: especificação, projeto e teste.

O segundo capítulo passa pelas "possíveis balas de prata" da época (orientação a objetos, aspectos, metodologias ágeis, frameworks, geradores, padrões de projeto, RAD, componentes, software livre) e defende que nenhuma resolve sozinha, o que funciona é uma boa combinação. Também separa duas coisas que muita gente trata como igual: o gerador de código, que gera uma base e te deixa com ela, e o gerador de artefatos, em que a manutenção é feita sempre na especificação de alto nível e não nos arquivos gerados.

## Os estudos de caso

Tem três sistemas reais no trabalho:

- SAPP, um sistema de apoio a páginas pessoais (que rodava o meu site na época): aproximadamente 90% da aplicação foi gerada.
- asSAI, um sistema aduaneiro pra controle das atividades de um porto, com 70 a 90 entidades, feito em equipe na Abstract: aproximadamente 50% do código foi gerado.
- Portal da Amazônia: entre 30 e 40% do sistema, com o ClassGenerator usado só como gerador de código e convivendo com uma parte em MVC.

Daí sai a métrica do trabalho: de 70 a 90% em sistemas simples, de 50 a 65% em sistemas normais e de 20 a 30% em sistemas complexos, com muita regra de negócio e muitas visões.

## Por que isso tá atual com IA gerando código

Relendo o texto mais de vinte anos depois, o que me chama atenção é que as perguntas são as mesmas de hoje. Só mudou o gerador.

### A especificação como fonte da verdade

A definição de gerador de artefatos que eu usei lá, manter sempre a especificação e nunca o arquivo gerado, é praticamente o que hoje chamam de spec-driven development: a especificação é a fonte da verdade e o código é um artefato gerado a partir dela. Um [artigo de 2026 sobre o tema](https://arxiv.org/abs/2602.00180) descreve isso como uma ideia antiga que os assistentes de código reacenderam. Em 2005 a "spec" era o esquema do banco e um cadastro de métodos. Hoje é um documento em texto que um agente lê.

### O acidental ficou barato, o essencial continua com a gente

O ClassGenerator atacava o trabalho repetitivo de implementação. Os modelos de linguagem fazem isso numa escala que eu não imaginava, pra qualquer linguagem e sem precisar de template. Só que a parte essencial, entender o problema e decidir o que construir, continua sendo o gargalo, do jeito que o Brooks disse em 1986.

### Código gerado não é sistema pronto

No asSAI a ferramenta gerou metade do código, e o trabalho já avisava que isso não queria dizer metade da aplicação pronta, porque a metade que faltava era a das regras de negócio, bem mais complexa. Vale igual pra quem mede produtividade de IA por linha de código ou por percentual de código gerado.

### Padrão e arquitetura antes da geração

O gerador só funcionava bem porque tinha uma arquitetura definida, regras de mapeamento e responsabilidades claras pra cada artefato. No asSAI, publicar e documentar todos os métodos resultou em menos código replicado e mais independência entre os desenvolvedores. Com agentes de código é a mesma coisa: sem padrão e contexto, cada geração sai de um jeito.

### O que mudou de verdade

Um gerador baseado em template é determinístico: a mesma entrada dá sempre a mesma saída, e por isso eu podia dizer que os artefatos gerados precisavam de menos teste. Com um modelo de linguagem isso não vale, a saída varia, então revisão e teste do que foi gerado ficam mais importantes, não menos. Em compensação, o limite do template sumiu: a IA gera também a regra de negócio e as visões, que eram justamente o que o ClassGenerator deixava pra mão.

E um detalhe que eu acho engraçado: na lista de trabalhos futuros de 2005 tem "adicionar inteligência computacional na geração das interfaces". Demorou um pouco, mas chegou 🙂

## Ficha

- Título: ClassGenerator: Um Gerador de Artefatos Multiplataforma
- Autor: Marcelio D'Oliveira Leal
- Orientador: Prof. Dr. Eloi Luiz Favero
- Banca: Prof. Dr. Eloi Luiz Favero, Prof. Msc. Alfredo Braga Furtado e Prof. Esp. Osiel Marlon Negrão da Silva
- Bacharelado em Ciência da Computação, Universidade Federal do Pará, Belém. Aprovado em 11 de fevereiro de 2005.

A tradução em inglês foi feita em 2026 com ajuda de IA. As figuras e as listagens de código são as do original.

This page is also available [in English](https://marcelioleal.com/en/thesis-classgenerator/).
