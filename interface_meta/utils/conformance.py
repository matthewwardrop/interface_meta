import inspect
import logging
from abc import abstractproperty

from .reporting import report_violation

try:
    from inspect import signature, Parameter, _empty
except ImportError:
    from funcsigs import signature, Parameter, _empty


def isfunction(member):
    return inspect.isfunction(member) or inspect.ismethod(member)


def verify_conformance(key, name, value, base_name, base_value,
                       explicit_overrides=True, raise_on_violation=False):

    if hasattr(base_value, '__objclass__'):  # Method is attached to metaclass, so should not be checked.
        return

    if inspect.isdatadescriptor(value) and not type(value) in (property, abstractproperty):
        logging.debug("`interface_meta` does not know how to handle attribute `{}.{}` with type: `{}`. Skipping.".format(name, key, type(value)))
        return

    if (
            isfunction(value) and getattr(value, '__override_force__', False)
            or inspect.isdatadescriptor(value) and getattr(value.fget, '__override_force__', False)
    ):
        return

    # Check that type of value has not changed.
    if type(value) is not type(base_value):
        if isfunction(value) and isfunction(base_value):
            # Python 2 distinguishes between instancemethods and functions
            pass
        elif type(value) in (abstractproperty, property) and not isfunction(base_value):
            # This should be okay, provided the property is properly crafted.
            pass
        elif isfunction(value):
            report_violation(
                "{}.{} changes the type of {}.{} ({} instead of {}) without using the @override decorator.".format(
                    name, key, base_name, key, type(value), type(base_value)
                ),
                raise_on_violation
            )
        else:  # Most other type changes should be fine
            pass

    if inspect.isdatadescriptor(value):
        if explicit_overrides and not getattr(value.fget, '__override__', False):
            report_violation(
                "{}.{} overrides interface property {}.{} without using the @override decorator.".format(
                    name, key, base_name, key
                ),
                raise_on_violation
            )

    elif isfunction(value):
        if explicit_overrides and not getattr(value, '__override__', False):
            report_violation(
                "{}.{} overrides interface method {}.{} without using the @override decorator.".format(
                    name, key, base_name, key
                ),
                raise_on_violation
            )
        verify_signature(key, name, value, base_name, base_value, raise_on_violation=raise_on_violation)


def verify_signature(key, name, value, base_name, base_value, raise_on_violation=False):
    sig = signature(value)
    base_sig = signature(base_value)

    if not check_signatures_compatible(sig, base_sig):
        message = "Signature `{}.{}{}` does not conform to interface `{}.{}{}`.".format(
            name, key, sig, base_name, key, base_sig
        )
        if raise_on_violation:
            raise RuntimeError(message)
        else:
            logging.warning(message)


def check_signatures_compatible(sig, ref_sig):
    params = iter(sig.parameters.values())
    base_params = iter(ref_sig.parameters.values())

    try:
        for index, bp in enumerate(base_params):
            cp = next(params)

            while bp.kind is Parameter.VAR_POSITIONAL and cp.kind is Parameter.POSITIONAL_OR_KEYWORD:
                cp = next(params)

            while bp.kind is Parameter.VAR_KEYWORD and cp.kind is not Parameter.VAR_KEYWORD:
                cp = next(params)

            if not (cp.name == bp.name and bp.kind == cp.kind and bp.default == cp.default and bp.annotation == cp.annotation):
                raise ValueError(bp, cp)

    except (StopIteration, ValueError):
        return False

    for param in params:
        if param.kind is Parameter.POSITIONAL_ONLY or param.kind is Parameter.POSITIONAL_OR_KEYWORD and param.default == _empty:
            return False

    return True
