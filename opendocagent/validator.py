import sys

class TemplateValidator:
    def validate(self, metadata: dict, tokens: list):
        style = metadata.get("style", "executive").lower()
        
        if style == "executive":
            self._validate_executive(tokens)
        elif style == "technical":
            self._validate_technical(tokens)
            
    def _validate_executive(self, tokens: list):
        # 1. Check for Appendix if slides > 15
        slide_count = sum(1 for t in tokens if t.type == "hr") + 1
        has_appendix = any(t.type == "heading_open" and tokens[i+1].content.strip().lower() == "appendix" 
                           for i, t in enumerate(tokens) if i+1 < len(tokens))
                           
        if slide_count > 15 and not has_appendix:
            print("WARNING [Lint]: Executive presentations over 15 slides should include an '# Appendix' for deep methodology.", file=sys.stderr)
            
    def _validate_technical(self, tokens: list):
        # 1. Check for Purpose or Methodology headers
        has_methodology = any(t.type == "heading_open" and "methodology" in tokens[i+1].content.strip().lower() 
                              for i, t in enumerate(tokens) if i+1 < len(tokens))
                              
        if not has_methodology:
            print("WARNING [Lint]: Technical documents should strictly include a 'Methodology' section for reproducibility.", file=sys.stderr)
