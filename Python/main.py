from fastapi import FastAPI
from app import generate_text
from pydantic import BaseModel

app = FastAPI(title="Learning")

class InputValue(BaseModel):
    question: str

@app.get('/')
def greet():
    return {
        "message": "Hello world! Im Sanmith"
    }

@app.post('/generate')
async def generate_res(req: InputValue):
    gemini_res = await generate_text(req.question)

    return {
        "Gemini Res": gemini_res
    }