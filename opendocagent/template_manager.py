import os

class TemplateManager:
    def __init__(self, template_dir=None):
        if template_dir is None:
            self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        else:
            self.template_dir = template_dir
        
    def get_template(self, name: str, style: str, format_type: str) -> str:
        """
        Returns the path to the requested template file.
        format_type should be one of 'potx', 'dotx', 'tex'
        """
        template_name = name if name else (style if style else "default")
        return os.path.join(self.template_dir, f"{template_name}.{format_type}")
