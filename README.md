[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
# prixCarburant-home-assistant
Client python permettant d'interroger l'openData du gouvernement sur le prix du carburant.

https://www.prix-carburants.gouv.fr/

<h3> C'est un FORK pour extraires des données instantanés (au lieu de 'hier'), par incorporer le prixCaruburantClient.py modifié </h3>

Le client permet de :
 - Trouver les stations les plus proches dans un cercle de X km configurable a partir de votre adresse defini dans home assistant
 - Extraire des stations spécifiques via son ID
 - faire des mises à jour intra-day

<h4> A noter: cet version utilise un folder /custom_components/PrixCarburantsData pour stocker les données (au lieu de les télécharger pour chaque sensor) </h4>

Aide à l'installation depuis HACS :

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


Exemple de données extraites :
```
Station ID: '44300020'
Gasoil: '1.519'
Last Update Gasoil: '2021-02-23T19:23:06'
E95: '1.622'
Last Update E95: '2021-02-23T19:23:07'
E98: '1.685'
Last Update E98: '2021-02-23T19:23:08'
E10: '1.563'
Last Update E10: '2021-02-23T19:23:07'
E85: None
Last Update E85: ''
GPLc: '0.909'
Last Update GPLc: '2021-02-23T19:23:07'
Station Address: 162 Route de Rennes Nantes
Station name: undefined
Last update: '2021-02-24'
unit_of_measurement: €
friendly_name: PrixCarburant_44300020
icon: 'mdi:currency-eur'
```
### Configuration d'affichage dans Home Assistant

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

![alt text]![image](https://user-images.githubusercontent.com/44190435/159111030-33358579-a21b-4c8b-b525-4aeb94ae9e4f.png)

* Carte markdown dynamique
```
type: markdown
title: Prix Gasoil
content: >-
  <table> <tr> <td><h4>Name</td> <td><h4>Gasoil</td><td><h4>maj</td></tr> {% for
  station in (states.sensor | sort(attribute='state')) if 'prix' in
  station.entity_id %} <tr><td> {{ state_attr(station.entity_id, 'Station name')
  }}</td> <td>{{-  state_attr(station.entity_id, 'Gasoil') }}</td>   <td>{%- set
  event = state_attr(station.entity_id,'Last Update Gasoil') | as_timestamp -%}
  {%- set delta = ((event - now().timestamp()) / 86400) | round  -%}
    {{ -delta }}j</td>
  {{- '\n' -}}  <tr> <td>{{ state_attr(station.entity_id, 'Station Address') }}
  </td><td>{{strptime(state_attr(station.entity_id, 'Last Update
  Gasoil'),"%Y-%m-%d %H:%M:%S").strftime("%H:%M") -}}</td></td> {% endfor %}
title: Prix des carburants
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

# Information

Source code d'origine (!) du client, maintenant intégré dans cet repo (si vous souhaitez l'analyser): "https://github.com/ryann72/essence"

Il s'agit d'un fork de https://github.com/max5962/prixCarburant-home-assistant, pour avoir des chiffres instantanés
