---
title: Queries em PHP – Operações assíncronas, paralelas e em backgroud.
date: '2007-11-20T01:53:36'
slug: queries-em-php-operacoes-assincronas-paralelas-e-em-backgroud
wp_id: 38
categories: [software-dev]
---

O PHP puro não suporta atividades paralela. No caso geral dos Banco de Dados(BD), o PHP fica bloqueado enquanto o BD executa a query. A forma e o tempo desse bloqueio depende da interface do BD.

No caso do MySQL, o bloqueio é até o fim do cálculo do resultado da query(unbuffered results, Prepared Statements) ou até tenha sido calculado e todos os resultados tenham sidos transferidos para o PHP(buffered results).

Esse [post](http://blog.ulf-wendel.de/?p=170) do blog "Internet Super Hero" apresenta uma forma de utilizar o paralelismo em backgroud de maneira transparente em PHP com a nova interface mysqlnd. O que, em alguns casos, melhora consideravelmente a execução de queries consecutivas em PHP/MySQL.

Abaixo uma figura de como funciona o novo processo paralelo.

<img src="/images/external/blog.ulf-wendel.de/background_fetch.gif" decoding="async" />

Muita onda!!!
