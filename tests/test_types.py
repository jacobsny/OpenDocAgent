"""Tests for opendocagent.types and structured serialization."""

from opendocagent.types import ParsedDocument, FormatType, StyleType
from opendocagent.validator import LintResult, Severity


def test_lint_result_to_dict():
    result = LintResult()
    result.add(Severity.ERROR, "E001", "Missing title")
    result.add(Severity.WARNING, "W001", "Slide count high")

    d = result.to_dict()
    assert d["valid"] is False
    assert d["total_issues"] == 2
    assert d["errors"] == 1
    assert d["warnings"] == 1
    assert d["infos"] == 0
    assert len(d["issues"]) == 2
    assert d["issues"][0]["code"] == "E001"
    assert d["issues"][0]["severity"] == "ERROR"
    assert d["issues"][1]["code"] == "W001"
    assert d["issues"][1]["severity"] == "WARNING"


def test_clean_lint_result_to_dict():
    result = LintResult()
    d = result.to_dict()
    assert d["valid"] is True
    assert d["total_issues"] == 0
    assert d["errors"] == 0
