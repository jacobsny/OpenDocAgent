class OpenDocAgentError(Exception):
    """Base exception for all OpenDocAgent errors."""
    pass

class TemplateNotFoundError(OpenDocAgentError):
    """Raised when a requested template cannot be found."""
    pass

class ValidationLintError(OpenDocAgentError):
    """Raised when the Markdown payload violates archetypal standards."""
    pass

class FormatNotSupportedError(OpenDocAgentError):
    """Raised when an unsupported output format is requested."""
    pass
