import logging

from app.core.config import settings
from app.rag.connection import get_client, ensure_collection
from app.rag.embedder import get_embedding

logger = logging.getLogger(__name__)


def search_knowledge(consulta: str, top_k: int | None = None) -> list[dict]:
    if top_k is None:
        top_k = settings.rag_top_k

    ensure_collection()

    client = get_client()
    embedding = get_embedding(consulta)

    response = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=embedding,
        limit=top_k,
        with_payload=True,
    )

    resultados = []
    for point in response.points:
        resultados.append(
            {
                "texto": point.payload.get("texto", ""),
                "seccion": point.payload.get("seccion", ""),
                "score": round(point.score, 4),
            }
        )

    logger.info(
        "RAG | consulta='%s' | fragmentos=%d", consulta, len(resultados)
    )

    return resultados
