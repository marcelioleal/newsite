---
title: 'Undergraduate Thesis — ClassGenerator: A Multiplatform Artifact Generator'
date: '2026-11-21T01:38:28'
slug: thesis-classgenerator
wp_id: 1592
translationKey: tcc-classgenerator
---

In February 2005 I defended my undergraduate thesis in Computer Science at the Federal University of Pará (UFPA), in Belém, Brazil, advised by Prof. Dr. Eloi Luiz Favero. It was about ClassGenerator, a tool I'd been using since 2001 to generate a good part of an information system from its database schema.

Here's a summary of the work, the PDF if you want to read all of it, and why I think a topic that looked like a 2000s thing is back now that AI writes code.

- [English translation (PDF, 73 pages)](/images/2026/11/ClassGenerator-Thesis-EN.pdf)
- [Original thesis in Portuguese (PDF, 76 pages)](/images/2008/08/tccfinal.pdf)

## What ClassGenerator is

ClassGenerator puts three things in one tool: a code generator, an artifact generator and a framework. It was written in PHP with MySQL, it runs in the browser, and the process starts from a database schema. From there it generates:

- basic classes (one per table, with getters and setters);
- business classes, in a three-tier architecture with the Facade pattern (Fachada, Cad and CadBD), which make the object-relational mapping transparent to whoever writes the business rules;
- web interfaces to create, edit, delete, list and show each entity, in XHTML with CSS (tableless) and JavaScript validation kept apart from the HTML;
- code documentation.

The classes could come out in PHP, Java or Python. The first run already gives you a working prototype, which can become the base of the system or just help refine requirements with the customer. You aren't locked in: you can keep maintaining the artifacts through the tool (registering new methods with their SQL, parameters and return type) or take the generated code and move on.

## The ideas behind it

The work starts from Fred Brooks's "No Silver Bullet", which splits software development into essential activities (creating the conceptual model of the system) and accidental ones (implementing that model in a program). ClassGenerator's goal was to improve the accidental ones directly, so there's more time and attention left for the essential ones: specification, design and testing.

The second chapter goes through the "possible silver bullets" of the time (object orientation, aspects, agile methodologies, frameworks, generators, design patterns, RAD, components, free software) and argues that none of them solves it alone; what works is a good combination. It also separates two things many people treat as the same: a code generator, which gives you a base and leaves you with it, and an artifact generator, where maintenance always happens in the high-level specification and never in the generated files.

## The case studies

There are three real systems in the thesis:

- SAPP, a system to support personal pages (it ran my own site back then): about 90% of the application was generated.
- asSAI, a customs system that controls the activities of a port, with 70 to 90 entities, built by a team at Abstract: about 50% of the code was generated.
- Portal da Amazônia (a portal for knowledge about the Amazon): between 30 and 40% of the system, with ClassGenerator used only as a code generator, next to a part built in MVC.

That's where the metric in the thesis comes from: 70 to 90% for simple systems, 50 to 65% for normal ones and 20 to 30% for complex ones, with many business rules and many views.

## Why this is current with AI generating code

Reading it again more than twenty years later, what gets me is that the questions are the same ones we're asking today. Only the generator changed.

### The specification as the source of truth

The definition of an artifact generator I used there, always maintain the specification and never the generated file, is pretty much what people now call spec-driven development: the specification is the source of truth and the code is an artifact generated from it. A [2026 paper on the topic](https://arxiv.org/abs/2602.00180) describes it as an old idea that AI coding assistants brought back. In 2005 the "spec" was the database schema plus a registry of methods. Today it's a text document that an agent reads.

### The accidental got cheap, the essential is still on us

ClassGenerator went after the repetitive implementation work. Language models do that at a scale I couldn't imagine, for any language and with no templates. But the essential part, understanding the problem and deciding what to build, is still the bottleneck, just like Brooks said in 1986.

### Generated code isn't a finished system

In asSAI the tool generated half of the code, and the thesis already warned that this didn't mean half of the application was done, because the missing half was the business rules, which were much more complex. The same goes for anyone measuring AI productivity by lines of code or by the percentage of code generated.

### Standards and architecture before generation

The generator only worked well because it had a defined architecture, mapping rules and clear responsibilities for each artifact. In asSAI, publishing and documenting every method led to less duplicated code and more independence between developers. It's the same with coding agents: without standards and context, every generation comes out differently.

### What really changed

A template-based generator is deterministic: the same input always gives the same output, which is why I could say the generated artifacts needed less testing. That doesn't hold for a language model. The output varies, so reviewing and testing what was generated matters more, not less. On the other hand, the template limit is gone: AI also generates the business rules and the views, which were exactly what ClassGenerator left to be done by hand.

And one detail I find funny: the future work list from 2005 includes "adding computational intelligence to the generation of interfaces". It took a while, but it got here 🙂

## Details

- Title: ClassGenerator: Um Gerador de Artefatos Multiplataforma (ClassGenerator: A Multiplatform Artifact Generator)
- Author: Marcelio D'Oliveira Leal
- Advisor: Prof. Dr. Eloi Luiz Favero
- Committee: Prof. Dr. Eloi Luiz Favero, Prof. MSc. Alfredo Braga Furtado and Prof. Esp. Osiel Marlon Negrão da Silva
- Bachelor's in Computer Science, Federal University of Pará (UFPA), Belém, Brazil. Approved on February 11, 2005.

The English translation was made in 2026 with the help of AI. The figures and code listings are the ones from the original, so their labels are in Portuguese.

Esta página também está disponível [em português](https://marcelioleal.com/tcc-classgenerator/).
