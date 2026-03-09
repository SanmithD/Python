from pydantic import BaseModel
from app.util import build_context

class ChatRequest(BaseModel):
    session_id: str
    message: str


def get_full_prompt(query, history, is_greeting=False, is_tech=False):

    if is_greeting:
        system_instruction = "You are a helpful AI assistant. Greet the user briefly."
        context_text = ""
    else:
        system_instruction = (
            "You are a technical assistant. "
            "Use the provided knowledge to answer. "
            "If knowledge is not relevant, use general knowledge. "
            "Keep answers to 2 sentences."
        )

        if is_tech:
            context_data = build_context(query)
            context_text = context_data["context"]
        else:
            context_text = ""
    
    # 2. Start building prompt
    prompt = f"System: {system_instruction}\n\n"

    # 3. Inject context
    if context_text:
        prompt += f"Context:\n{context_text}\n\n"

    # 4. Inject last 6 messages
    recent_history = history[-6:]

    for msg in recent_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"

    # 5. Add current query
    prompt += f"User: {query}\nAssistant:"

    return prompt

def tool_router_prompt(query):
    return f"""
You are an AI agent that decides if a tool should be used.

TOOLS AVAILABLE:
get_current_time → returns current time
calculate → solves math expressions

Rules:
- Only respond with one line
- If a tool is needed use:
TOOL: tool_name | INPUT: value

- If no tool is needed respond:
NO_TOOL

User query:
{query}
"""