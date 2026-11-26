---
title: Viagem pra Belém
date: '2024-03-08T14:47:35'
slug: viagem-pra-belem
wp_id: 151
translationKey: viagem-pra-belem
---

Belém é minha cidade natal. Essa página junta os lugares em que eu sempre volto quando chego — restaurantes, cafés, bares e os clássicos imbatíveis de tacacá e açaí.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
<div id="belem-map" style="height:440px;width:100%;border:1px solid var(--border);border-radius:8px;margin:1.8em 0;background:var(--entry);"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function(){
  if(!document.getElementById('belem-map')||!window.L)return;
  L.Icon.Default.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
  var r=[
    ['Casa do Saulo — Onze Janelas','Cidade Velha',-1.4572,-48.5058,'https://www.google.com/maps/search/?api=1&query=Casa+do+Saulo+Onze+Janelas+Rua+Siqueira+Mendes+Cidade+Velha+Belem'],
    ['Remanso do Peixe','Marco',-1.4379,-48.4548,'https://www.google.com/maps/search/?api=1&query=Remanso+do+Peixe+Travessa+Barao+do+Triunfo+2590+Belem'],
    ['Puba Bar','Cidade Velha',-1.4645,-48.5001,'https://www.google.com/maps/search/?api=1&query=Puba+Bar+Rua+Veiga+Cabral+649+Cidade+Velha+Belem'],
    ['Shinko Sushi','Humaitá / Vileta',-1.4392,-48.4633,'https://www.google.com/maps/search/?api=1&query=Shinko+Sushi+Travessa+Vileta+2501+Belem'],
    ['Armazém Belém','Shopping Boulevard',-1.4463,-48.4897,'https://www.google.com/maps/search/?api=1&query=Armazem+Belem+Shopping+Boulevard+Avenida+Visconde+de+Souza+Franco'],
    ['Mousi Café','Piedade 45 (Reduto)',-1.4499,-48.4939,'https://www.google.com/maps/search/?api=1&query=Mousi+Cafe+Travessa+Piedade+Reduto+Belem'],
    ['Amazon Deli','Braz de Aguiar',-1.4543,-48.4843,'https://www.google.com/maps/search/?api=1&query=Amazon+Deli+Avenida+Bras+de+Aguiar+400+Belem'],
    ['Muamba Bar','Vila Container (Umarizal)',-1.4473,-48.4875,'https://www.google.com/maps/search/?api=1&query=Muamba+Bar+Vila+Container+Belem'],
    ['Marcelino Café','Braz de Aguiar',-1.4555,-48.4835,'https://www.google.com/maps/search/?api=1&query=Marcelino+Cafe+Avenida+Bras+de+Aguiar+653+Belem']
  ];
  var map=L.map('belem-map',{scrollWheelZoom:false}).setView([-1.4530,-48.4850],13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',maxZoom:19}).addTo(map);
  var g=L.featureGroup();
  r.forEach(function(x){
    var html='<strong>'+x[0]+'</strong><br><span style="color:#6b7280;font-size:12px">'+x[1]+'</span><br><a href="'+x[4]+'" target="_blank" rel="noopener">Abrir no Google Maps →</a>';
    g.addLayer(L.marker([x[2],x[3]]).bindPopup(html));
  });
  g.addTo(map);
  map.fitBounds(g.getBounds().pad(0.08));
})();
</script>

## Culinária paraense

{{% place name="Casa do Saulo ★" bairro="Cidade Velha" highlight="true" %}}
Comando do chef Saulo Jennings, representa o Pará contemporâneo no melhor cenário possível — os casarões da Cidade Velha. O **filé de pirarucu grelhado no molho de castanha-do-pará com banana da terra e camarão rosa** é obrigatório. Tem duas unidades: **Onze Janelas** (Rua Siqueira Mendes, s/n, Cidade Velha) e **Quinta de Pedras** (Rua Doutor Assis, 834, dentro do Hotel Atrium).

[Instagram](https://www.instagram.com/casadosauloparaoficial/) · [Maps (Onze Janelas)](https://www.google.com/maps/search/?api=1&query=Casa+do+Saulo+Onze+Janelas+Rua+Siqueira+Mendes+Cidade+Velha) · [Maps (Quinta de Pedras)](https://www.google.com/maps/search/?api=1&query=Casa+do+Saulo+Quinta+de+Pedras+Rua+Doutor+Assis+834)
{{% /place %}}

{{% place name="Remanso do Peixe" bairro="Marco" %}}
Família Castanho (Thiago Castanho), referência em peixes amazônicos. Casa simples, cardápio direto: moquecas, caldeiradas, casquinha de caranguejo. Ir no almoço de terça a sábado e no domingo (fecha segunda). Travessa Barão do Triunfo, 2590, Marco.

[Instagram](https://www.instagram.com/remansodopeixe/) · [Maps](https://www.google.com/maps/search/?api=1&query=Remanso+do+Peixe+Travessa+Barao+do+Triunfo+2590+Marco+Belem)
{{% /place %}}

{{% place name="Shinko Sushi" bairro="Humaitá / Vileta" %}}
Japonês perto de casa, Travessa Vileta esquina com 25 de Setembro / Humaitá. Faz o japonês com qualidade brasileira paraense — tem combinados generosos e peixe fresco.

[Maps](https://www.google.com/maps/search/?api=1&query=Shinko+Sushi+Travessa+Vileta+2501+Belem)
{{% /place %}}

{{% place name="Armazém Belém" bairro="Shopping Boulevard" %}}
Fica logo na entrada do Shopping Boulevard. Eu adoro o **café** de lá e o **peixe paraense** é bem feito — vale tanto pra um café da tarde quanto pra um almoço. Padaria também, bom pra um pão fresco.

[Maps](https://www.google.com/maps/search/?api=1&query=Armazem+Belem+Shopping+Boulevard+Avenida+Visconde+de+Souza+Franco)
{{% /place %}}

## Bares que não falham

{{% place name="Muamba Bar ★" bairro="Vila Container (Umarizal)" highlight="true" %}}
**Melhor bar de drinks que eu fui nos últimos anos** e minha parada obrigatória em Belém. Coquetelaria autoral com ingredientes amazônicos sob a batuta do Yvens Penna — tem chicória, cumaru, jambu, bacuri, taperebá no cardápio. O Ariramba (gin com jambu e coentro) e o Urucum Pisco Sour são imperdíveis.

[Instagram](https://www.instagram.com/muamba.bar/) · [Maps](https://www.google.com/maps/search/?api=1&query=Muamba+Bar+Vila+Container+Belem)
{{% /place %}}

{{% place name="Puba Bar" bairro="Cidade Velha" %}}
Projeto do Thiago Castanho e Gustavo Rodrigues. Carta de vinhos única em Belém, drinks autorais, e um cardápio inteiro construído em cima da **mandioca** em todas as formas (puba inclusive). Ter a sáb, 19h–23h30. Rua Veiga Cabral, 649, Cidade Velha.

[Instagram](https://www.instagram.com/pubabar.belem/) · [Maps](https://www.google.com/maps/search/?api=1&query=Puba+Bar+Rua+Veiga+Cabral+649+Cidade+Velha+Belem)
{{% /place %}}

{{% place name="Amazon Beer" %}}
Ótimo chope artesanal e um bom exemplar do **filhote na crosta de castanha** acompanhado de arroz no tucupi.

[Instagram](https://www.instagram.com/amazonbeer/)
{{% /place %}}

{{% place name="Black Dog" %}}
Beba um bom chope e dê um abraço pro meu amigo Iuri.

[Instagram](https://www.instagram.com/blackdoghenglishpubb/)
{{% /place %}}

{{% place name="Cosanostra" %}}
**Melhor carpaccio do mundo.** Pizza ótima e chope super honesto.

[Instagram](https://www.instagram.com/cosanostra_pub/)
{{% /place %}}

## Cafés

{{% place name="Mousi Café ★" bairro="Piedade 45 / Reduto" highlight="true" %}}
Fica no piso do prédio Piedade 45 (onde funcionava a Housi). **Café absurdo de bom** — torrefação da Alquimista, máquina Sanremo Zoe, tudo pensado. Vale o deslocamento mesmo que você não esteja hospedado perto.

[Maps](https://www.google.com/maps/search/?api=1&query=Mousi+Cafe+Travessa+Piedade+Reduto+Belem)
{{% /place %}}

{{% place name="Amazon Deli" bairro="Braz de Aguiar" %}}
Café confort, no sentido literal. Tem presença de casa do bairro — bom pra um café da tarde sem pressa ou pra trabalhar uma manhã. Av. Braz de Aguiar, 400.

[Instagram](https://www.instagram.com/amazon_deli/) · [Maps](https://www.google.com/maps/search/?api=1&query=Amazon+Deli+Avenida+Bras+de+Aguiar+400+Belem)
{{% /place %}}

{{% place name="Marcelino Café" bairro="Braz de Aguiar" %}}
Café pequeno, torra especializada, atendimento bom. O que eu chamo de "competente" — você entra, pede, sai satisfeito. Av. Braz de Aguiar, 653.

[Instagram](https://www.instagram.com/marcelinocafe/) · [Maps](https://www.google.com/maps/search/?api=1&query=Marcelino+Cafe+Avenida+Bras+de+Aguiar+653+Belem)
{{% /place %}}

{{% place name="Delicidade" bairro="Braz de Aguiar" %}}
Nostalgia pura — café com tapioca na sombra das mangueiras. Ver detalhe na [página de cafés](/recomendacoes/cafes/#belém-).
{{% /place %}}

## Tacacá e açaí — os clássicos

{{% place name="Tacacá do Renato (ex-Tacacá do Leandro)" %}}
Ponto clássico de tacacá. [Instagram](https://www.instagram.com/tacacadorenatoficial/)
{{% /place %}}

{{% place name="Point do Açaí" %}}
[Instagram](https://www.instagram.com/pointdoacaibelem/)
{{% /place %}}

{{% place name="Bliss" %}}
[Instagram](https://www.instagram.com/bliss.belem/)
{{% /place %}}

## Me confirma / preciso dos detalhes

Esses você me mencionou mas eu não consegui identificar com certeza — se me mandar nome ou endereço, eu termino de preencher e pino no mapa:

- **Restaurante a quilo na esquina da Braz de Aguiar com a Rui Barbosa** — "super variado e super bom"
- **Cachorro-quente ao lado das Americanas** — qual Americanas (Pres. Vargas? Boulevard?)
- **Segundo endereço do Puba Bar** — achei só a Cidade Velha; qual é o outro endereço?
