# InterfaceMeta

[![PyPI - Version](https://img.shields.io/pypi/v/interface_meta.svg)](https://pypi.org/project/interface_meta/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/interface_meta.svg)
![PyPI - Status](https://img.shields.io/pypi/status/interface_meta.svg)
[![build](https://img.shields.io/github/workflow/status/matthewwardrop/interface_meta/Run%20Tox%20Tests)](https://github.com/matthewwardrop/interface_meta/actions?query=workflow%3A%22Run+Tox+Tests%22)
[![codecov](https://codecov.io/gh/matthewwardrop/interface_meta/branch/master/graph/badge.svg?token=W4LD72EQMM)](https://codecov.io/gh/matthewwardrop/interface_meta)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

`interface_meta` provides a convenient way to expose an extensible API with
enforced method signatures and consistent documentation.

- **Documentation:** See below (full documentation will come at some point).
- **Source:** https://github.com/matthewwardrop/interface_meta
- **Bug reports:** https://github.com/matthewwardrop/interface_meta/issues

## Overview

This library has been extracted (with some modifications) from
[`omniduct`](https://github.com/airbnb/omniduct), a library also principally
written by this author, where it was central to the extensible plugin
architecture. It places an emphasis on the functionality required to create a
well-documented extensible plugin system, whereby the act of subclassing is
sufficient to register the plugin and ensure compliance to the parent API. As
such, this library boasts the following features:

- All subclasses of an interface must conform to the parent's API.
- Hierarchical runtime property existence and method signature checking. Methods
  are permitted to add additional *optional* arguments, but otherwise must
  conform to the API of their parent class (which themselves may have extended
  the API of the interface).
- Subclass definition time hooks (e.g. for registration of subclasses into a
  library of plugins, etc).
- Optional requirement for methods in subclasses to explicity decorate methods
  with an `override` decorator when replacing methods on an interface, making
  it clearer as to when a class is introducing new methods versus replacing
  those that form the part of the interface API.
- Generation of clear docstrings on implementations that stitches together the
  base interface documentation with any downstream extensions and quirks.
- Support for extracting the quirks documentation for a method from other method
  docstrings, in the event that subclass implementations are done in an internal
  method.
- Compatibility with ABCMeta from the standard library.

## Example code

```python
from abc import abstractmethod, abstractproperty
from interface_meta import InterfaceMeta, override, quirk_docs

class MyInterface(metaclass=InterfaceMeta):
    """
    An example interface.
    """

    INTERFACE_EXPLICIT_OVERRIDES = True
    INTERFACE_RAISE_ON_VIOLATION = False
    INTERFACE_SKIPPED_NAMES = {'__init__'}

    def __init__(self):
        """
        MyInterface constructor.
        """
        pass

    @abstractproperty
    def name(self):
        """
        The name of this interface.
        """
        pass

    @quirk_docs(method='_do_stuff')
    def do_stuff(self, a, b, c=1):
        """
        Do things with the parameters.
        """
        return self._do_stuff(a, b, c)

    @abstractmethod
    def _do_stuff(self, a, b, c):
        pass

class MyImplementation(MyInterface):
    """
    This implementation of the example interface works nicely.
    """

    @quirk_docs(method='_init', mro=False)
    def __init__(self, a):
        """
        MyImplementation constructor.
        """
        self._init(a)

    def _init(self, a):
        """
        In this instance, we do nothing with a.
        """
        pass

    @property
    @override
    def name(self):
        return "Peter"

    @override
    def _do_stuff(self, a, b, c):
        """
        In this implementation, we sum the parameters.
        """
        return a + b + c
```

Running `help(MyImplementation)` reveals how the documentation is generated:

```python
class MyImplementation(MyInterface)
 |  This implementation of the example interface works nicely.
 |
 |  Method resolution order:
 |      MyImplementation
 |      MyInterface
 |      builtins.object
 |
 |  Methods defined here:
 |
 |  __init__(self, a)
 |      MyImplementation constructor.
 |
 |      In this instance, we do nothing with a.
 |
 |  do_stuff(self, a, b, c=1)
 |      Do things with the parameters.
 |
 |      MyImplementation Quirks:
 |          In this implementation, we sum the parameters.
 ...
```

## Related projects and prior art

This library is released into an already crowded space, and the author would
like to recognise some of the already wonderful work done by others. The primary
difference between this and other libraries is typically these other libraries
focus more on abstracting interface definitions and compliance, and less on the
documentation and plugin registration work. While this work overlaps with these
projects, its approach is sufficiently different (in the author's opinion)
to warrant a separate library.

- [`pure_interface`](https://github.com/seequent/pure_interface)
- [`python-interface`](https://github.com/ssanderson/interface)

`python-interface` has an emphasis on ensuring that implementations of various
interfaces *strictly* adhere to the methods and properties associated with
the interface, and that helpful errors are raised when this is violated.

By
comparison this library focusses on functional comformance to parent classes,
whereby methods on subclasses are allowed to include additional parameters. It
also focusses on ensuring that documentation for such quirks in method signatures are correctly composed into the final documentation rendered for that method.
