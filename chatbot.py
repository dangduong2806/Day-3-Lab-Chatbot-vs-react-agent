"""
Lab 3 — Part 1: Chatbot baseline (Smart E-commerce Assistant theme).
Provider from .env: google (default) | openai | local

  python chatbot.py
  python chatbot.py --interactive
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.core.llm_provider import LLMProvider
from src.core.local_provider import validate_model_file
from src.core.provider_factory import get_llm_provider

TEST_CASES = [
    {
        "id": "simple",
        "label": "Simple Q&A (chatbot should do OK)",
        "prompt": "What is a coupon code and how do customers typically use one?",
    },
    {
        "id": "multi_step",
        "label": "Multi-step order (chatbot likely fails vs real tools)",
        "prompt": (
            "I want to buy 2 iPhones using code 'WINNER' and ship to Hanoi. "
            "What is the total price in VND? Show your calculation."
        ),
    },
]


def _resolve_local_model_path() -> str:
    raw = os.getenv(
        "LOCAL_MODEL_PATH",
        "./models/Phi-3-mini-4k-instruct-q4.gguf",
    )
    return os.path.abspath(raw)


def _validate_env(provider: str) -> None:
    if provider == "local":
        path = _resolve_local_model_path()
        try:
            validate_model_file(path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}")
            sys.exit(1)
        return

    if provider in ("google", "gemini"):
        key = os.getenv("GEMINI_API_KEY", "")
        if not key or key.startswith("your_"):
            print("Error: Set GEMINI_API_KEY in .env (or use DEFAULT_PROVIDER=local).")
            sys.exit(1)
        return

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or key.startswith("your_"):
            print("Error: Set OPENAI_API_KEY in .env.")
            sys.exit(1)
        return

    print(f"Error: Unknown DEFAULT_PROVIDER='{provider}'. Use local, google, or openai.")
    sys.exit(1)


class EcommerceChatbot:
    """Baseline chatbot that answers directly without calling tools."""

    SYSTEM_PROMPT = """You are a baseline Smart E-commerce Assistant for an electronics store in Vietnam.
Answer in the same language as the user.

You do not have access to tools in this baseline version.
For general questions, answer helpfully and concisely.
For exact inventory, pricing, discounts, shipping, or multi-step totals, explain that a tool-based agent is needed for reliable live calculations. If the prompt provides all required numbers, you may calculate from those numbers.
"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def chat(self, user_input: str) -> str:
        result = self.llm.generate(user_input, system_prompt=self.SYSTEM_PROMPT)
        return result.get("content", "").strip()


def run_demo(chatbot: EcommerceChatbot) -> None:
    print("=" * 60)
    print("Lab 3 — Chatbot Baseline (no tools)")
    print("=" * 60)

    for case in TEST_CASES:
        print(f"\n[{case['id']}] {case['label']}")
        print(f"User: {case['prompt']}\n")
        print("Assistant: ", end="", flush=True)
        reply = chatbot.chat(case["prompt"])
        print(reply)
        print("-" * 60)


def run_interactive(chatbot: EcommerceChatbot) -> None:
    print("Interactive mode. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        print("\nAssistant:\n", end="", flush=True)
        print(chatbot.chat(user_input))
        print()


def main() -> None:
    load_dotenv()

    provider = os.getenv("DEFAULT_PROVIDER", "google").lower()
    _validate_env(provider)

    if provider == "local":
        print(f"Loading provider '{provider}' (first run may take a minute)...\n", flush=True)
    else:
        print(f"Loading provider '{provider}'...\n", flush=True)
    llm = get_llm_provider()
    chatbot = EcommerceChatbot(llm)

    label = provider.upper()
    if provider == "local":
        label = f"LOCAL CPU | {llm.model_name}"
    elif provider in ("google", "gemini"):
        label = f"Gemini | {llm.model_name}"
    print(f"Provider: {label}\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive(chatbot)
    else:
        run_demo(chatbot)
        print("\nTip: python chatbot.py --interactive")
        print("Logs: logs/")


if __name__ == "__main__":
    main()
