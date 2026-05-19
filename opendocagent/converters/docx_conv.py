import docx
from docx.shared import Pt
from .base import BaseConverter

class DocxConverter(BaseConverter):
    def convert(self, parsed: dict, output_path: str):
        doc = docx.Document(self.template_path) if self.template_path else docx.Document()
        
        tokens = parsed.get("tokens", [])
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "heading_open":
                level = int(token.tag[1]) # 'h1' -> 1
                # next token is inline content
                i += 1
                inline_token = tokens[i]
                doc.add_heading(inline_token.content, level=level)
                
            elif token.type == "paragraph_open":
                i += 1
                inline_token = tokens[i]
                
                # Check for blockquote pretending to be speaker notes (skip them for Word, or add as quotes)
                if inline_token.content.startswith("Note:"):
                    p = doc.add_paragraph(inline_token.content, style='Quote')
                else:
                    p = doc.add_paragraph()
                    self._process_inline(p, inline_token.children)
                    
            elif token.type == "hr":
                doc.add_page_break()
                
            i += 1
            
        doc.save(output_path)
        
    def _process_inline(self, paragraph, children):
        if not children:
            return
            
        for child in children:
            if child.type == "text":
                paragraph.add_run(child.content)
            elif child.type == "strong_open":
                # Find matching text and close
                pass # Simple implementation doesn't handle nested formatting elegantly yet, just raw text for now
            # To do full inline rendering, we maintain state.
            # For simplicity, we just use the raw text if children handling gets complex.
        
        # fallback if children iteration is too basic:
        # paragraph.add_run(inline_token.content) is simpler, but let's try basic children handling.
        # Actually, python-docx runs can be bolded.
        current_run = None
        bold = False
        italic = False
        
        for child in children:
            if child.type == "strong_open":
                bold = True
            elif child.type == "strong_close":
                bold = False
            elif child.type == "em_open":
                italic = True
            elif child.type == "em_close":
                italic = False
            elif child.type == "text":
                run = paragraph.add_run(child.content)
                run.bold = bold
                run.italic = italic

