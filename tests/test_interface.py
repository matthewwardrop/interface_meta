from interface_meta import InterfaceMeta


class Base(metaclass=InterfaceMeta):
    """Base class"""

    ATTRIBUTE = "class attribute"

    __doc_attrs = """
    ATTRIBUTE (str): An attribute.
    """

    def __init__(self, a, b, c):
        """Constructor"""
        pass

    @property
    def property_method(self):
        """Property Method"""
        return "property_method"

    def regular_method(self, a, b, c):
        """Regular Method"""
        return "regular_method"

    @staticmethod
    def static_method(a, b, c):
        """Static Method"""
        return "static_method"

    @classmethod
    def class_method(cls, a, b, c):
        """Class Method"""
        return "class_method"

    @InterfaceMeta.inherit_docs("_split_method")
    def split_method(self, a, b, c):
        """Split Method"""
        return self._split_method(a, b, c)

    def _split_method(self, a, b, c):
        pass

    def mro_documented(self, a, b, c):
        """Documentation in Base"""


class SubBase(Base):
    """SubBase class"""

    ATTRIBUTE = "subclass attribute"

    def __init__(self, a, b, c):
        """Subclass Constructor"""
        pass

    @Base.override
    def regular_method(self, a, b, c):
        """Subclass Regular Method"""
        return "regular_method"

    @Base.override
    @staticmethod
    def static_method(a, b, c):
        """Subclass Static Method"""
        return "static_method"

    @Base.override(force=True)
    @classmethod
    def class_method(cls, a, b, c):
        """Subclass Class Method"""
        return "class_method"

    def _split_method(self, a, b, c):
        """Subclass split_method quirks"""
        pass

    @Base.inherit_docs(mro=False)
    def mro_documented(self, a, b, c):
        """Documentation in SubBase"""


def test_consistency():
    for key, value in Base.__dict__.items():
        if key in SubBase.__dict__:
            assert issubclass(type(value), type(SubBase.__dict__[key]))


def test_docstrings():
    assert (
        SubBase.__doc__
        == "SubBase class\n\nAttributes inherited from Base:\n    ATTRIBUTE (str): An attribute."
    )
    assert SubBase.__init__.__doc__ == "Subclass Constructor"
    assert SubBase.property_method.__doc__ == "Property Method"
    assert (
        SubBase.regular_method.__doc__
        == "Regular Method\n\nSubBase Quirks:\n    Subclass Regular Method"
    )
    assert (
        SubBase.static_method.__doc__
        == "Static Method\n\nSubBase Quirks:\n    Subclass Static Method"
    )
    assert SubBase.class_method.__doc__ == "Subclass Class Method"
    assert (
        SubBase.split_method.__doc__
        == "Split Method\n\nSubBase Quirks:\n    Subclass split_method quirks"
    )
    assert SubBase.mro_documented.__doc__ == "Documentation in SubBase"
