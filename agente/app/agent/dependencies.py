from dataclasses import dataclass

from app.memory.redis_store import RedisModelMessageStore


@dataclass
class Deps:
    redis_store: RedisModelMessageStore
    session_id: str
    workspace_id: str   # UUID del workspace (multi-tenant)
    user_id: str        # UUID del usuario (extraído del JWT)
