Changelog
=========

0.15.0 (2021-??-??)
-------------------

Preparations towards a 1.0 release

**Breaking changes**

``zds_client.schema.Schema`` was removed. The initial reason to add it was to serve as
a tool for NLX url rewriting middleware, which became obsolete with `zgw-consumers`_'
built-in support. If you need to parse OpenAPI 3.0 schema's, openapi-parser_ looks
viable.

.. _zgw-consumers: https://pypi.org/project/zgw-consumers/
.. _openapi-parser: https://pypi.org/project/openapi-parser/

**Deprecations**
