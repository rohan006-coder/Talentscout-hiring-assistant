import os
import json
from typing import Any, Dict, List, Optional

class LLMClient:
    """
    Minimal LLM client:
    - If OPENAI_API_KEY is present and user enables "Use LLM", uses OpenAI Chat Completions.
    - Otherwise the app falls back to rule-based question generation.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    def is_ready(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
        """
        if not self.is_ready():
            return "LLM is not configured. Please set OPENAI_API_KEY or disable LLM."

        # Lazy import so requirements remain light unless needed
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()

    def generate_questions(self, messages: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Expects the assistant response to be valid JSON.
        Returns: { "Python": ["Q1", "Q2", ...], "Django": [...] }
        """
        text = self.chat(messages)
        try:
            data = json.loads(text)
            # basic validation
            if isinstance(data, dict):
                clean: Dict[str, List[str]] = {}
                for k, v in data.items():
                    if isinstance(k, str) and isinstance(v, list):
                        clean[k] = [str(x).strip() for x in v if str(x).strip()]
                return clean
        except Exception:
            pass
        # If parsing fails, return empty dict and app will fall back
        return {}