import redis

redis_client = redis.Redis(
    host="localhost", # Docker cannot access localhost directly
    port=6379,
    decode_responses=True
)

