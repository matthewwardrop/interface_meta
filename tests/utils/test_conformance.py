from interface_meta.utils.conformance import check_signatures_compatible
from interface_meta.utils.inspection import signature


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
