from pkg_resources import get_distribution

from .client import Client

__version__ = get_distribution('gemma-zds-client').version

__all__ = ['Client']
