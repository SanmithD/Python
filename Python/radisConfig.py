import os
import redis 
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

def save_memory_in_redis(userId, role, message):

    key = f"chat : {userId}"

    redis_client.rpush(
        key,
        json.dumps({
            "role": role,
            "content": message
        })
    )

    redis_client.ltrim(key, -10, -1) # save only latest 10 messages to prevent token


def get_memory_from_redis(userId):

    key = f"chat: {userId}"

    messages = redis_client.lrange(key, 0, -1)

    return [json.loads(m) for m in messages]

def track_usage(user_id, tokens):

    redis_client.incrby(f"usage:{user_id}", tokens)


