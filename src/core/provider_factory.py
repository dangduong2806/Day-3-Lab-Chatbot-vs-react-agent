import os
from typing import Optional

from dotenv import load_dotenv

from src.core.llm_provider import LLMProvider


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """Build an LLM provider from environment variables."""
    load_dotenv()

    name = (provider or os.getenv("DEFAULT_PROVIDER", "google")).lower()
    model_name = model or os.getenv("DEFAULT_MODEL", "")

    if name in ("google", "gemini"):
        from src.core.gemini_provider import GeminiProvider

        return GeminiProvider(
            model_name=model_name or "gemini-2.5-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    if name == "openai":
        from src.core.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model_name=model_name or "gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    if name == "local":
        from src.core.local_provider import LocalProvider

        model_path = os.path.abspath(
            model_name
            or os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        )
        n_ctx = int(os.getenv("LOCAL_N_CTX", "4096"))
        max_tokens = int(os.getenv("LOCAL_MAX_TOKENS", "512"))
        n_threads = os.getenv("LOCAL_N_THREADS")
        threads = int(n_threads) if n_threads else None

        return LocalProvider(
            model_path=model_path,
            n_ctx=n_ctx,
            max_tokens=max_tokens,
            n_threads=threads,
        )

    raise ValueError(
        f"Unknown DEFAULT_PROVIDER '{name}'. Use google, openai, or local."
    )
