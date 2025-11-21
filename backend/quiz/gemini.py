import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL = "gemini-1.5-pro"

def generate_mcqs(pdf_text, weak_topics=None):
    extra = ""
    if weak_topics:
        extra = f"Focus more questions on: {', '.join(weak_topics)}."

    prompt = f"""
    Generate 50 multiple-choice questions based on this study material.

    {extra}

    Return ONLY valid JSON:
    [
      {{
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "explanation": "..."
      }}
    ]

    Study Material:
    {pdf_text}
    """

    response = genai.GenerativeModel(MODEL).generate_content(prompt)
    return response.text
