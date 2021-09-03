from interface_meta import override
from interface_meta.utils.inspection import (
    _get_member,
    functional_delattr,
    functional_getattr,
    functional_hasattr,
    functional_setattr,
    get_class_attr_docs,
    get_functional_docs,
    get_functional_signature,
    get_functional_wrapper,
    get_quirk_docs_method,
    get_quirk_docs_mro,
    has_class_attr_docs,
    has_explicit_override,
    has_forced_override,
    has_quirk_docs_method,
    has_quirk_docs_mro,
    has_updatable_docs,
    is_functional_member,
    is_method,
    set_functional_docs,
    set_quirk_docs_method,
    set_quirk_docs_mro,
    signature,
)


class Test:

    __doc_attrs = "Documented attributes"

    attribute = False

    @property
    def property_method(self):
        """Property Docs"""
        return "Hello World"

    @property_method.setter
    def property_method(self, value):
        pass

    def method(self, a, b, c):
        """Method Docs"""
        pass

    @override
    @classmethod
    def class_method(cls, a, b, c):
        """Class Method Docs"""
        pass

    @override(force=True)
    @staticmethod
    def static_method(a, b, c):
        """Static Method Docs"""
        pass


ATTRIBUTE = Test.__dict__["attribute"]
PROPERTY = Test.__dict__["property_method"]
METHOD = Test.__dict__["method"]
CLASS_METHOD = Test.__dict__["class_method"]
STATIC_METHOD = Test.__dict__["static_method"]


def test__get_member():
    assert not is_method(_get_member(ATTRIBUTE))
    assert is_method(_get_member(PROPERTY))
    assert is_method(_get_member(METHOD))
    assert is_method(_get_member(CLASS_METHOD))
    assert is_method(_get_member(STATIC_METHOD))


def test_is_method():
    assert not is_method(Test.attribute)
    assert not is_method(Test.property_method)
    assert is_method(Test.method)
    assert is_method(Test().method)
    assert is_method(Test.class_method)
    assert is_method(Test.static_method)
    assert not is_method(ATTRIBUTE)
    assert not is_method(PROPERTY)
    assert is_method(METHOD)
    assert not is_method(CLASS_METHOD)
    assert not is_method(STATIC_METHOD)


def test_is_functional_member():
    assert not is_functional_member(ATTRIBUTE)
    assert not is_functional_member(PROPERTY)
    assert is_functional_member(METHOD)
    assert is_functional_member(CLASS_METHOD)
    assert is_functional_member(STATIC_METHOD)


def test_get_functional_wrapper():
    wrapped = get_functional_wrapper(STATIC_METHOD)

    for functional in [PROPERTY, METHOD, CLASS_METHOD, STATIC_METHOD]:
        wrapped = get_functional_wrapper(functional)
        for attr in [
            "__doc__",
            "_quirks_method",
            "_quirks_mro",
            "__override__",
            "__override_force__",
        ]:
            if functional_hasattr(functional, attr):
                assert functional_getattr(wrapped, attr) == functional_getattr(
                    functional, attr
                )

        if functional is PROPERTY:
            assert wrapped.fset is PROPERTY.fset
            assert wrapped.fdel is PROPERTY.fdel


def test_get_functional_signature():
    assert get_functional_signature(METHOD) == signature(METHOD)
    assert get_functional_signature(CLASS_METHOD) == signature(
        CLASS_METHOD.__get__(object, object).__func__
    )
    assert get_functional_signature(STATIC_METHOD) == signature(
        STATIC_METHOD.__get__(object, object)
    )


def test_functional_attrs():
    assert functional_getattr(PROPERTY, "__doc__") == "Property Docs"
    assert functional_getattr(METHOD, "__doc__") == "Method Docs"
    assert functional_getattr(CLASS_METHOD, "__doc__") == "Class Method Docs"
    assert functional_getattr(STATIC_METHOD, "__doc__") == "Static Method Docs"

    assert functional_hasattr(CLASS_METHOD, "__my_attr__") is False
    functional_setattr(CLASS_METHOD, "__my_attr__", "Foo")
    assert functional_hasattr(CLASS_METHOD, "__my_attr__") is True
    assert functional_getattr(CLASS_METHOD, "__my_attr__") == "Foo"
    functional_delattr(CLASS_METHOD, "__my_attr__")
    assert functional_hasattr(CLASS_METHOD, "__my_attr__") is False


def test_overrides():
    assert has_explicit_override(PROPERTY) is False
    assert has_forced_override(PROPERTY) is False

    assert has_explicit_override(METHOD) is False
    assert has_forced_override(METHOD) is False

    assert has_explicit_override(CLASS_METHOD) is True
    assert has_forced_override(CLASS_METHOD) is False

    assert has_explicit_override(STATIC_METHOD) is True
    assert has_forced_override(STATIC_METHOD) is True


def test_has_updatable_docs():
    assert not has_updatable_docs(ATTRIBUTE)
    assert has_updatable_docs(PROPERTY)
    assert has_updatable_docs(METHOD)
    assert has_updatable_docs(CLASS_METHOD)
    assert has_updatable_docs(STATIC_METHOD)


def test_has_class_attr_docs():
    assert has_class_attr_docs(Test)


def test_get_class_attr_docs():
    assert get_class_attr_docs(Test) == "Documented attributes"


def test_quirk_docs():
    assert not has_quirk_docs_method(PROPERTY)
    set_quirk_docs_method(PROPERTY, "__test__")
    assert get_quirk_docs_method(PROPERTY) == "__test__"
    assert has_quirk_docs_method(PROPERTY)

    assert not has_quirk_docs_mro(CLASS_METHOD)
    set_quirk_docs_mro(CLASS_METHOD, True)
    assert get_quirk_docs_mro(CLASS_METHOD) == True
    assert has_quirk_docs_mro(CLASS_METHOD)


def test_get_functional_docs():
    assert get_functional_docs(PROPERTY) == "Property Docs"
    assert get_functional_docs(METHOD) == "Method Docs"
    assert get_functional_docs(CLASS_METHOD) == "Class Method Docs"
    assert get_functional_docs(STATIC_METHOD) == "Static Method Docs"


def test_set_functional_docs():
    set_functional_docs(PROPERTY, "New Docs")
    assert functional_getattr(PROPERTY, "__doc__") == "New Docs"
    assert functional_getattr(PROPERTY, "__doc_orig__") == "Property Docs"

    assert get_functional_docs(PROPERTY, orig=True) == "Property Docs"
    assert get_functional_docs(PROPERTY, orig=False) == "New Docs"
