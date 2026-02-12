import asyncio
import os
from typing import List, Dict
from app.api.core.config import settings

try:
    import openai
except Exception:
    openai = None

try:
    from google import genai
except Exception:
    genai = None

class LLMClient:
    def __init__(self):
        # keys: prefer settings, fallback to standard env var names
        self.openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_key = settings.gemini_api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.openai_key is None and self.gemini_key is None:
            raise RuntimeError("No LLM API keys found: set OPENAI_API_KEY and/or GOOGLE_API_KEY/GEMINI_API_KEY")
        # check libs availability
        if self.openai_key and (openai is None or not hasattr(openai, "OpenAI")):
            raise RuntimeError("openai>=1.0 is required for GPT calls. Install/upgrade: pip install --upgrade openai")
        if self.gemini_key and genai is None:
            raise RuntimeError("google-genai is required for Gemini calls. Install: pip install google-genai")

    async def generate(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 300) -> str:
        lname = model.lower()
        if "gpt" in lname:
            return await self._call_openai(model, messages, temperature, max_tokens)
        if "gemini" in lname or "bison" in lname or "text-bison" in lname:
            return await self._call_gemini(model, messages, temperature, max_tokens)
        raise ValueError(f"Unsupported model '{model}'")

    async def _call_openai(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        if not self.openai_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        def _sync():
            client = openai.OpenAI(api_key=self.openai_key)
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content.strip()
        return await asyncio.to_thread(_sync)

    async def _call_gemini(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        if not self.gemini_key:
            raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY not set")
        # build plaintext prompt from messages
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        prompt_text = "\n\n".join(parts)

        def _sync():
            client = genai.Client(api_key=self.gemini_key)
            # use models.generate_content for single-turn generation
            resp = client.models.generate_content(model=model, contents=prompt_text)
            # modern SDK exposes `text` on response
            return getattr(resp, "text", str(resp))
        return await asyncio.to_thread(_sync)

# singleton factory
_singleton: LLMClient | None = None
def get_llm_client() -> LLMClient:
    global _singleton
    if _singleton is None:
        _singleton = LLMClient()
    return _singleton