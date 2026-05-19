import os

class TemplateManager:
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        
    def get_template(self, name: str, format_type: str) -> str:
        """
        Returns the path to the requested template file.
        format_type should be one of 'potx', 'dotx', 'tex'
        """
        # TODO: Implement template resolution
        return os.path.join(self.template_dir, f"{name}.{format_type}")
