import argparse
import sys
import json
import os

from opendocagent.pipeline import DocumentPipeline
from opendocagent.converters import DocxConverter, PptxConverter, LatexConverter
from opendocagent.exceptions import OpenDocAgentError

def build_pipeline() -> DocumentPipeline:
    pipeline = DocumentPipeline()
    pipeline.register_converter("docx", "dotx", DocxConverter)
    pipeline.register_converter("pptx", "potx", PptxConverter)
    pipeline.register_converter("latex", "tex", LatexConverter)
    return pipeline

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
            print(f"Error: File {args.input_file} not found.", file=sys.stderr)
            sys.exit(1)
            
        context = None
        if args.data:
            if not os.path.exists(args.data):
                print(f"Error: Data file {args.data} not found.", file=sys.stderr)
                sys.exit(1)
            try:
                with open(args.data, "r", encoding="utf-8") as df:
                    context = json.load(df)
            except Exception as e:
                print(f"Error reading JSON data: {e}", file=sys.stderr)
                sys.exit(1)
                
        pipeline = build_pipeline()
        
        try:
            output_file = pipeline.build_from_file(
                input_file=args.input_file,
                output_format=args.format,
                context=context,
                template_override=args.template
            )
            print(f"Success! Generated {output_file}")
        except OpenDocAgentError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
