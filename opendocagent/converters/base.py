import os
import tempfile
from pathlib import Path
from typing import Any
from opendocagent.types import ParsedDocument


class BaseConverter:
    def __init__(self, template_path: str | Path | None = None) -> None:
        self.template_path = str(template_path) if template_path is not None else None

    def convert(self, ast: dict[str, Any] | ParsedDocument, output_path: str | Path) -> None:
        """
        Converts the Markdown AST to the target format and writes to output_path.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement convert()")

    def convert_bytes(self, ast: dict[str, Any] | ParsedDocument) -> bytes:
        """
        Converts the Markdown AST to raw bytes in memory.
        Default implementation writes to a temporary file using convert()
        and reads back bytes, ensuring universal compatibility.
        Subclasses can override this with pure memory buffer rendering.
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.convert(ast, tmp_path)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

