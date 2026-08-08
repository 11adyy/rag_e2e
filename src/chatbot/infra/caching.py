import unicodedata
import hashlib
from src.chatbot.core.config import get_settings
import redis
import json
settings = get_settings()

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

def normalize_and_hash_for_cache(string: str):
    string = string.strip().lower()
    string = unicodedata.normalize("NFKD", string).encode("ASCII", "ignore").decode("utf-8")
    normalized_hash = hashlib.sha256(string.encode("utf-8")).hexdigest()
    return normalized_hash

def get_cache(key_hash):
    value = r.get(key_hash)

    if value is None:
        return None

    return json.loads(value)


def set_cache(key_hash, value):
    r_set = r.set(
        key_hash,
        json.dumps(value, ensure_ascii=False),
    )

    return r_set