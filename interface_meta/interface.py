from abc import ABCMeta

from .utils.conformance import verify_conformance, verify_not_overridden
from .utils.docs import update_docs


class InterfaceMeta(ABCMeta):
    """
    A metaclass that helps subclasses of a class to conform to its API.

    It also makes sure that documentation that might be useful to a user
    is inherited appropriately, and provides a hook for class to handle
    subclass operations.
    """

    INTERFACE_EXPLICIT_OVERRIDES = True
    INTERFACE_RAISE_ON_VIOLATION = False
    INTERFACE_SKIPPED_NAMES = {'__init__'}

    def __init__(cls, name, bases, dct):
        ABCMeta.__init__(cls, name, bases, dct)

        # Register interface class for subclasses
        if not hasattr(cls, '__interface__'):
            cls.__interface__ = cls

        # Read configuration
        explicit_overrides = cls.__get_config(bases, dct, 'INTERFACE_EXPLICIT_OVERRIDES')
        raise_on_violation = cls.__get_config(bases, dct, 'INTERFACE_RAISE_ON_VIOLATION')
        skipped_names = cls.__get_config(bases, dct, 'INTERFACE_SKIPPED_NAMES')

        # Iterate over names in `dct` and check for conformance to interface
        for key, value in dct.items():

            # Skip any key in skipped_names
            if key in skipped_names:  # pragma: no cover
                continue

            # Identify the first instance of this key in the MRO, if it exists, and check conformance
            is_override = False
            for base in cls.__mro__[1:]:
                if base is object:
                    continue
                if key in base.__dict__:
                    is_override = True
                    cls.__verify_conformance(
                        key, name, value, base.__name__, base.__dict__[key],
                        explicit_overrides=explicit_overrides,
                        raise_on_violation=raise_on_violation
                    )
                    break

            if not is_override:
                verify_not_overridden(key, name, value, raise_on_violation=raise_on_violation)

        # Update documentation
        cls.__update_docs(cls, name, bases, dct)

        # Call subclass registration hook
        cls.__register_implementation__()

    def __register_implementation__(cls):
        pass

    @classmethod
    def __get_config(mcls, bases, dct, key):
        default = getattr(mcls, key, None)
        if bases:
            default = getattr(bases[0], key, default)
        return dct.get(key, default)

    @classmethod
    def __verify_conformance(mcls, key, name, value, base_name, base_value,
                             explicit_overrides=True, raise_on_violation=False):
        return verify_conformance(
            key, name, value, base_name, base_value,
            explicit_overrides=explicit_overrides,
            raise_on_violation=raise_on_violation
        )

    @classmethod
    def __update_docs(mcls, cls, name, bases, dct):
        skipped_names = mcls.__get_config(bases, dct, 'INTERFACE_SKIPPED_NAMES')
        return update_docs(cls, name, bases, dct, skipped_names=skipped_names)
