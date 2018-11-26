import time
import warnings

import jwt


class ClientAuth:
    """
    Auth for the ZDS client, using JWT.

    Usage:

    >>> auth = ClientAuth(
            client_id='zrc',
            secret='my-secret',
            scopes=['zds.scopes.zaken.aanmaken']
        )
    >>> auth.set_claims(zaaktypes=['http://ztc.nl/api/v1/zaaktype/1234'])
    >>> auth.credentials()
    {
        'Authorization': '<base64>.<base64>.<base64>'
    }
    >>> requests.get(url, **auth.credentials())
    """

    def __init__(self, client_id: str, secret: str, **claims):
        self.client_id = client_id

        if secret is None:
            warnings.warn("`None` secret received -  casting to empty string", UserWarning)
            secret = ''

        self.secret = secret

        self.claims = claims

    def set_claims(self, **kwargs) -> None:
        """
        Set the claims for the client.
        """
        claims = self.claims.copy()
        claims.update(**kwargs)

        # invalidate cache if needed (claims have changed)
        if hasattr(self, '_credentials') and claims != self.claims:
            del self._credentials

        self.claims = claims

    def credentials(self) -> dict:
        """
        Return the HTTP Header containing the credentials.
        """
        if not hasattr(self, '_credentials'):
            payload = {
                # standard claims
                'iss': self.client_id,
                'iat': int(time.time()),
                # custom claims
                'zds': self.claims,
            }
            headers = {
                'client_identifier': self.client_id,
            }
            encoded = jwt.encode(payload, self.secret, headers=headers, algorithm='HS256')
            encoded = encoded.decode()  # bytestring to string

            self._credentials = {
                'Authorization': f"Bearer {encoded}"
            }
        return self._credentials
