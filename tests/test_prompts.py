import pytest
from opendocagent.prompts import get_agent_prompt

def test_get_agent_prompt_executive():
    prompt = get_agent_prompt("executive")
    assert "EXECUTIVE" in prompt
    assert "Pyramid Principle" in prompt
    assert "YAML frontmatter" in prompt

def test_get_agent_prompt_technical():
    prompt = get_agent_prompt("technical")
    assert "TECHNICAL" in prompt
    assert "reproducibility" in prompt
    assert "YAML frontmatter" in prompt

def test_get_agent_prompt_default():
    prompt = get_agent_prompt("unknown")
    assert "YAML frontmatter" in prompt
    assert "EXECUTIVE" not in prompt
    assert "TECHNICAL" not in prompt
