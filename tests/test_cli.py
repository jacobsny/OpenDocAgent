import os
import tempfile
import sys
from unittest.mock import patch
from opendocagent.cli import main

def test_cli_build(tmp_path):
    # Create a dummy markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("---\nformat: docx\n---\n# Test\n", encoding="utf-8")
    
    # Run the CLI with the test file
    test_args = ["opendoc", "build", str(md_file)]
    
    with patch.object(sys, 'argv', test_args):
        # Prevent sys.exit(0) if it's there, but we don't call it on success
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
            
    # Check that a .docx file was created next to the md file
    docx_file = tmp_path / "test.docx"
    assert docx_file.exists()
