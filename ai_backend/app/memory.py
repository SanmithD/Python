from app.redis_client import redis_client
import json

def save_messages(session_id, messages):

    redis_client.rpush(session_id, json.dumps(messages))
    redis_client.expire(session_id, 3600) # session will expire after 1 hour

def get_messages(session_id):

    messages = redis_client.lrange(session_id, 0, -1)

    return [json.loads(msg) for msg in messages]

def in_memory_questions(message: str): 
    keywords = [
        "last question",
        "previous question",
        "what did i ask",
        "repeat my question",
        "earlier"
    ]

    message = message.lower()

    return any(k in message for k in keywords)

# AI Models do not saves the last conversations
# Redis saves the conversation messages temporally