from typing import List, Dict, Any, Optional

from src.agent.parsers import parse_action, parse_final_answer
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ReActAgent:
    """
    ReAct agent: Thought -> Action -> Observation loop until Final Answer.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history: List[str] = []
        self._tool_map = {t["name"]: t for t in tools}

    def get_system_prompt(self) -> str:
        tool_lines = []
        for t in self.tools:
            params = ", ".join(f'{k}="{v}"' for k, v in t["parameters"].items())
            tool_lines.append(f"- {t['name']}({params}): {t['description']}")

        tools_block = "\n".join(tool_lines)
        tool_names = ", ".join(t["name"] for t in self.tools)

        return f"""You are a Smart E-commerce Assistant for an electronics store in Vietnam.
Answer in the same language as the user (Vietnamese or English).

You MUST solve multi-step order questions by calling tools — do not guess prices or stock.

Available tools:
{tools_block}

Respond using EXACTLY this format (one step at a time):

Thought: <brief reasoning>
Action: tool_name(arg_name="value", ...)

After each Action you will receive:
Observation: <tool result>

Repeat Thought/Action until you have enough data, then end with:

Final Answer: <clear answer with numbers in VND if applicable>

Rules:
- Only use these tools: {tool_names}
- Action syntax examples: check_stock(item_name="iPhone"), get_discount(coupon_code="WINNER"), calc_shipping(weight=0.7, destination="Hanoi"), reserve_item(item_name="MacBook Air M3", quantity=1, customer_name="Nguyen Van A"), track_order(order_id="ORD-1002"), calculate_installment(amount_vnd=28990000, months=6)
- For order totals: check_stock → get_discount (if coupon) → calc_shipping (weight = unit weight × quantity)
- For reservations: check_stock first, then reserve_item only if the user explicitly asks to reserve or hold an item
- For order tracking: use track_order when the user provides an order ID
- For installments: check_stock first if the user names a product, then calculate_installment using the price or discounted amount
- Do NOT invent missing arguments such as destination, coupon code, customer name, quantity, order ID, or months; ask for the missing information in Final Answer
- If a tool returns Error, fix arguments or explain in Final Answer
- Do NOT invent Observation lines — only the system provides them
- If you output an Action, stop immediately after that Action and wait for the Observation before writing Final Answer
- One Action per turn

Example:
Thought: I need the iPhone unit price and weight first.
Action: check_stock(item_name="iPhone")
"""

    def _build_prompt(self, user_input: str) -> str:
        parts = [f"User question: {user_input}"]
        if self.history:
            parts.append("\n".join(self.history))
        parts.append("What is your next step?")
        return "\n\n".join(parts)

    def run(self, user_input: str) -> str:
        logger.log_event(
            "AGENT_START",
            {"input": user_input, "model": self.llm.model_name, "max_steps": self.max_steps},
        )

        self.history = []
        steps = 0
        final_answer: Optional[str] = None

        while steps < self.max_steps:
            current_prompt = self._build_prompt(user_input)
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = result.get("content", "")

            logger.log_event("AGENT_STEP", {
                "step": steps + 1,
                "llm_output": content,
                "usage": result.get("usage", {}),
                "latency_ms": result.get("latency_ms", 0),
            })

            self.history.append(content)

            action = parse_action(content)
            if action:
                tool_name, kwargs = action
                observation = self._execute_tool(tool_name, kwargs)
                self.history.append(f"Observation: {observation}")
            else:
                final_answer = parse_final_answer(content)
                if final_answer:
                    logger.log_event("AGENT_END", {"steps": steps + 1})
                    return final_answer

                self.history.append(
                    "Observation: No valid action found. Continue using the required ReAct format."
                )

            steps += 1

        logger.log_event("AGENT_END", {"steps": steps})
        return "I could not complete the task within the maximum number of steps."

    def _execute_tool(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """
        Helper method to execute tools by name.
        """
        tool = self._tool_map.get(tool_name)
        if not tool:
            return f"Tool {tool_name} not found."

        tool_function = tool.get("function")
        if tool_function is None:
            return f"Tool {tool_name} has no function configured."

        try:
            result = tool_function(**kwargs)
            logger.log_event("TOOL_CALL", {
                "tool_name": tool_name,
                "args": kwargs,
                "result": result,
            })
            return str(result)
        except Exception as exc:
            return f"Tool {tool_name} failed: {exc}"

        return f"Tool {tool_name} not found."
