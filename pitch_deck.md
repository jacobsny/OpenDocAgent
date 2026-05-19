---
format: beamer
style: executive
title: "OpenDocAgent"
author: "OpenDocAgent Contributors"
date: "2026"
beamer_theme: "Madrid"
beamer_colortheme: "default"
beamer_aspectratio: "169"
toc: false
---

# OpenDocAgent

The Agentic Document Generation Engine

## The Problem: AI Can't Format

- **Friction:** Agents dump raw text into chat windows.
- **Lost Time:** Humans spend hours copying, pasting, and formatting AI output into PowerPoint and Word.
- **Inconsistent Branding:** No way to enforce corporate templates automatically.

## The Solution: OpenDocAgent

- **Native Agent Integration:** Accepts standardized Markdown payloads from any LLM.
- **Format Flexibility:** Outputs perfectly styled PDF, PPTX, and DOCX files instantly.
- **Archetype Enforcement:** Built-in Executive and Technical guardrails ensure structural quality.

## Advanced Capabilities

- **Visuals:** Native Mermaid.js diagram compilation.
- **Dynamic:** Jinja2 data injection for real-time reporting.
- **Infrastructure:** Dockerized with automated GitHub Actions CI/CD.

## The Ask & Roadmap

- **Goal:** Become the default document rendering engine for all AI Agents.
- **Immediate Next Steps:** Expand the template registry and add HTML/EPUB output support.
- **Join Us:** Open-source on GitHub — contributions welcome!

# Appendix

## Architecture Overview

```
Agent LLM --> MarkdownParser --> TemplateManager --> Converters
                                                  --> PPTX
                                                  --> DOCX
                                                  --> PDF/Beamer
```
