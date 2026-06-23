"""
Módulo RAG (Retrieval-Augmented Generation) para el asistente financiero.

Provee el pipeline completo de indexación y recuperación:
- connection:   Conector a Qdrant y gestión de colecciones
- ingester:     Script de ingesta (chunking → embedding → Qdrant)
- retriever:    Motor de búsqueda semántica (query → chunks relevantes)
"""

from app.rag.connection import (
    ensure_collection_async,
    ensure_collection_sync,
    get_async_client,
    get_sync_client,
)
from app.rag.retriever import Retriever

__all__ = [
    "Retriever",
    "ensure_collection_async",
    "ensure_collection_sync",
    "get_async_client",
    "get_sync_client",
]
