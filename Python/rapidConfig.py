import os
from TypeSafety import RapidPayload
import httpx

async def get_rapid_res(inputPayload: RapidPayload):

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "gemini-pro-ai.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    payload = f"""
Context: {inputPayload.context}

Question: {inputPayload.question}

Tool Result: {inputPayload.tool_result}
"""

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://gemini-pro-ai.p.rapidapi.com/",
            headers=headers,
            content=payload
        )

    return res.text
