import pypandoc
import os
from pathlib import Path
from .base import BaseConverter


def _find_project_root() -> Path:
    """Walk up from this file until pyproject.toml is found."""
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / "pyproject.toml").exists():
            return candidate
        candidate = candidate.parent
    raise RuntimeError("Could not locate project root (no pyproject.toml found).")


TEMPLATES_DIR = _find_project_root() / "templates" / "latex"


class LatexConverter(BaseConverter):
    """
    Converts parsed Markdown payloads to PDF via pypandoc/pdflatex.

    Supports two sub-modes driven by the ``format`` frontmatter key:
      - ``beamer``  → Pandoc Beamer presentation (16:9 slides)
      - anything else (``pdf``) → Pandoc article/report document

    All Pandoc variables can be set in the Markdown frontmatter. An optional
    ``pandoc_vars`` dict in frontmatter allows arbitrary ``-V key:value`` flags.
    """

    def convert(self, parsed: dict, output_path: str) -> None:
        content = parsed.get("content", "")
        metadata = parsed.get("metadata", {})

        extra_args = []

        # Custom Pandoc template (rarely used; auto-style is preferred)
        if self.template_path and os.path.exists(self.template_path):
            extra_args.append(f"--template={self.template_path}")

        # PDF engine (default pdflatex; override with pdf_engine in frontmatter)
        pdf_engine = metadata.get("pdf_engine", "pdflatex")
        extra_args.append(f"--pdf-engine={pdf_engine}")

        # Determine output format from extension
        _, ext = os.path.splitext(output_path)
        out_fmt = "pdf" if ext.lower() == ".pdf" else "latex"

        target_fmt = metadata.get("format", "").lower()

        if target_fmt == "beamer":
            self._configure_beamer(extra_args, metadata)
        else:
            self._configure_document(extra_args, metadata)

        # Arbitrary extra pandoc -V flags from frontmatter
        for key, val in metadata.get("pandoc_vars", {}).items():
            extra_args.extend(["-V", f"{key}:{val}"])

        pypandoc.convert_text(
            content,
            out_fmt,
            format="md",
            outputfile=output_path,
            extra_args=extra_args,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _configure_beamer(self, extra_args: list, metadata: dict) -> None:
        """Add Pandoc flags for a Beamer presentation PDF."""
        theme       = metadata.get("beamer_theme", "Madrid")
        colortheme  = metadata.get("beamer_colortheme", "whale")
        fonttheme   = metadata.get("beamer_fonttheme", "professionalfonts")
        aspectratio = metadata.get("beamer_aspectratio", "169")
        title       = metadata.get("title", "")
        subtitle    = metadata.get("subtitle", "")
        author      = metadata.get("author", "")
        institute   = metadata.get("institute", "")
        date        = metadata.get("date", "")

        extra_args.extend([
            "-t", "beamer",
            "--slide-level=2",
            "-V", f"theme:{theme}",
            "-V", f"colortheme:{colortheme}",
            "-V", f"fonttheme:{fonttheme}",
            "-V", f"aspectratio={aspectratio}",
        ])

        for key, val in [
            ("title", title),
            ("subtitle", subtitle),
            ("author", author),
            ("institute", institute),
            ("date", date),
        ]:
            if val:
                extra_args.extend(["-V", f"{key}:{val}"])

        # Auto-include brand style header
        style_file = TEMPLATES_DIR / "beamer_style.tex"
        if style_file.exists():
            extra_args.append(f"--include-in-header={style_file}")

    def _configure_document(self, extra_args: list, metadata: dict) -> None:
        """Add Pandoc flags for a standard document PDF."""
        documentclass = metadata.get("documentclass", "article")
        geometry      = metadata.get("geometry", "margin=2.5cm,top=3cm")
        fontsize      = metadata.get("fontsize", "11pt")

        extra_args.extend([
            "-V", f"documentclass:{documentclass}",
            "-V", f"geometry:{geometry}",
            "-V", f"fontsize:{fontsize}",
            # Color hyperlinks using brand blue
            "-V", "colorlinks:true",
            "-V", "linkcolor:NavyBlue",
            "-V", "urlcolor:NavyBlue",
            "-V", "toccolor:NavyBlue",
        ])

        if metadata.get("toc"):
            extra_args.append("--toc")

        if metadata.get("numbersections"):
            extra_args.append("--number-sections")

        toc_depth = metadata.get("toc_depth")
        if toc_depth:
            extra_args.extend(["--toc-depth", str(toc_depth)])

        # Auto-include brand style header
        style_file = TEMPLATES_DIR / "document_style.tex"
        if style_file.exists():
            extra_args.append(f"--include-in-header={style_file}")
