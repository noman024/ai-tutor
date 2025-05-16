import redis
from backend.app.core.config import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=getattr(settings, "REDIS_PASSWORD", None),
    decode_responses=True
)

def get_redis_client():
    return redis_client 