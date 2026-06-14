from dataclasses import dataclass

from app.memory.redis_store import RedisModelMessageStore


@dataclass
class Deps:
    redis_store: RedisModelMessageStore
    session_id: str
    workspace_id: int
    user_id: int
