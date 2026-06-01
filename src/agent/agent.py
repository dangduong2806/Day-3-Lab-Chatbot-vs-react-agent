from typing import List, Dict, Any, Optional

from src.agent.parsers import parse_action, parse_final_answer
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

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
- Action syntax: check_stock(item_name="iPhone"), get_discount(coupon_code="WINNER"), calc_shipping(weight_kg=0.7, destination="Hanoi")
- For order totals: check_stock → get_discount (if coupon) → calc_shipping (weight = unit weight × quantity)
- If a tool returns Error, fix arguments or explain in Final Answer
- Do NOT invent Observation lines — only the system provides them
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
            # TODO: Generate LLM response
            # result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            # TODO: Parse Thought/Action from result
            
            # TODO: If Action found -> Call tool -> Append Observation
            
            # TODO: If Final Answer found -> Break loop
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
