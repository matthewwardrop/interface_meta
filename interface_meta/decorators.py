def quirk_docs(method=None):
    def doc_wrapper(f):
        f._quirks_method = method
        return f
    return doc_wrapper


def override(f=None, force=False):
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
