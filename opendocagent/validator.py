"""
OpenDocAgent Markdown Linter & Validator

Provides:
  - LintIssue     — a single diagnostic with severity, code, and message
  - LintResult    — aggregate result of a lint pass
  - TemplateValidator — runs all lint checks; errors block builds, warnings are advisory
"""

import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Severity model
# ---------------------------------------------------------------------------

class Severity(Enum):
    INFO    = "INFO"
    WARNING = "WARNING"
    ERROR   = "ERROR"


@dataclass
class LintIssue:
    """A single lint diagnostic."""
    severity: Severity
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.code}: {self.message}"


@dataclass
class LintResult:
    """Aggregate result of a lint pass over a Markdown document."""
    issues: List[LintIssue] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add(self, severity: Severity, code: str, message: str) -> None:
        self.issues.append(LintIssue(severity, code, message))

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == Severity.INFO]

    def print_all(self, file=None) -> None:
        """Pretty-print all issues to *file* (default stderr)."""
        out = file or sys.stderr
        for issue in self.issues:
            print(str(issue), file=out)


# ---------------------------------------------------------------------------
# Valid values
# ---------------------------------------------------------------------------

VALID_FORMATS = {"pdf", "docx", "pptx", "latex", "beamer"}
VALID_STYLES  = {"executive", "technical"}


# ---------------------------------------------------------------------------
# TemplateValidator
# ---------------------------------------------------------------------------

class TemplateValidator:
    """
    Runs a comprehensive lint pass over a parsed OpenDocAgent Markdown document.

    Usage::

        result = validator.lint(metadata, tokens, raw_content)
        if result.has_errors:
            raise ValidationLintError(...)

    The legacy ``validate()`` method is kept for backward compatibility; it
    calls ``lint()`` internally and prints warnings while raising on errors.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def lint(self, metadata: dict, tokens: list, content: str = "") -> LintResult:
        """
        Run all lint checks and return a :class:`LintResult`.

        Parameters
        ----------
        metadata : dict
            Parsed YAML frontmatter.
        tokens : list
            markdown-it-py token stream (post-AST manipulation).
        content : str
            Raw Markdown body (after frontmatter has been stripped).
        """
        result = LintResult()

        self._check_frontmatter_schema(metadata, result)
        self._check_empty_document(tokens, result)
        self._check_jinja2_syntax(content, result)

        # Format-specific structural checks (only run if format is known-valid)
        fmt   = metadata.get("format", "").lower()
        style = metadata.get("style", "executive").lower()

        if fmt in VALID_FORMATS:
            if fmt in {"beamer", "pptx"}:
                self._check_slide_separators(tokens, fmt, result)

            if style == "executive":
                self._check_executive_structure(tokens, result)
            elif style == "technical":
                self._check_technical_structure(tokens, result)

        return result

    def validate(self, metadata: dict, tokens: list, content: str = "") -> None:
        """
        Legacy validate() kept for pipeline compatibility.

        Runs ``lint()``, prints warnings to stderr, and raises
        ``ValidationLintError`` if any ERROR-severity issues are found.
        """
        from opendocagent.exceptions import ValidationLintError

        result = self.lint(metadata, tokens, content)

        for issue in result.warnings + result.infos:
            print(str(issue), file=sys.stderr)

        if result.has_errors:
            messages = "; ".join(str(e) for e in result.errors)
            raise ValidationLintError(messages)

    # ------------------------------------------------------------------
    # Frontmatter schema checks
    # ------------------------------------------------------------------

    def _check_frontmatter_schema(self, metadata: dict, result: LintResult) -> None:
        """Validate presence and values of YAML frontmatter fields."""

        # F001 — format is required
        fmt = metadata.get("format", "")
        if not fmt:
            result.add(
                Severity.ERROR, "F001",
                "Missing required frontmatter key 'format'. "
                f"Must be one of: {', '.join(sorted(VALID_FORMATS))}."
            )
        elif fmt.lower() not in VALID_FORMATS:
            result.add(
                Severity.ERROR, "F001",
                f"Invalid frontmatter value format='{fmt}'. "
                f"Must be one of: {', '.join(sorted(VALID_FORMATS))}."
            )

        # F002 — style is optional but must be a known value if present
        style = metadata.get("style", "")
        if style and style.lower() not in VALID_STYLES:
            result.add(
                Severity.ERROR, "F002",
                f"Invalid frontmatter value style='{style}'. "
                f"Must be one of: {', '.join(sorted(VALID_STYLES))}."
            )

        # F003 — title is strongly recommended
        if not metadata.get("title"):
            result.add(
                Severity.WARNING, "F003",
                "Missing recommended frontmatter key 'title'. "
                "Documents without a title may render with a blank heading."
            )

        # F004 — author is recommended for formal documents
        if not metadata.get("author"):
            result.add(
                Severity.INFO, "F004",
                "Missing optional frontmatter key 'author'. "
                "Adding an author improves document credibility."
            )

    # ------------------------------------------------------------------
    # Content checks
    # ------------------------------------------------------------------

    def _check_empty_document(self, tokens: list, result: LintResult) -> None:
        """D001 — warn if the document body produces no tokens at all."""
        meaningful = [
            t for t in tokens
            if t.type not in {"softbreak", "hardbreak"}
        ]
        if not meaningful:
            result.add(
                Severity.WARNING, "D001",
                "Document body is empty. The output file will contain no content."
            )

    def _check_jinja2_syntax(self, content: str, result: LintResult) -> None:
        """J001 — detect obviously malformed Jinja2 expressions."""
        # Mismatched {{ without matching }}
        opens  = len(re.findall(r"\{\{", content))
        closes = len(re.findall(r"\}\}", content))
        if opens != closes:
            result.add(
                Severity.ERROR, "J001",
                f"Malformed Jinja2 expression: found {opens} opening '{{{{' "
                f"but {closes} closing '}}}}'. Check your template variables."
            )

    # ------------------------------------------------------------------
    # Structural checks — slides
    # ------------------------------------------------------------------

    def _check_slide_separators(
        self, tokens: list, fmt: str, result: LintResult
    ) -> None:
        """S001 — beamer/pptx documents should use '---' to create slides."""
        has_separators = any(t.type == "hr" for t in tokens)
        if not has_separators:
            result.add(
                Severity.WARNING, "S001",
                f"Format '{fmt}' expects slide separators ('---' on a blank line) "
                "to delineate individual slides, but none were found. "
                "The entire document will be rendered as a single slide."
            )

    # ------------------------------------------------------------------
    # Structural checks — executive archetype
    # ------------------------------------------------------------------

    def _check_executive_structure(
        self, tokens: list, result: LintResult
    ) -> None:
        """Run structural checks for executive-style documents."""
        slide_count = sum(1 for t in tokens if t.type == "hr") + 1

        # S002 — executive presentations over 15 slides should include Appendix
        if slide_count > 15:
            has_appendix = self._has_heading(tokens, "appendix")
            if not has_appendix:
                result.add(
                    Severity.WARNING, "S002",
                    f"Executive document has {slide_count} slides/sections but no "
                    "'# Appendix'. Move detailed data and methodology there to "
                    "keep the core narrative concise."
                )

        # S003 — executive documents should not exceed 25 slides total
        if slide_count > 25:
            result.add(
                Severity.ERROR, "S003",
                f"Executive document exceeds 25 slides ({slide_count} found). "
                "This violates the Pyramid Principle archetype. "
                "Significantly condense the content or switch to style: technical."
            )

    # ------------------------------------------------------------------
    # Structural checks — technical archetype
    # ------------------------------------------------------------------

    def _check_technical_structure(
        self, tokens: list, result: LintResult
    ) -> None:
        """Run structural checks for technical-style documents."""

        # S004 — technical documents should have a Methodology section
        if not self._has_heading(tokens, "methodology"):
            result.add(
                Severity.WARNING, "S004",
                "Technical document is missing a 'Methodology' section. "
                "Add '## Methodology' to document your process for reproducibility."
            )

        # S005 — technical documents should have a Purpose or Scope section
        has_purpose = self._has_heading(tokens, "purpose") or self._has_heading(tokens, "scope")
        if not has_purpose:
            result.add(
                Severity.INFO, "S005",
                "Technical document has no 'Purpose' or 'Scope' section. "
                "Consider adding one to orient readers."
            )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _has_heading(tokens: list, keyword: str) -> bool:
        """Return True if any heading token contains *keyword* (case-insensitive)."""
        for i, token in enumerate(tokens):
            if token.type == "heading_open" and i + 1 < len(tokens):
                heading_text = tokens[i + 1].content.strip().lower()
                if keyword.lower() in heading_text:
                    return True
        return False
