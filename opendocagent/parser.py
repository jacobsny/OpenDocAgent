import markdown_it
import yaml
import re
import jinja2

class MarkdownParser:
    def __init__(self):
        self.md = markdown_it.MarkdownIt()
        self.frontmatter_regex = re.compile(r"^-{3,}\s*\n(.*?)\n-{3,}\s*\n", re.DOTALL)
        
    def parse(self, content: str, context: dict = None):
        """
        Parses Markdown content and returns an AST (Abstract Syntax Tree)
        along with any parsed frontmatter metadata.
        If a context dictionary is provided, the content is rendered via Jinja2 first.
        """
        if context:
            template = jinja2.Template(content)
            content = template.render(**context)
            
        metadata = {}
        
        # Extract YAML frontmatter if it exists
        match = self.frontmatter_regex.match(content)
        if match:
            try:
                metadata = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse frontmatter: {e}")
            
            # Remove frontmatter from content before passing to markdown parser
            content = content[match.end():]
            
        # Feature 5: Auto-Table of Contents
        if metadata.get("toc"):
            content = "# Table of Contents\n\n[[TOC]]\n\n---\n" + content
            
        # Feature 4: Multi-Column Layout Directives
        # Replace ::: col with a custom HTML block or token
        content = re.sub(r":::\s*col", "<!-- col -->", content)
            
        # Feature 1: Mermaid.js integration placeholder
        # In a full implementation, we'd find ```mermaid blocks, run mmdc via subprocess, 
        # and replace them with ![diagram](path.png)
        content = re.sub(r"```mermaid(.*?)```", r"![Mermaid Diagram](mermaid_placeholder.png)", content, flags=re.DOTALL)
            
        tokens = self.md.parse(content)
        
        return {
            "metadata": metadata,
            "tokens": tokens,
            "content": content
        }

