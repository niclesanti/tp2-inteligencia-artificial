"""
Motor de búsqueda semántica para el pipeline RAG.

El ``Retriever`` es la única puerta de entrada a la base de conocimiento
financiera. Se usa desde ``tool_recuperacion_RAG`` en el agente.

Características:
- Carga diferida (lazy) del modelo de embeddings — la primera llamada
  descarga el modelo si no está cacheados.
- Ejecuta la codificación de la query en un **thread worker** separado
  para no bloquear el event loop de FastAPI.
- Formatea los resultados como texto plano con metadatos (fuente, sección,
  score de relevancia) para que el LLM pueda citar sus respuestas.
"""

import asyncio
import logging

from app.core.config import settings
from app.rag.connection import ensure_collection_async, get_async_client

logger = logging.getLogger(__name__)


class Retriever:
    """Motor de búsqueda semántica para el RAG.

    Uso:
        retriever = Retriever()
        contexto = await retriever.retrieve("¿cómo ahorrar?")
    """

    def __init__(self):
        self._model = None
        self._qdrant = None

    async def ensure_model(self):
        """Inicializa el modelo de embeddings de forma **eager** (precarga).

        Útil para cargar el modelo al iniciar el servidor en lugar de
        esperar a la primera consulta RAG. Es seguro llamarlo múltiples
        veces (es idempotente).
        """
        await self._ensure_model()

    # ─── Inicialización diferida ─────────────────────────────────

    async def _ensure_model(self):
        """Carga el modelo de Sentence Transformers (lazy, una sola vez).

        Se ejecuta en un thread separado para no bloquear el event loop.
        """
        if self._model is not None:
            return self._model

        logger.info(
            "🔧 Retriever: cargando modelo '%s' (lazy)...",
            settings.embedding_model_name,
        )
        try:
            from sentence_transformers import SentenceTransformer

            self._model = await asyncio.to_thread(
                SentenceTransformer,
                settings.embedding_model_name,
            )
            dim = self._model.get_embedding_dimension()
            logger.info(
                "✅ Retriever: modelo cargado (dimensión=%d, device=%s)",
                dim,
                self._model.device,
            )
        except Exception as e:
            logger.error(
                "❌ Retriever: error al cargar modelo '%s': %s",
                settings.embedding_model_name,
                e,
            )
            raise

        return self._model

    async def _ensure_qdrant(self):
        """Asegura el cliente de Qdrant y la colección (lazy, una sola vez)."""
        if self._qdrant is not None:
            return self._qdrant

        self._qdrant = get_async_client()

        try:
            await ensure_collection_async(self._qdrant)
        except ConnectionError as e:
            logger.warning(
                "Retriever: Qdrant no disponible aún (%s). "
                "Se reintentará en la próxima consulta.",
                e,
            )
            self._qdrant = None
            raise

        return self._qdrant

    # ─── Búsqueda principal ──────────────────────────────────────

    async def retrieve(self, query: str, top_k: int | None = None) -> str:
        """Busca los chunks más relevantes para *query* en la base de conocimiento.

        El pipeline completo:
            1. Embediza la query (en thread separado).
            2. Busca los ``top_k`` vectores más cercanos por distancia coseno en Qdrant.
            3. Formatea el resultado como texto plano con metadatos.

        Args:
            query: Consulta en lenguaje natural del usuario.
            top_k: Cantidad de chunks a recuperar (opcional; usa el valor de
                   configuración :attr:`settings.rag_top_k` si no se especifica).

        Returns:
            String con los fragmentos recuperados formateados para inyectar
            como contexto al LLM, o cadena vacía si no hay resultados.
        """
        k = top_k or settings.rag_top_k

        # 1. Embedizar la query
        try:
            model = await self._ensure_model()
            query_embedding = await asyncio.to_thread(
                model.encode, query, normalize_embeddings=True
            )
        except Exception as e:
            logger.error("Retriever: error al embedizar query: %s", e)
            return ""

        # 2. Buscar en Qdrant
        try:
            qdrant = await self._ensure_qdrant()
        except ConnectionError:
            return ""

        try:
            # Usar query_points (API v1.18+ reemplaza al antiguo search)
            response = await qdrant.query_points(
                collection_name=settings.qdrant_collection_name,
                query=query_embedding.tolist(),
                limit=k,
                with_payload=True,
            )
            results = response.points
        except Exception as e:
            logger.error("Retriever: error al buscar en Qdrant: %s", e)
            return ""

        if not results:
            logger.info("Retriever: sin resultados para query='%s'", query[:80])
            return ""

        # 3. Formatear resultados
        context_parts = []
        for i, hit in enumerate(results, 1):
            payload = hit.payload or {}
            texto = payload.get("text", "")
            fuente = payload.get("fuente", "Desconocida")
            seccion = payload.get("seccion", "")
            score = hit.score

            header = f"[{i}] Fuente: {fuente}"
            if seccion:
                header += f" | Sección: {seccion}"
            header += f" (relevancia: {score:.2f})"

            context_parts.append(f"{header}\n{texto}")

        logger.info(
            "Retriever: %d resultados para query='%s' (top score=%.2f)",
            len(results),
            query[:60],
            results[0].score if results else 0.0,
        )

        return "\n\n---\n\n".join(context_parts)

    # ─── Limpieza ────────────────────────────────────────────────

    async def close(self) -> None:
        """Cierra la conexión con Qdrant (si estaba abierta)."""
        if self._qdrant is not None:
            await self._qdrant.close()
            logger.debug("Retriever: conexión a Qdrant cerrada")
