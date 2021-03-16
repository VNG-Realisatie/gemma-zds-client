Changelog
=========

1.0.0 (2021-03-16)
------------------

Stable release - according to semantic versioning new minor releases will be backwards
compatible and breaking changes will bump the major version number. Note that this
applies to the *public* API.

The public API is frozen in this release. Anything documented in ``docs`` (including
the reference) is considered public API, anything else is considered private API.

**Breaking changes**

A number of deprecations have been removed:

* ``zds_client.ClientAuth`` - any extra kwargs are now included in the JWT payload
  rather than being nested in a ``zds`` namespace object.

  Before:

  .. code-block:: python

      auth = ClientAuth("client-id", "secret", foo="bar")

  would lead to the payload:

  .. code-block:: json

      {
        "iss": "client-id",
        "iat": "1615891267",
        "client_id": "client-id",
        "user_id": "",
        "user_representation": "",
        "zds": {
            "foo": "bar",
        }
      }

  Now the resulting payload is:

  .. code-block:: json

      {
        "iss": "client-id",
        "iat": "1615891267",
        "client_id": "client-id",
        "user_id": "",
        "user_representation": "",
        "foo": "bar"
      }

* The custom ``client_identifier`` JWT header is removed. This was only kept for
  interaction with alpha releases of the ZGW standard. The ``client_id`` claim in the
  payload is the canonical source of this information.

* ``zds_client.tests`` package is removed, which included the ``MockClient``. Replace
  these calls with requests-mock_ or responses_ instead.

* Removed ``zds_client.nlx`` - use `zgw-consumers`_ instead.

0.15.0 (2021-03-15)
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

* ``zds_client.nlx`` module is deprecated. `zgw-consumers`_ is a better solution for
  Django-based projects. This module was Django-only already because of the dependency
  ``nlx-url-rewriter``.

.. _requests-mock: https://pypi.org/project/requests-mock/
.. _responses: https://pypi.org/project/responses/

**New stuff**

* Added public API documentation, hosted on readthedocs.io
* Added docs build to CI workflow
