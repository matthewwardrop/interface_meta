from collections import OrderedDict
import textwrap

import decorator
import six
import inspect


def update_docs(cls, name, bases, dct, skipped_names=None):

    @decorator.decorator
    def wrapped(f, *args, **kw):
        return f(*args, **kw)

    mro = inspect.getmro(cls)
    mro = mro[:mro.index(cls.__interface__) + 1]
    skipped_names = skipped_names or set()

    # Handle module-level documentation
    module_docs = [cls.__doc__]
    for klass in mro:
        if hasattr(klass, '_{}__doc_attrs'.format(klass.__name__)):
            module_docs.append([
                'Attributes:' if klass is cls else 'Attributes inherited from {}:'.format(klass.__name__),
                inspect.cleandoc(getattr(klass, '_{}__doc_attrs'.format(klass.__name__)))
            ])

    cls.__doc__ = doc_join(*module_docs)

    # Handle function/method-level documentation
    for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):

        # Check if there is anything to do
        if (
            inspect.isabstract(member) or
            getattr(member, '__override_force__', False)
            or name in skipped_names and not hasattr(member, '_quirks_method')
        ):
            continue

        # Extract documentation from this member and the quirks member
        method_docs = OrderedDict()
        last_docs = None
        for i, klass in enumerate(reversed(mro) if getattr(member, '_quirks_mro', True) else mro[:1]):
            if member.__name__ in klass.__dict__:
                klass_member = getattr(klass, member.__name__)
                member_docs = klass_member.__doc_orig__ if hasattr(klass_member, '__doc_orig__') else klass_member.__doc__
                if (i == 0 or member_docs) and member_docs != last_docs:
                    last_docs = method_docs[klass.__name__] = member_docs

        if hasattr(member, '_quirks_method') and member._quirks_method in cls.__dict__:
            quirk_member = getattr(cls, member._quirks_method, None)
            if quirk_member:
                quirk_member_docs = quirk_member.__doc_orig__ if hasattr(quirk_member, '__doc_orig__') else quirk_member.__doc__
                if quirk_member_docs:
                    if cls.__name__ in method_docs:
                        method_docs[cls.__name__] = inspect.cleandoc(method_docs[cls.__name__]) + '\n\n' + inspect.cleandoc(quirk_member_docs)
                    else:
                        method_docs[cls.__name__] = quirk_member_docs

        if method_docs:
            # Overide method object with new object so we don't modify
            # underlying method that may be shared by multiple classes.
            member = wrapped(member)
            if not hasattr(member, '__doc_orig__'):
                member.__doc_orig__ = member.__doc__
            member.__doc__ = doc_join(*[
                docs if i == 0 else [source + ' Quirks:', docs]
                for i, (source, docs) in enumerate(method_docs.items())
            ])
            setattr(cls, name, wrapped(member))


def doc_join(*docs, **kwargs):
    out = []
    for doc in docs:
        if doc in (None, ''):
            continue
        elif isinstance(doc, six.string_types):
            out.append(textwrap.dedent(doc).strip('\n'))
        elif isinstance(doc, (list, tuple)):
            if len(doc) < 2:
                continue
            d = doc_join(*doc[1:])
            if d:
                if not out:
                    out.append('\n')
                out.append(
                    '{header}\n{body}'.format(
                        header=doc[0].strip(),
                        body='    ' + d.replace('\n', '\n    ')  # textwrap.indent not available in python2
                    )
                )
        else:
            raise ValueError("Unrecognised doc format: {}".format(type(doc)))
    return '\n\n'.join(out)
