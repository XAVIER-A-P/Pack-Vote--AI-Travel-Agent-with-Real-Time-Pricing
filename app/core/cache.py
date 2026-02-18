import os
import json
import redis
import functools
from typing import Callable

# Initialize Redis Connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url, decode_responses=True)

def cache_result(ttl_seconds: int = 3600):
    """
    Decorator to cache function results in Redis.
    ttl_seconds: Time to live (default 1 hour)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Generate a unique Cache Key based on function name & arguments
            # Create a string like "flight_search:JFK:LHR:2026-05-15"
            arg_str = ":".join([str(arg) for arg in args if arg is not None])
            kwarg_str = ":".join([f"{k}={v}" for k, v in kwargs.items()])
            cache_key = f"{func.__name__}:{arg_str}:{kwarg_str}"

            # 2. Check Redis
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    print(f"⚡ Cache Hit: {cache_key}")
                    return json.loads(cached_data) # Return cached JSON
            except redis.RedisError as e:
                print(f"⚠️ Redis Error: {e}") # Fallback to live API if Redis fails

            # 3. Call actual function (API Request)
            print(f"🌍 API Call: {cache_key}")
            result = func(*args, **kwargs)

            # 4. Save to Redis
            try:
                # Store as JSON string
                redis_client.setex(
                    name=cache_key,
                    time=ttl_seconds,
                    value=json.dumps(result)
                )
            except redis.RedisError:
                pass

            return result
        return wrapper
    return decorator