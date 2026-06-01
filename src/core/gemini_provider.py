import time
from typing import Dict, Any, Optional, Generator

import google.generativeai as genai

from src.core.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for DEFAULT_PROVIDER=google")
        genai.configure(api_key=api_key)
        self._model_name = model_name

    def _model(self, system_prompt: Optional[str] = None) -> genai.GenerativeModel:
        if system_prompt:
            return genai.GenerativeModel(
                self._model_name,
                system_instruction=system_prompt,
            )
        return genai.GenerativeModel(self._model_name)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        response = self._model(system_prompt).generate_content(prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        usage_meta = response.usage_metadata
        usage = {
            "prompt_tokens": usage_meta.prompt_token_count,
            "completion_tokens": usage_meta.candidates_token_count,
            "total_tokens": usage_meta.total_token_count,
        }

        return {
            "content": response.text,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "google",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        response = self._model(system_prompt).generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
