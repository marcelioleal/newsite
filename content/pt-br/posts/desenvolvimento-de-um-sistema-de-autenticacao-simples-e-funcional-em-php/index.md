---
title: Desenvolvimento de um sistema de autenticação simples e funcional em PHP
date: '2007-11-17T00:19:57'
slug: desenvolvimento-de-um-sistema-de-autenticacao-simples-e-funcional-em-php
wp_id: 36
---

Um sistema de autenticação é parte da maioria dos sistemas. Um desenvolvedor ou instituição deve ter pelo menos uma base para utilização de um sistema desta natureza para que não perca muito tempo neste requisito.

Este post/tutorial/artigo apresenta uma solução simples de sistema de autenticação desenvolvida em [PHP](http://www.php.net). Esta solução é interessante para sistemas pequenos ou soluções rápidas. Também é interessante para que iniciantes assimilem conceitos importantes sobre desenvolvimento de sistemas web e segurança.

**1. Os Requisitos do Sistema**

Segurança é um sub-sistema onde, geralmente, os erros custam são mais caros. Portanto, deve-se ter mais cuidado para se implementar corretamente todos seus requisitos.

Lista de Funcionalidades básicas

- Login - autênticação
- Cadastro de Usuários
- Reset de Senha
- Controle de Acesso à páginas/funcionalidades

Não iremos detalhar muitos cada um dos requisitos e iremos implementar o básico. O sistema pode ser evoluido muito ainda.

**2. Modelo de Dados**

O Modelo de Dados desenvolvido é muito simples, no decorrer do post vamos explicar como utilizá-lo de forma melhor.

\
*Figura 1 - Modelo de Dados.*

Para baixar o modelo de dados desenvolvido no [DBDesigner](http://fabforce.net/dbdesigner4/) é só clicar [aqui](http://2.download-1.files-upload.com/50/2007/11/15/22-40/0/model.xml).

As senhas serão armazenadas utilizando o algoritmo de encriptação [MD5](http://pt.wikipedia.org/wiki/MD5).

**3. Projeto**

Vamos utilizar o [Classgenerator](http://codigolivre.org.br/projects/classgenerator/), [gerador de artefatos](http://www.lbd.dcc.ufmg.br:8080/colecoes/sbes/2001/020.pdf), para criar a base do projeto. O que envolve a arquitetura e código inicial.

Veja mais sobre o Classgenerator na [Apresentação no FISL 2007.](http://marcelioleal.com/files/2007/11/app.pdf "Classgenerator")

A arquitetura utilizada é a apresentada na figura 2.



*Figura 2 - Arquitetura do sistema gerado pelo Classgenerator.*

Nesse artigo não irei entrar em maiores detalhes sobre o Classgenerator, mas qualquer dúvida estarei a disposição.

**4. Implementação**

Depois de gerar os artefatos pelo classgenerator, deve-se realizar o básico para a aplicação começar a rodar:

- Descompactar a biblioteca [ADOdb](http://adodb.sourceforge.net/). (fig. 3)
- Configurar a classe Conexão(autenticacao/classes/class.Conexao.php). (fig. 4)
- Configurar o diretório no arquivo templatHeaders (autenticacao/templates/templateHeaders.php). (fig. 5)



*Figura 3 - Pasta classe e adodb.*



*Figura 4 - Classe Conexao - Configuração.*



*Figura 5 - Configuração do templateHeaders.*

Após as atividades básicas de configuração as tarefas serão :

- Desenvolver a tela de login.
- Customizar o cadastro de usuário
- Gerência de usuário.

Existem outras atividades, mas o sistema final deste tutorial/post/artigo vai estar incompleto é só customizar para cada situação.

Não é o objetivo deste tutorial mostrar boas técnicas e bom gosto no layout. Realmente acho essa uma tarefa bem mais difícil. 🙂

**Tela de Login**

A tela de login é bastante simplificada conforme a figura 6.



*Figura 6 - Tela de Login*.

O código HTML da tela de login é bastante simples e submete os dados para a mesma página "**index.php**" .



O código que processa a requisição é o seguinte:



Incluimos a classe *FrontController* que inclui os métodos de login e de permissão de cada página. Na linha 7 verificamos se o valor do botão *btnLogin* foi submetido, posteriormente chamamos o método *login* passando o login e a senha digitada. Neste ponto seria seguro utilizar HTTPS para que os dados fossem enviados encriptados.

Abaixo o código do método *login* na classe *FrontController*.



Na linha 25 chamamos o método *loginUser* da classe *Fachada*, que a interface única com o BD. Esse método recebe como parâmetros o login e a senha encriptada(utilizando o md5). O método *Util::forString()* (método stático - para saber mais [clique aqui](http://www.php.net/manual/pt_BR/keyword.paamayim-nekudotayim.php)) formata a string para formar o SQL.

Se o retorno do método *loginUser* for um objeto então os seguintes passos são executados:

- Atribuir o objeto para uma variável de sessão.
- Redirecionar o usuário para a sua página home de acordo com o seu grupo de usuário.

A classe *Constante* encapsula os valores fixos do *userGroup* e do nome da página home de cada usuário. Abaixo um techo com os dois principais métodos da classe.



É muito interessante utilizar uma classe do estilo da *Constante* pois centraliza os valores constantes da aplicação, facilitando a evolução e manutenção.

Abaixo uma parte da classe *User*, que é uma classe básica(ou bean no Java). Tem apenas os métodos get, set e métodos afins.



O método *loginUser* na classe *Fachada* é simplesmente a chamada do mesmo método na classe *CadUser*. Realizando apenas a função de ser a interface única com o BD.



Na classe *CadUser* a implementação do método *loginUser* chama o método correspondente na classe *CadUserBD* e trata o seu retorno. Caso seja positivo, retorna um objeto do tipo *User*, caso não seja positivo o resultado retorna false.



Na classe *CadUserBD* o SQL é montado e executado. O SQL verifica, além do login e da senha, o status do usuário. Depois de sua execução é retornado um registro da tabela user ou um registro vazio.



Após o login, o usuário é redirecionado para sua página home correspondente. Abaixo o código da página home do administrador.



A página é bastante simples também:

- Na linha 2 incluimos a classe FrontController, que faz a inclusão das demais classes que utilizaremos.
- Na linha 3 iniciamos a sessão para que possamos utilizar os valores adicionados nela.
- Na linha 5 instânciamos a classe FrontController.
- Na linha 6 chamamos o método allowPage(), que permite ou não a visualização da página.

Bastam esses passos para todas as páginas para se garantir que os usuários só acessarão as páginas que os mesmos têm permissão.

Abaixo o código do método allowPage.



A primeira verificação é se existe o usuário na sessão. Posteriormente é extraído a url e chamado o método allow da classe UserGroupPages. Este método retorna true se houver permissão para visualização pelo grupo do usuário.

Esta é apenas uma das maneiras mais simples de se realizar isso, dependendo dos requisitos do sistema ela deve ser evoluida.

Abaixo um trecho da classe UserGroupPages.



**Refactoring**

Em muitos casos temos sistemas de autenticação muito falhos e incompletos. Nestes casos é indicao um refactoring no código para que todas as regras de permissão sejam obedecidas.

É muito interessante utilizar uma abordagem como essa pois o método chamado na FrontController não possui parâmetros diferentes para cada página, tornando mais fácil essa modificação em todas as página.

Indico a construção de um software que insira as linhas de 2 à 6 da página homeAdm(home do Administrador) como as primeiras linhas de cada página com acesso restrito e que sejam definidas as regras na classe UserGroupPages.

**Conclusão**

É realmente simples desenvolver uma aplicação reutilizável para controle de acesso e autênticação em PHP. Recomendo que seja dedicado um pouco mais de tempo para esta função com o objetivo de se fazer um sistema reutilizável.

Existem outras arquiteturas e implementações para estes tipos de sistema. O objetivo foi mostrar como funciona basicamente esta tarefa.

Este código executa em PHP 4 e 5. E segue a orientação a objetos do PHP 4. Não há muita diferença para implementações que seguem o PHP 5. Em termos funcionais é bem pequena a diferença.

**Arquivos**

Para baixar os arquivos do exemplo clique abaixo:

- [Sistema.](http://rapidshare.com/files/112002880/autenticacao.zip.html)
- [SQL e Banco.](http://rapidshare.com/files/112003290/doc.zip.html)

**Dúvida, Sugestões e Correções**

Mail-me marcelio \[at\] gmail \[ponto\] com

**Outros artigos**

[Sistema de Login com PHP orientado a objetos](http://maozinhadaweb.blogspot.com/2007/06/sistema-de-login-com-php-orientado.html) - Bruno Nunes
