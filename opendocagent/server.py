"""
FastMCP Server for OpenDocAgent.
Exposes document linting, compiling, guidelines, and templates to AI agents.
Requires Python >= 3.12 and mcp>=1.2.0.
"""

import json
from pathlib import Path
from typing import Any
try:
    # mcp >= 2.0 (FastMCP evolved into MCPServer)
    from mcp.server.mcpserver import MCPServer as FastMCP
except Exception:
    try:
        # mcp 1.x
        from mcp.server.fastmcp import FastMCP  # type: ignore[attr-defined,no-redef]
    except Exception:
        # standalone fastmcp package
        from fastmcp import FastMCP  # type: ignore[no-redef]

from opendocagent.pipeline import DocumentPipeline
from opendocagent.prompts import get_agent_prompt
from opendocagent.types import FormatType, StyleType, LintResultDict


DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Initialize FastMCP application
mcp = FastMCP("OpenDocAgent")


def _get_pipeline() -> DocumentPipeline:
    from opendocagent.converters import DocxConverter, PptxConverter, LatexConverter
    pipeline = DocumentPipeline()
    pipeline.register_converter("docx", "dotx", DocxConverter)
    pipeline.register_converter("pptx", "potx", PptxConverter)
    pipeline.register_converter("latex", "tex", LatexConverter)
    return pipeline


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def lint_document(content: str, context_json: str | None = None) -> LintResultDict:
    """
    Validates and lints OpenDocAgent Markdown content against style guide and schema rules.
    Returns structured diagnostics including errors, warnings, rule codes, and valid status.
    """
    context = json.loads(context_json) if context_json else None
    pipeline = _get_pipeline()
    result = pipeline.lint(content, context=context)
    return result.to_dict()


@mcp.tool()
def compile_document(
    content: str,
    output_path: str,
    output_format: str = "auto",
    context_json: str | None = None,
    template_override: str | None = None,
) -> dict[str, Any]:
    """
    Compiles specialized OpenDocAgent Markdown into PDF, DOCX, PPTX, or LaTeX.
    Writes the compiled artifact to output_path.
    """
    context = json.loads(context_json) if context_json else None
    pipeline = _get_pipeline()
    try:
        generated_file = pipeline.build(
            markdown_content=content,
            base_filename=output_path,
            output_format=output_format,
            context=context,
            template_override=template_override,
        )
        return {
            "success": True,
            "output_file": generated_file,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "output_file": None,
            "error": str(exc),
        }


@mcp.tool()
def get_style_guidelines(style: str = "executive") -> str:
    """
    Returns authoring guidelines and structural constraints for a document style (e.g. executive or technical).
    """
    return get_agent_prompt(style=style)


@mcp.tool()
def list_supported_formats() -> list[str]:
    """
    Returns list of supported target document formats (pdf, docx, pptx, latex, beamer).
    """
    return ["pdf", "docx", "pptx", "latex", "beamer"]


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

@mcp.resource("opendocagent://docs/syntax")
def get_syntax_docs() -> str:
    """Returns the official OpenDocAgent syntax and layout reference."""
    syntax_file = DOCS_DIR / "syntax.md"
    if syntax_file.exists():
        return syntax_file.read_text(encoding="utf-8")
    return "Syntax documentation file not found."


@mcp.resource("opendocagent://docs/architecture")
def get_architecture_docs() -> str:
    """Returns the OpenDocAgent pipeline and AST manipulation reference."""
    arch_file = DOCS_DIR / "architecture.md"
    if arch_file.exists():
        return arch_file.read_text(encoding="utf-8")
    return "Architecture documentation file not found."


# ---------------------------------------------------------------------------
# MCP Prompts
# ---------------------------------------------------------------------------

@mcp.prompt()
def draft_document(style: str = "executive", format: str = "pdf") -> str:
    """
    Generates system instructions for drafting a compliant OpenDocAgent document.
    """
    style_guidance = get_agent_prompt(style=style)
    return (
        f"{style_guidance}\n\n"
        f"Target Format: {format}\n"
        f"Make sure your response begins immediately with YAML frontmatter specifying ormat: {format} and style: {style}."
    )
