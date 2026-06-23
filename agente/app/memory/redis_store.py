import json

from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage
from redis.asyncio import Redis

from app.core.config import settings

model_messages_adapter: TypeAdapter[list[ModelMessage]] = TypeAdapter(list[ModelMessage])


class RedisModelMessageStore:
    def __init__(self, redis_client: Redis, ttl: int = settings.redis_session_ttl):
        self.redis = redis_client
        self.ttl = ttl

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    async def get_messages(self, session_id: str) -> list[ModelMessage]:
        data = await self.redis.get(self._key(session_id))
        if data is None:
            return []
        return model_messages_adapter.validate_json(data)

    async def save_messages(self, session_id: str, messages: list[ModelMessage]) -> None:
        data = model_messages_adapter.dump_json(messages)
        await self.redis.setex(self._key(session_id), self.ttl, data)
