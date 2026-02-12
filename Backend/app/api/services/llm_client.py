import asyncio
from typing import List, Dict, Optional
from app.api.core.config import settings

try:
    import openai
except Exception:
    openai = None

class BaseLLMClient:
    async def generate(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 300) -> str:
        raise NotImplementedError

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str):
        if openai is None:
            raise RuntimeError("openai package not installed")
        openai.api_key = api_key

    async def generate(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 300) -> str:
        def _call():
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp["choices"][0]["message"]["content"].strip()
        return await asyncio.to_thread(_call)

class MockLLMClient(BaseLLMClient):
    async def generate(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 300) -> str:
        # Return a deterministic reply summarizing last user content
        last = ""
        for m in reversed(messages):
            if m.get("role") in ("assistant", "user"):
                last = m.get("content", "")
                break
        return f"[mock reply by {model}] Responding to: {last[:200]}"

def get_llm_client() -> BaseLLMClient:
    key = settings.openai_api_key
    if key and openai is not None:
        return OpenAIClient(api_key=key)
    return MockLLMClient()