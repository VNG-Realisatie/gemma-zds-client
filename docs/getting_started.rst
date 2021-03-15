Getting started
===============

Installation
------------

Install with pip

.. code-block:: bash

    pip install gemma-zds-client

Initialization
--------------

**Initialise (static configuration)**

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

**Initialise (ad-hoc configuration)**

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

Using the client methods
------------------------

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
