
# ── Inicializar observabilidad ANTES de cualquier otro import ────
# Esto garantiza que Langfuse + OpenTelemetry estén activos
# desde el segundo cero del ciclo de vida del servidor.
from app.services.logging_config import init_observability

init_observability()

import json
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse
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
    # Flush de trazas pendientes en Langfuse antes de cerrar
    try:
        from langfuse import get_client

        get_client().flush()
    except Exception:
        pass



app = FastAPI(
    title="Asistente de Consulta Analítica e Inteligencia Financiera",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str
    workspace_id: str
    user_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


async def validar_token(token: str) -> dict | None:
    """Valida el JWT contra el backend Spring Boot.

    Llama a GET /api/auth/status con el token en el header Authorization.
    Retorna el objeto user si está autenticado, None en caso contrario.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{settings.backend_url}/api/auth/status",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("authenticated"):
                return data["user"]
            return None
    except httpx.RequestError:
        return None


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


@app.get("/api/agente/chat/stream")
async def chat_stream(
    message: str = Query(...),
    session_id: str = Query(...),
    workspace_id: str = Query(...),
    token: str = Query(...),
    request: Request = None,
):
    # 1. Validar JWT contra el backend Spring Boot
    user = await validar_token(token)
    if not user:
        async def unauth_event():
            yield f"event: error-message\ndata: {json.dumps('No autorizado')}\n\n"

        return StreamingResponse(
            unauth_event(),
            media_type="text/event-stream",
            status_code=401,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    store: RedisModelMessageStore = request.app.state.redis_store
    user_id = user["id"]

    # 2. Cargar historial de la sesión desde Redis
    history = await store.get_messages(session_id)

    # 3. Crear dependencias para las tools del agente
    deps = Deps(
        redis_store=store,
        session_id=session_id,
        workspace_id=workspace_id,
        user_id=user_id,
    )

    async def event_stream():
        try:
            # 4. Ejecutar el agente con streaming.
            # run_stream es @asynccontextmanager, se usa con async with
            async with agent.run_stream(
                message, deps=deps, message_history=history
            ) as result:
                # 5. Streamear tokens del LLM en tiempo real.
                # stream_output() yield el texto acumulado en cada paso;
                # calculamos el delta para enviar solo el texto nuevo.
                prev_text = ""
                async for chunk in result.stream_output():
                    delta = chunk[len(prev_text):]
                    prev_text = chunk
                    if delta:
                        yield f"event: token\ndata: {json.dumps(delta)}\n\n"

                # 6. Persistir historial actualizado en Redis
                all_messages = result.all_messages()
                await store.save_messages(session_id, all_messages)

                # 7. Enviar metadata final
                usage = result.usage
                metadata = {
                    "functionsCalled": [],
                    "tokensUsed": usage.total_tokens if usage else 0,
                }
            yield f"event: done\ndata: {json.dumps(metadata)}\n\n"
        except Exception as e:
            yield f"event: error-message\ndata: {json.dumps(str(e))}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agente-ia"}


@app.get("/")
async def root():
    return {"message": "Bienvenido al Microservicio de IA del Asistente Financiero"}
