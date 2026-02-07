import os
import http.client
from TypeSafety import RapidPayload

async def get_rapid_res(inputPayload: RapidPayload):

    conn = http.client.HTTPSConnection("gemini-pro-ai.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "gemini-pro-ai.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    payload = f""" 
Context: {inputPayload.context}

question: { inputPayload.question }

Tool Result: { inputPayload.tool_result }
"""

    conn.request("POST", "/", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")