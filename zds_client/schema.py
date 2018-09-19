from urllib.parse import urlparse

DEFAULT_PATH_PARAMETERS = {
    'version': '1',
}


def get_operation_url(spec: dict, operation: str, pattern_only=False, **kwargs) -> str:
    url = spec['servers'][0]['url']
    base_path = urlparse(url).path

    for path, methods in spec['paths'].items():
        for name, method in methods.items():
            if name == 'parameters':
                continue

            if method['operationId'] == operation:
                format_kwargs = DEFAULT_PATH_PARAMETERS.copy()
                format_kwargs.update(**kwargs)
                if not pattern_only:
                    path = path.format(**format_kwargs)
                return '{base_path}{path}'.format(base_path=base_path, path=path)

    raise ValueError('Operation {operation} not found'.format(operation=operation))


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
