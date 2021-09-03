import textwrap

import six

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


if not six.PY2:
    exec(
        textwrap.dedent(
            """
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
    """
        ),
        globals(),
    )


def test_signature_checking():
    # Check that all signatures are self-compatible
    all_tests = [a, b, c, d, e, f]
    if not six.PY2:
        all_tests.extend([g, h, i, j, k])  # noqa: F821

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
    }
    if not six.PY2:
        solutions.update(
            {
                (f, g): False,  # noqa: F821
                (h, g): True,  # noqa: F821
                (i, h): False,  # noqa: F821
                (j, i): True,  # noqa: F821
                (i, j): False,  # noqa: F821
                (k, j): False,  # noqa: F821
                (j, k): True,  # noqa: F821
            }
        )

    for (impl, ref), solution in solutions.items():
        assert check_signatures_compatible(signature(impl), signature(ref)) is solution
