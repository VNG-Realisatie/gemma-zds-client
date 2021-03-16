import time

from .compat import jwt_encode


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

            # TODO: drop custom header in 1.0
            headers = {"client_identifier": self.client_id}
            encoded = jwt_encode(
                payload, self.secret, headers=headers, algorithm="HS256"
            )

            self._credentials = {
                "Authorization": "Bearer {encoded}".format(encoded=encoded)
            }
        return self._credentials
