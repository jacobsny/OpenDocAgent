import os
import tempfile
from opendocagent.converters import DocxConverter, PptxConverter, LatexConverter

def test_docx_converter():
    converter = DocxConverter()
    
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        out_path = tmp.name
        
    try:
        converter.convert({"metadata": {}, "tokens": []}, out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)

def test_pptx_converter():
    converter = PptxConverter()
    
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        out_path = tmp.name
        
    try:
        converter.convert({"metadata": {}, "tokens": []}, out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)
            
def test_latex_converter():
    converter = LatexConverter()
    
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
        out_path = tmp.name
        
    try:
        converter.convert({"metadata": {}, "tokens": []}, out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
    finally:
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except:
                pass
