==========================================================
ZDS-Client - Generieke client voor GEMMA-zaken componenten
==========================================================

De ZDS-Client is een (voorlopig) interne client die op basis van OAS 3.0
specificaties met GEMMA-zaken componenten communiceert.

.. contents::

.. section-numbering::

Features
========

* Ophalen van OAS 2.0 spec en conversie naar OAS 3.0
* Aanmaken van resources volgens specificatie
* Generieke opzet, maar specifiek gebruik in de zaakgericht-werken services
* Introspectie in het OAS schema: lees op basis van een resource URL uit wat
  er precies hoort achter deze URL te zitten.

Geplande features
-----------------

* Ophalen OAS 3.0 spec zonder conversie

Installatie
===========

Benodigdheden
-------------

* Python 3.6 of hoger
* setuptools 30.3.0 of hoger

Installeren
-----------

.. code-block:: bash

    pip install gemma-zds-client

Gebruik
=======

Initialiseren (statische configuratie)
--------------------------------------

De client moet geinitialiseerd worden met de locatie van de componenten. Dit
doe je eenmalig:

.. code-block:: bash

    from zds_client import Client

    Client.load_config('/pad/naar/config.yml')


De makkelijkste manier is configuratie via een ``yaml`` bestand, in het formaat:

.. code-block:: yaml

    ---

    zrc:
      scheme: http
      host: localhost
      port: 8000

    drc:
      scheme: http
      host: localhost
      port: 8001

    ztc:
      scheme: http
      host: localhost
      port: 8002

    orc:
      scheme: http
      host: localhost
      port: 8003


De key is de naam van de component.

Je kan echter ook de configuratie zonder yaml bestand doen, en volledig
gebruik maken van Python dictonaries, bijvoorbeeld:

.. code-block:: python

    from zds_client import Client

    ZRC = {
        'scheme': 'http',
        'host': 'localhost',
        'port': 8000,
    }

    DRC = {
        'scheme': 'http',
        'host': 'localhost',
        'port': 8001,
    }

    Client.load_config(**{
        'zrc': ZRC,
        'drc': DRC,
        ...
    })

Initialiseren (ad-hoc configuratie)
-----------------------------------

Je kan ook een client instance verkrijgen op basis van een specifieke resource
URL.

.. code-block:: python

    from zds_client import Client

    client = Client.from_url('https://api.nl/v1/resource/123', base_dir='/path/to/node_modules')

.. note::
   Momenteel moet je nog het pad naar `node_modules` opgeven waar de
   `swagger2openapi` beschikbaar is om on the fly conversie van OAS 2.0 naar
   OAS 3.0 te doen. Deze moet dus in je eigen project beschikbaar zijn.

   Er zijn plannen om dit uit de client te slopen, en af te dwingen dat de
   server MOET OAS 3.0 serveren. Dit betekent dat dan OAS 2.0 support
   gedropped wordt.


Resources manipuleren
---------------------

Per component kan je vervolgens een client resources laten opvragen of
manipuleren:

.. code-block:: python

    zrc_client = Client('zrc')  # gebruik alias uit configuratie

    # oplijsten
    zaken = zrc_client.list('zaak')

    # opvragen
    zaak = zrc_client.retrieve('zaak', uuid='<uuid>')

    # aanmaken
    zaak = zrc_client.create('zaak', {
        'bronorganisatie': '000000000',
        'zaaktype': 'http://localhost:8002/api/v1/zaaktypen/<uuid>'
    })


Schema introspectie
-------------------

Met de ``schema`` module kan je introspectie doen op resource URLs:

.. code-block:: python

    from zds_client import Client
    from zds_client.schema import Schema

    zrc_client = Client('zrc')  # gebruik alias uit configuratie

    schema = Schema(zrc_client.schema)

    input_schema = schema.get_request_resource_schema(
        'https://api.nl/v1/resource/123', method='GET'
    )
    assert input_schema['type'] == 'object'

    params = schema.get_request_parameters(
        'https://api.nl/v1/resource/123', method='GET'
    )
    assert type(params) == list

    output_schema = schema.get_response_resource_schema(
        'https://api.nl/v1/resource/123',
        method='GET', status_code='200'
    )
    assert output_schema['type'] == 'object'
