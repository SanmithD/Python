from google import genai
from functools import partial
import os
import asyncio

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

if not client:
    print('error', client)

async def generate_text(input: str) -> str:

    if not input or not input.strip():
        return "Empty input"
    
    loop = asyncio.get_event_loop()
    
    response = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content(
                model="gemini-1.5-flash",
                contents=input,
            )
        )
    )

    return response.text