from app.core.redis import redis_client
from app.core.config import settings
from app.schemas.authorize import AuthorizeUserParams
import uuid
import json
from app.utils.logger import logger
from typing import Optional


async def store_auth_code(data: AuthorizeUserParams):
    code = str(uuid.uuid4())
    key = f"auth_code:{code}"
    response = await redis_client.setex(
        key, settings.REDIS_CACHE_EXPIRE_SECONDS, json.dumps(data.model_dump())
    )
    if not response:
        logger.error("Failed to store auth code in redis")
        return None
    return code


async def consume_auth_code(code: str) -> Optional[AuthorizeUserParams]:
    key = f"auth_code:{code}"

    raw = await redis_client.get(key)
    if not raw:
        return None

    await delete_cache(key)

    return AuthorizeUserParams(**json.loads(raw))


async def delete_cache(key: str):
    await redis_client.delete(key)


async def store_access_token(token: str, user_id: str, expire_seconds: int):
    key = f"access_token:{token}"
    await redis_client.setex(key, expire_seconds, user_id)


async def revoke_access_token(token: str):
    key = f"access_token:{token}"
    await redis_client.delete(key)


async def is_token_revoked(token: str) -> bool:
    key = f"access_token:{token}"
    return not await redis_client.exists(key)
