import pytest

from interface_meta.utils.errors import InterfaceConformanceError
from interface_meta.utils.reporting import report_violation


def test_report_violation_logs_warning(caplog):
    import logging

    with caplog.at_level(logging.WARNING):
        report_violation("something went wrong", raise_on_violation=False)
    assert "something went wrong" in caplog.text


def test_report_violation_raises():
    with pytest.raises(InterfaceConformanceError, match="something went wrong"):
        report_violation("something went wrong", raise_on_violation=True)
