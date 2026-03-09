from app.ollama_client import generate_response
from app.parse_tool_res import parse_tool_response
from app.tool_registry import TOOLS
from app.safety import tool_router_prompt

def agent_run(query):

    print("Query", query)

    decision = generate_response(tool_router_prompt(query))

    print("Decision", decision)
    tool_name, tool_input = parse_tool_response(decision)

    print("Tool Name", tool_name)

    if tool_name and tool_name in TOOLS:
        if tool_input:
            result = TOOLS[tool_name](tool_input)
        else:
            result = TOOLS[tool_name]()

        final_prompt = f"""
Tool result:
{result}

Use this result to answer the user clearly.

User:
{query}
"""
        return generate_response(final_prompt)
    return generate_response(query)