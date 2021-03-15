.. Common Ground API Client documentation master file, created by
   sphinx-quickstart on Mon Mar 15 11:19:21 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Common Ground API Client's documentation!
====================================================

The Common Ground API Client is a generic client for Common Ground API's built with
OpenAPI 3.0 specifications.

|build-status| |coverage| |docs| |pypi-version|

|linting| |black| |python-versions|

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

.. |build-status| image:: https://github.com/VNG-Realisatie/gemma-zds-client/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/VNG-Realisatie/gemma-zds-client/actions?query=workflow%3A%22Run+CI%22

.. |coverage| image:: https://codecov.io/gh/VNG-Realisatie/gemma-zds-client/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/VNG-Realisatie/gemma-zds-client
    :alt: Coverage status

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |docs| image:: https://readthedocs.org/projects/gemma-zds-client/badge/?version=latest
   :alt: Documentation Status
   :target: https://gemma-zds-client.readthedocs.io/en/latest/?badge=latest

.. |linting| image:: https://github.com/VNG-Realisatie/gemma-zds-client/actions/workflows/code_quality.yml/badge.svg
   :alt: Code quality checks
   :target: https://github.com/VNG-Realisatie/gemma-zds-client/actions/workflows/code_quality.yml

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/gemma-zds-client.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/gemma-zds-client.svg
    :target: https://pypi.org/project/gemma-zds-client/
