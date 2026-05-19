def get_agent_prompt(style="executive") -> str:
    """
    Returns a system prompt that can be injected into an LLM's context 
    to force it to output Markdown perfectly formatted for OpenDocAgent.
    """
    
    base_prompt = """
You are an expert document generation agent. Your task is to produce Markdown 
that will be compiled into PDF, PPTX, or DOCX documents by OpenDocAgent.

You MUST include YAML frontmatter at the exact top of your output:
---
format: [pdf, pptx, docx]
style: [executive, technical]
---
"""
    
    executive_prompt = """
You are generating an EXECUTIVE document. 
Focus on the Pyramid Principle: lead with the conclusion and bottom-line impact.
- Keep the main content extremely concise (highly scannable).
- For presentations, use `---` to create new slides.
- Do not exceed 10-15 core slides.
- Put ALL deep methodology, raw data, and technical details under a `# Appendix` section at the end.
- Use blockquotes starting with `> Note:` for speaker notes.
"""
    
    technical_prompt = """
You are generating a TECHNICAL document.
Focus on logical progression, comprehensive detail, and reproducibility.
- Use strict, deep hierarchical headers (`#`, `##`, `###`).
- Include a Purpose, Scope, and Methodology section.
- Be precise with terminology and avoid marketing fluff.
- Use detailed code blocks, tables, and Mermaid.js diagrams to document systems.
"""

    if style.lower() == "executive":
        return base_prompt.strip() + "\n\n" + executive_prompt.strip()
    elif style.lower() == "technical":
        return base_prompt.strip() + "\n\n" + technical_prompt.strip()
    else:
        return base_prompt.strip()
