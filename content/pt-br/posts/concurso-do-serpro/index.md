---
title: Concurso do SERPRO
date: '2008-12-13T20:15:02'
slug: concurso-do-serpro
wp_id: 102
categories: [software-dev]
---

Neste último domingo fiz a prova do concurso do SERPRO realizado pelo CESPE.

Nunca tinha visto uma prova de concurso tão mal feita. Muitas questões "baseadas" na Wikipedia em português.

Já é sabido que a Wikipedia é uma fonte de informações que tem o objetivo de apenas informar superficialmente os leitores, bem como não há confiabilidade nas suas fontes de informação Assim, não se pode referenciar as informações contidas na Wikipedia em nenhum lugar que utilize informações formalmente, por exemplo, concursos, artigos, trabalhos acadêmicos.

Em diversos fóruns na internet as pessoas estão discutindo a prova, aqui apresento algumas argumentações sobre a prova. Se os avaliadores dos recursos que foram enviados forem razoavelmente sensatos pelo menos 12 questões terão suas respostas modificadas ou anuladas, ou seja, pelo menos 10% da prova deve ser modificada.

A prova do SERPRO para o cargo de Especialização em Desenvolvimento de Sistemas pode ser baixada <a href="http://www.cespe.unb.br/concursos/SERPRO2008/arquivos/SERPRO_CARGO_05.pdf" target="_blank" rel="noopener noreferrer">aqui</a>.

Questões

Como eu já havia dito, são várias as questões mal elaboradas na prova, porém vou me deter apenas as questões de conhecimentos específicos.

As primeiras 12 questões foram de Segurança da Informação. Realmente muitas questões para este importante tópico, mas uma prova que não tem nenhuma questão de CMMI, MPS.BR, RUP e 1 de UML, leva a crer que foram muitíssimas questões de Segurança de Informação.

Só de normas e políticas de Segurança de Informação foram 4. Normas tais que dificilmente são utilizadas diretamente por Desenvolvedores, talvez mais úteis pra Administradores, Gerentes, Coordenadores, cargos tais que tinham outras provas.

Depois foram mais 5 questões de modelo de ciclo de vida de software. Com destaque (negativo) pra uma questão básica de cascata, uma questão confusa de modelo incremental e outra de modelo orientado à reuso (que é totalmente inútil com o advento do processo de reutilização que compõe os modelos de processo CMMI, MPS.BR, etc.).

As questões até aqui não foram polêmicas.

Tivemos 10 questões de Banco de Dados. A maioria muito mal feita.

A questão 69 fala sobre o PostgreSQL e afirma que é um modelo em código aberto que tem como base o modelo de desenvolvimento bazar. Tudo bem que eles queriam misturar os conceitos, mas falar que o Postgre é um modelo em uma prova de concurso é no mínimo polêmico.

A questão 70 afirma:

"MySQL é um SGBD relacional para sistemas proprietários que não funciona em sistemas operacionais livres como o Linux."

Sem dúvida a questão mais idiota que eu vi em um concurso. O edital do concurso responde a questão. Lá é afirmado que o tópico pra estudo é: MySQL para Linux. Uma vergonha essa questão.

A questão 71 é alvo de vários recursos:

"O XML é uma linguagem de marcação que, entre outras funções, interliga bancos de dados distintos de maneira hierárquica. "

As principais argumentações para a anulação da questão são:

- A questão leva a pensar que a interligação é hierárquica e não a linguagem XML.
- Não é possivel dizer nada acerca da interligação entre os bancos distintos apenas por usar a linguagem XML para fazer esta ligação, portanto fica-se sem subsídio para se responder esta questão.

A questão 72 erra a sigla SGBD e escreve SGDB. Não percebi isso na prova, mas o pessoal percebeu isso na net.

As demais questões de Banco de Dados focam diversos aspectos, uma nota ruim é o foco em modelos já ultrapassados em contrapartida a modelos mais atuais.

Posteriormente temos 22 questões de tecnologia: servidores, linguagens e frameworks.

A questão 78 pode ser respondida pelo edital também, já que nela há a afirmação que Phyton é o SGBD do Zope.

A questão 81 fala sobre o Tomcat e afirma que este é um servidor de aplicação. Afirmação tal que gerou muita polêmica, principalmente entre os desenvolvedores Java. Mas ela tem um erro claro de digitação em uma palavra que não deveria ter: **JavServer** Pages (JSP). Acho que isso vai ser o suficiente para anulá-la

A questão 82 tem um erro de ortografia (esqueceram uma vírgula) que mata a questão:

"C++ é uma linguagem de programação**<span style="text-decoration:line-through;">,</span>** orientada a objetos, de primeira geração."

A questão 83 é a que tem mais erros (por ser copiada da Wikipedia?):

"A linguagem Java, orientada a objetos, tem como característica ser compilada em um código executado em máquina virtual."

Dentre os erros pode-se citar:

- O correto seria compilado para um código, e não em um código.
- Uma máquina virtual não pode executar nenhum código, quem executa é a UCP do computador. A máquina virtual Java interpreta o bytecode gerado para código de máquina, este sim executado pela UCP (unidade Central de processamento).
- A linguagem Java é uma linguagem interpretada por padrão, a questão leva o candidato à entender que ela é compilada. (compilada + executada e não compilada + interpretada)
- A linguagem Java pode ser compilada para código de máquina sem precisar da máquina virtual com o GCJ \[1\]. \[1\] <a href="http://gcc.gnu.org/java/" target="_blank" rel="noopener noreferrer">http://gcc.gnu.org/java/</a> .

Acho que ela vai ser anulada mesmo.

A questão 85 é sobre Phyton novamente:

"Python é uma linguagem livre de alto nível, orientada a objetos e de difícil leitura, pois não permite identação de linhas de código. "

Podiam ter citado qualquer característica de Phyton, mas não... Citaram a mais conhecida.

A questão 86 é sobre Ruby. Achei a melhor questão da prova:

"A Ruby é uma linguagem orientada a objetos, com sintaxe de fácil leitura e tipagem dinâmica e forte."

A questão 90 é sobre Ajax:

"O Ajax basicamente oferece uma metodologia para desenvolvimento de aplicações na Web que une Javascript e XML, mas que só pode ser executado em browsers lançados após 2001."

Altamente copiada da Wikipedia em Português. Até a Wikipedia em inglês diz algo diferente, nem isso se deram ao trabalho de observar. Existem várias informações controversas quanto ao ano que o Internet Explorer suportou Ajax. Enfim, acho que ela deveria ser anulada também.

Depois disso vem uma série de questões de Java. Acho que deveriam aproveitar melhor a prova com questões mais bem elaboradas, com códigos, diagramas, etc.

A questão 99 é sobre GTK, mas gera um absurdo. Afirma que o GTK é feito em Java. GTK é leve, Java pesado, portanto questão errada. 🙂

A partir da questão 101 vem uma série de questões pra descontrair quem fez a prova. Estas questões foram feitas pra ter certeza que o candidato não poderia zerar a prova.

Uma passada rápida pelas questões:

"UML (**universal** modelling language) é uma linguagem de modelagem **proprietária ...**"

"A modelagem de processos **burocráticos**, ou BPM, ... alinhar esses processos, otimizando-os e tornando-os mais eficientes, sem **burocracia**."

Essa linguagem faz mágica!!!

A questão 103 tem indícios de que foi baseada na Wikipedia também. Foi a única referência pra justificar que a afirmação está errada:

"A modelagem lógica de banco de dados tem como base a construção de um diagrama de entidade e relacionamento."

A questão 104 teve um erro de tradução:

"LDD e **LDM** são linguagens usadas para definir esquemas e formas de manipulação de dados."

LDM ? Linguagem Dados Manipulação ? uhm...

A questão 105 a afirmação é se PL/SQL(Procedural Language /SQL ) não é uma linguagem procedural. Uhm... Talvez 🙂

As próximas questões apresentam fases de um processo de desenvolvimento de software e há também uma de Swebok, que por sinal não aparece no edital do concurso.

As questões de processo estão todas descontextualizadas em relação aos modelos de qualidade de processo de desenvolvimento de software como CMMI, MPS.BR e ISO 12207.O erro mais gritante destas acontece na questão que trata de gerenciamento de requisitos.

"O gerenciamento de requisitos inclui, entre outras, as seguintes atividades: levantar, analisar, especificar, validar e prototipar requisitos funcionais e não-funcionais."

Houve uma clara confusão entre Engenharia de Requisitos e Gerência de Requisitos, talvez influenciada pela Wikipedia. A gerência de requisitos não inclui especificação e prototipação, pelo menos não nos modelos de qualidade.

Depois temos as questões de padrões de projeto. Questões relativamente bem feitas, com exceção da questão que trata de polimorfismo.

"No polimorfismo, que é um tipo de padrão GRASP, um mesmo método pode apresentar várias formas."

Sei que a intenção não foi essa, mas um método não pode apresentar várias formas de forma nenhuma. Polimorfismo é o princípio pelo qual duas ou mais classes derivadas de uma mesma superclasse podem invocar métodos que têm a mesma identificação (assinatura) mas comportamentos distintos, especializados para cada classe derivada, usando para tanto uma referência a um objeto do tipo da superclasse.

As demais questões fala de duas normas ISO, computação em grade (grid), SOA e datawharehouse (ops datawarehouse, mas estava escrito errado na prova.).

Enfim, uma prova muito mal elaborada. Podia ter sido utilizada para selecionar melhores funcionários para o SERPRO, mas não sei se isso vai acontecer, espero que sim.

PS.: Desculpem a falta de links, mas o post ficou muito grande e muito trabalhoso pra linkar as coisas...
