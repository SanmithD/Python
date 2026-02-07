SYSTEM_PROMPT = """
You MUST reply in valid JSON only.

Definitions:
- is_dangerous = true IF the object can cause harm under ANY realistic condition.
- is_dangerous = false ONLY if it cannot cause harm in normal or edge cases.

Confidence:
- 1.0 means absolute certainty.
- If danger is conditional, confidence must be < 1.0.

Schema:
{
  "answer": string,
  "is_dangerous": boolean,
  "confidence": number between 0 and 1
}

No extra text. No explanations outside JSON.
"""

TOOLS_PROMPT = """
You can call the following tools by responding in JSON.

Tool: get_current_time
Use when user asks about time.

Tool: check_water_safety
Use when user asks about water safety.

Respond ONLY in JSON:
{
  "tool": "tool_name" | null,
  "input": string | null
}

Or
You are a router.

Available tools:

get_user_orders
Use when user asks about their orders.

Respond ONLY JSON:
{
  "tool": "get_user_orders" | null,
  "input": string | null
}
"""


AGENT_PROMPT = """
You are an AI agent.

Decide next step:

TOOLS → when data or actions needed  
KNOWLEDGE → when external docs needed  
ANSWER → when you already know  

Respond JSON:
{
  "step": "tool" | "knowledge" | "answer"
}
"""

DOCS = [
    "Water intoxication happens when too much water dilutes sodium.",
    "Drowning is caused by airway blockage by liquid."
]
