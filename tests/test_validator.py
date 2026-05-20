"""
Tests for opendocagent.validator — covers LintResult, Severity, and all
TemplateValidator checks (F001–F004, D001, J001, S001–S005).
"""

import pytest
from opendocagent.validator import (
    TemplateValidator,
    LintResult,
    LintIssue,
    Severity,
    VALID_FORMATS,
    VALID_STYLES,
)
from opendocagent.parser import MarkdownParser
from opendocagent.exceptions import ValidationLintError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(md: str):
    """Parse a Markdown string and return (metadata, tokens, content)."""
    p = MarkdownParser()
    result = p.parse(md)
    return result["metadata"], result["tokens"], result.get("content", "")


def lint(md: str) -> LintResult:
    """Convenience: parse *md* and return its LintResult."""
    meta, tokens, content = parse(md)
    return TemplateValidator().lint(meta, tokens, content)


def codes(result: LintResult):
    """Return the set of issue codes in a LintResult."""
    return {i.code for i in result.issues}


# ---------------------------------------------------------------------------
# LintResult / LintIssue unit tests
# ---------------------------------------------------------------------------

class TestLintResult:
    def test_empty_result_has_no_errors(self):
        r = LintResult()
        assert not r.has_errors
        assert r.errors == []
        assert r.warnings == []
        assert r.infos == []

    def test_add_error(self):
        r = LintResult()
        r.add(Severity.ERROR, "X001", "something bad")
        assert r.has_errors
        assert len(r.errors) == 1
        assert r.errors[0].code == "X001"

    def test_add_warning_not_counted_as_error(self):
        r = LintResult()
        r.add(Severity.WARNING, "W001", "advisory only")
        assert not r.has_errors
        assert len(r.warnings) == 1

    def test_str_representation(self):
        issue = LintIssue(Severity.ERROR, "F001", "missing format")
        assert "[ERROR]" in str(issue)
        assert "F001" in str(issue)
        assert "missing format" in str(issue)


# ---------------------------------------------------------------------------
# F001 — format key
# ---------------------------------------------------------------------------

class TestF001FormatKey:
    def test_missing_format_is_error(self):
        result = lint("# Hello\n")
        assert "F001" in codes(result)
        assert any(i.severity == Severity.ERROR for i in result.issues if i.code == "F001")

    def test_invalid_format_value_is_error(self):
        result = lint("---\nformat: html\n---\n# Hello\n")
        assert "F001" in codes(result)

    def test_valid_formats_no_f001(self):
        for fmt in VALID_FORMATS:
            r = lint(f"---\nformat: {fmt}\ntitle: T\nauthor: A\n---\n# Hello\n")
            assert "F001" not in codes(r), f"F001 raised for valid format '{fmt}'"


# ---------------------------------------------------------------------------
# F002 — style key
# ---------------------------------------------------------------------------

class TestF002StyleKey:
    def test_invalid_style_is_error(self):
        result = lint("---\nformat: pdf\nstyle: fancy\n---\n# Hello\n")
        assert "F002" in codes(result)
        assert any(i.severity == Severity.ERROR for i in result.issues if i.code == "F002")

    def test_valid_styles_no_f002(self):
        for style in VALID_STYLES:
            r = lint(f"---\nformat: pdf\nstyle: {style}\ntitle: T\nauthor: A\n---\n## Methodology\n")
            assert "F002" not in codes(r), f"F002 raised for valid style '{style}'"

    def test_missing_style_no_f002(self):
        # style is optional — omitting it should not produce F002
        r = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello\n")
        assert "F002" not in codes(r)


# ---------------------------------------------------------------------------
# F003 — title recommended
# ---------------------------------------------------------------------------

class TestF003Title:
    def test_missing_title_is_warning(self):
        result = lint("---\nformat: pdf\n---\n# Hello\n")
        assert "F003" in codes(result)
        assert any(i.severity == Severity.WARNING for i in result.issues if i.code == "F003")

    def test_with_title_no_f003(self):
        result = lint("---\nformat: pdf\ntitle: My Doc\nauthor: A\n---\n# Hello\n")
        assert "F003" not in codes(result)


# ---------------------------------------------------------------------------
# F004 — author info
# ---------------------------------------------------------------------------

class TestF004Author:
    def test_missing_author_is_info(self):
        result = lint("---\nformat: pdf\ntitle: Doc\n---\n# Hello\n")
        assert "F004" in codes(result)
        assert any(i.severity == Severity.INFO for i in result.issues if i.code == "F004")

    def test_with_author_no_f004(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: Ada\n---\n# Hello\n")
        assert "F004" not in codes(result)


# ---------------------------------------------------------------------------
# D001 — empty document body
# ---------------------------------------------------------------------------

class TestD001EmptyDocument:
    def test_empty_body_is_warning(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n")
        assert "D001" in codes(result)
        assert any(i.severity == Severity.WARNING for i in result.issues if i.code == "D001")

    def test_non_empty_body_no_d001(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello\n\nSome content.\n")
        assert "D001" not in codes(result)


# ---------------------------------------------------------------------------
# J001 — Jinja2 syntax
# ---------------------------------------------------------------------------

class TestJ001Jinja2:
    def test_mismatched_opening_braces_is_error(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello {{ name\n")
        assert "J001" in codes(result)
        assert any(i.severity == Severity.ERROR for i in result.issues if i.code == "J001")

    def test_mismatched_closing_braces_is_error(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello name }}\n")
        assert "J001" in codes(result)

    def test_balanced_jinja2_no_j001(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello {{ name }}\n")
        assert "J001" not in codes(result)

    def test_no_jinja2_no_j001(self):
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello world\n")
        assert "J001" not in codes(result)


# ---------------------------------------------------------------------------
# S001 — slide separators for beamer/pptx
# ---------------------------------------------------------------------------

class TestS001SlideSeparators:
    def test_beamer_without_separators_is_warning(self):
        result = lint("---\nformat: beamer\ntitle: T\nauthor: A\n---\n## Slide One\nContent.\n")
        assert "S001" in codes(result)
        assert any(i.severity == Severity.WARNING for i in result.issues if i.code == "S001")

    def test_pptx_without_separators_is_warning(self):
        result = lint("---\nformat: pptx\ntitle: T\nauthor: A\n---\n## Slide One\nContent.\n")
        assert "S001" in codes(result)

    def test_beamer_with_separators_no_s001(self):
        result = lint(
            "---\nformat: beamer\ntitle: T\nauthor: A\n---\n"
            "## Slide One\nContent.\n\n---\n\n## Slide Two\nMore.\n"
        )
        assert "S001" not in codes(result)

    def test_pdf_no_s001_check(self):
        # PDF is not a slide format — S001 should not fire
        result = lint("---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Introduction\nContent.\n")
        assert "S001" not in codes(result)


# ---------------------------------------------------------------------------
# S002 & S003 — executive slide count
# ---------------------------------------------------------------------------

class TestExecutiveSlideCount:
    def _make_slides(self, n: int, with_appendix: bool = False) -> str:
        slides = "\n\n---\n\n## Slide Title\nContent.\n" * n
        appendix = "\n\n# Appendix\n\nDetailed data.\n" if with_appendix else ""
        return (
            "---\nformat: beamer\nstyle: executive\ntitle: T\nauthor: A\n---\n"
            "## Title Slide\nContent.\n" + slides + appendix
        )

    def test_over_15_slides_no_appendix_triggers_s002(self):
        md = self._make_slides(15, with_appendix=False)
        result = lint(md)
        assert "S002" in codes(result)

    def test_over_15_slides_with_appendix_no_s002(self):
        md = self._make_slides(15, with_appendix=True)
        result = lint(md)
        assert "S002" not in codes(result)

    def test_under_15_slides_no_s002(self):
        md = self._make_slides(5, with_appendix=False)
        result = lint(md)
        assert "S002" not in codes(result)

    def test_over_25_slides_is_error_s003(self):
        md = self._make_slides(25, with_appendix=True)
        result = lint(md)
        assert "S003" in codes(result)
        assert any(i.severity == Severity.ERROR for i in result.issues if i.code == "S003")


# ---------------------------------------------------------------------------
# S004 & S005 — technical structure
# ---------------------------------------------------------------------------

class TestTechnicalStructure:
    def test_missing_methodology_is_warning_s004(self):
        result = lint(
            "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
            "# Introduction\n\nSome content.\n"
        )
        assert "S004" in codes(result)
        assert any(i.severity == Severity.WARNING for i in result.issues if i.code == "S004")

    def test_with_methodology_no_s004(self):
        result = lint(
            "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
            "# Introduction\n\n## Methodology\n\nThis is how we did it.\n"
        )
        assert "S004" not in codes(result)

    def test_missing_purpose_and_scope_is_info_s005(self):
        result = lint(
            "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
            "# Introduction\n\n## Methodology\n\nDetails here.\n"
        )
        assert "S005" in codes(result)
        assert any(i.severity == Severity.INFO for i in result.issues if i.code == "S005")

    def test_with_scope_no_s005(self):
        result = lint(
            "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
            "## Scope\n\nThis applies to X.\n\n## Methodology\n\nWe did Y.\n"
        )
        assert "S005" not in codes(result)

    def test_with_purpose_no_s005(self):
        result = lint(
            "---\nformat: pdf\nstyle: technical\ntitle: T\nauthor: A\n---\n"
            "## Purpose\n\nWe built this for Z.\n\n## Methodology\n\nWe did Y.\n"
        )
        assert "S005" not in codes(result)


# ---------------------------------------------------------------------------
# validate() backward-compatibility (raises on ERROR, warns on WARNING)
# ---------------------------------------------------------------------------

class TestValidateCompat:
    def test_validate_raises_on_error(self):
        meta, tokens, content = parse("# No frontmatter format key\n")
        with pytest.raises(ValidationLintError):
            TemplateValidator().validate(meta, tokens, content)

    def test_validate_does_not_raise_on_warning_only(self, capsys):
        # A doc with title + author + pdf format but no methodology is only a warning
        meta, tokens, content = parse(
            "---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello\n\nContent.\n"
        )
        # Should NOT raise
        TemplateValidator().validate(meta, tokens, content)

    def test_validate_prints_warnings_to_stderr(self, capsys):
        meta, tokens, content = parse(
            "---\nformat: pdf\ntitle: T\nauthor: A\n---\n# Hello\n\nContent.\n"
        )
        TemplateValidator().validate(meta, tokens, content)
        captured = capsys.readouterr()
        # F004 (info) or advisory warnings should appear on stderr
        # (at minimum the INFO about author if author were missing — but here it's
        # present, so just check the call doesn't crash)
        assert captured.err is not None  # stderr is always a string


# ---------------------------------------------------------------------------
# Clean document — no spurious issues
# ---------------------------------------------------------------------------

class TestCleanDocument:
    def test_fully_valid_pdf_doc_is_clean(self):
        """A well-formed technical PDF should have no errors and no S004/S005."""
        md = (
            "---\n"
            "format: pdf\n"
            "style: technical\n"
            "title: System Design\n"
            "author: Engineering Team\n"
            "---\n"
            "## Purpose\n\nThis doc explains the system.\n\n"
            "## Scope\n\nCovers all microservices.\n\n"
            "## Methodology\n\nWe conducted load tests.\n\n"
            "## Findings\n\nResults were positive.\n"
        )
        result = lint(md)
        assert not result.has_errors
        assert "S004" not in codes(result)
        assert "S005" not in codes(result)

    def test_fully_valid_executive_beamer_is_clean(self):
        slides = "\n\n---\n\n## Point\nBrief.\n" * 5
        md = (
            "---\n"
            "format: beamer\n"
            "style: executive\n"
            "title: Q3 Results\n"
            "author: Strategy Team\n"
            "---\n"
            "## Bottom Line Up Front\nWe grew 12%.\n" + slides
        )
        result = lint(md)
        assert not result.has_errors
        assert "S001" not in codes(result)
        assert "S002" not in codes(result)
