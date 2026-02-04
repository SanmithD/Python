# venv\Scripts\activate

from app import generate_text, client, allow, decide_tool, explain_by_ai, safe_generate
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
import asyncio
import json
from functools import partial
from SYSTEM_INSTRACTION import SYSTEM_PROMPT
from TypeSafety import SafeResponse, InputValue
from Tools import get_current_time, check_water_safety, run_tool

app = FastAPI(title="Learning")

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

@app.post("/db_tool")
async def get_res_from_db(req: InputValue, request: Request):
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    decision = await decide_tool(req.question)

    try:
        data = json.loads(decision)
    except:
        return { "error": "Model decision invalid" }

    tool = data.get("tool")

    user_id = "u123"

    tool_result = await run_tool(tool, user_id)
    final_answer = await safe_generate(
        lambda: explain_by_ai(req.question, tool_result)
    )

    return {
        "data": tool_result,
        "explanation": final_answer
    }