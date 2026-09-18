"""
Strongly typed models and aliases for OpenDocAgent.
Requires Python >= 3.12 (PEP 695 type aliases, modern TypedDict).
"""

from typing import Any, Literal, TypedDict
from markdown_it.token import Token

type FormatType = Literal["pdf", "docx", "pptx", "latex", "beamer"]
type StyleType = Literal["executive", "technical"]


class ParsedDocument(TypedDict):
    """
    Represents the parsed document returned by MarkdownParser.parse().
    Subclasses TypedDict for 100% dictionary subscription compatibility.
    """
    metadata: dict[str, Any]
    tokens: list[Token]
    content: str


class LintIssueDict(TypedDict):
    """Dictionary representation of a single lint diagnostic."""
    severity: str
    code: str
    message: str


class LintResultDict(TypedDict):
    """Dictionary representation of an entire lint pass."""
    valid: bool
    total_issues: int
    errors: int
    warnings: int
    infos: int
    issues: list[LintIssueDict]
