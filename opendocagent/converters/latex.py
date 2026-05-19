import pypandoc
from .base import BaseConverter
import os

class LatexConverter(BaseConverter):
    def convert(self, parsed: dict, output_path: str):
        content = parsed.get("content", "")
        
        extra_args = []
        if self.template_path and os.path.exists(self.template_path):
            extra_args.append(f'--template={self.template_path}')
            
        # Determine format from output_path extension
        _, ext = os.path.splitext(output_path)
        out_fmt = 'pdf' if ext.lower() == '.pdf' else 'latex'
        
        pypandoc.convert_text(
            content,
            out_fmt,
            format='md',
            outputfile=output_path,
            extra_args=extra_args
        )
