from app.core.radis import redis_client
from app.core.config import settings
from app.schemas.authorize import AuthorizeParams
import uuid
import json


async def store_auth_code(data: AuthorizeParams) -> str:
    code = str(uuid.uuid4())
    key = f"auth_code:{code}"
    await redis_client.setex(
        key, settings.REDIS_CACHE_EXPIRE_SECONDS, json.dumps(data.model_dump())
    )
    return code


async def consume_auth_code(code: str):
    key = f"auth_code:{code}"

    raw = await redis_client.get(key)
    if not raw:
        return None

    await delete_cache(key)

    return json.loads(raw)


async def delete_cache(key: str):
    await redis_client.delete(key)
