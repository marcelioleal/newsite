---
title: E o MySQL continua indo bem…
date: '2008-02-14T16:09:32'
slug: e-o-mysql-continua-indo-bem
wp_id: 53
---

Mesmo após o anúncio de venda da [MySQL AB](http://www.mysql.com/) pra [SUN](http://www.sun.com) o MySQL continua evoluindo em um caminho bem interessante. 🙂

Uma das coisas mais estailes que eu acho do MySQL, além dele funcionar perfeitamente, é a flexibilidade na escolha da [storage engine](http://en.wikipedia.org/wiki/Database_engine), onde eu ficava alternando entre [MyISAM](http://en.wikipedia.org/wiki/MyISAM) e [InnoDB](http://en.wikipedia.org/wiki/InnoDB).

[Neste artigo](http://blog.cidandrade.pro.br/database/mysql-movido-a-maria-novo-engine/) do [blog do Cid Andrade](http://blog.cidandrade.pro.br/), ele explica um pouco mais sobre este aspecto e fala um pouco sobre o [novo storage engine](http://blog.cidandrade.pro.br/database/o-storage-engine-maria-do-mysql-em-detalhes/) disponível a partir da versão 6 do MySQL.

Em resumo:

"Maria is a crash safe, non-transactional version of MyISAM. The Maria storage engine supports all of the main functionality of the MyISAM engine, but includes recovery support (in the event of a data crash), full logging (including CREATE, DROP, RENAME and TRUNCATE operations), all MyISAM row formats and a new Maria specific row format."

Mais detalhes podem ser vistos na [documentação](http://forge.mysql.com/wiki/Maria_Docs).
