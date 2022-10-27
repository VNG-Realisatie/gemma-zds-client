import time

# from typing import Protocol
from typing import Dict

import jwt

JWT_ALG = "HS256"


HeaderDict = Dict[str, str]


# class ClientAuthProtocol(Protocol):

#     def credentials(self) -> HeaderDict:
#         ...


class ClientAuth:
    """
    Auth for the ZDS client, using JWT.

    Usage:

    >>> auth = ClientAuth(
            client_id="zrc",
            secret="my-secret",
            user_id="my-id",
            user_representation="my-name"
        )
    >>> auth.credentials()
    {
        'Authorization': '<base64>.<base64>.<base64>'
    }
    >>> requests.get(url, **auth.credentials())

    TODO: make pluggable and implement some common auth schemes.
    """

    def __init__(
        self,
        client_id: str,
        secret: str,
        user_id: str = "",
        user_representation: str = "",
        **claims
    ):
        """
        Initialize the client authentication configuration.
        """
        self.client_id = client_id
        self.secret = secret
        # audit information
        self.user_id = user_id
        self.user_representation = user_representation

        # any extra arbitrary claims are just forwarded to the payload
        self.claims = claims

    def credentials(self) -> dict:
        """
        Return the HTTP Header containing the credentials.
        """
        if not hasattr(self, "_credentials"):
            payload = {
                # standard claims
                "iss": self.client_id,
                "iat": int(time.time()),
                # custom claims
                "client_id": self.client_id,
                "user_id": self.user_id,
                "user_representation": self.user_representation,
                **self.claims,
            }

            encoded = jwt.encode(payload, self.secret, algorithm=JWT_ALG)

            self._credentials = {
                "Authorization": "Bearer {encoded}".format(encoded=encoded)
            }
        return self._credentials
