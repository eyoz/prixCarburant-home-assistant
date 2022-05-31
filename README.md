[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

# prixCarburant-home-assistant
Client python permettant d'interroger l'openData du gouvernement sur le prix du carburant: https://www.prix-carburants.gouv.fr/
Le client permet de :
 - Trouver les stations les plus proches dans un cercle de X km configurable a partir de votre adresse defini dans home assistant
 - Extraire des stations spécifiques via son ID
 - Faire des mises à jour intra-day (SCAN_INTERVAL dans sensor.py)

<h4> A noter: utilise folder "[config]/custom_components/PrixCarburantsData" pour stocker les données, au lieu de les télécharger pour chaque sensor individuel </h4>

## Updates
- 20220524: v1.2.1 ajout de l'option pour choisir un autre carburant dans 'state' value (maintenant gazoil par defaut), reduction des messages dans logs
- 20220523: v1.1.5 ajoutes des lat/lon pour une utilisation dans map-card (voir ci-sessus)
- 20220320: amelioration pour iOS, les datetime maintenant en format ISO avec 'T' (YYYY-MM-DDTHH:MM:SS)
- 20220319: améliorer le traitement des télechargements/unzip, ajout: Distance et City
- 20220318: version de base, fork et adaptation au prix instantanés

## Installation depuis HACS :

Dans HACS, cliquer sur ... puis depots personnalisés
Ajouter :
- URL : https://github.com/vingerha/prixCarburant-home-assistant
- Catégorie : Intégration

## Configuration
Exemples de configuration :

### Configuration pour récupérer les stations dans un rayon de 20 km
```
sensor:
  platform: prixCarburant
  maxDistance: 20
```
### Configuration pour avoir des prix de carburant différent en 'state' (defaut: gazoil)
- Options: E95, E98, E10, E85, GPL, GAZOIL (en majuscules)
- Note: si le API ne donne pas de prix selon fuelType, state montre 'None'
Exemple pour E85
```
sensor:
  platform: prixCarburant
  maxDistance: 20
  fuelType: E85
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
Last Update Gasoil: 2022-03-17T17:05:00
E95: None
Last Update E95: 
E98: 2.119
Last Update E98: 2022-03-16T16:55:00
E10: 1.999
Last Update E10: 2022-03-16T16:55:00
E85: None
Last Update E85: 
GPLc: None
Last Update GPLc: 
Station City: MOUGINS
Station Address: 10641126 AVENUE SAINT MARTIN 06250 MOUGINS
Station name: BP MOUGINS SAINT MARTIN
Distance: 9.999
Last update: 2022-03-19T09:28
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
    multi_delimiter: <br />
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

#### via carte map + auto-entities, dynamique
```
type: custom:auto-entities
card:
  type: map
  show_empty: false
filter:
  template: >
    [{% set ns = namespace(count=0) %} {% for x in expand(states.sensor)|
    sort(attribute='state')| map(attribute='entity_id') %} {% if 'prix' in x and
    ns.count < 12 %}'{{x}}',{% set ns.count = ns.count + 1 %}{% endif %}{%-
    endfor %}]
```
![image](https://user-images.githubusercontent.com/44190435/169685871-3641d686-0fea-4054-92a1-e6531832cfa9.png)

#### stack-in-card (hacs) et flex-table, dynamique
Pas parfait mais ça marche, If faut 
- changer le 'binary_sensor' pour quelquechose local
- ajouter un photo dans config/www/images (ici c'est essence.jpeg)
```
type: custom:vertical-stack-in-card
card_mod:
  style: |
    ha-card {
     --ha-card-background: rgba(0, 0, 0, 0.1);
    ha-card {
      margin-top: 0em;
        }         
mode: vertical
cards:
  - type: picture-entity
    entity: binary_sensor.above_3_0
    image: /local/image/essence.jpeg
    show_name: true
    show_state: false
    name: Station Service
    tap_action:
      action: none
    hold_action:
      action: none
  - type: divider
    style:
      height: 2px
      width: 100%
      margin-left: auto
      margin-right: auto
      background: rgba(255, 255, 255, 0.5)
  - type: custom:flex-table-card
    clickable: true
    sort_by: E10+
    max_rows: 5
    entities:
      include: sensor.prixcarburant*
    columns:
      - name: nom station
        data: Station name, Station Address
      - name: E10
        data: E10
        suffix: €
      - name: Valid.
        data: Last Update E10
        modify: Math.round((Date.now() - Date.parse(x)) / 36000 / 100 /24)
        align: left
        suffix: J
      - name: Dist.
        data: Distance
        modify: Math.round(x)
        suffix: km
    css:
      tbody tr:nth-child(odd): 'background-color: rgba(255, 255, 255, 0.2)'
      tbody tr:nth-child(even): 'background-color: rgba(255, 255, 255, 0.1)'
      tbody tr:nth-child(1): 'color: #00ff00'
      tbody tr:nth-child(5): 'color: #FF0000'
    card_mod:
      style: |
        ha-card {
        border-radius: 10px;
        padding-bottom: 10px;
        background-color: rgba(0, 0, 0, 0.1)
        }
        :host {
        font-size: 13px;
        border-radius: 10px;
        }
  - type: divider
    style:
      height: 2px
      width: 100%
      margin-left: auto
      margin-right: auto
      background: rgba(255, 255, 255, 0.5)
  - type: custom:flex-table-card
    clickable: true
    sort_by: E85+
    max_rows: 5
    entities:
      include: sensor.prixcarburant*
    columns:
      - name: nom station
        data: Station name, Station Address
      - name: E85
        data: E85
        suffix: €
      - name: Valid.
        data: Last Update E85
        modify: Math.round((Date.now() - Date.parse(x)) / 36000 / 100 /24)
        align: left
        suffix: J
      - name: Dist.
        data: Distance
        modify: Math.round(x)
        suffix: km
    css:
      tbody tr:nth-child(odd): 'background-color: rgba(255, 255, 255, 0.2)'
      tbody tr:nth-child(even): 'background-color: rgba(255, 255, 255, 0.1)'
      tbody tr:nth-child(1): 'color: #00ff00'
      tbody tr:nth-child(5): 'color: #FF0000'
    card_mod:
      style: |
        ha-card {
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.1)
        }
        :host {
        font-size: 13px;
        border-radius: 10px;
        }
```        
![image](https://user-images.githubusercontent.com/44190435/171111718-36c02c34-d2f2-4710-8267-86fe2d72b5e4.png)


## Information & thanks
Le tout est un basé sur les taff de https://github.com/max5962/prixCarburant-home-assistant et https://github.com/ryann72/essence

# Un grand MERCI a ces deux !!

