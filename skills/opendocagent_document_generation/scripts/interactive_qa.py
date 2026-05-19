import sys

def get_questionnaire():
    questions = [
        "To ensure the final document perfectly meets your needs, please answer a few quick questions:",
        "",
        "1. **Output Format:** Would you like a Presentation (PPTX), a PDF, or a Word Document (DOCX)?",
        "2. **Styling Archetype:** Should this be an **Executive** document (high-level, concise, decision-first) or a **Technical** document (deeply detailed, methodological, strictly structured)?",
        "3. **Branding:** Do you have a specific template in mind, or should I use the default organizational templates?",
        "4. **Dynamic Data:** Do you have any specific JSON data payloads you want injected into the document?",
        "",
        "Let me know, and I'll generate the document immediately!"
    ]
    return "\n".join(questions)

if __name__ == "__main__":
    print(get_questionnaire())
