from __future__ import print_function

import inspect
import logging
import textwrap
from abc import ABCMeta
from collections import OrderedDict

import decorator
import six

try:
    from inspect import signature, Parameter
except ImportError:
    from funcsigs import signature, Parameter


class InterfaceMeta(ABCMeta):

    INTERFACE_EXPLICIT_OVERRIDES = True
    INTERFACE_RAISE_ON_VIOLATION = False

    def __new__(mcls, name, bases, dct):
        INTERFACE_EXPLICIT_OVERRIDES = dct.get('INTERFACE_EXPLICIT_OVERRIDES', mcls.INTERFACE_EXPLICIT_OVERRIDES)
        INTERFACE_RAISE_ON_VIOLATION = dct.get('INTERFACE_RAISE_ON_VIOLATION', mcls.INTERFACE_RAISE_ON_VIOLATION)
        for key, value in dct.items():
            if not hasattr(value, '__call__'):
                continue
            for base in bases:
                if base is object:
                    continue
                if hasattr(base, key):
                    method = getattr(base, key)
                    if key is '__init__' or hasattr(method, '__objclass__'):
                        continue
                    if INTERFACE_EXPLICIT_OVERRIDES and not getattr(value, '__override__', False):
                        message = "{}.{} overrides interface method {}.{} without using the @override decorator.".format(
                            name, value.__name__, base.__name__, getattr(base, key).__name__
                        )
                        if INTERFACE_RAISE_ON_VIOLATION:
                            raise RuntimeError(message)
                        else:
                            logging.warning(message)
                    if not getattr(value, '__override_force__', False):
                        mcls.__check_signature(name, base.__name__, getattr(base, key), value, raise_on_violation=INTERFACE_RAISE_ON_VIOLATION)
                    break
        return ABCMeta.__new__(mcls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        ABCMeta.__init__(cls, name, bases, dct)
        if not hasattr(cls, '__interface__'):
            cls.__interface__ = cls
        cls.__doc_update(name, bases, dct)
        cls.__register_implementation__()

    def __register_implementation__(cls):
        pass

    @classmethod
    def __check_signature(mcls, name, basename, from_base, from_class, raise_on_violation=False):
        base_sig = signature(from_base)
        class_sig = signature(from_class)

        base_params = iter(base_sig.parameters.values())
        class_params = iter(class_sig.parameters.values())

        try:
            for index, bp in enumerate(base_params):
                cp = next(class_params)

                while bp.kind is Parameter.VAR_POSITIONAL and cp.kind is Parameter.POSITIONAL_OR_KEYWORD:
                    cp = next(class_params)

                while bp.kind is Parameter.VAR_KEYWORD and cp.kind is not Parameter.VAR_KEYWORD:
                    cp = next(class_params)

                if not (cp.name == bp.name and bp.kind == cp.kind and bp.annotation == cp.annotation):
                    raise ValueError(bp, cp)
        except (StopIteration, ValueError):
            message = "Signature `{}.{}{}` does not conform to interface `{}.{}{}`.".format(
                name, from_class.__name__, class_sig, basename, from_base.__name__, base_sig
            )
            if raise_on_violation:
                raise RuntimeError(message)
            else:
                logging.warning(message)

    def __doc_update(cls, name, bases, dct):

        @decorator.decorator
        def wrapped(f, *args, **kw):
            f.__doc_orig__ = f.__doc__
            return f(*args, **kw)

        mro = inspect.getmro(cls)
        mro = mro[:mro.index(cls.__interface__) + 1]

        # Handle module-level documentation
        module_docs = [cls.__doc__]
        for klass in mro:
            if klass != cls and hasattr(klass, '_{}__doc_attrs'.format(klass.__name__)):
                module_docs.append([
                    'Attributes inherited from {}:'.format(klass.__name__),
                    inspect.cleandoc(getattr(klass, '_{}__doc_attrs'.format(klass.__name__)))
                ])

        cls.__doc__ = cls.__doc_join(*module_docs)

        # Handle function/method-level documentation
        for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):

            # Check if there is anything to do
            if (
                inspect.isabstract(member) or
                getattr(member, '__override_force__', False)
            ):
                continue

            # Extract documentation from this member and the quirks member
            method_docs = OrderedDict()
            for i, klass in enumerate(reversed(mro)):
                if member.__name__ in klass.__dict__:
                    klass_member = getattr(klass, member.__name__)
                    member_docs = klass_member.__doc_orig__ if hasattr(klass_member, '__doc_orig__') else klass_member.__doc__
                    if i == 0 or member_docs:
                        method_docs[klass.__name__] = member_docs

            if hasattr(member, '_quirks_method') and member._quirks_method in cls.__dict__:
                quirk_member = getattr(cls, member._quirks_method, None)
                if quirk_member:
                    quirk_member_docs = quirk_member.__doc_orig__ if hasattr(quirk_member, '__doc_orig__') else quirk_member.__doc__
                    if quirk_member_docs:
                        if cls.__name__ in method_docs:
                            method_docs[cls.__name__] += '\n\n' + quirk_member_docs
                        else:
                            method_docs[cls.__name__] = quirk_member_docs

            if method_docs:
                # Overide method object with new object so we don't modify
                # underlying method that may be shared by multiple classes.
                member = wrapped(member)
                member.__doc_orig__ = member.__doc__
                member.__doc__ = cls.__doc_join(*[
                    docs if i == 0 else [source + ' Quirks:', docs]
                    for i, (source, docs) in enumerate(method_docs.items())
                ])
                setattr(cls, name, wrapped(member))

    def __doc_join(cls, *docs, **kwargs):
        out = []
        for doc in docs:
            if doc in (None, ''):
                continue
            elif isinstance(doc, six.string_types):
                out.append(textwrap.dedent(doc).strip('\n'))
            elif isinstance(doc, (list, tuple)):
                if len(doc) < 2:
                    continue
                d = cls.__doc_join(*doc[1:])
                if d:
                    out.append(
                        '{header}\n{body}'.format(
                            header=doc[0].strip(),
                            body='    ' + d.replace('\n', '\n    ')  # textwrap.indent not available in python2
                        )
                    )
            else:
                raise ValueError("Unrecognised doc format: {}".format(type(doc)))
        return '\n\n'.join(out)
