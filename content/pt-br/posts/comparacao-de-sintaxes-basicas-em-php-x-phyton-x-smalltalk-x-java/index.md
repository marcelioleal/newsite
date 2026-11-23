---
title: Comparação de sintaxes básicas em PHP X Phyton X Smalltalk X Java
date: '2007-09-03T03:53:08'
slug: comparacao-de-sintaxes-basicas-em-php-x-phyton-x-smalltalk-x-java
wp_id: 11
categories: [software-dev]
---

Tudo começou no blog [batteries not included](http://blog.danielfmartins.com) com o post sobre [Smalltalk X Java](http://blog.danielfmartins.com/2007/05/07/smalltalk-x-java/). Neste post são apresentados trechos de códigos básicos nas linguagens [Java](https://pt.wikipedia.org/wiki/Java_(linguagem_de_programa%C3%A7%C3%A3o)) e [Smalltalk](https://pt.wikipedia.org/wiki/Smalltalk), fazendo um comparativo entre as vantagens das sintaxes entre as linguagens. O resultado ficou subjetivo, mas com leve vantagem para a sintaxe do Smalltalk, embora os exemplos em Java pudessem ser melhorados, conforme foi descrito nos comentários.

Depois o negócio foi pro [Fecha Tag](http://blog.elcio.com.br/), por sinal um belo blog. Lá o autor escreveu um [post](http://blog.elcio.com.br/python-x-java-x-smalltalk/) com os exemplos em [Phyton](https://pt.wikipedia.org/wiki/Python).

Os exemplos comparados foram:

- Fatorial
- Listar números de 0 à 10
- Imprimir Colections
- Mostrar pares e ímpares entre 1 e 10
- Invocar métodos via Reflection

Nas comparações feitas entre o Smalltalk(vencedor do primeiro confronto) e o Phyton, ficam as minhas seguintes conclusões:

- As implementações são bastantes parecidas
- A simplicidade do Phyton é um pouco superior e elegante
- Em Smalltak [Reflection](https://en.wikipedia.org/wiki/Reflection_%28computer_science%29) é muito style

Nos comentários do fecha tag o leitor [Fábio](http://blog.elcio.com.br/python-x-java-x-smalltalk/#comment-54121) implementa os exemplos em [PHP](https://pt.wikipedia.org/wiki/PHP), abaixo transcrevo os códigos com uma modificação no fatorial.\
FATORIAL

function factorial(\$n) {\
if(\$n \>0) return \$n\*factorial(\$n-1);\
elseif(\$n ==0) return 1;\
else return 0;\
}

ou

function factorial(\$n) {\
return (\$n \> 0)?\$n\*factorial(\$n-1):((\$n==0)?1:0);\
}

Listar Números\
foreach(range(0, 10) as \$n)\
print \$n;

Collections\
\$l = array ('Em PHP,','chamamos as','collections','de "arrays"',);\
echo implode(\$l, "\n");

ODD/EVEN\
foreach(range(0, 10) as \$n)\
echo (1 & \$n) ? "\$n is odd, " : "\$n is even, ";

Reflection\
\$o = new ReflectionClass('MyClass');\
\$o-\>newInstance()-\>showMessage();

Um dia desses conversando com o meu amigo [Antonio Fonseca](http://antoniofonseca.wordpress.com/) sobre linguagens, mais especificamente sobre Phyton e sua simplicidade e elegância. Sem dúvida Phyton é simples e elegante, mas esses fatores não colocam essa linguagem acima do PHP ou do [Ruby](https://pt.wikipedia.org/wiki/Ruby_(linguagem_de_programa%C3%A7%C3%A3o)), pois cada linguagem tem seu principal ramo de aplicação trazendo a tona os seus principais benefícios e simplicidades.

Com estas implementações fica claro que em termos de simplicidade, Phyton e PHP se equivalem. Talvez em estilo alguns gostem mais de uma ou outra linguagem. Particularmente, existem pontos da sintaxe melhor em uma ou outra linguagem, o que, na minha opinião, as deixam num mesmo patamar.

Mas ainda vou fazer duas camisas com essas frases abaixo, só pra descrontrair:

*"Toda Linguagem decente tem ;"*

*"Toda variável é String até que se prove o contrário"*
