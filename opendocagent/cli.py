import argparse
import sys
import os
import json

from opendocagent.parser import MarkdownParser
from opendocagent.template_manager import TemplateManager
from opendocagent.converters import DocxConverter, PptxConverter, LatexConverter
from opendocagent.validator import TemplateValidator

def main():
    parser = argparse.ArgumentParser(description="OpenDocAgent CLI")
    parser.add_argument("command", choices=["build"], help="Command to run")
    parser.add_argument("input_file", help="Path to the agent-generated Markdown file")
    parser.add_argument("--format", choices=["pdf", "pptx", "docx", "latex", "auto"], default="auto", help="Output format. If 'auto', reads from markdown frontmatter.")
    parser.add_argument("--template", help="Name of the template to apply")
    parser.add_argument("--data", help="Path to a JSON file containing dynamic data for Jinja2 templating")
    
    args = parser.parse_args()
    
    if args.command == "build":
        if not os.path.exists(args.input_file):
            print(f"Error: File {args.input_file} not found.")
            sys.exit(1)
            
        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        context = None
        if args.data:
            if not os.path.exists(args.data):
                print(f"Error: Data file {args.data} not found.")
                sys.exit(1)
            with open(args.data, "r", encoding="utf-8") as df:
                context = json.load(df)
            
        md_parser = MarkdownParser()
        parsed = md_parser.parse(content, context=context)
        metadata = parsed["metadata"]
        
        # Pre-flight linting validation
        validator = TemplateValidator()
        validator.validate(metadata, parsed["tokens"])
        
        # Determine format
        target_format = args.format
        if target_format == "auto":
            target_format = metadata.get("format")
            if not target_format:
                print("Error: No format specified in CLI or markdown frontmatter.")
                sys.exit(1)
                
        target_format = target_format.lower()
        if target_format not in ["pdf", "pptx", "docx", "latex"]:
            print(f"Error: Unsupported format '{target_format}'")
            sys.exit(1)
            
        # Determine template
        style_name = metadata.get("style", "executive")
        template_name = args.template or metadata.get("template")
        template_mgr = TemplateManager()
        
        # Map format to converter and template extension
        ext_map = {
            "docx": ("dotx", DocxConverter),
            "pptx": ("potx", PptxConverter),
            "pdf": ("tex", LatexConverter),
            "latex": ("tex", LatexConverter),
        }
        
        tmpl_ext, ConverterClass = ext_map[target_format]
        template_path = template_mgr.get_template(template_name, style_name, tmpl_ext)
        
        # We might want to pass None if default template file doesn't exist
        if not os.path.exists(template_path):
            print(f"Warning: Template {template_path} not found. Proceeding without it.")
            template_path = None
            
        converter = ConverterClass(template_path=template_path)
        
        # Output path
        base_name, _ = os.path.splitext(args.input_file)
        out_ext = "pdf" if target_format == "latex" else target_format # pylatex handles .pdf
        output_file = f"{base_name}.{out_ext}"
        
        print(f"Building {output_file} from {args.input_file} using format {target_format.upper()}...")
        converter.convert(parsed, output_file)
        print(f"Success! Generated {output_file}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
