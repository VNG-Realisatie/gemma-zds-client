import time
import warnings

from .compat import jwt_encode


def _warn_ac():
    warnings.warn(
        "Starting with 1.0, specifying claims will no longer be "
        "supported. Authorizations should be configured on the AC "
        "instead",
        DeprecationWarning,
    )


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

        if claims:
            _warn_ac()
        self.claims = claims

        self.user_id = user_id
        self.user_representation = user_representation

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
            }
            if self.claims:
                payload["zds"] = self.claims

            # TODO: drop custom header in 1.0
            headers = {"client_identifier": self.client_id}
            encoded = jwt_encode(
                payload, self.secret, headers=headers, algorithm="HS256"
            )

            self._credentials = {
                "Authorization": "Bearer {encoded}".format(encoded=encoded)
            }
        return self._credentials
