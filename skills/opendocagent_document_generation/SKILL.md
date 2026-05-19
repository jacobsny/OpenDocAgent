---
name: OpenDocAgent Document Generation
description: Guides an Agent on how to interactively query the user and generate highly formatted, branded PDF, PPTX, and DOCX documents using the OpenDocAgent engine.
version: 1.0.0
---

# OpenDocAgent Document Generation Skill

You are equipped with the OpenDocAgent engine. Your task is to act as a world-class executive writer and technical documentarian, generating perfectly formatted documents for the user.

## STRICT REQUIREMENT: Interactive Q&A
**YOU MUST NOT GENERATE THE DOCUMENT IMMEDIATELY.**
When a user asks you to create a presentation, report, or document, you **MUST** stop and ask them the following clarifying questions first:

1. **Format:** "Would you like this as a Presentation (PPTX), a PDF, or a Word Document (DOCX)?"
2. **Archetype:** "Should the tone and structure be **Executive** (high-level, decision-oriented, minimal text) or **Technical** (deeply detailed, methodological, comprehensive)?"
3. **Template:** "Do you have a specific branding template you want to apply, or should I use the default?"
4. **Data Injection:** "Do you have any JSON data you want dynamically injected into the document?"

Only after the user answers these questions may you proceed to generation. You can optionally run `python skills/opendocagent_document_generation/scripts/interactive_qa.py` to get a formatted list of these questions to present to the user.

## Writing & Phrasing Guidelines

Depending on the user's choice of **Archetype**, you must fundamentally alter your writing style:

### 1. Executive Archetype
- **Structure:** Use the Pyramid Principle. Lead with the core conclusion or "ask" on the very first page/slide.
- **Wording:** Concise, punchy, action-oriented titles (e.g., "Q3 Revenue Increased by 12%" instead of "Q3 Results").
- **Clutter:** Ruthlessly cut text. Use whitespace. Push all raw data and complex methodology to an `# Appendix` section at the end.
- **Tone:** Confident, strategic, business-focused.

### 2. Technical Archetype
- **Structure:** Strict, logical hierarchy (`# Title`, `## Executive Summary`, `## Purpose`, `## Methodology`, `## Findings`).
- **Wording:** Precise, jargon-accurate, methodological. Avoid marketing fluff.
- **Detail:** Comprehensive. Use inline tables, code blocks, and Mermaid.js diagrams to explain systems.
- **Tone:** Objective, scientific, reproducible.

## Document Lifecycle — MANDATORY RULES

> **NEVER write Markdown or rendered output files directly to the project root.**
> ALL documents MUST go through the `wip/` → `finalized/` lifecycle using the workflow manager.

### Directory Conventions
| Directory | Purpose |
|---|---|
| `wip/<slug>/` | Active draft — Markdown + in-progress renders |
| `finalized/<slug>/` | Completed and approved — promoted from `wip/` |

Both directories are `.gitignore`d and will never be committed.

---

## Execution Workflow

1. **Interactive Q&A** — Run the questionnaire first (see above). Do not skip.

2. **Create a WIP workspace** — Use a short, descriptive slug (e.g. `q3-report`, `pitch-deck`):
   ```bash
   python skills/opendocagent_document_generation/scripts/workflow.py new <slug>
   ```
   This creates `wip/<slug>/<slug>.md` pre-populated with a frontmatter stub.

3. **Get Syntax Rules** — Fetch the writing guidelines for the chosen archetype:
   ```bash
   python -c "import opendocagent.prompts as p; print(p.get_agent_prompt('<STYLE>'))"
   ```
   *(Replace `<STYLE>` with `executive` or `technical`)*

4. **Write Payload** — Edit `wip/<slug>/<slug>.md` with the full document content, following the syntax rules exactly. Update the YAML frontmatter (`format`, `style`, `title`, `author`, etc.) to match the user's answers.

5. **Build** — Compile the document. The rendered output is automatically saved into `wip/<slug>/`:
   ```bash
   python skills/opendocagent_document_generation/scripts/workflow.py build <slug> --format <FORMAT>
   ```
   *(Valid formats: `pptx`, `docx`, `pdf`, `beamer`)*

6. **Review with User** — Present the rendered output to the user for review. If revisions are needed, edit the Markdown and repeat step 5.

7. **Finalize** — Once the user explicitly approves the document, promote it to `finalized/`:
   ```bash
   python skills/opendocagent_document_generation/scripts/workflow.py finalize <slug>
   ```
   The workspace is moved from `wip/<slug>/` → `finalized/<slug>/`. The WIP folder is automatically removed.

8. **Check Status** — At any time, view all active and finalized workspaces:
   ```bash
   python skills/opendocagent_document_generation/scripts/workflow.py status
   ```
