import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        logger.info(
            "Conectado a Qdrant en %s:%s", settings.qdrant_host, settings.qdrant_port
        )
    return _client


def ensure_collection():
    client = get_client()
    try:
        client.get_collection(settings.qdrant_collection_name)
        logger.info(
            "Colección '%s' ya existe", settings.qdrant_collection_name
        )
    except (UnexpectedResponse, ValueError):
        logger.info(
            "Creando colección '%s'...", settings.qdrant_collection_name
        )
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )
        logger.info(
            "Colección '%s' creada", settings.qdrant_collection_name
        )
