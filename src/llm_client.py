"""Provider-agnostic LLM client. Works with any OpenAI-compatible API
(Groq, OpenAI, OpenRouter, local servers, etc.) via base_url override.
"""

import os
from openai import OpenAI


def get_client():
    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")

    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY not set. Copy .env.example to .env and add your key."
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def get_model():
    return os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")


def chat_completion(messages, temperature=0.1, **kwargs):
    client = get_client()
    model = get_model()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
    return response.choices[0].message.content
