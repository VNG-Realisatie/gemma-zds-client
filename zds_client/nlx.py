"""
Implements an NLX URL-rewrite client.

Requires the nlx-url-rewriter package.
"""
import warnings
from typing import Any, Optional, Union

from nlx_url_rewriter.rewriter import Rewriter

from .client import Client

warnings.warn(
    "NLX support in gemma-zds-client is deprecated and scheduled for removal in 1.0. "
    "Instead, you should migrate to https://pypi.org/project/zgw-consumers.",
    DeprecationWarning,
)


class NLXClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rewriter = Rewriter()

    def pre_request(self, method: str, url: str, **kwargs) -> Any:
        """
        Rewrite NLX urls in the request body and params.
        """
        json = kwargs.get("json")
        if json:
            self.rewriter.forwards(json)

        params = kwargs.get("params")
        if params:
            self.rewriter.forwards(params)

        return super().pre_request(method, url, **kwargs)

    def post_response(
        self, pre_id: Any, response_data: Optional[Union[dict, list]] = None
    ) -> None:
        if response_data:
            self.rewriter.backwards(response_data)
        super().post_response(pre_id, response_data)
