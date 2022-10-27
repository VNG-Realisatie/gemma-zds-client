from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

DEFAULT_PORTS = {
    "https": 443,
    "http": 80,
}


@dataclass
class ClientConfig:
    scheme: str = "https"
    host: str = "localhost"
    port: Optional[int] = None
    base_path: str = "/"

    @classmethod
    def from_api_root(cls, api_root: str) -> "ClientConfig":
        parsed_url = urlparse(api_root)
        if ":" in parsed_url.netloc:
            host, port = parsed_url.netloc.split(":")
        else:
            host, port = parsed_url.netloc, None
        return cls(
            scheme=parsed_url.scheme,
            host=host,
            port=int(port) if port is not None else None,
            base_path=parsed_url.path or "/",
        )

    @property
    def base_url(self) -> str:
        """
        Calculate the base URL, without the api root base path.
        """
        base = "{}://{}".format(self.scheme, self.host)

        # if it's the default ports, we don't need to be explicit
        default_port = DEFAULT_PORTS[self.scheme]
        if self.port == default_port:
            return base

        return "{}:{}".format(base, self.port)
