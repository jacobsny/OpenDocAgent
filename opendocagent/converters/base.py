class BaseConverter:
    def __init__(self, template_path: str = None):
        self.template_path = template_path

    def convert(self, ast: dict, output_path: str):
        """
        Converts the Markdown AST to the target format.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement convert()")
