.. Common Ground API Client documentation master file, created by
   sphinx-quickstart on Mon Mar 15 11:19:21 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Common Ground API Client's documentation!
====================================================

The Common Ground API Client is a generic client for Common Ground API's built with
OpenAPI 3.0 specifications.

Features
--------

* Driven by OAS 3.0 specification
* (Pluggable) caching of api specifications
* Create/mutate resources according to the api specifications
* Support for multiple authentication schemes

    * ZGW auth (JWT based)
    * API-key via HTTP headers
    * or none, for open APIs

* Generic approach, but very well suited for the "API's voor zaakgericht werken" standard
* Built on top of battle-proven `requests`_ library.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   nlx
   reference
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _requests: https://pypi.org/project/requests/
