from fastapi import FastAPI, HTTPException
from app.ollama_client import generate_response
from app.memory import save_messages, get_messages
from app.safety import ChatRequest
from app.knowledge_loader import load_knowledge
from app.vector_db import search_document
from app.intent import small_greet, is_tech_message
from app.redis_client import redis_client
from app.pdf_loader import load_all_pdf
import traceback

app = FastAPI(title="AI Learning by Ollama")

# Load Knowledege
@app.on_event("startup")
def startup():
    load_all_pdf()

@app.post('/clear_session/{session_id}')
def clear_session(session_id: str):

    print(session_id)
    redis_client.delete(session_id)

    return {
        "message": f"Session {session_id} is cleared"
    }

@app.post('/chat')
def chat(request: ChatRequest):
    try:
        history = get_messages(request.session_id)
        
        # Check if it's a greeting/introduction
        is_greeting = small_greet(request.message)

        is_tech = is_tech_message(request.message)

        knowledge_results = []

        if is_tech:    
            # Search in vector db only for non-greetings
            knowledge_results = search_document(request.message)

        # Build prompt based on context
        if is_greeting:
            system_instruction = "You are a helpful AI assistant. Greet the user briefly."
        else:
            system_instruction = (
                "You are a technical assistant. Use the provided knowledge to answer. "
                "If the knowledge is not relevant, use your general knowledge. "
                "Keep answers to 2 sentences."
            )
        
        # 3. ASSEMBLE FINAL PROMPT
        full_prompt = f"System: {system_instruction}\n\n"

        if knowledge_results:
            full_prompt += "Context Knowledge:\n"
            for k in knowledge_results:
                full_prompt += f"- {k['text']}\n"
            full_prompt += "\n"

        # Only include recent history (limit to last 6 messages)
        recent_history = history[-6:]
        
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n"

        # 5. ADD CURRENT QUESTION
        full_prompt += f"User: {request.message}\nAssistant:"

        ai_response = generate_response(full_prompt)

        # Clean up the response (sometimes Ollama repeats "Assistant:" in the string)
        ai_response = ai_response.replace("Assistant:", "").strip()

        save_messages(request.session_id, {"role": "user", "content": request.message})
        save_messages(request.session_id, {"role": "assistant", "content": ai_response})

        return {"response": ai_response}

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

   