from app import generate_text, client, allow, decide_tool
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ValidationError
import asyncio
import time
import json
from functools import partial
from SYSTEM_INSTRACTION import SYSTEM_PROMPT

app = FastAPI(title="Learning")

class InputValue(BaseModel):
    question: str

class SafeResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    is_dangerous: bool
    confidence: float = Field(..., ge=0, le=1)

def get_current_time():
    return {"time": time.time()}

def check_water_safety():
    return {
        "is_dangerous": True,
        "reason": "Can cause drowning or intoxication"
    }

@app.get('/')
def greet():
    return {
        "message": "Hello world! Im Sanmith"
    }

@app.post('/generate')
async def generate_res(req: InputValue, request: Request):
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")

    gemini_res = await generate_text(req.question)

    print('Res', gemini_res)
    return {
        "Gemini Res": gemini_res
    }

@app.post('/stream')
async def generate_stream(req: InputValue, request: Request):
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")

    async def stream():
        loop = asyncio.get_event_loop()

        stream = await loop.run_in_executor(
            None,
            partial(
                client.models.generate_content_stream,
                model="gemini-3-flash-preview",
                contents=req.question,
            )
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text
    
    return StreamingResponse(stream(), media_type="text/plain")


@app.post('/system')
async def generate_system(req: InputValue, request: Request) -> SafeResponse:
    ip = request.client.host
    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")

    loop = asyncio.get_event_loop()

    stream = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content_stream,
            model="gemini-3-flash-preview",
            contents=f"{SYSTEM_PROMPT}\n\nUser: {req.question}",
        )
    )

    chunks = []
    for chunk in stream:
        if chunk.text:
            chunks.append(chunk.text)

    raw = "".join(chunks).strip()

    try:
        data = json.loads(raw)
        return SafeResponse(**data)
    except (json.JSONDecodeError, ValidationError):
        return SafeResponse(
            answer="Model failed to respond correctly",
            is_dangerous=False,
            confidence=0.0
        )
    

@app.post('/tool')
async def get_data_from_tool(req: InputValue, request: Request):
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    decision = await decide_tool(req.question)

    try:
        data = json.loads(decision)
    except json.JSONDecodeError:
        return {"error": "Invalid tool decision from model"}

    tool = data.get("tool")

    if tool == "get_current_time":
        result = get_current_time()
    
    elif tool == "check_water_safety":
        result = check_water_safety()
    
    else:
        result = { "message": "No tool needed" }
    
    return {
        "tool_used": tool,
        "result": result
    }