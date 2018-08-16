"""
Abstraction on top of generic client to facilitate common ZGW patterns.
"""
from urllib.parse import urlparse

from .client import Client
from .schema import get_operation_url


def path_to_bits(path: str) -> list:
    return [bit for bit in reversed(path.split('/')) if bit]


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


class ZDSClient:

    def __init__(self, *, zrc: Client=None, drc: Client=None, ztc: Client=None):
        self.zrc = zrc
        self.drc = drc
        self.ztc = ztc

    def create_zaak(self, zaaktype: str, zaak_data: dict, **options):
        zaaktype_pattern = get_operation_url(self.ztc.schema, 'zaak_read', pattern_only=True)
        zaaktype_params = extract_params(zaaktype, zaaktype_pattern)

        # fetch zaaktype
        zaaktype = self.ztc.retrieve('zaaktype', **zaaktype_params)

        # TODO: apply zaak_data['geplandeEinddatum'] = zaak_data['startdatum'] + zaaktype['doorlooptijd']
        # TODO: serialize/deserialize to native python types?

        return self.zrc.create('zaak', zaak_data, **options)
