from pydantic import BaseModel, Field

class InputValue(BaseModel):
    question: str

class SafeResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    is_dangerous: bool
    confidence: float = Field(..., ge=0, le=1)