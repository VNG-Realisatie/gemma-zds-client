import copy
import logging
import re
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from requests.structures import CaseInsensitiveDict

from .auth import ClientAuth
from .config import ClientConfig
from .log import Log
from .oas import schema_fetcher
from .schema import get_headers, get_operation_url

logger = logging.getLogger(__name__)

Object = Dict[str, Any]

UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}",
    flags=re.I,
)


class ClientError(Exception):
    pass


def _get_default_op_suffix_mapping() -> Dict[str, str]:
    return {
        "list": "_list",
        "retrieve": "_read",
        "create": "_create",
        "update": "_update",
        "partial_update": "_partial_update",
        "delete": "_delete",
    }


@dataclass
class Client:
    api_root: str
    auth: Optional[ClientAuth] = None
    operation_suffix_mapping: Dict[str, str] = field(
        default_factory=_get_default_op_suffix_mapping
    )

    _schema: Optional[dict] = field(init=False, default=None)
    _config: ClientConfig = field(init=False)
    _log = Log()

    def __post_init__(self):
        self._config = ClientConfig.from_api_root(self.api_root)

    @classmethod
    def from_url(cls, detail_url: str) -> "Client":
        warnings.warn("Client.from_url will be removed in 2.0", DeprecationWarning)
        parsed_url = urlparse(detail_url)

        # we know that API endpoints look like:
        # - /base_path/collection/<uuid> or
        # - /base_path/collection/<uuid>/subcollection or
        # - /base_path/collection/<uuid>/subcollection/<uuid>
        # So, splitting on UUIDs gives us the base_path + collection
        bits = re.split(UUID_PATTERN, parsed_url.path)
        base_path = (bits[0].rstrip("/").rsplit("/", 1))[0] + "/"

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
        warnings.warn("Client.log will be removed in 2.0", DeprecationWarning)
        return (
            entry for entry in self._log.entries() if entry["service"] == self.service
        )

    @property
    def base_url(self) -> str:
        default = f"{self._config.base_url}{self.base_path}"
        return self._base_url or default

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        self._base_url = base_url

    @property
    def schema(self):
        if self._schema is None:
            self.fetch_schema()
        return self._schema

    def pre_request(self, method: str, url: str, **kwargs) -> Any:
        """
        Perform any pre-request processing required.

        The kwargs are literally passed to :meth:`requests.request` and may
        be mutated in place.

        The return value is passed as first argument to :meth:`post_response`.
        """
        pass

    def request(
        self,
        path: str,
        operation: str,
        method="GET",
        expected_status=200,
        request_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> Union[List[Object], Object]:
        """
        Make the HTTP request using requests.

        The URL is created based on the path and base URL and any defaults
        from the OAS schema are injected.

        :return: a list or dict, the result of calling response.json()
        :raises: :class:`requests.HTTPException` for internal server errors
        :raises: :class:`ClientError` for HTTP 4xx status codes
        """
        url = urljoin(self.base_url, path)

        if request_kwargs:
            kwargs.update(request_kwargs)

        headers = CaseInsensitiveDict(kwargs.pop("headers", {}))
        headers.setdefault("Accept", "application/json")
        headers.setdefault("Content-Type", "application/json")
        schema_headers = get_headers(self.schema, operation)
        for header, value in schema_headers.items():
            headers.setdefault(header, value)
        if self.auth:
            headers.update(self.auth.credentials())

        kwargs["headers"] = headers

        pre_id = self.pre_request(method, url, **kwargs)

        response = requests.request(method, url, **kwargs)

        try:
            response_json = response.json()
        except Exception:
            response_json = None

        self.post_response(pre_id, response_json)

        self._log.add(
            self.service,
            url,
            method,
            dict(headers),
            copy.deepcopy(kwargs.get("data", kwargs.get("json", None))),
            response.status_code,
            dict(response.headers),
            response_json,
            params=kwargs.get("params"),
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code >= 500:
                raise
            raise ClientError(response_json) from exc

        assert response.status_code == expected_status, response_json
        return response_json

    def post_response(
        self, pre_id: Any, response_data: Optional[Union[dict, list]] = None
    ) -> None:
        pass

    def fetch_schema(self) -> None:
        url = urljoin(self.base_url, "schema/openapi.yaml")
        logger.info("Fetching schema at '%s'", url)
        self._schema = schema_fetcher.fetch(url, {"v": "3"})

    def list(
        self,
        resource: str,
        params=None,
        query_params=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> List[Object]:
        op_suffix = self.operation_suffix_mapping["list"]
        operation_id = f"{resource}{op_suffix}"
        url = get_operation_url(
            self.schema, operation_id, base_url=self.base_url, **path_kwargs
        )
        if query_params and not params:
            warnings.warn(
                "Client.list 'query_params' kwarg is deprecated, use 'params' instead.",
                DeprecationWarning,
            )
            params = query_params

        return self.request(
            url, operation_id, params=params, request_kwargs=request_kwargs
        )

    def retrieve(
        self,
        resource: str,
        url=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Object:
        op_suffix = self.operation_suffix_mapping["retrieve"]
        operation_id = f"{resource}{op_suffix}"
        if url is None:
            url = get_operation_url(
                self.schema, operation_id, base_url=self.base_url, **path_kwargs
            )
        return self.request(url, operation_id, request_kwargs=request_kwargs)

    def create(
        self,
        resource: str,
        data: dict,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Object:
        op_suffix = self.operation_suffix_mapping["create"]
        operation_id = f"{resource}{op_suffix}"
        url = get_operation_url(
            self.schema, operation_id, base_url=self.base_url, **path_kwargs
        )
        return self.request(
            url,
            operation_id,
            method="POST",
            json=data,
            expected_status=201,
            request_kwargs=request_kwargs,
        )

    def update(
        self,
        resource: str,
        data: dict,
        url=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Object:
        op_suffix = self.operation_suffix_mapping["update"]
        operation_id = f"{resource}{op_suffix}"
        if url is None:
            url = get_operation_url(
                self.schema, operation_id, base_url=self.base_url, **path_kwargs
            )
        return self.request(
            url,
            operation_id,
            method="PUT",
            json=data,
            expected_status=200,
            request_kwargs=request_kwargs,
        )

    def partial_update(
        self,
        resource: str,
        data: dict,
        url=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Object:
        op_suffix = self.operation_suffix_mapping["partial_update"]
        operation_id = f"{resource}{op_suffix}"
        if url is None:
            url = get_operation_url(
                self.schema, operation_id, base_url=self.base_url, **path_kwargs
            )
        return self.request(
            url,
            operation_id,
            method="PATCH",
            json=data,
            expected_status=200,
            request_kwargs=request_kwargs,
        )

    def delete(
        self,
        resource: str,
        url=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Object:
        op_suffix = self.operation_suffix_mapping["delete"]
        operation_id = f"{resource}{op_suffix}"
        if url is None:
            url = get_operation_url(
                self.schema, operation_id, base_url=self.base_url, **path_kwargs
            )
        return self.request(
            url,
            operation_id,
            method="DELETE",
            expected_status=204,
            request_kwargs=request_kwargs,
        )

    def operation(
        self,
        operation_id: str,
        data: dict,
        method="POST",
        url=None,
        request_kwargs: Optional[dict] = None,
        **path_kwargs,
    ) -> Union[List[Object], Object]:
        if url is None:
            url = get_operation_url(
                self.schema, operation_id, base_url=self.base_url, **path_kwargs
            )
        return self.request(
            url, operation_id, method=method, json=data, request_kwargs=request_kwargs
        )
