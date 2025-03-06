import redis
import re
from tenacity import retry, stop_after_attempt, wait_exponential
from hashlib import md5
import os


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = 6379

def redis_object():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True
        )
        # r.ping()  
    except redis.ConnectionError as r:
        print("Error: Could not connect to Redis. Make sure Redis is running!")
        exit(1)
    return r

def get_cache_key(query):
    """Generate a normalized cache key."""
    clean = re.sub(r'\s+', ' ', query).lower().strip()
    return md5(clean.encode()).hexdigest()
