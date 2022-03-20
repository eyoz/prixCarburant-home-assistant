[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

# prixCarburant-home-assistant
<h4> C'est un fork de max5962, adapté pour extraires des données instantanés et inclus aussi une modification de prixCaruburantClient.py </h4>

Client python permettant d'interroger l'openData du gouvernement sur le prix du carburant.

https://www.prix-carburants.gouv.fr/

Le client permet de :
 - Trouver les stations les plus proches dans un cercle de X km configurable a partir de votre adresse defini dans home assistant
 - Extraire des stations spécifiques via son ID
 - Faire des mises à jour intra-day (SCAN_INTERVAL dans sensor.py)

<h4> A noter: utilise folder /custom_components/PrixCarburantsData pour stocker les données, au lieu de les télécharger pour chaque sensor individuel </h4>

## Updates
- 20220320: pour ameliorer sur iOS les datetime en ISO avec 'T' (YYYY-MM-DDTHH:MM:SS)

## Installation depuis HACS :

Dans HACS, cliquer sur ... puis depots personnalisés
Ajouter :
- URL : https://github.com/vingerha/prixCarburant-home-assistant
- Catégorie : Intégration

## Configuration
Exemple de configuration :

### Configuration pour récupérer les stations dans un rayon de 20 km
```
sensor:
  platform: prixCarburant
  maxDistance: 20
```

### Configuration pour récupérer les stations très spécifique   
```
sensor:
  platform: prixCarburant
  #maxDistance: 20
  stationID:
    - 59000009
    - 59000080
```

### Exemple de données extraites :
```
Station ID: 6250011
Gasoil: 2.039
Last Update Gasoil: 2022-03-17 17:05:00
E95: None
Last Update E95: 
E98: 2.119
Last Update E98: 2022-03-16 16:55:00
E10: 1.999
Last Update E10: 2022-03-16 16:55:00
E85: None
Last Update E85: 
GPLc: None
Last Update GPLc: 
Station City: MOUGINS
Station Address: 10641126 AVENUE SAINT MARTIN 06250 MOUGINS
Station name: BP MOUGINS SAINT MARTIN
Distance: 9.999
Last update: 2022-03-19 09:28
unit_of_measurement: €
icon: mdi:currency-eur
friendly_name: PrixCarburant_6250011
```
### Exemples de configuration d'affichage dans Home Assistant

#### via carte markdown statique

Permet d'afficher le prix des différents carburants proposés par la station.

La date d'actualisation des prix est également affichée
```
{{state_attr("sensor.prixcarburant_44300020", "Station name")}} - Maj : {{state_attr("sensor.prixcarburant_44300020", "Last update")}}
{%- if state_attr("sensor.prixcarburant_44300020", "Gasoil") != "None"  %}
Gasoil : {{ state_attr("sensor.prixcarburant_44300020", "Gasoil") }} €
{%- endif %}
{%- if state_attr("sensor.prixcarburant_44300020", "E10") != "None"  %}
E10 : {{ state_attr("sensor.prixcarburant_44300020", "E10") }} €
{%- endif %}
{%- if state_attr("sensor.prixcarburant_44300020", "E95") != "None"  %}
SP95 : {{ state_attr("sensor.prixcarburant_44300020", "E95") }} €
{%- endif %}
{%- if   state_attr("sensor.prixcarburant_44300020", "E98") != "None"  %}
SP98 : {{ state_attr("sensor.prixcarburant_44300020", "E98") }} €
{%- endif %}
{%- if   state_attr("sensor.prixcarburant_44300020", "GPLc") != "None"  %}
GPLc : {{ state_attr("sensor.prixcarburant_44300020", "GPLc") }} €
{%- endif %}
```

#### via carte markdown dynamique (petite modification pour prix d'aujourd'hui)

![image](https://user-images.githubusercontent.com/44190435/159115045-7e02a1ad-6396-4f1f-b453-8ac1715c7578.png)

* Carte markdown dynamique
```
type: markdown
title: Prix Gasoil
content: >-
  <table> <tr> <td><h4>Name</td><td><h4>Gasoil</td><td><h4>maj</td><td><h4>heure</td><td><h4>dist</td></tr> 
  {% for station in (states.sensor | sort(attribute='state')) if 'prix' in station.entity_id %} 
  <tr><td> {{ state_attr(station.entity_id, 'Station name') }}({{ state_attr(station.entity_id, 'Station City') }})</td>
  <td>{{-  state_attr(station.entity_id, 'Gasoil') }}</td>
  <td>{%- set event = state_attr(station.entity_id,'Last Update Gasoil') | as_timestamp -%} {%- set delta = ((event - now().timestamp()) / 86400) | round  -%}
  {{ -delta }}j</td>
  </td><td>{{strptime(state_attr(station.entity_id, 'Last Update Gasoil'),"%Y-%m-%dT%H:%M:%S").strftime("%H:%M") -}}</td><td>{{ state_attr(station.entity_id, 'Distance') | round(1) }}</td> {% endfor %}
```

#### via carte multiple-entity-row

![alt text](https://forum.hacf.fr/uploads/default/original/2X/5/5bcb6d091aa764431ddb271c3087c7544013c599.png)

```
type: entities
title: Prix carburants
entities:
  - entity: sensor.prixcarburant_12340001
    type: custom:multiple-entity-row
    name: Auchan
    icon: mdi:gas-station
    show_state: false
    entities:
      - attribute: E98
        name: E98
        unit: €
      - attribute: E10
        name: E10
        unit: €
      - attribute: GPLc
        name: GPL
        unit: €
  - entity: sensor.prixcarburant_12340003
    type: custom:multiple-entity-row
    name: E.Leclerc
    icon: mdi:gas-station
    show_state: false
    entities:
```
#### via carte flex-table-card

![image](https://user-images.githubusercontent.com/44190435/159131530-d8089e78-bd5c-45a8-9b0b-9c32b1ae32a2.png)


```
type: custom:flex-table-card
clickable: true
sort_by: Gasoil
max_rows: 8
title: Gasoil
entities:
  include: sensor.prixcarburant*
columns:
  - name: nom station
    data: Station name,Station City
  - name: Gasoil
    data: Gasoil
    suffix: €
  - name: Valid.
    data: Last Update Gasoil
    modify: Math.round((Date.now() - Date.parse(x)) / 36000 / 100 /24)
    align: left
    suffix: J
  - name: Dist.
    data: Distance
    modify: Math.round(x)
    suffix: km
css:
  tbody tr:nth-child(1): 'color: #00ff00'
  tbody tr:nth-child(5): 'color: #f00020'
style: null
```

## Information
Sensor: fork de https://github.com/max5962/prixCarburant-home-assistant
Client: maintenant intégré dans cet repo (si vous souhaitez l'analyser): "https://github.com/ryann72/essence"

