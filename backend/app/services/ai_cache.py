from backend.app.utils.redis_client import get_redis_client

CACHE_EXPIRE_SECONDS = 3600  # 1 hour

redis_client = get_redis_client()

def get_cached_answer(question: str) -> str | None:
    return redis_client.get(f"ai_answer:{question}")

def set_cached_answer(question: str, answer: str):
    redis_client.set(f"ai_answer:{question}", answer, ex=CACHE_EXPIRE_SECONDS) 