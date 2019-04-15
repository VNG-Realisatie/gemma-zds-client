import copy
import logging
import re
from typing import Any, Dict, List, Union
from urllib.parse import urljoin, urlparse

import requests
import yaml

from .config import ClientConfig
from .log import Log
from .oas import schema_fetcher
from .registry import registry
from .schema import get_operation_url

logger = logging.getLogger(__name__)

Object = Dict[str, Any]

UUID_PATTERN = re.compile(
    r'[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}',
    flags=re.I
)


def get_headers(spec: dict, operation: str) -> dict:
    """
    Extract required headers and use the default value from the API spec.
    """
    headers = {}

    def filter_header_params(params: list):
        return [
            param for param in params
            if param['in'] == 'header' and param['required']
        ]

    for path, methods in spec['paths'].items():
        path_parameters = filter_header_params(methods.get('parameters', []))
        for name, method in methods.items():
            if name == 'parameters':
                continue

            if method['operationId'] != operation:
                continue

            method_parameters = filter_header_params(method.get('parameters', []))

            for param in path_parameters + method_parameters:
                enum = param['schema'].get('enum', [])
                default = param['schema'].get('default')

                assert len(enum) == 1 or default, "Can't choose an appropriate default header value"
                headers[param['name']] = default or enum[0]

    return headers


class ClientError(Exception):
    pass


class Client:

    _schema = None
    _log = Log()

    auth = None

    def __init__(self, service: str, base_path: str='/api/v1/'):
        # pull out the config, so that we should be thread safe
        try:
            self._config = registry[service]
        except KeyError:
            raise RuntimeError(
                f"Service '{service}' is not known in the client registry. "
                "Did you load the config first through `Client.load_config(path, **manual)`?"
            )

        self.service = service
        self.base_path = base_path

        self._base_url = None

        self.auth = self._config.auth

    def __repr__(self):
        return "<%s: service=%r base_url=%r>" % (
            self.__class__.__name__,
            self.service,
            self.base_url
        )

    @classmethod
    def load_config(cls, path: str=None, **manual):
        """
        Initialize the client configuration.

        The configuration is delegated to the registry, so multiple instances
        of the client share the same configuration.

        The config file should have the following format:

        .. code-block:: yaml

            alias1:
              scheme: http(s)
              host: localhost
              port: 8000
              auth:
                client_id: some-client-id
                secret: very-secret
                scopes:
                  - scope1
                  - scope2

        Multiple service configs are supported, each with their own alias.
        The `port` and `auth` keys are optional. Port will default to 80 or
        443 depending on the scheme.

        :param path: path to the yaml file holding the config
        :param manual: any manual overrides, as kwargs. Note this completely
          overwrites any existing config in the YAML file if specified.
        """
        if path is not None:
            logger.info("Loading config from %s", path)
            with open(path, 'r') as config_file:
                client_configs = yaml.safe_load(config_file)

            for alias, _config in client_configs.items():
                config = ClientConfig.from_dict(_config)
                registry.register(alias, config)

        if manual:
            logger.info("Applying manual config: %r", manual)
            for alias, _config in manual.items():
                config = ClientConfig.from_dict(_config)
                registry.register(alias, config)

    @classmethod
    def from_url(cls, detail_url: str) -> 'Client':
        parsed_url = urlparse(detail_url)

        # we know that API endpoints look like:
        # - /base_path/collection/<uuid> or
        # - /base_path/collection/<uuid>/subcollection or
        # - /base_path/collection/<uuid>/subcollection/<uuid>
        # So, splitting on UUIDs gives us the base_path + collection
        bits = re.split(UUID_PATTERN, parsed_url.path)
        base_path = (
            bits[0]
            .rstrip('/')
            .rsplit('/', 1)
        )[0] + '/'

        # register the config
        config = ClientConfig.from_url(detail_url)
        alias = config.base_url
        registry.register(alias, config)
        return cls(alias, base_path)

    @property
    def log(self):
        """
        Local log entries.
        """
        return (entry for entry in self._log.entries() if entry['service'] == self.service)

    def _get_base_url(self) -> str:
        if self._base_url is not None:
            return self._base_url
        return f"{self._config.base_url}{self.base_path}"

    def _set_base_url(self, base_url: str) -> None:
        self._base_url = base_url

    base_url = property(_get_base_url, _set_base_url)

    @property
    def schema(self):
        if self._schema is None:
            self.fetch_schema()
        return self._schema

    def request(self, path: str, operation: str, method='GET', expected_status=200,
                **kwargs) -> Union[List[Object], Object]:
        """
        Make the HTTP request using requests.

        The URL is created based on the path and base URL and any defaults
        from the OAS schema are injected.

        :return: a list or dict, the result of calling response.json()
        :raises: :class:`requests.HTTPException` for internal server errors
        :raises: :class:``ClientError` for HTTP 4xx status codes
        """
        url = urljoin(self.base_url, path)

        headers = kwargs.pop('headers', {})
        headers.setdefault('Accept', 'application/json')
        headers.setdefault('Content-Type', 'application/json')
        headers.update(get_headers(self.schema, operation))

        if self.auth:
            headers.update(self.auth.credentials())

        kwargs['headers'] = headers

        response = requests.request(method, url, **kwargs)

        try:
            response_json = response.json()
        except Exception:
            response_json = None

        self._log.add(
            self.service,
            url,
            method,
            headers,
            copy.deepcopy(kwargs.get('data', kwargs.get('json', None))),
            response.status_code,
            dict(response.headers),
            response_json,
            params=kwargs.get('params'),
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code >= 500:
                raise
            raise ClientError(response_json) from exc

        assert response.status_code == expected_status, response_json
        return response_json

    def fetch_schema(self) -> None:
        url = urljoin(self.base_url, 'schema/openapi.yaml')
        logger.info("Fetching schema at '%s'", url)
        self._schema = schema_fetcher.fetch(url, {'v': '3'})

    def list(self, resource: str, query_params=None, **path_kwargs) -> List[Object]:
        operation_id = '{resource}_list'.format(resource=resource)
        url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, params=query_params)

    def retrieve(self, resource: str, url=None, **path_kwargs) -> Object:
        operation_id = '{resource}_read'.format(resource=resource)
        if url is None:
            url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id)

    def create(self, resource: str, data: dict, **path_kwargs) -> Object:
        operation_id = '{resource}_create'.format(resource=resource)
        url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, method='POST', json=data, expected_status=201)

    def update(self, resource: str, data: dict, url=None, **path_kwargs) -> Object:
        operation_id = '{resource}_update'.format(resource=resource)
        if url is None:
            url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, method='PUT', json=data, expected_status=200)

    def partial_update(self, resource: str, data: dict, url=None, **path_kwargs) -> Object:
        operation_id = '{resource}_partial_update'.format(resource=resource)
        if url is None:
            url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, method='PATCH', json=data, expected_status=200)

    def delete(self, resource: str, url=None, **path_kwargs) -> Object:
        operation_id = '{resource}_delete'.format(resource=resource)
        if url is None:
            url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, method='DELETE', expected_status=204)

    def operation(self, operation_id: str, data: dict, url=None, **path_kwargs) -> Union[List[Object], Object]:
        if url is None:
            url = get_operation_url(self.schema, operation_id, base_url=self.base_url, **path_kwargs)
        return self.request(url, operation_id, method='POST', json=data)
