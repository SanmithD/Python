from fastapi import FastAPI, HTTPException
from app.ollama_client import generate_response
from app.memory import save_messages, get_messages, in_memory_questions
from app.safety import ChatRequest, get_full_prompt
from app.intent import small_greet, is_tech_message
from app.redis_client import redis_client
from app.pdf_loader import load_all_pdf
import traceback

app = FastAPI(title="AI Learning by Ollama")

# Load Knowledege
# @app.on_event("startup")
# def startup():
#     if collection.count_documents({}) == 0:
#         load_all_pdf()

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
        
        if in_memory_questions(request.message):
            if history:
                last_user_msg = [m for m in history if m["role"] == "user"]
                if last_user_msg:
                    return {
                        "response": last_user_msg[-1]["content"]
                    }
            return {
                "response": "You haven't asked anything yet."
            }

        # Check if it's a greeting/introduction 
        is_greeting = small_greet(request.message)

        is_tech = is_tech_message(request.message)

        # 5. ADD CURRENT QUESTION
        full_prompt = get_full_prompt(
            query=request.message,
            history=history,
            is_greeting=is_greeting,
            is_tech=is_tech
        )

        ai_response = generate_response(full_prompt)

        # Clean up the response (sometimes Ollama repeats "Assistant:" in the string)
        ai_response = ai_response.replace("Assistant:", "").strip()

        save_messages(request.session_id, {"role": "user", "content": request.message})
        save_messages(request.session_id, {"role": "assistant", "content": ai_response})

        return {"response": ai_response.split("\n")}

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

   