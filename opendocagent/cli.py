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


def cmd_build(args) -> int:
    """Handle the 'build' sub-command."""
    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.", file=sys.stderr)
        return 1

    context = None
    if args.data:
        if not os.path.exists(args.data):
            print(f"Error: Data file {args.data} not found.", file=sys.stderr)
            return 1
        try:
            with open(args.data, "r", encoding="utf-8") as df:
                context = json.load(df)
        except Exception as e:
            print(f"Error reading JSON data: {e}", file=sys.stderr)
            return 1

    pipeline = build_pipeline()

    try:
        output_file = pipeline.build_from_file(
            input_file=args.input_file,
            output_format=args.format,
            context=context,
            template_override=args.template,
        )
        print(f"Success! Generated {output_file}")
        return 0
    except OpenDocAgentError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def cmd_lint(args) -> int:
    """
    Handle the 'lint' sub-command.

    Parses the Markdown file and runs the full lint suite, printing every
    issue to stdout.  Exits with code 0 when no ERROR-severity issues are
    found, or code 1 when at least one ERROR is present.
    """
    from opendocagent.parser import MarkdownParser
    from opendocagent.validator import TemplateValidator

    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.", file=sys.stderr)
        return 1

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    parser   = MarkdownParser()
    parsed   = parser.parse(raw)
    metadata = parsed["metadata"]
    tokens   = parsed["tokens"]
    content  = parsed.get("content", "")

    validator = TemplateValidator()
    result    = validator.lint(metadata, tokens, content)

    if not result.issues:
        print(f"✓ {args.input_file} — no lint issues found.")
        return 0

    # Group by severity for a readable report
    for issue in result.issues:
        print(str(issue))

    total   = len(result.issues)
    n_err   = len(result.errors)
    n_warn  = len(result.warnings)
    n_info  = len(result.infos)
    print(
        f"\n{total} issue(s): "
        f"{n_err} error(s), {n_warn} warning(s), {n_info} info(s)."
    )

    return 1 if result.has_errors else 0


def main():
    parser = argparse.ArgumentParser(
        description="OpenDocAgent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # ------------------------------------------------------------------ build
    build_p = sub.add_parser("build", help="Compile a Markdown file into a document.")
    build_p.add_argument("input_file", help="Path to the Markdown file.")
    build_p.add_argument(
        "--format",
        choices=["pdf", "pptx", "docx", "latex", "beamer", "auto"],
        default="auto",
        help="Output format. Defaults to the 'format' key in frontmatter.",
    )
    build_p.add_argument("--template", help="Override the template name.")
    build_p.add_argument(
        "--data",
        help="Path to a JSON file containing Jinja2 template variables.",
    )

    # ------------------------------------------------------------------ lint
    lint_p = sub.add_parser("lint", help="Lint a Markdown file without building it.")
    lint_p.add_argument("input_file", help="Path to the Markdown file to lint.")

    args = parser.parse_args()

    if args.command == "build":
        sys.exit(cmd_build(args))
    elif args.command == "lint":
        sys.exit(cmd_lint(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
