import logging

import pytest

from interface_meta.utils.conformance import (
    check_signatures_compatible,
    verify_conformance,
    verify_not_overridden,
    verify_signature,
)
from interface_meta.utils.inspection import set_explicit_override, signature


def a(a):
    pass


def b(a, b):
    pass


def c(a, *args):
    pass


def d(a, b, *args):
    pass


def e(a, b=None):
    pass


def f(a, b=None, c=None):
    pass


def g(a, *args, b=None):
    pass


def h(a, d, *args, b=None, e=None):
    pass


def i(a, *args, **kwargs):
    pass


def j(a, *args, b=None, **kwargs):
    pass


def k(a, *args, b=None):
    pass


def test_signature_checking():
    # Check that all signatures are self-compatible
    all_tests = [a, b, c, d, e, f, g, h, i, j, k]

    for impl in all_tests:
        assert check_signatures_compatible(signature(impl), signature(impl)) is True

    # Check explicitly expected compatibility
    solutions = {
        (a, b): False,
        (b, a): False,
        (b, c): False,
        (c, b): False,
        (c, d): False,
        (d, c): True,
        (e, b): False,
        (b, e): False,
        (e, f): False,
        (f, e): True,
        (f, g): False,
        (h, g): True,
        (i, h): False,
        (j, i): True,
        (i, j): False,
        (k, j): False,
        (j, k): True,
    }

    for (impl, ref), solution in solutions.items():
        assert check_signatures_compatible(signature(impl), signature(ref)) is solution


# --- verify_conformance type-mismatch branches ---


def test_verify_conformance_property_replacing_attribute():
    # property replacing a plain attribute is acceptable (no violation)
    prop = property(lambda self: None)
    verify_conformance("attr", "Child", prop, "Parent", "some_string_value")


def test_verify_conformance_method_replacing_attribute(caplog):
    # functional member replacing a plain attribute reports a type-change violation
    def my_method(self):
        pass

    with caplog.at_level(logging.WARNING):
        verify_conformance("attr", "Child", my_method, "Parent", "some_string_value")
    assert "changes the type" in caplog.text


def test_verify_conformance_other_type_change():
    # non-functional, non-property type mismatch is silently accepted
    verify_conformance("attr", "Child", 42, "Parent", "hello")


# --- verify_signature raise_on_violation ---


def test_verify_signature_incompatible_warns(caplog):
    def impl(a, b):
        pass

    def ref(a):
        pass

    with caplog.at_level(logging.WARNING):
        verify_signature("method", "Child", impl, "Parent", ref, raise_on_violation=False)
    assert "does not conform" in caplog.text


def test_verify_signature_incompatible_raises():
    def impl(a, b):
        pass

    def ref(a):
        pass

    with pytest.raises(RuntimeError, match="does not conform"):
        verify_signature("method", "Child", impl, "Parent", ref, raise_on_violation=True)


# --- verify_not_overridden ---


def test_verify_not_overridden_warns_when_override_set(caplog):
    def my_method():
        pass

    set_explicit_override(my_method)
    with caplog.at_level(logging.WARNING):
        verify_not_overridden("my_method", "MyClass", my_method)
    assert "claims to override interface method" in caplog.text
