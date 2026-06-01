import os
import time
from typing import Dict, Any, Optional, Generator

from src.core.llm_provider import LLMProvider

# Phi-3-mini-4k-instruct-q4.gguf is ~2.39 GB when complete
MIN_MODEL_BYTES = 2_000_000_000


def validate_model_file(model_path: str) -> None:
    """Raise clear errors before llama-cpp loads a broken/partial GGUF."""
    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            "Download: python scripts/download_model.py"
        )

    size = os.path.getsize(model_path)
    if size < MIN_MODEL_BYTES:
        raise ValueError(
            f"Model file is incomplete ({size / (1024**2):.0f} MB, need ~2400 MB).\n"
            f"Delete and re-download:\n"
            f"  del \"{model_path}\"\n"
            f"  python scripts/download_model.py"
        )

    with open(model_path, "rb") as f:
        if f.read(4) != b"GGUF":
            raise ValueError(
                f"File is not a valid GGUF model: {model_path}\n"
                "Re-download: python scripts/download_model.py"
            )


class LocalProvider(LLMProvider):
    """
    LLM Provider for local models using llama-cpp-python.
    Optimized for CPU usage with GGUF models (Phi-3-mini).
    """

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 4096,
        max_tokens: int = 512,
        n_threads: Optional[int] = None,
    ):
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise ImportError(
                "llama-cpp-python is not installed. Run:\n"
                "  pip install llama-cpp-python --extra-index-url "
                "https://abetlen.github.io/llama-cpp-python/whl/cpu"
            ) from exc

        model_path = os.path.abspath(model_path)
        validate_model_file(model_path)

        super().__init__(model_name=os.path.basename(model_path))

        self.max_tokens = max_tokens
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
        except ValueError as exc:
            raise ValueError(
                f"llama-cpp could not load: {model_path}\n"
                "Usually the download was interrupted. Run:\n"
                "  python scripts/download_model.py"
            ) from exc

    def _format_prompt(self, prompt: str, system_prompt: Optional[str]) -> str:
        if system_prompt:
            return (
                f"<|system|>\n{system_prompt}<|end|>\n"
                f"<|user|>\n{prompt}<|end|>\n"
                f"<|assistant|>\n"
            )
        return f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        full_prompt = self._format_prompt(prompt, system_prompt)

        response = self.llm(
            full_prompt,
            max_tokens=self.max_tokens,
            stop=["<|end|>", "<|user|>"],
            echo=False,
        )

        latency_ms = int((time.time() - start_time) * 1000)
        content = response["choices"][0]["text"].strip()
        usage = {
            "prompt_tokens": response["usage"]["prompt_tokens"],
            "completion_tokens": response["usage"]["completion_tokens"],
            "total_tokens": response["usage"]["total_tokens"],
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "local",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        full_prompt = self._format_prompt(prompt, system_prompt)
        stream = self.llm(
            full_prompt,
            max_tokens=self.max_tokens,
            stop=["<|end|>", "<|user|>"],
            stream=True,
        )

        for chunk in stream:
            token = chunk["choices"][0]["text"]
            if token:
                yield token
