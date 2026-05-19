import pytest
from opendocagent.parser import MarkdownParser

def test_parser_with_frontmatter():
    md = """---
format: pdf
template: test_template
---
# Header
Some text.
"""
    parser = MarkdownParser()
    parsed = parser.parse(md)
    
    # Check frontmatter
    assert parsed["metadata"]["format"] == "pdf"
    assert parsed["metadata"]["template"] == "test_template"
    
    # Check markdown tokens
    tokens = parsed["tokens"]
    assert len(tokens) > 0
    
    # First token should be the heading, not the frontmatter
    assert tokens[0].type == "heading_open"
    assert tokens[0].tag == "h1"

def test_parser_without_frontmatter():
    md = """# Header
Some text.
"""
    parser = MarkdownParser()
    parsed = parser.parse(md)
    
    assert parsed["metadata"] == {}
    
    tokens = parsed["tokens"]
    assert tokens[0].type == "heading_open"
    assert tokens[0].tag == "h1"
