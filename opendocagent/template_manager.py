import os
import zipfile

# Style aliases mapping for template fallback
STYLE_ALIASES: dict[str, dict[str, list[str]]] = {
    "potx": {
        "executive": ["executive.potx", "executive_deck.potx"],
        "technical": ["technical.potx", "technical_deck.potx"],
    },
    "dotx": {
        "executive": ["executive.dotx", "executive_summary.dotx"],
        "technical": ["technical.dotx", "technical_spec.dotx"],
    },
}


class TemplateManager:
    def __init__(self, template_dir=None):
        if template_dir is None:
            self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        else:
            self.template_dir = template_dir
        
    def get_template(self, name: str | None, style: str | None, format_type: str) -> str:
        """
        Returns the path to the requested template file.
        format_type should be one of 'potx', 'dotx', 'tex'
        """
        template_name = name if name else (style if style else "default")
        primary_path = os.path.join(self.template_dir, f"{template_name}.{format_type}")

        if os.path.exists(primary_path):
            return primary_path

        # Check aliases if primary is not found on disk
        aliases = STYLE_ALIASES.get(format_type, {}).get(template_name, [])
        for alias in aliases:
            alias_path = os.path.join(self.template_dir, alias)
            if os.path.exists(alias_path):
                return alias_path

        return primary_path

    def is_valid_template(self, path: str) -> bool:
        """Check if a template file exists and is a valid package."""
        if not os.path.exists(path):
            return False
        _, ext = os.path.splitext(path)
        if ext.lower() in [".potx", ".pptx", ".dotx", ".docx"]:
            return zipfile.is_zipfile(path)
        return os.path.getsize(path) > 0

