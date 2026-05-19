import os
from opendocagent.template_manager import TemplateManager

def test_get_template():
    manager = TemplateManager(template_dir="dummy_dir")
    
    docx_path = manager.get_template("corporate", "executive", "dotx")
    assert docx_path == os.path.join("dummy_dir", "corporate.dotx")
    
    pptx_path = manager.get_template("", "technical", "potx")
    assert pptx_path == os.path.join("dummy_dir", "technical.potx")
