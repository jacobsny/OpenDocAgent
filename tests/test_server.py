"""Tests for OpenDocAgent FastMCP server tools, resources, and prompts."""

import json
from opendocagent.server import (
    lint_document,
    compile_document,
    get_style_guidelines,
    list_supported_formats,
    get_syntax_docs,
    get_architecture_docs,
    draft_document,
)


def test_mcp_lint_document_valid():
    md = """---
title: "Technical Specification"
author: "Lead Engineer"
format: "pdf"
style: "technical"
---
## Purpose
Define requirements.
## Scope
Core modules.
## Methodology
Step-by-step.
"""
    result = lint_document(md)
    assert result["valid"] is True
    assert result["errors"] == 0


def test_mcp_lint_document_invalid():
    md = """# No frontmatter here"""
    result = lint_document(md)
    assert result["valid"] is False
    assert result["errors"] > 0
    assert any(issue["code"] == "F001" for issue in result["issues"])


def test_mcp_compile_document(tmp_path):
    out_file = str(tmp_path / "output.docx")
    md = """---
title: "Title"
author: "Author"
format: "docx"
style: "executive"
---
# Heading
Body text.
"""
    res = compile_document(md, output_path=out_file, output_format="docx")
    assert res["success"] is True
    assert (tmp_path / "output.docx").exists()


def test_mcp_style_guidelines():
    guidance = get_style_guidelines("executive")
    assert "EXECUTIVE" in guidance
    assert "Pyramid Principle" in guidance


def test_mcp_supported_formats():
    formats = list_supported_formats()
    assert "docx" in formats
    assert "pdf" in formats
    assert "pptx" in formats


def test_mcp_resources():
    syntax = get_syntax_docs()
    assert len(syntax) > 0
    arch = get_architecture_docs()
    assert len(arch) > 0


def test_mcp_prompts():
    prompt = draft_document(style="executive", format="docx")
    assert "Target Format: docx" in prompt
    assert "EXECUTIVE" in prompt
