from pkg_resources import get_distribution

from .client import Client
from .schema import extract_params, get_operation_url

__version__ = get_distribution('gemma-zds-client').version

__all__ = ['Client', 'extract_params', 'get_operation_url']