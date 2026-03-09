def parse_tool_response(response):

    if not response:
        return None, None
    
    print("Response", response)
    
    tool_part = response.replace("TOOL:", "").strip()

    print("Tool Part: ", tool_part)
    
    if "INPUT:" in tool_part:
        parts = tool_part.split("INPUT:")
        tool_name = parts[0].strip()
        tool_input = parts[1].strip() if len(parts) > 1 else None
    else:
        tool_name = tool_part
        tool_input = None
    
    return tool_name, tool_input

    