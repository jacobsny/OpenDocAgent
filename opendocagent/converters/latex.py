import pypandoc
from .base import BaseConverter
import os

class LatexConverter(BaseConverter):
    def convert(self, parsed: dict, output_path: str):
        content = parsed.get("content", "")
        metadata = parsed.get("metadata", {})
        
        extra_args = []
        if self.template_path and os.path.exists(self.template_path):
            extra_args.append(f'--template={self.template_path}')
            
        # Determine format from output_path extension
        _, ext = os.path.splitext(output_path)
        out_fmt = 'pdf' if ext.lower() == '.pdf' else 'latex'
        
        target_fmt = metadata.get("format", "").lower()
        if target_fmt == "beamer":
            # Slide-level 2 means every ## heading becomes a new slide frame
            theme = metadata.get("beamer_theme", "Madrid")
            colortheme = metadata.get("beamer_colortheme", "default")
            aspectratio = metadata.get("beamer_aspectratio", "169")
            title = metadata.get("title", "Presentation")
            author = metadata.get("author", "")
            date = metadata.get("date", "")

            extra_args.extend([
                "-t", "beamer",
                "--slide-level=2",
                "-V", f"theme:{theme}",
                "-V", f"colortheme:{colortheme}",
                "-V", f"aspectratio={aspectratio}",
                "-V", f"title:{title}",
            ])
            if author:
                extra_args.extend(["-V", f"author:{author}"])
            if date:
                extra_args.extend(["-V", f"date:{date}"])

        pypandoc.convert_text(
            content,
            out_fmt,
            format='md',
            outputfile=output_path,
            extra_args=extra_args
        )

