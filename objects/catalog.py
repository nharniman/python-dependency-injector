"""Catalog module."""

from .providers import Provider


class AbstractCatalog(object):

    """Abstract object provides catalog."""

    def __init__(self, *used_providers):
        """Initializer."""
        self.__used_providers__ = set(used_providers)

    def __getattribute__(self, item):
        """Return providers."""
        attribute = super(AbstractCatalog, self).__getattribute__(item)
        if item in ('__used_providers__',):
            return attribute

        if attribute not in self.__used_providers__:
            raise AttributeError('Provider \'{}\' is not listed in '
                                 'dependencies'.format(item))
        return attribute

    @classmethod
    def __all_providers__(cls, provider_type=Provider):
        """Return set of all class providers."""
        providers = set()
        for attr_name in set(dir(cls)) - set(dir(AbstractCatalog)):
            provider = getattr(cls, attr_name)
            if not isinstance(provider, provider_type):
                continue
            providers.add((attr_name, provider))
        return providers

    @classmethod
    def __override___(cls, overriding):
        """
        Override current catalog providers by overriding catalog providers.

        :param overriding: AbstractCatalog
        """
        overridden = overriding.__all_providers__() - cls.__all_providers__()
        for name, provider in overridden:
            overridden_provider = getattr(cls, name)
            overridden_provider.__override__(provider)


def overrides(catalog):
    """Catalog overriding decorator."""
    def decorator(overriding_catalog):
        """Overriding decorator."""
        catalog.__override___(overriding_catalog)
        return overriding_catalog
    return decorator