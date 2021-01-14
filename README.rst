==========================================================
ZDS-Client - Generieke client voor GEMMA-zaken componenten
==========================================================

|build-status|

De ZDS-Client is een (voorlopig) interne client die op basis van OAS 3.0
specificaties met GEMMA-zaken componenten communiceert.

.. contents::

.. section-numbering::

Features
========

* Ophalen van OAS 3.0 spec & caching
* Aanmaken van resources volgens specificatie
* Generieke opzet, maar specifiek gebruik in de zaakgericht-werken services
* Introspectie in het OAS schema: lees op basis van een resource URL uit wat
  er precies hoort achter deze URL te zitten.
* ZDS autorisatiemodel via JWT out-of-the-box ondersteund.

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
kan eenmalig of just-in-time wanneer je de client nodig hebt:

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
      auth:
        client_id: my-zrc-client-id
        secret: my-zrc-client-secret
        scopes:
          - zds.scopes.zaken.aanmaken

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

    client = Client.from_url('https://api.nl/v1/resource/123')

Indien autorisatie hierop nodig is, kan je deze zelf assignen:

.. code-block:: python

    from zds_client import ClientAuth

    client.auth = ClientAuth(
        client_id='my-client-id',
        secret='my-client-secret',
    )

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

    # opvragen met URL
    zaak = zrc_client.retrieve('zaak', url='<zaak_url>')

    # aanmaken
    zaak = zrc_client.create('zaak', {
        'bronorganisatie': '000000000',
        'zaaktype': 'http://localhost:8002/api/v1/zaaktypen/<uuid>'
    })

**Operation suffixes**

De ``operation_id`` van de OAS-operations staan centraal - op basis hiervan wordt de
URL + HTTP method opgehaald die nodig is voor de call. Je kan deze suffixes overriden
in client subclasses:

.. code-block:: python

    class MyClient(Client):
        operation_suffix_mapping = {
            "list": "List",
            "retrieve": "Retrieve",
            "create": "Create",
            "update": "Update",
            "partial_update": "PartialUpdate",
            "delete": "Delete",
        }


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

Usage with NLX
--------------

When you're using NLX outways, the URLs of resources change because of this.
Services expoxed via NLX inways don't understand local outway URLs, so these
need to get rewritten.

In Django projects, you can make use of `nlx-url-rewriter`_ to define rewrite
targets before the requests are sent and right after responses are received.

The rewriter is implemented in the ``zds_client.nlx.NLXClient`` class, which
you can use instead of ``zds_client.Client``.

Install using:

.. code-block:: bash

    pip install gemma-zds-client[nlx]

This will pull in the extra dependencies. Make sure to follow the `nlx-url-rewriter`_
setup instructions.

.. |build-status| image:: https://github.com/VNG-Realisatie/gemma-zds-client/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/VNG-Realisatie/gemma-zds-client/actions?query=workflow%3A%22Run+CI%22

.. _nlx-url-rewriter: https://pypi.org/project/nlx-url-rewriter/
