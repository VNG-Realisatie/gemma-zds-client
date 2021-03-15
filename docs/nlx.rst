Usage with NLX_
===============

When you're using NLX outways, the URLs of resources change because of this.
Services expoxed via NLX inways don't understand local outway URLs, so these
need to get rewritten.

In Django projects, you can use `zgw-consumers`_, which has built-in support for NLX
and the required URL rewrites. This library is a dependency of ``zgw-consumers``.

.. _NLX: https://nlx.io
.. _zgw-consumers: https://pypi.org/project/zgw-consumers/
