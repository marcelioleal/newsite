---
title: Kitesurf
date: '2024-03-17T06:36:31'
slug: kitesurf
wp_id: 252
translationKey: kitesurf
---

Kite é uma paixão pra mim, faz parte da minha vida de forma a ser uma das minhas metas anuais. É também uma forma de conhecer lugares e pessoas super legais. Nesta página eu deixo recomendações pra quem vai velejar por alguns lugares que eu já passei.

**Dica de temporada**: o Nordeste tem a melhor janela de **agosto a janeiro** (ventos alísios de leste, consistentes). O Sul (Floripa) tem melhor temporada de **novembro a março**. A Amazônia (Pará) tem ventos sazonais que variam bastante por canto.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
<div id="kite-map" style="height:460px;width:100%;border:1px solid var(--border);border-radius:8px;margin:1.8em 0;background:var(--entry);"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function(){
  if(!document.getElementById('kite-map')||!window.L)return;
  L.Icon.Default.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
  var spots=[
    ['São Miguel do Gostoso','RN',-5.1273,-35.6361,'Vila tranquila, lagoa flat, side-on consistente. Perfeito pra progredir sem multidão.','sao-miguel-do-gostoso-rn-'],
    ['Icaraí de Amontada','CE',-3.2611,-39.9064,'Uma das lagoas mais lindas do Brasil. Ventos fortes, público mais internacional.','icara%c3%ad-de-amontada-ce-'],
    ['Ilha do Guajiru','CE',-3.0333,-39.7833,'Lagoa gigante, água rasa, puro freestyle. Lugar mais remoto, menos turístico.','ilha-do-guajiru-ce-'],
    ['Jericoacoara / Preá','CE',-2.7956,-40.5131,'O eixo mais badalado. Mix de oceano e lagoas (Guriú, Lagoinha), vento forte, vida noturna em Jeri.','jericoacoara--pre%c3%a1-ce-'],
    ['Cumbuco','CE',-3.6250,-38.7333,'Praia enorme, downwind pela costa com dunas no caminho. Logística fácil (perto de Fortaleza).','cumbuco-ce-'],
    ['Atins','MA',-2.5833,-42.7333,'Dentro dos Lençóis Maranhenses. Logística difícil, vento excelente, dunas + lagoas de chuva. Intermediário pra cima.','atins-ma-'],
    ['Salinópolis','PA',-0.6133,-47.3561,'Vento sazonal jan–mai em algumas praias, água morna, atmosfera 100% paraense.','salin%c3%b3polis-pa-'],
    ['Algodoal / Fortalezinha','PA',-0.5894,-47.5869,'Ilha isolada, acesso de barco, vento forte fora da chuva. Experiência rústica.','algodoal--fortalezinha-pa-'],
    ['Alter do Chão','PA',-2.5097,-54.9478,'Vento no rio Tapajós, água doce, cenário amazônico. Janela curta mas vale.','santar%c3%a9m--alter-do-ch%c3%a3o-pa-'],
    ['Mosqueiro','PA',-1.0831,-48.4231,'Praia fluvial perto de Belém. Kite de fim de semana com galera local.','mosqueiro-pa-'],
    ['Florianópolis','SC',-27.6819,-48.4756,'Praias do leste e sul (Campeche, Armação, Guarda do Embaú). Temporada oposta ao Nordeste.','florian%c3%b3polis-sc-']
  ];
  var map=L.map('kite-map',{scrollWheelZoom:false}).setView([-6.5,-45,-0],4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',maxZoom:19}).addTo(map);
  var g=L.featureGroup();
  spots.forEach(function(s){
    var html='<strong>'+s[0]+'</strong> <span style="color:#6b7280;font-size:11px;letter-spacing:.05em;text-transform:uppercase">'+s[1]+'</span><p style="margin:6px 0 8px;line-height:1.4;color:#374151;font-size:13px">'+s[4]+'</p><a href="#'+s[5]+'">Ver mais ↓</a>';
    g.addLayer(L.marker([s[2],s[3]]).bindPopup(html,{maxWidth:280}));
  });
  g.addTo(map);
  map.fitBounds(g.getBounds().pad(0.18));
})();
</script>

## Nordeste — a jornada clássica do kiteiro brasileiro

### São Miguel do Gostoso <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/3/30/Bandeira_do_Rio_Grande_do_Norte.svg" alt="bandeira do Rio Grande do Norte" width="22" height="16" loading="lazy">

Vila tranquila, lagoa flat, side-on consistente. Perfeito pra progredir sem multidão. Vida noturna quase inexistente, o que pra mim é parte do charme — você vai pra kitar, comer peixe e dormir cedo.

### Icaraí de Amontada <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Bandeira_do_Ceará.svg" alt="bandeira do Ceará" width="22" height="16" loading="lazy">

Uma das lagoas mais lindas do Brasil. Ventos fortes, público mais internacional, rotina pousada–kite–sunset. Lugar pra quem quer o kite como centro da viagem.

### Ilha do Guajiru <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Bandeira_do_Ceará.svg" alt="bandeira do Ceará" width="22" height="16" loading="lazy">

Lagoa gigante, água rasa, puro freestyle. Lugar mais remoto, menos turístico. Bom se você for com família — tem onde ficar sem exigir nível técnico avançado.

### Jericoacoara / Preá <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Bandeira_do_Ceará.svg" alt="bandeira do Ceará" width="22" height="16" loading="lazy">

O eixo mais badalado. Mix de oceano e lagoas (Guriú, Lagoinha), vento forte, vida noturna em Jeri. Fica nas pousadas do Preá se o foco é kitar — é mais vazio e você vai pras lagoas de buggy.

### Cumbuco <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Bandeira_do_Ceará.svg" alt="bandeira do Ceará" width="22" height="16" loading="lazy">

Praia enorme, downwind pela costa com dunas no caminho. Logística fácil (perto de Fortaleza, ~40 min). Multidão maior em alta temporada mas tem espaço pra todo mundo.

### Atins <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/4/45/Bandeira_do_Maranhão.svg" alt="bandeira do Maranhão" width="22" height="16" loading="lazy">

Dentro dos Lençóis Maranhenses. Logística difícil (4x4 obrigatório, chegada por barco em alguns trechos), vento excelente, visual único (dunas brancas + lagoas de chuva). Nível intermediário em diante — não é um lugar pra começar.

## Pará — kite amazônico, menos óbvio

### Salinópolis <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/0/02/Bandeira_do_Pará.svg" alt="bandeira do Pará" width="22" height="16" loading="lazy">

Vento sazonal entre janeiro e maio em algumas praias, água morna, atmosfera 100% paraense. Vai pra viver um pouco do Nordeste paraense — a praia é imensa quando a maré baixa.

### Algodoal / Fortalezinha <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/0/02/Bandeira_do_Pará.svg" alt="bandeira do Pará" width="22" height="16" loading="lazy">

Ilha isolada, acesso de barco, vento forte fora da temporada de chuva. Experiência rústica — sem carros, pouca estrutura, muito silêncio. Pra quem quer kitar e desconectar.

### Santarém / Alter do Chão <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/0/02/Bandeira_do_Pará.svg" alt="bandeira do Pará" width="22" height="16" loading="lazy">

Vento no rio Tapajós, condições únicas (água doce, cenário amazônico). Janela curta (ventos mais consistentes entre agosto e dezembro) mas vale a pena pela experiência.

### Mosqueiro <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/0/02/Bandeira_do_Pará.svg" alt="bandeira do Pará" width="22" height="16" loading="lazy">

Praia fluvial perto de Belém. Kite de fim de semana com galera local — o tipo de sessão que salva um fim de semana parado em casa.

## Pelo Brasil

### Florianópolis <img class="state-flag" src="https://upload.wikimedia.org/wikipedia/commons/1/1a/Bandeira_de_Santa_Catarina.svg" alt="bandeira de Santa Catarina" width="22" height="16" loading="lazy">

Praias do leste e sul da ilha (Campeche, Armação, Guarda do Embaú). Temporada oposta ao Nordeste — bom pra quem quer kitar o ano inteiro sem precisar se mudar.

---

Se quiser falar sobre algum desses lugares, me chama nas redes. Tenho contatos de pousadas e dicas locais em cada canto.
