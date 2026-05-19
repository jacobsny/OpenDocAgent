from pptx import Presentation
from .base import BaseConverter

class PptxConverter(BaseConverter):
    def convert(self, parsed: dict, output_path: str):
        prs = Presentation(self.template_path) if self.template_path else Presentation()
        
        tokens = parsed.get("tokens", [])
        
        current_slide = None
        current_text_frame = None
        
        # Determine layout indices (these vary by template, but 0 and 1 are standard)
        TITLE_SLIDE_LAYOUT = prs.slide_layouts[0]
        CONTENT_SLIDE_LAYOUT = prs.slide_layouts[1]
        
        # Start the first slide as a content slide unless we see an H1 first
        # But let's wait to create the first slide until we see content or hr
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "hr":
                current_slide = None # Next content will create a new slide
                
            elif token.type == "heading_open":
                level = int(token.tag[1])
                i += 1
                inline_token = tokens[i]
                
                if level == 1:
                    # Title slide
                    current_slide = prs.slides.add_slide(TITLE_SLIDE_LAYOUT)
                    current_slide.shapes.title.text = inline_token.content
                    # Subtitle will just be the next paragraph if we wanted to handle it nicely
                elif level == 2:
                    # Content slide
                    if not current_slide:
                        current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
                    if current_slide.shapes.title:
                        current_slide.shapes.title.text = inline_token.content
                    
                    # Set up text frame for body
                    if len(current_slide.placeholders) > 1:
                        current_text_frame = current_slide.placeholders[1].text_frame
                        current_text_frame.text = "" # clear default
                        
            elif token.type == "paragraph_open":
                i += 1
                inline_token = tokens[i]
                
                if inline_token.content.startswith("Note:"):
                    # Add to speaker notes
                    if current_slide and current_slide.has_notes_slide:
                        notes_slide = current_slide.notes_slide
                        notes_text_frame = notes_slide.notes_text_frame
                        notes_text_frame.text += inline_token.content + "\n"
                else:
                    if not current_slide:
                        current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
                        if len(current_slide.placeholders) > 1:
                            current_text_frame = current_slide.placeholders[1].text_frame
                            current_text_frame.text = ""
                            
                    if current_text_frame:
                        p = current_text_frame.add_paragraph()
                        p.text = inline_token.content
                        
            elif token.type == "bullet_list_open":
                # Handle lists basically
                pass
                
            elif token.type == "list_item_open":
                # Advance past paragraph open if it exists
                if i + 1 < len(tokens) and tokens[i+1].type == "paragraph_open":
                    i += 2
                else:
                    i += 1
                
                inline_token = tokens[i]
                if inline_token.type == "inline" and current_text_frame:
                    p = current_text_frame.add_paragraph()
                    p.text = inline_token.content
                    p.level = 1
                    
            i += 1
            
        prs.save(output_path)

