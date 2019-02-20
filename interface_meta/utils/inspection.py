import functools
import inspect
from abc import abstractproperty

try:
    from abc import abstractclassmethod, abstractstaticmethod
except ImportError:  # pragma: no cover
    abstractclassmethod = classmethod
    abstractstaticmethod = staticmethod

try:
    from inspect import signature
except ImportError:  # pragma: no cover
    from funcsigs import signature


# Abstract away differences between functions, methods and descriptors

def _get_member(member):
    if inspect.ismethod(member):
        return member.__func__
    if inspect.isdatadescriptor(member):
        return member.fget
    if isinstance(member, classmethod):
        return member.__get__(object, object).__func__
    if inspect.ismethoddescriptor(member):
        return member.__get__(object, object)
    return member


def member_type_understood(member):
    return not (
        inspect.isdatadescriptor(member) and not isinstance(member, (property, abstractproperty))
        or inspect.ismethoddescriptor(member) and not isinstance(member, (classmethod, staticmethod, abstractclassmethod, abstractstaticmethod))
    )


def is_method(member):
    return inspect.isfunction(member) or inspect.ismethod(member)


def is_functional_member(member):
    """
    Check whether a class member from the __dict__ attribute is a method.

    In Python, this can be true in three ways:
        - It is literally a Python function (in Python 3)
        - It is a Python method (in Python 2)
        - It is a method descriptor (wrapping a function)

    Args:
        member (object): An object in the class __dict__.

    Returns:
        bool: `True` if the member is a function (or acts like one).
    """
    return (
        inspect.isfunction(member)
        or inspect.ismethod(member)
        or (
            inspect.ismethoddescriptor(member)
            and isinstance(member, (classmethod, staticmethod))
        )
    )


def get_functional_signature(member):
    return signature(_get_member(member))


def functional_hasattr(member, attr):
    return hasattr(_get_member(member), attr)


def functional_getattr(member, attr, default=None):
    return getattr(_get_member(member), attr, default)


def functional_setattr(member, attr, value):
    setattr(_get_member(member), attr, value)


def functional_delattr(member, attr):
    delattr(_get_member(member), attr)


def get_functional_wrapper(member):
    """
    Return a new functional wrapper around the provided member.

    Since `interface_meta` rewrites documentation strings, if the affected
    method is from a parent class, then we need to create a new function wrapper
    so that mutating the documentation does not leak to higher classes. This
    function does just that.

    Args:
        member (functional): The functional object to be wrapped.

    Returns:
        functional: An object that is functionally equivalent to `member`,
            but which can have its own attributes.
    """
    class_method = isinstance(member, classmethod)
    property_method = isinstance(member, property)
    static_method = isinstance(member, staticmethod)

    function = _get_member(member)

    @functools.wraps(function)
    def wrapper(*args, **kwargs):  # pragma: no cover
        return function(*args, **kwargs)

    for attr in ['_quirks_method', '_quirks_mro', '__override__', '__override_force__']:
        if hasattr(function, attr):
            setattr(wrapper, attr, getattr(function, attr))

    if class_method:
        return classmethod(wrapper)
    elif property_method:
        return property(fget=wrapper, fset=member.fset, fdel=member.fdel)
    elif static_method:
        return staticmethod(wrapper)
    return wrapper


# Override checking

def has_explicit_override(member):
    return functional_getattr(member, '__override__', False)


def has_forced_override(member):
    return functional_getattr(member, '__override_force__', False)


# Documentation helpers

def has_updatable_docs(member):
    return (
        is_functional_member(member) or inspect.isdatadescriptor(member) and isinstance(member, (property, abstractproperty))
    )


def get_functional_docs(member, orig=True):
    if orig and functional_hasattr(member, '__doc_orig__'):
        return functional_getattr(member, '__doc_orig__')
    return functional_getattr(member, '__doc__')


def set_functional_docs(member, docs):
    if not functional_hasattr(member, '__doc_orig__'):
        functional_setattr(member, '__doc_orig__', functional_getattr(member, '__doc__'))
    functional_setattr(member, '__doc__', docs)


def has_class_attr_docs(cls):
    return hasattr(cls, '_{}__doc_attrs'.format(cls.__name__))


def get_class_attr_docs(cls):
    return getattr(cls, '_{}__doc_attrs'.format(cls.__name__))


# Quirk documentation helpers

def has_quirk_docs_method(member):
    return functional_hasattr(member, '_quirks_method')


def get_quirk_docs_method(member):
    return functional_getattr(member, '_quirks_method', None)


def set_quirk_docs_method(member, method):
    return functional_setattr(member, '_quirks_method', method)


def has_quirk_docs_mro(member):
    return functional_hasattr(member, '_quirks_mro')


def get_quirk_docs_mro(member):
    return functional_getattr(member, '_quirks_mro', True)


def set_quirk_docs_mro(member, mro):
    return functional_setattr(member, '_quirks_mro', mro)
