import logging
from typing import List, Mapping, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_PATH_PARAMETERS = {
    'version': '1',
}

TYPE_ARRAY = 'array'


def get_operation_url(spec: dict, operation: str, pattern_only=False, **kwargs) -> str:
    url = spec['servers'][0]['url']
    base_path = urlparse(url).path

    for path, methods in spec['paths'].items():
        for name, method in methods.items():
            if name == 'parameters':
                continue

            if method['operationId'] == operation:
                format_kwargs = DEFAULT_PATH_PARAMETERS.copy()
                format_kwargs.update(**kwargs)
                if not pattern_only:
                    path = path.format(**format_kwargs)
                return '{base_path}{path}'.format(base_path=base_path, path=path)

    raise ValueError('Operation {operation} not found'.format(operation=operation))


def path_to_bits(path: str, transform=reversed) -> list:
    """
    Split a path into a list of parts.

    By default the parts are returned in reverse order to match two paths
    by their ends and discard any mismatching prefixes.
    """
    return [bit for bit in transform(path.split('/')) if bit]


def extract_params(url: str, pattern: str) -> dict:
    """
    Given an actual url and a pattern, extract the matching parameters.

    Example:

    >>> pattern = '/api/v1/zaken/{uuid}'
    >>> url = 'https://example.com/zrc/api/v1/zaken/1234'
    >>> extract_params(url, pattern)
    {'uuid': '1234'}
    """
    path_url = urlparse(url).path
    path_pattern = urlparse(pattern).path

    # pattern should be shortest, since actual urls may be hosted on a subpath
    pattern_bits = path_to_bits(path_pattern)
    url_bits = path_to_bits(path_url)[:len(pattern_bits)]

    return {
        pattern[1:-1]: value for pattern, value in zip(pattern_bits, url_bits)
        if pattern != value
    }


def noop(arg):
    return arg


class Schema:
    """
    Read configuration from the OpenAPI schema.
    """

    def __init__(self, spec: dict, content_type='application/json'):
        self.spec = spec
        self.content_type = content_type

    def get_root(self, url: str) -> str:
        """
        Find the spec server matching the URL.

        :raises ValueError: if no server matched.
        """
        for server in self.spec['servers']:
            if url.startswith(server['url']):
                return server['url']
        raise ValueError(f"No matching server found for '{url}'")

    def get_relative_path_parts(self, url: str) -> list:
        """
        Split the (fully qualified) url into parts from the api root.

        This yields a list of parts that can be compared against (template)
        paths from self.spec['paths'].
        """
        root = self.get_root(url)
        relative_path = url[len(root):]
        return path_to_bits(relative_path, transform=noop)

    def _get_path_config(self, url: str) -> dict:
        """
        Introspect the API spec to find the matching operation spec.

        :param url: The API endpoint to look up the resource for. Should be
          qualified as much as the spec['servers'] URLs.
        """
        rel_path_parts = self.get_relative_path_parts(url)

        for path_template, path_config in self.spec['paths'].items():
            path_template_bits = path_to_bits(path_template, transform=noop)

            if len(path_template_bits) != len(rel_path_parts):
                continue

            mismatch = False
            for (path_template_bit, rel_path_bit) in zip(path_template_bits, rel_path_parts):
                # a template var looks like {foo}, so we cannot make any
                # assumptions about those, so skip...
                if path_template_bit.startswith('{') and path_template_bit.endswith('}'):
                    continue

                # mismatch, skip...
                if path_template_bit != rel_path_bit:
                    mismatch = True
                    break

            if mismatch:
                # try the next path...
                continue

            return path_config

        raise ValueError(f"No operation found for url '{url}'")

    def _lookup_schema(self, schema: dict) -> Union[List, Mapping]:
        """
        Perform lookup of schema reference to the actual schema.
        """
        is_collection = schema.get('type') == TYPE_ARRAY

        if is_collection:
            ref = schema['items']['$ref']
        else:
            ref = schema.get('$ref')

        if ref is None:
            raise NotImplementedError("Currently only schema refs are supported")

        _schema = self.spec.copy()
        for key in ref.split('/')[1:]:
            _schema = _schema[key]
        return _schema if not is_collection else [_schema]

    def get_request_resource_schema(self, url: str, method: str) -> dict:
        """
        Retrieve the schema of the request body resource.

        :param url: The API endpoint to look up the resource for. Should be
          qualified as much as the spec['servers'] URLs.
        :param method: the HTTP method of the request.
        """
        # process the URL so that we can match on self.spec['paths']
        method = method.lower()
        path_config = self._get_path_config(url)

        request_body = path_config[method]['requestBody']
        schema = request_body['content'][self.content_type]['schema']

        return self._lookup_schema(schema)

    def get_request_parameters(self, url: str, method: str) -> list:
        """
        Retrieve the supported parameters for a given URL and HTTP method.

        :param url: The API endpoint to look up the resource for. Should be
          qualified as much as the spec['servers'] URLs.
        :param method: the HTTP method of the request.
        """
        method = method.lower()
        try:
            path_config = self._get_path_config(url)
        except ValueError:
            logger.warning("No path config found for url '%s'", url)
            return []

        # parameters key MAY be present
        method_parameters = path_config[method].get('parameters', [])

        # merge endpoint parameters with method parameters
        return path_config['parameters'] + method_parameters

    def get_response_resource_schema(self, url: str, method: str, status_code: str) -> Union[List, Mapping]:
        """
        Retrieve the schema of the request body resource.

        :param url: The API endpoint to look up the resource for. Should be
          qualified as much as the spec['servers'] URLs.
        :param method: the HTTP method of the request.
        :param status_code: the status code of the response, stringified.
        """
        method = method.lower()
        path_config = self._get_path_config(url)

        responses = path_config[method]['responses'][status_code]
        schema = responses['content'][self.content_type]['schema']

        return self._lookup_schema(schema)
