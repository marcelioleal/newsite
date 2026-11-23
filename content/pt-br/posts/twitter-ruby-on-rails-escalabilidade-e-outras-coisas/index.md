---
title: Twitter, Ruby on Rails, Escalabilidade e outras coisas…
date: '2008-05-05T20:36:14'
slug: twitter-ruby-on-rails-escalabilidade-e-outras-coisas
wp_id: 80
categories: [software-dev]
---

Pela lista [PHP-MG](http://groups.google.com.br/group/phpmg) vi a notícia que o [Twitter](https://twitter.com/) (grande case em [Ruby on Rails](http://www.rubyonrails.org/)) estava pensando em migrar para outra plataforma: PHP ou Java.

O principal motivo, segundo a notícia, seria a estabilidade e a [escalabilidade](https://pt.wikipedia.org/wiki/Escalabilidade)(A Wikipedia não é o melhor lugar para se um conceito aplicado à este caso, mas em todo caso tá linkado) da plataforma/framework.

O [Blog PHPZine](http://www.php-zine.net/2008/05/05/twitter-pretende-abandonar-rails/) explica bem o caso e cita a notícia inicial no [Techcrunch.](http://www.techcrunch.com/) Só discordo quando ele diz que o Ruby on Rails é um divisor de águas. De fato, a sintaxe do [Ruby](https://pt.wikipedia.org/wiki/Ruby_(linguagem_de_programa%C3%A7%C3%A3o)) é muito show, porém o Rails não é, e nem foi, algo revolucionário. Muitos outros frameworks e geradores de artefato já executavam a mesma idéia. Porém, ele realmente se tornou o mais famoso e público caso de sucesso destes tipos de aplicações.

No [blog do Akita On Rail](http://www.akitaonrails.com/2008/5/2/a-est-pida-controv-rsia-twitter), ele cita que já foi desmentido esta afirmação e complementa seu artigo expondo seus argumentos em favor da tecnologia. Cito aqui duas afirmações que comento logo abaixo.

A primeira é que escalabilidade é um mito e que qualquer coisa escala. De fato isso não é verdade. Escalabilidade é um requisito não-funcional que envolve custo-benefício, portanto, depende do ambiente que está configurado para aplicação, em especial, as restrições para este ambiente. A escalabilidade tembém varia de acordo com o objetivo do sistema. Portanto, a escalabilidade é um conceito que depende de contextualização.

É um fato que PHP precisa de menos hardware para aplicações Web que JAVA, ou seja, em condições iguais de hardware (hardware limitado - "servidores reais") e aplicações normais, PHP é mais escalável. Porém essa afirmação pode ser contextada quando precisamos de transações assíncronas, temos maior hardware (grandes servidores SUN), etc.

[Jon Udell](https://www.infoworld.com/archives/emailPrint.jsp?R=printThis&A=/article/04/08/13/33FEmyth6_1.html) já havia falado sobre isso, porém é importante dizer que ele não quis afirmar que todas as coisas são escaláveis, mas que não podemos afirmar, como geralmente se afirma, que determinada plataforma não é escalável sem contextualizar.

Outro aspecto importante é se os frameworks influenciam na escalabilidade. É claro que sim, porém menor escala que a plataforma. De fato, não é só trocando o framework que teremos resolvido a maioria dos problemas, porém ele podem de fato ter uma influência direta na performance/escalabilidade. Há algum tempo atrás conversando com o colega [Aldrin Leal](http://www.leal.eng.br/mnemetica/), discutiamos sobre o overhead que o [hibernate](http://www.hibernate.org/) adicionava em uma aplicação. Nesta ocasião ele fez alguns testes mudando a máquina virtual, compilando o código, etc. E conseguiu resultados bem melhores que as configurações iniciais.

Da mesma maneira faz diferença, em alguns casos, utilizar o padrão [Active Record](http://martinfowler.com/eaaCatalog/activeRecord.html) e o [Data Mapper](http://martinfowler.com/eaaCatalog/dataMapper.html), que são padrões, que geralmente, estão encapsulados pelos frameworks.
