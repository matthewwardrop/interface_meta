import pytest

from interface_meta import InterfaceMeta
from interface_meta.utils.docs import doc_join

# --- doc_join edge cases ---


def test_doc_join_skips_none_and_empty_string():
    assert doc_join(None, "", "hello") == "hello"


def test_doc_join_skips_short_sequence():
    # A list with fewer than 2 elements contributes nothing
    assert doc_join(["only header"]) is None


def test_doc_join_nested_header_when_output_empty():
    # When the very first item is a section (not a plain string), a leading
    # newline separator is prepended so the section stands on its own.
    result = doc_join(["Section:", "body text"])
    assert result is not None
    assert "Section:" in result
    assert "body text" in result


def test_doc_join_invalid_format_raises():
    with pytest.raises(ValueError, match="Unrecognised doc format"):
        doc_join(12345)


# --- update_docs: quirks_method when class already has its own entry ---


def test_update_docs_quirks_method_appended_to_existing_class_docs():
    # Trigger the branch where cls.__name__ is already in method_docs when the
    # quirks_method content is being merged in (docs.py line 111).
    class Base(metaclass=InterfaceMeta):
        @InterfaceMeta.inherit_docs("_impl")
        def public_method(self):
            """Base public docs"""

        def _impl(self):
            pass

    class Child(Base):
        @Base.override
        @Base.inherit_docs("_impl")
        def public_method(self):
            """Child public docs"""

        def _impl(self):
            """Child impl docs"""

    # Child's public_method docs should combine its own + _impl quirks
    assert Child.public_method.__doc__ is not None
    assert "Child impl docs" in Child.public_method.__doc__
