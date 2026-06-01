import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

import ast

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.
        """

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # TODO: Generate LLM response
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            # TODO: Parse Thought/Action from result
            content = result.get("content", "")

            logger.log_event("AGENT_STEP", {
                "step": steps + 1,
                "llm_output": content,
                "usage": result.get("usage", {}),
                "latency_ms": result.get("latency_ms", 0),
            })

            final_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL)
            if final_match:
                final_answer = final_match.group(1).strip()
                logger.log_event("AGENT_END", {"steps": steps + 1})
                return final_answer
            
            action_match = re.search(
                r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)",
                content,
                re.DOTALL
            )
            
            # TODO: If Action found -> Call tool -> Append Observation
            if action_match:
                tool_name = action_match.group(1).strip()
                args = action_match.group(2).strip()

                observation = self._execute_tool(tool_name, args)

                current_prompt = f"""
    {current_prompt}

    {content}

    Observation: {observation}
    """
            else:
                current_prompt = f"""
    {current_prompt}

    {content}

    Observation: No valid action found. Continue using the required ReAct format.
    """
            # TODO: If Final Answer found -> Break loop
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "I could not complete the task within the maximum number of steps."
        return "Not implemented. Fill in the TODOs!"

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                tool_function = tool.get("function")

                if tool_function is None:
                    return f"Tool {tool_name} has no function configured."
                
                try:
                    parsed_call = ast.parse(f"tool_call({args})", mode="eval").body

                    positional_args = [
                        ast.literal_eval(arg)
                        for arg in parsed_call.args
                    ]

                    keyword_args = {
                        keyword.arg: ast.literal_eval(keyword.value)
                        for keyword in parsed_call.keywords
                    }

                    result = tool_function(*positional_args, **keyword_args)

                    logger.log_event("TOOL_CALL", {
                        "tool_name": tool_name,
                        "args": args,
                        "result": result,
                    })

                    return str(result)
                except Exception as exc:
                    return f"Tool {tool_name} failed: {exc}"
                return f"Result of {tool_name}"
        return f"Tool {tool_name} not found."
