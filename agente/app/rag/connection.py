"""
Conector a la base de datos vectorial Qdrant y gestión de la colección.

Proporciona clientes síncrono (para scripts de ingesta) y asíncrono
(para el retriever dentro del servidor FastAPI), así como la función
para asegurar que la colección exista con la configuración adecuada.
"""

import logging

from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_sync_client() -> QdrantClient:
    """Retorna un cliente **síncrono** de Qdrant (para scripts de ingesta)."""
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def get_async_client() -> AsyncQdrantClient:
    """Retorna un cliente **asíncrono** de Qdrant (para el retriever en producción)."""
    return AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection_sync(client: QdrantClient) -> None:
    """Crea la colección en Qdrant si no existe (versión síncrona).

    Args:
        client: Cliente síncrono de Qdrant.

    Raises:
        ConnectionError: si no se puede conectar con Qdrant.
    """
    try:
        collections = client.get_collections().collections
        names = {c.name for c in collections}

        if settings.qdrant_collection_name not in names:
            client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "Colección '%s' creada en Qdrant "
                "(dimensión=%d, distancia=coseno)",
                settings.qdrant_collection_name,
                settings.embedding_dimension,
            )
        else:
            logger.info(
                "Colección '%s' ya existe en Qdrant",
                settings.qdrant_collection_name,
            )
    except UnexpectedResponse as e:
        logger.error("Error de comunicación con Qdrant: %s", e)
        raise ConnectionError(f"No se pudo conectar con Qdrant: {e}") from e


async def ensure_collection_async(client: AsyncQdrantClient) -> None:
    """Crea la colección en Qdrant si no existe (versión asíncrona).

    Args:
        client: Cliente asíncrono de Qdrant.

    Raises:
        ConnectionError: si no se puede conectar con Qdrant.
    """
    try:
        response = await client.get_collections()
        names = {c.name for c in response.collections}

        if settings.qdrant_collection_name not in names:
            await client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "Colección '%s' creada en Qdrant "
                "(dimensión=%d, distancia=coseno)",
                settings.qdrant_collection_name,
                settings.embedding_dimension,
            )
        else:
            logger.info(
                "Colección '%s' ya existe en Qdrant",
                settings.qdrant_collection_name,
            )
    except UnexpectedResponse as e:
        logger.error("Error de comunicación con Qdrant: %s", e)
        raise ConnectionError(f"No se pudo conectar con Qdrant: {e}") from e
