==========================================================
ZDS-Client - Generieke client voor GEMMA-zaken componenten
==========================================================

De ZDS-Client is een (voorlopig) interne client die op basis van OAS 3.0
specificaties met GEMMA-zaken componenten communiceert.

.. contents::

.. section-numbering::

Features
========

* Ophalen van OAS 3.0 specificatie
* Aanmaken van resources volgens specificatie
* Generiek

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

Initialiseren
-------------

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
