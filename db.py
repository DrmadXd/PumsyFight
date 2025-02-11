import redis

# Upstash Redis Configuration
REDIS_HOST = "picked-bengal-10585.upstash.io"
REDIS_PORT = 6379
REDIS_PASSWORD = "ASlZAAIjcDFlYTVjZDgwZWIwNzc0OWU0YmU4OGExOTViYTNmMTNmM3AxMA"

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True,  # Upstash requires SSL
    decode_responses=True
)

# Get user data
def get_user(user_id):
    key = f"user:{user_id}"
    pussy_size = redis_client.hget(key, "pussy_size")
    last_grow = redis_client.hget(key, "last_grow")

    if pussy_size is None:
        return None  # User not found
    return int(pussy_size), int(last_grow or 0)

# Update user size
def update_user(user_id, size_change):
    key = f"user:{user_id}"
    current_size = int(redis_client.hget(key, "pussy_size") or 5)
    new_size = max(0, current_size + size_change)

    redis_client.hset(key, "pussy_size", new_size)
    return new_size

# Update last grow time
def update_grow_time(user_id, timestamp):
    key = f"user:{user_id}"
    redis_client.hset(key, "last_grow", int(timestamp))