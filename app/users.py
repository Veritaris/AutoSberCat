from typing import List

import aioredis

from app.config import settings
from app.models import SessionData
import redis as sync_redis

redis = aioredis.from_url(
    f"redis://{settings.redis_connection_string}",
    encoding="utf-8",
    decode_responses=True
)

redis_conn = sync_redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    username=settings.redis_user,
    password=settings.redis_pass
)


async def add_user(user: SessionData) -> None:
    await redis.sadd(
        settings.sbercat_redis_table,
        user.sbercat_token
    )


async def delete_user(user: SessionData) -> None:
    if user is None:
        return

    await redis.srem(
        settings.sbercat_redis_table,
        user.sbercat_token
    )


async def get_users_for_auto() -> List[str]:
    users_raw = await redis.smembers(settings.sbercat_redis_table)
    if users_raw is None:
        return []
    return [token for token in users_raw]


def get_users_for_auto_sync() -> List[str]:
    users_raw = redis_conn.smembers(settings.sbercat_redis_table)
    if users_raw is None:
        return []
    return [token for token in users_raw]
