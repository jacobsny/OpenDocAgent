import io
import os
import re
from pathlib import Path
from typing import Any
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

from opendocagent.types import ParsedDocument
from .base import BaseConverter


NOTE_PATTERN = re.compile(r"^(?:>\s*)?(?:speaker\s+)?note:\s*(.*)", re.IGNORECASE | re.DOTALL)


class PptxConverter(BaseConverter):
    def _build_presentation(self, parsed: dict[str, Any] | ParsedDocument) -> Any:
        prs = Presentation(self.template_path) if self.template_path else Presentation()
        
        tokens = parsed.get("tokens", [])
        
        current_slide = None
        current_text_frame = None
        is_title_slide = False
        list_depth = 0
        has_columns = False
        
        # Determine layout indices (0: title, 1: content)
        TITLE_SLIDE_LAYOUT = prs.slide_layouts[0] if len(prs.slide_layouts) > 0 else prs.slide_layouts[0]
        CONTENT_SLIDE_LAYOUT = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "hr":
                current_slide = None
                current_text_frame = None
                is_title_slide = False
                has_columns = False
                list_depth = 0
                
            elif token.type == "heading_open":
                level = int(token.tag[1]) if len(token.tag) > 1 and token.tag[1].isdigit() else 2
                i += 1
                inline_token = tokens[i]
                heading_text = inline_token.content if inline_token else ""
                
                if level == 1:
                    # Title slide
                    current_slide = prs.slides.add_slide(TITLE_SLIDE_LAYOUT)
                    if current_slide.shapes.title:
                        current_slide.shapes.title.text = heading_text
                    is_title_slide = True
                    has_columns = False
                    current_text_frame = None
                else:
                    # Content slide (Level 2+)
                    current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
                    if current_slide.shapes.title:
                        current_slide.shapes.title.text = heading_text
                    is_title_slide = False
                    has_columns = False
                    
                    if len(current_slide.placeholders) > 1:
                        current_text_frame = current_slide.placeholders[1].text_frame
                        current_text_frame.text = ""  # clear default prompt
                    else:
                        tb = current_slide.shapes.add_textbox(
                            Inches(1.0), Inches(1.5), Inches(8.0), Inches(5.0)
                        )
                        current_text_frame = tb.text_frame
                        
            elif token.type in ("bullet_list_open", "ordered_list_open"):
                list_depth += 1
                
            elif token.type in ("bullet_list_close", "ordered_list_close"):
                list_depth = max(0, list_depth - 1)
                
            elif token.type == "list_item_open":
                pass
                    
            elif token.type == "paragraph_open":
                i += 1
                inline_token = tokens[i]
                text = inline_token.content if inline_token else ""
                
                # Check for column directives
                if "<!-- col -->" in text or "::: col" in text:
                    new_tf = self._split_columns(prs, current_slide)
                    if new_tf:
                        current_text_frame = new_tf
                    has_columns = True
                # Check for Mermaid diagram placeholder
                elif "![Mermaid Diagram]" in text or "mermaid_placeholder.png" in text:
                    self._add_diagram_box(prs, current_slide)
                # Check for Speaker Notes
                elif NOTE_PATTERN.match(text):
                    note_match = NOTE_PATTERN.match(text)
                    clean_note = note_match.group(1).strip() if note_match else text
                    self._add_speaker_note(current_slide, prs, clean_note)
                elif is_title_slide:
                    # Paragraph on title slide is the subtitle
                    if current_slide and len(current_slide.placeholders) > 1:
                        current_slide.placeholders[1].text = text
                    is_title_slide = False
                else:
                    if not current_slide:
                        current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
                        if len(current_slide.placeholders) > 1:
                            current_text_frame = current_slide.placeholders[1].text_frame
                            current_text_frame.text = ""
                            
                    if current_text_frame:
                        p = current_text_frame.add_paragraph()
                        p.text = text
                        p.level = max(0, min(list_depth - 1, 8)) if list_depth > 0 else 0
                        
            elif token.type == "html_block":
                content = token.content or ""
                if "<!-- col -->" in content or "::: col" in content:
                    new_tf = self._split_columns(prs, current_slide)
                    if new_tf:
                        current_text_frame = new_tf
                    has_columns = True
                elif NOTE_PATTERN.match(content):
                    note_match = NOTE_PATTERN.match(content)
                    clean_note = note_match.group(1).strip() if note_match else content
                    self._add_speaker_note(current_slide, prs, clean_note)
                    
            i += 1
            
        return prs

    def _split_columns(self, prs: Any, current_slide: Any) -> None:
        """Splits the current slide body into two side-by-side columns."""
        if not current_slide:
            return
            
        slide_width = prs.slide_width
        slide_height = prs.slide_height
        
        col_width = int(slide_width * 0.44)
        top = int(slide_height * 0.25)
        height = int(slide_height * 0.65)
        
        # Adjust left placeholder
        if len(current_slide.placeholders) > 1:
            left_ph = current_slide.placeholders[1]
            left_ph.width = col_width
            top = left_ph.top
            height = left_ph.height
            
        # Create right column textbox
        right_left = int(slide_width * 0.52)
        right_box = current_slide.shapes.add_textbox(right_left, top, col_width, height)
        right_tf = right_box.text_frame
        right_tf.word_wrap = True
        return right_tf

    def _add_speaker_note(self, current_slide: Any, prs: Any, note_text: str) -> None:
        """Adds speaker notes to the current slide (lazily creating notes_slide)."""
        if not current_slide:
            CONTENT_SLIDE_LAYOUT = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
            current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
            
        # Direct access to .notes_slide lazily creates notes slide in python-pptx
        notes_slide = current_slide.notes_slide
        notes_tf = notes_slide.notes_text_frame
        if notes_tf.text:
            notes_tf.text = (notes_tf.text.rstrip() + "\n\n" + note_text).strip()
        else:
            notes_tf.text = note_text

    def _add_diagram_box(self, prs: Any, current_slide: Any) -> None:
        """Adds a visual diagram placeholder box to the slide for Mermaid diagrams."""
        if not current_slide:
            CONTENT_SLIDE_LAYOUT = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
            current_slide = prs.slides.add_slide(CONTENT_SLIDE_LAYOUT)
            
        left = Inches(1.5)
        top = Inches(2.2)
        width = Inches(7.0)
        height = Inches(3.8)
        
        shape = current_slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(240, 244, 248)
        shape.line.color.rgb = RGBColor(180, 195, 210)
        shape.line.width = Pt(1.5)
        
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "[Mermaid Architecture Diagram]"
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(50, 70, 95)

    def convert(self, parsed: dict[str, Any] | ParsedDocument, output_path: str | Path) -> None:
        prs = self._build_presentation(parsed)
        prs.save(str(output_path))

    def convert_bytes(self, parsed: dict[str, Any] | ParsedDocument) -> bytes:
        prs = self._build_presentation(parsed)
        buf = io.BytesIO()
        prs.save(buf)
        return buf.getvalue()


