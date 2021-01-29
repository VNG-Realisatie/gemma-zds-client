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

* ``zds_client.auth.ClientAuth.claims`` - claims namespaced under ``zds`` in the JWT
  payload are deprecated and scheduled for removal in 1.0.

  These claims became obsolete after the shift to store the application authorizations
  in the Autorisaties API.

  1.0 will support extra claims, but they will be added to the token payload without
  the ``zds`` namespace.

* ``zds_client.Client.list``: ``query_params`` arg is deprecated in favour of
  ``params``. This matches the underlying ``requests`` interface.

* ``zds_client.tests.mocks`` is deprecated. The mock client shim is overly complex and
  requires Django. Use requests-mock_ or responses_ instead to mock the underlying
  ``requests`` calls.

.. _requests-mock: https://pypi.org/project/requests-mock/
.. _responses: https://pypi.org/project/responses/
