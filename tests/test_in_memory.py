"""Tests for in-memory byte generation across converters and pipeline."""

from opendocagent.pipeline import DocumentPipeline
from opendocagent.converters import DocxConverter, PptxConverter


def _get_pipeline():
    p = DocumentPipeline()
    p.register_converter("docx", "dotx", DocxConverter)
    p.register_converter("pptx", "potx", PptxConverter)
    return p


def test_docx_convert_bytes():
    conv = DocxConverter()
    data = conv.convert_bytes({"metadata": {}, "tokens": []})
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pptx_convert_bytes():
    conv = PptxConverter()
    data = conv.convert_bytes({"metadata": {}, "tokens": []})
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pipeline_build_bytes_docx():
    p = _get_pipeline()
    md = """---
title: "Quarterly Report"
author: "Agent"
format: "docx"
style: "executive"
---
# Executive Summary
Key performance indicators were met.
"""
    data, ext = p.build_bytes(md)
    assert ext == "docx"
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pipeline_build_bytes_pptx():
    p = _get_pipeline()
    md = """---
title: "Slide Deck"
author: "Agent"
format: "pptx"
style: "executive"
---
# Slide One
Overview of quarterly metrics.
"""
    data, ext = p.build_bytes(md)
    assert ext == "pptx"
    assert isinstance(data, bytes)
    assert len(data) > 0
