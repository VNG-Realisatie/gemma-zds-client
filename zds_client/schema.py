from urllib.parse import urlparse

DEFAULT_PATH_PARAMETERS = {
    'version': '1',
}


def get_operation_url(spec: dict, operation: str, **kwargs) -> str:
    url = spec['servers'][0]['url']
    base_path = urlparse(url).path

    for path, methods in spec['paths'].items():
        for name, method in methods.items():
            if name == 'parameters':
                continue

            if method['operationId'] == operation:
                format_kwargs = DEFAULT_PATH_PARAMETERS.copy()
                format_kwargs.update(**kwargs)
                path = path.format(**format_kwargs)
                return '{base_path}{path}'.format(base_path=base_path, path=path)

    raise ValueError('Operation {operation} not found'.format(operation=operation))
