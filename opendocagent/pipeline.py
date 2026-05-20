import os
from opendocagent.parser import MarkdownParser
from opendocagent.template_manager import TemplateManager
from opendocagent.validator import TemplateValidator
from opendocagent.exceptions import FormatNotSupportedError

class DocumentPipeline:
    def __init__(self):
        self.parser = MarkdownParser()
        self.validator = TemplateValidator()
        self.template_mgr = TemplateManager()
        self._converters = {}
        
    def register_converter(self, format_name: str, tmpl_ext: str, converter_cls):
        self._converters[format_name.lower()] = (tmpl_ext, converter_cls)
        
    def build_from_file(self, input_file: str, output_format: str = "auto", context: dict = None, template_override: str = None):
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        return self.build(content, input_file, output_format, context, template_override)
        
    def build(self, markdown_content: str, base_filename: str, output_format: str = "auto", context: dict = None, template_override: str = None):
        from opendocagent.exceptions import ValidationLintError
        import sys

        parsed = self.parser.parse(markdown_content, context=context)
        metadata = parsed["metadata"]
        content  = parsed.get("content", "")

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
        template_path = self.template_mgr.get_template(template_name, style_name, tmpl_ext)
        
        if not os.path.exists(template_path):
            template_path = None
            
        converter = ConverterClass(template_path=template_path)
        
        # Output path
        base_name, _ = os.path.splitext(base_filename)
        out_ext = "pdf" if target_format == "latex" else target_format # pylatex/pypandoc handles .pdf
        output_file = f"{base_name}.{out_ext}"
        
        converter.convert(parsed, output_file)
        return output_file
