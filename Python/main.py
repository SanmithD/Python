# venv\Scripts\activate

from app import generate_text, client, allow, decide_tool, explain_by_ai, safe_generate, save_memory, explain_with_memory, get_memory, get_tool_response
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
import asyncio
import json
from functools import partial
from SYSTEM_INSTRACTION import SYSTEM_PROMPT, AGENT_PROMPT
from TypeSafety import SafeResponse, InputValue, InputOrder, MemoryInput, RapidPayload
from Tools import get_current_time, check_water_safety, run_tool
from db import insertDoc
import time
from rapidConfig import get_rapid_res
from rag import search_knowledge
from radisConfig import get_memory_from_redis, save_memory_in_redis, track_usage

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

@app.post('/insert')
async def insertUserOrder(orderInput: InputOrder, request: Request) -> dict:
    if not orderInput:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    res = insertDoc(orderInput)

    if not res:
        raise HTTPException(status_code=400, detail="Fail to insert data")
    
    return {
        "message": res
    }

COMBINED_PROMPT = """You are a helpful AI assistant. Analyze the user's question and respond.

Instructions:
1. First, determine if you need to use a tool or knowledge base
2. Then provide a natural, helpful response

Respond in this JSON format:
{{
    "step": "tool" | "knowledge" | "direct",
    "tool_name": "tool name if step is tool, else null",
    "response": "your natural language response"
}}

Conversation History:
{history}

Available Knowledge Context:
{knowledge}

User Question: {question}
"""

@app.post("/memory_model")
async def get_memory_res(req: MemoryInput, request: Request):
    start_time = time.time()
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    print('question', req.question , req.userId)

    loop = asyncio.get_running_loop()
    history = get_memory(req.userId)

    knowledge_task = await loop.run_in_executor(
        None,
        search_knowledge,
        req.question
    )

    knowledge_results = knowledge_task

    context = "\n".join(
        f"{msg['role']} : {msg['content']}" for msg in history
    )

    knowledge_text = "\n".join(knowledge_results) if knowledge_results else "No relevant knowledge found"
    
    # ✅ SINGLE API CALL instead of 3
    prompt = COMBINED_PROMPT.format(
        history=context,
        knowledge=knowledge_text,
        question=req.question
    )

    res = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-3-flash-preview",  # ✅ Use stable model, not preview
            contents=prompt
        )
    )

    try:
        data = json.loads(res.text)
        final_answer = data.get("response", res.text)
    except json.JSONDecodeError:
        data = {"raw": res.text}
        final_answer = res.text
    
    # Handle tool execution if needed
    if data.get("step") == "tool" and data.get("tool_name"):
        tool_result = await run_tool(data["tool_name"], req.question)
        # Make follow-up call only if tool was used
        final_answer = await get_tool_response(req.question, tool_result, context)

    save_memory(req.userId, "user", req.question)
    save_memory(req.userId, "assistant", final_answer)

    print(f"Response time: {time.time() - start_time:.2f}s")
    
    return {
        "data": data,
        "AI_Res": final_answer
    }

@app.post('/rapid')
async def rapidTestRes(req: MemoryInput, request: Request):

    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    loop = asyncio.get_running_loop()

    history = get_memory(req.userId)

    knowledge_task = await loop.run_in_executor(
        None,
        search_knowledge,
        req.question
    )

    knowledge_results = knowledge_task

    context = "\n".join(
        f"{msg['role']} : {msg['content']}" for msg in history
    )

    knowledge_text = "\n".join(knowledge_results) if knowledge_results else "No relevant knowledge found"
    
    # ✅ SINGLE API CALL instead of 3
    prompt = COMBINED_PROMPT.format(
        history=context,
        knowledge=knowledge_text,
        question=req.question
    )

    res = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-3-flash-preview",  
            contents=prompt
        )
    )

    try:
        data = json.loads(res.text)
        final_answer = data.get("response", res.text)
    except json.JSONDecodeError:
        data = {"raw": res.text}
        final_answer = res.text
    
    # Handle tool execution if needed
    if data.get("step") == "tool" and data.get("tool_name"):
        tool_result = await run_tool(data["tool_name"], req.question)
        # Make follow-up call only if tool was used
        final_answer = await get_rapid_res(req.question, req.userId, context, tool_result)

    save_memory(req.userId, "user", req.question)
    save_memory(req.userId, "assistant", final_answer)

    return {
        "final_answer": final_answer
    }

@app.post('/save_in_redis')
async def get_response_from_redis(req: MemoryInput, request: Request, bg: BackgroundTasks):

    # Rate limit
    ip = request.client.host

    if not allow(ip):
        raise HTTPException(status_code=429, detail="Too many request")
    
    # Load Redis Memory
    history = get_memory_from_redis(req.userId)
    loop = asyncio.get_running_loop()

    context = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in history
    )

    # Agent Decision    
    agent_prompt = AGENT_PROMPT.format(
        history = context,
        question = req.question
    )

    decision_res  = await loop.run_in_executor(
        None,
        partial(
            client.models.generate_content,
            model="gemini-2.0-flash",  
            contents=agent_prompt
        )
    )

    try:
        decision = json.loads(decision_res.text)
    except json.JSONDecodeError:
        decision = {"step": "answer"}

    step = decision.get("step")

    tool_result = None
    knowledge_result = None

    # Tool / RAG / Knowledge
    if step == "tool" and decision.get("tool_name"):

        tool_result = await run_tool(
            decision["tool_name"],
            req.question
        )

    elif step == "knowledge":
        knowledge_result = await loop.run_in_executor(
            None, 
            search_knowledge,
            req.question
        )

    # Stream Response
    
    async def stream():

        prompt = COMBINED_PROMPT.format(
            history=context,
            knowledge="\n".join(knowledge_result) if knowledge_result else "No relevant question found",
            tool_data=tool_result if tool_result else "None",
            question=req.question
        )

        payload = RapidPayload(
            question=req.question,
            context=prompt,
            tool_result=tool_result
        )

        full_text = await get_rapid_res(payload)

        yield full_text

        # Token Tracking (fake estimate)
        track_usage(req.userId, len(full_text.split()))

        # Save Memory
        save_memory_in_redis(req.userId, "user", req.question)
        save_memory_in_redis(req.userId, "assistant", full_text)

        if len(req.question) > 200:
            bg.add_task(search_knowledge, req.question)

    return StreamingResponse(stream(), media_type="text/plain")
    