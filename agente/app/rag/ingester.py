#!/usr/bin/env python3
"""
Ingesta del documento de educación financiera en Qdrant.

Ejecutar una sola vez para poblar la base vectorial:
    python -m app.rag.ingester

Si el documento cambia, volver a ejecutar (recrea la colección).
"""

import logging
import os
import re

from qdrant_client.http.models import PointStruct

from app.core.config import settings
from app.rag.connection import get_client, ensure_collection
from app.rag.embedder import get_embedding

logger = logging.getLogger(__name__)

RAG_DOC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "docs RAG",
    "guia_finanzas_personales_rag.md",
)

MAX_CHUNK_CHARS = 1200


def _contar_tokens_aproximado(texto: str) -> int:
    return len(texto) // 4


def _slugify(titulo: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", titulo.lower().strip())


def _chunkear_documento(ruta: str) -> list[dict]:
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    secciones = re.split(r"\n## ", contenido)
    chunks = []

    for i, seccion in enumerate(secciones):
        if i == 0 and not seccion.startswith("## "):
            seccion_texto = seccion.strip()
            if not seccion_texto:
                continue
        else:
            if not seccion.strip():
                continue

        lineas = seccion.split("\n", 1)
        titulo = lineas[0].strip().lstrip("#").strip()
        cuerpo = lineas[1].strip() if len(lineas) > 1 else ""

        parrafos = [p.strip() for p in re.split(r"\n\n+", cuerpo) if p.strip()]

        chunk_actual = ""
        for parrafo in parrafos:
            if not parrafo:
                continue
            if chunk_actual and _contar_tokens_aproximado(
                chunk_actual + "\n\n" + parrafo
            ) > (MAX_CHUNK_CHARS // 4):
                chunks.append(
                    {
                        "texto": chunk_actual,
                        "seccion": titulo,
                        "tokens_approx": _contar_tokens_aproximado(chunk_actual),
                    }
                )
                chunk_actual = parrafo
            else:
                if chunk_actual:
                    chunk_actual += "\n\n" + parrafo
                else:
                    chunk_actual = parrafo

        if chunk_actual:
            chunks.append(
                {
                    "texto": chunk_actual,
                    "seccion": titulo,
                    "tokens_approx": _contar_tokens_aproximado(chunk_actual),
                }
            )

    return chunks


def run_ingestion():
    client = get_client()

    collection_name = settings.qdrant_collection_name
    try:
        client.delete_collection(collection_name)
        logger.info("Colección '%s' eliminada para re-indexación", collection_name)
    except Exception:
        pass

    ensure_collection()

    chunks = _chunkear_documento(RAG_DOC_PATH)
    logger.info("Documento chunked en %d fragmentos", len(chunks))

    points = []
    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["texto"])
        points.append(
            PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "texto": chunk["texto"],
                    "seccion": chunk["seccion"],
                    "tokens_approx": chunk["tokens_approx"],
                },
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )

    logger.info(
        "Ingesta completada: %d fragmentos indexados en '%s'",
        len(points),
        collection_name,
    )

    max_tokens = max(c["tokens_approx"] for c in chunks) if chunks else 0
    logger.info(
        "Chunk más grande: ~%d tokens", max_tokens
    )


def ensure_indexed():
    """Indexa si la colección está vacía. Idempotente: safe llamar siempre."""
    try:
        client = get_client()
        collection_info = client.get_collection(settings.qdrant_collection_name)
        if collection_info.points_count > 0:
            logger.info(
                "RAG ya indexado (%d puntos). Skip.",
                collection_info.points_count,
            )
            return
    except Exception:
        pass

    logger.info("RAG no indexado. Ejecutando ingesta...")
    run_ingestion()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_ingestion()
