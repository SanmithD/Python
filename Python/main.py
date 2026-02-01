from app import generate_text, client, allow
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from functools import partial

app = FastAPI(title="Learning")

class InputValue(BaseModel):
    question: str

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