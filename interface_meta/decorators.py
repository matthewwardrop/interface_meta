def quirk_docs(method=None, mro=True):
    """
    Indicate to `InterfaceMeta` how the wrapped method should be documented.

    Methods need not normally be decorated with this decorator, except in the
    following cases:
    - documentation for quirks should be lifted not from overrides to a
      method, but from some other method (e.g. because subclasses or
      implementations of the interface should override behaviour in a "private"
      method rather than the top-level public method).
    - the method has been nominated by the interface configuration to be
      skipped, in which case decorating with this method will enable
      documentation generation as if it were not.

    Use this decorator as `@quirk_docs([method=...], [mro=...])`.

    Args:
        method (str, None): A method from which documentation for implementation
            specific quirks should be extracted. [Useful when implementations
            of an interface are supposed to change underlying methods rather
            than the public method itself].
        mro (bool): Whether to include documentation from all levels of the
            MRO, starting from the most primitive class that implementated it.
            All higher levels will be considered as "quirks" to the interface's
            definition.

    Returns:
        function: A function wrapper that attaches attributes `_quirks_method` and
        `_quirks_mro` to the method, for interpretation by `InterfaceMeta`.
    """
    def doc_wrapper(f):
        f._quirks_method = method
        f._quirks_mro = mro
        return f
    return doc_wrapper


def override(f=None, force=False):
    """
    Indicate to `InterfaceMeta` that this method has intentionally overridden an interface method.

    This decorator also allows one to indicate that the method should be
    overridden without warnings even when it does not conform to the API.

    Use this decorator as `@override` or `@override(force=True)`.

    Args:
        f (function, None): The function, if method is decorated by the decorator
            without arguments (e.g. @override), else None.
        force (bool): Whether to force override of method even if the API does
            note match. Note that in this case, documentation is not inherited
            from the MRO.

    Returns:
        function: The wrapped function of function wrapper depending on which
            arguments are present.
    """
    if f is not None:
        f.__override__ = True
        f.__override_force__ = force
        return f
    else:
        def override(f):
            f.__override__ = True
            f.__override_force__ = force
            return f
        return override
