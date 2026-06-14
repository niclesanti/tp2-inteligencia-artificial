from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic import BaseModel
from redis.asyncio import Redis

from app.agent.dependencies import Deps
from app.agent.orchestrator import agent
from app.core.config import settings
from app.memory.redis_store import RedisModelMessageStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    app.state.redis_store = RedisModelMessageStore(redis_client)
    yield
    await redis_client.close()


app = FastAPI(
    title="Asistente de Consulta Analítica e Inteligencia Financiera",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str
    workspace_id: int
    user_id: int


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.post("/api/agente/chat")
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    store: RedisModelMessageStore = request.app.state.redis_store

    history = await store.get_messages(body.session_id)

    deps = Deps(
        redis_store=store,
        session_id=body.session_id,
        workspace_id=body.workspace_id,
        user_id=body.user_id,
    )

    result = await agent.run(body.message, deps=deps, message_history=history)

    all_messages = result.all_messages()
    await store.save_messages(body.session_id, all_messages)

    return ChatResponse(response=result.output, session_id=body.session_id)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agente-ia"}


@app.get("/")
async def root():
    return {"message": "Bienvenido al Microservicio de IA del Asistente Financiero"}
