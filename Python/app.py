from google import genai
from functools import partial
import os
import asyncio
from dotenv import load_dotenv
from time import time
from collections import defaultdict

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

if not client:
    print('error', client)

CACHE = {}
TTL = 60 * 5
RATE_LIMIT = defaultdict(list)

def allow(ip: str):
    now = time()

    RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < 60]
    if len(RATE_LIMIT[ip]) > 10:
        return False
    RATE_LIMIT[ip].append(now)
    return True

async def generate_text(input: str) -> str:

    now = time()

    if input in CACHE:
        cached, ts = CACHE[input]
        if now - ts < TTL:
            return cached
        
    if not input or not input.strip().lower():
        return "Empty input"
    
    loop = asyncio.get_running_loop()
    
    response = await asyncio.wait_for(
        loop.run_in_executor(
            None,
            partial(
                client.models.generate_content,
                model="gemini-3-flash-preview",
                contents=input,
            )
        ),
        timeout=8
    )

    CACHE[input] = (response.text, now)
    return response.text
