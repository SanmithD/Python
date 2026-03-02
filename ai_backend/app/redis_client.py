import redis

r = redis.Redis(host="127.0.0.1", port=6379)
print(r.ping())

redis_client = redis.Redis(
    host="localhost", # Docker cannot access localhost directly
    port=6379,
    decode_responses=True
)

