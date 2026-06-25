import logging

from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def get_embedding(texto: str) -> list[float]:
    global _model
    if _model is None:
        logger.info(
            "Cargando modelo de embeddings: %s", settings.embedding_model_name
        )
        _model = SentenceTransformer(settings.embedding_model_name)
        logger.info("Modelo de embeddings cargado correctamente")
    return _model.encode(texto, normalize_embeddings=True).tolist()
