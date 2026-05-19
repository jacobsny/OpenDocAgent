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
            
        tokens = self.md.parse(content)
        
        # AST Manipulation (Phase 4 Refactor)
        from markdown_it.token import Token
        new_tokens = []
        
        # Feature 5: Auto-Table of Contents (inject at top)
        if metadata.get("toc"):
            h1_open = Token("heading_open", "h1", 1)
            h1_text = Token("inline", "", 0)
            h1_text.content = "Table of Contents"
            h1_close = Token("heading_close", "h1", -1)
            toc_token = Token("inline", "", 0)
            toc_token.content = "[[TOC]]"
            hr_token = Token("hr", "hr", 0)
            new_tokens.extend([h1_open, h1_text, h1_close, toc_token, hr_token])
            
        for token in tokens:
            # Feature 4: Multi-Column Layout Directives
            if token.type == "inline" and "::: col" in token.content:
                token.content = token.content.replace("::: col", "<!-- col -->")
                
            # Feature 1: Mermaid.js integration
            if token.type == "fence" and token.info == "mermaid":
                img_token = Token("inline", "", 0)
                img_token.content = "![Mermaid Diagram](mermaid_placeholder.png)"
                new_tokens.append(img_token)
                continue
                
            new_tokens.append(token)
            
        tokens = new_tokens
        
        return {
            "metadata": metadata,
            "tokens": tokens,
            "content": content
        }

