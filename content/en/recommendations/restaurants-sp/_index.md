---
title: Restaurants in São Paulo
date: '2026-11-24T00:00:00'
slug: restaurants-sp
translationKey: restaurants-sp
---

São Paulo is home now, but my palate is still from the North. On this page I share restaurants in São Paulo that serve food from Pará and the Amazon — places where I can find the taste of home (tacacá, maniçoba, pato no tucupi, pirarucu, filhote, jambu, tucupi) without needing to catch a flight.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
<div id="rest-map" style="height:440px;width:100%;border:1px solid var(--border);border-radius:8px;margin:1.8em 0;background:var(--entry);"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function(){
  if(!document.getElementById('rest-map')||!window.L)return;
  L.Icon.Default.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
  var r=[
    ['Sororoca Bar','Vila Madalena',-23.5552,-46.6881,'https://www.google.com/maps/search/?api=1&query=Sororoca+Bar+Rua+Harmonia+321+Vila+Madalena'],
    ['Combu — Produtos da Amazônia','Bela Vista',-23.5596,-46.6411,'https://www.google.com/maps/search/?api=1&query=Combu+Produtos+da+Amazonia+Rua+Martiniano+de+Carvalho+97+Bela+Vista'],
    ['DaSelva (Downtown)','Centro',-23.5480,-46.6417,'https://www.google.com/maps/search/?api=1&query=DaSelva+Peixaria+Amazonica+Rua+da+Consolacao+41'],
    ['DaSelva (V. N. Conceição)','Vila Nova Conceição',-23.5974,-46.6682,'https://www.google.com/maps/search/?api=1&query=DaSelva+Avenida+Helio+Pellegrino+204+Vila+Nova+Conceicao'],
    ['Quintal Paraense','Casa Verde',-23.5141,-46.6633,'https://www.google.com/maps/search/?api=1&query=Quintal+Paraense+Rua+Horacio+Vergueiro+Rudge+535+Casa+Verde'],
    ['Namazônia','Vila Mariana',-23.5875,-46.6452,'https://www.google.com/maps/search/?api=1&query=Namazonia+Rua+Aurea+361+Vila+Mariana'],
    ['Amazônia Casa Brasileira','Bela Vista (Bixiga)',-23.5574,-46.6456,'https://www.google.com/maps/search/?api=1&query=Amazonia+Casa+Brasileira+Rua+Rui+Barbosa+218+Bela+Vista']
  ];
  var map=L.map('rest-map',{scrollWheelZoom:false}).setView([-23.56,-46.65],12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',maxZoom:19}).addTo(map);
  var g=L.featureGroup();
  r.forEach(function(x){
    var html='<strong>'+x[0]+'</strong><br><span style="color:#6b7280;font-size:12px">'+x[1]+'</span><br><a href="'+x[4]+'" target="_blank" rel="noopener">Open in Google Maps →</a>';
    g.addLayer(L.marker([x[2],x[3]]).bindPopup(html));
  });
  g.addTo(map);
  map.fitBounds(g.getBounds().pad(0.08));
})();
</script>

## Pará / Amazon cuisine

### Sororoca Bar — Vila Madalena

Contemporary bar and restaurant focused on fish and seafood, with a Pará twist. The menu changes every week depending on what fresh fish arrives — served raw, marinated, grilled, or fried, always with the fish at the center of the plate. The **fish bao** is the highlight, and there's a nice vegetarian option like cassava flour couscous with tucupi. Caipirinhas with exotic fruits and signature cocktails round out the drinks. Rua Harmonia, 321.

[Instagram](https://www.instagram.com/sororoca.bar/) · [Website](https://www.sororoca.com.br/) · [Maps](https://www.google.com/maps/search/?api=1&query=Sororoca+Bar+Rua+Harmonia+321+Vila+Madalena)

### Combu — Produtos da Amazônia — Bela Vista

Not a restaurant in the classic sense — it's an Amazonian-ingredient grocer/distributor opened in 2015, carrying more than 100 products from Pará, Amazonas, and Acre (tucupi, jambu, cupuaçu, pirarucu, nuts, flours). The name honors Ilha do Combu, the island across from Belém. They deliver in São Paulo via e-commerce and iFood — perfect for cooking Northern food at home when homesickness hits. Rua Martiniano de Carvalho, 97.

[iFood](https://www.ifood.com.br/delivery/sao-paulo-sp/combu---produtos-da-amazonia-bela-vista/b30f7615-b50b-4394-bc4a-03cce4e3d696) · [Maps](https://www.google.com/maps/search/?api=1&query=Combu+Produtos+da+Amazonia+Rua+Martiniano+de+Carvalho+97+Bela+Vista)

### DaSelva Peixaria Amazônica — Downtown / Vila Nova Conceição

Amazonian fish house with Manaus DNA — opened first downtown, across from the Mário de Andrade Library, and later added a second location in Vila Nova Conceição. The proposal is to bring freshwater fish from the Amazon (pirarucu, tambaqui, tucunaré) to São Paulo's culinary center with preparations that honor the ingredient. The downtown branch is 150m from Anhangabaú metro station — easy to combine with a metro outing.

- **Downtown:** Rua da Consolação, 41 — Tue–Sat 12pm–10pm, Sun 12pm–3pm
- **Vila Nova Conceição:** Av. Hélio Pellegrino, 204

[Maps (Downtown)](https://www.google.com/maps/search/?api=1&query=DaSelva+Peixaria+Amazonica+Rua+da+Consolacao+41) · [Maps (V. N. Conceição)](https://www.google.com/maps/search/?api=1&query=DaSelva+Avenida+Helio+Pellegrino+204+Vila+Nova+Conceicao)

### Quintal Paraense — Casa Verde

Opened in 2016 by three people from Pará who, after a decade in São Paulo, got tired of being far from their food. The menu is the wishlist of any Pará native living away from home: **tacacá, vatapá, maniçoba, caruru, crab, filhote, pato no tucupi**, and açaí with cupuaçu for dessert. Saturdays usually have a carimbó dance performance. It's up in the north zone, a trek from the west side, but worth the trip. Rua Horácio Vergueiro Rudge, 535.

Wed–Sat 12pm–10pm · Sun 12pm–5pm.

[Instagram](https://www.instagram.com/quintalparaense/) · [iFood](https://www.ifood.com.br/delivery/sao-paulo-sp/quintal-paraense-casa-verde/7c8bd627-ae20-4cfc-9f83-3875a58fe29a) · [Maps](https://www.google.com/maps/search/?api=1&query=Quintal+Paraense+Rua+Horacio+Vergueiro+Rudge+535+Casa+Verde)

### Namazônia — Vila Mariana

Used to be called Amazônia Soul for 5 years — rebranded as Namazônia after a big visual redesign led by chef and CEO Pedro Henrique Amaral. The decor uses indigenous graphics and lots of plants to create a sensory immersion in the rainforest. The menu has the classics (tacacá, maniçoba, pato no tucupi, vatapá, crab claw) plus some standouts like **golden fried tambaqui ribs**. Pirarucu and filhote are the house's base fish. Rua Áurea, 361.

[Instagram](https://www.instagram.com/namazoniaoficial/) · [Maps](https://www.google.com/maps/search/?api=1&query=Namazonia+Rua+Aurea+361+Vila+Mariana)

### Amazônia Casa Brasileira — Bela Vista (Bixiga)

Chef Paulo Leite's house — he's been representing Amazonian cuisine in São Paulo since 1995, and the restaurant itself opened in 2008. It's in Bixiga, the heart of downtown São Paulo's food scene. They serve à la carte year-round, but the real draw is the **Seven Classics Buffet** on weekends and holidays: pato no tucupi, peixada, caranguejada, maniçoba, vatapá do Pará, caruru, and pirarucu de casaca. Rua Rui Barbosa, 218.

Mon 12pm–3pm · Wed–Fri 12pm–3pm and 7pm–11pm · Sat 12pm–4pm and 7pm–11pm · Sun 12pm–4:30pm.

[Maps](https://www.google.com/maps/search/?api=1&query=Amazonia+Casa+Brasileira+Rua+Rui+Barbosa+218+Bela+Vista)
