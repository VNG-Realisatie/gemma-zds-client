import logging
import os
import shutil
import subprocess
import tempfile
from urllib.parse import urljoin

import requests
import yaml

from .schema import get_operation_url

logger = logging.getLogger(__name__)


# TODO: clean this up
BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
))


class Swagger2OpenApi:
    """
    Wrapper around node swagger2openapi
    """

    def __init__(self, swagger: bytes):
        self.swagger = swagger

    def convert(self) -> dict:
        # FIXME: need to find the install of the converter
        tempdir = tempfile.mkdtemp()

        infile = os.path.join(tempdir, 'swagger2.0.yaml')
        outfile = os.path.join(tempdir, 'openapi.yaml')

        try:
            with open(infile, 'wb') as _infile:
                _infile.write(self.swagger)

            cmd = f'node_modules/.bin/swagger2openapi {infile} --outfile {outfile}'
            subprocess.call(cmd, shell=True, cwd=BASE_DIR)

            with open(outfile, 'rb') as _outfile:
                return yaml.safe_load(_outfile)

        finally:
            shutil.rmtree(tempdir)


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


class Client:

    _schema = None

    CONFIG = None

    def __init__(self, service: str, base_path: str='/api/v1/'):
        self.service = service
        self.base_path = base_path

    @classmethod
    def load_config(cls, path: str=None, **manual):
        if cls.CONFIG is not None:
            logger.warning("Re-configuring clients")
        else:
            cls.CONFIG = {}

        if path is not None:
            logger.info("Loading config from %s", path)
            with open(path, 'r') as _config:
                cls.CONFIG.update(yaml.safe_load(_config))

        if manual:
            logger.info("Applying manual config: %r", manual)
            for alias, config in manual.items():
                cls.config.setdefault(alias, {})
                cls.config[alias].update(config)

    @property
    def base_url(self) -> str:
        if self.CONFIG is None:
            raise RuntimeError("You need to load the config first through `Client.load_config(path)`")
        try:
            config = self.CONFIG[self.service]
        except KeyError:
            raise KeyError(f"Service {self.service} unknown, did you specify it in the config?")
        return f"{config['scheme']}://{config['host']}:{config['port']}{self.base_path}"

    @property
    def schema(self):
        if self._schema is None:
            self.fetch_schema()
        return self._schema

    def request(self, path: str, operation: str, method='GET', **kwargs):
        url = urljoin(self.base_url, path)
        headers = kwargs.pop('headers', {})
        headers.setdefault('Accept', 'application/json')
        headers.setdefault('Content-Type', 'application/json')
        headers.update(get_headers(self.schema, operation))
        kwargs['headers'] = headers
        return requests.request(method, url, **kwargs)

    def fetch_schema(self):
        url = urljoin(self.base_url, 'schema/openapi.yaml')
        response = requests.get(url)
        swagger2openapi = Swagger2OpenApi(response.content)
        self._schema = swagger2openapi.convert()

    def list(self, resource: str, **path_kwargs):
        operation_id = f'{resource}_list'
        url = get_operation_url(self.schema, operation_id, **path_kwargs)
        response = self.request(url, operation_id)
        assert response.status_code == 200, response.json()
        return response.json()

    def retrieve(self, resource: str, **path_kwargs):
        operation_id = f'{resource}_read'
        url = get_operation_url(self.schema, operation_id, **path_kwargs)
        response = self.request(url, operation_id)
        assert response.status_code == 200, response.json()
        return response.json()

    def create(self, resource: str, data: dict, **path_kwargs):
        operation_id = f'{resource}_create'
        url = get_operation_url(self.schema, operation_id, **path_kwargs)
        response = self.request(url, operation_id, method='POST', json=data)
        assert response.status_code == 201, response.json()
        return response.json()
