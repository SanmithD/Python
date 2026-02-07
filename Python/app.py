from google import genai
from google.genai import types
from functools import partial
import os
import asyncio
from dotenv import load_dotenv
from time import time
from collections import defaultdict
from SYSTEM_INSTRACTION import TOOLS_PROMPT

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=30000,
    )
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

async def safe_generate(fn, retries=5):
    for i in range(retries):
        try:
            return await fn()
        except Exception as e:
            print("Gemini Faild", e)

            if i == retries -1:
                return "AI server is temporally busy"
            
            await asyncio.sleep(1.5)

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

async def decide_tool(question: str):
    loop = asyncio.get_running_loop()

    response = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-3-flash-preview",
            contents=f"{TOOLS_PROMPT}\n\nUser: {question}"
        )
    )

    return response.text

async def explain_by_ai(question: str, tool_result):

    loop = asyncio.get_running_loop()

    res = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-3-flash-preview",
            contents=f"""
User question: {question}
Database result: {tool_result}

Explain clearly and summarize.
"""
        )
    )

    return res.text

QUERY_CACHE = {}
CACHE_MEMORY = {}

def save_memory(user_id, role, message):
    if user_id not in CACHE_MEMORY:
        CACHE_MEMORY[user_id] = []

    CACHE_MEMORY[user_id].append({
        "role": role,
        "content": message
    })
    if len(CACHE_MEMORY[user_id]) > 20:
        CACHE_MEMORY[user_id] = CACHE_MEMORY[user_id][-20:]

def get_memory(user_id: str, limit=6):
    return CACHE_MEMORY.get(user_id, [])[-limit:]


async def explain_with_memory(user_id: str, question: str, tool_result):

    history = get_memory(user_id)

    context = "\n".join(
        f"{msg['role']} : {msg['content']}" for msg in history
    )

    loop = asyncio.get_running_loop()

    res = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-3-flash-preview",
            contents=f"""Conversation History {context}
            User question: 
            {question}

tool result:
{tool_result}

respond naturally.
            """
        )
    )

    
    return res.text


async def get_tool_response(question: str, tool_result, context: str) -> str:
    """Only called when tool is actually used"""
    loop = asyncio.get_running_loop()
    
    res = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-2.0-flash",
            contents=f"""Context: {context}
Question: {question}
Tool Result: {tool_result}

Provide a natural response based on the tool result."""
        )
    )
    return res.text