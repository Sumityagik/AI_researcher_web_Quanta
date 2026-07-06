"""
Thin wrapper around Google's Gemini API (the current `google-genai` SDK).

Keeps the prompt-engineering and API call in one place so app.py stays
simple, and so it's easy to swap the model or prompt later.
"""

import os

from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """You are Quanta, an AI research assistant embedded in a
web app. A user will ask about a research topic, concept, or question. Your
job is to answer like a well-organized research brief, not a casual chat
reply.

Always structure your answer in Markdown using this shape (skip a section
only if it genuinely does not apply):

# <Topic Title>

## Definition
A clear, precise explanation of what it is, 2-4 sentences.

## Key Points
- 4-6 bullet points, each starting with a short **bolded label** followed by
  a colon and one explanatory sentence.

## Examples / Use Cases
- 2-4 concrete, real-world examples or applications.

## Why It Matters
1-2 sentences on significance, impact, or current relevance.

Be accurate and specific. If the topic is ambiguous, answer the most likely
interpretation and briefly note the assumption. Do not use conversational
filler like "Great question!" -- start directly with the title heading."""

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/app/apikey and put it in your .env file."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def ask_gemini(query: str) -> str:
    """Send a research question to Gemini and return the Markdown answer."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=1024,
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response. Try rephrasing your question.")
    return text
