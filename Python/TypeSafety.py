from pydantic import BaseModel, Field

class InputValue(BaseModel):
    question: str

class SafeResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    is_dangerous: bool
    confidence: float = Field(..., ge=0, le=1)

class InputOrder(BaseModel):
    amount: int
    title: str
    userId: str
    status: str

class MemoryInput(BaseModel):
    question: str
    userId: str

class RapidPayload(BaseModel):
    question: str
    userId: str
    context: str
    tool_result: str