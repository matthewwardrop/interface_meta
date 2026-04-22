from interface_meta import InterfaceMeta, inherit_docs, skip


def test_inherit_docs_wraps_method():
    @inherit_docs(method="_impl", mro=False)
    def my_method(self):
        pass

    assert my_method._quirks_method == "_impl"
    assert my_method._quirks_mro is False


def test_skip_marks_and_returns_function():
    def my_method(self):
        pass

    result = skip(my_method)
    assert result is my_method
    assert result.__interface_meta_skip__ is True


def test_skip_is_honoured_by_interface_meta():
    class Base(metaclass=InterfaceMeta):
        def method(self):
            pass

    class Child(Base):
        @skip
        def method(self):
            pass
