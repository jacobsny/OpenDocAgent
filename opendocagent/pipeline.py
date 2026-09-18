import os
import sys
from pathlib import Path
from typing import Any
from opendocagent.exceptions import FormatNotSupportedError, ValidationLintError
from opendocagent.parser import MarkdownParser
from opendocagent.template_manager import TemplateManager
from opendocagent.validator import LintResult, TemplateValidator
from opendocagent.types import ParsedDocument


class DocumentPipeline:
    def __init__(self) -> None:
        self.parser = MarkdownParser()
        self.validator = TemplateValidator()
        self.template_mgr = TemplateManager()
        self._converters: dict[str, tuple[str, type]] = {}
        
    def register_converter(self, format_name: str, tmpl_ext: str, converter_cls: type) -> None:
        self._converters[format_name.lower()] = (tmpl_ext, converter_cls)

    def lint(self, markdown_content: str, context: dict[str, Any] | None = None) -> LintResult:
        """Run structural validation and linting on markdown content."""
        parsed = self.parser.parse(markdown_content, context=context)
        return self.validator.lint(parsed["metadata"], parsed["tokens"], parsed.get("content", ""))
        
    def build_from_file(
        self,
        input_file: str | Path,
        output_format: str = "auto",
        context: dict[str, Any] | None = None,
        template_override: str | None = None,
    ) -> str:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        return self.build(content, str(input_file), output_format, context, template_override)
        
    def _prepare_build(
        self,
        markdown_content: str,
        output_format: str = "auto",
        context: dict[str, Any] | None = None,
        template_override: str | None = None,
    ) -> tuple[ParsedDocument, Any, str]:
        parsed = self.parser.parse(markdown_content, context=context)
        metadata = parsed["metadata"]
        content = parsed.get("content", "")

        lint_result = self.validator.lint(metadata, parsed["tokens"], content)
        lint_result.print_all(file=sys.stderr)

        if lint_result.has_errors:
            error_msgs = "; ".join(str(e) for e in lint_result.errors)
            raise ValidationLintError(f"Lint errors blocked the build: {error_msgs}")
        
        target_format = metadata.get("format") if output_format == "auto" else output_format
        if not target_format:
            raise FormatNotSupportedError("No output format specified.")
            
        target_format = target_format.lower()
        # Aliases
        if target_format in ["pdf", "beamer"]:
            target_format = "latex"
            
        if target_format not in self._converters:
            raise FormatNotSupportedError(f"Unsupported format '{target_format}'")
            
        tmpl_ext, ConverterClass = self._converters[target_format]
        
        style_name = metadata.get("style", "executive")
        template_name = template_override or metadata.get("template")
        resolved_path: str = self.template_mgr.get_template(template_name, style_name, tmpl_ext)
        
        template_path: str | None = resolved_path if os.path.exists(resolved_path) else None
            
        converter = ConverterClass(template_path=template_path)
        out_ext = "pdf" if target_format == "latex" else target_format
        return parsed, converter, out_ext

    def build(
        self,
        markdown_content: str,
        base_filename: str,
        output_format: str = "auto",
        context: dict[str, Any] | None = None,
        template_override: str | None = None,
    ) -> str:
        parsed, converter, out_ext = self._prepare_build(
            markdown_content,
            output_format=output_format,
            context=context,
            template_override=template_override,
        )
        base_name, _ = os.path.splitext(base_filename)
        output_file = f"{base_name}.{out_ext}"
        converter.convert(parsed, output_file)
        return output_file

    def build_bytes(
        self,
        markdown_content: str,
        output_format: str = "auto",
        context: dict[str, Any] | None = None,
        template_override: str | None = None,
    ) -> tuple[bytes, str]:
        """
        Build markdown content directly into raw bytes in memory.
        Returns a tuple of (file_bytes, extension_name).
        """
        parsed, converter, out_ext = self._prepare_build(
            markdown_content,
            output_format=output_format,
            context=context,
            template_override=template_override,
        )
        data = converter.convert_bytes(parsed)
        return data, out_ext
