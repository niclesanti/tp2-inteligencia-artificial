"""
Script de ingesta: lee documentos Markdown, los chunkifica,
genera embeddings con Sentence Transformers y los sube a Qdrant.

Uso (una sola vez, y cada vez que se agreguen nuevos documentos):

    docker exec -it python-agente-ia python -m app.rag.ingester

El script es **idempotente**: vacía la colección y la vuelve a poblar.
"""

import logging
import re
import sys
from pathlib import Path

from qdrant_client.http.models import PointStruct

from app.core.config import settings
from app.rag.connection import ensure_collection_sync, get_sync_client

logger = logging.getLogger(__name__)

# ─── Ruta base del directorio de documentos ──────────────────────
# Se resuelve relativamente a la raíz del proyecto agente/.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = _PROJECT_ROOT / settings.docs_rag_dir


# ─── Chunking de Markdown ────────────────────────────────────────


def chunk_markdown(filepath: Path) -> list[dict]:
    """Divide un archivo Markdown en chunks semánticos.

    Estrategia (alineada con la Clase 3 de la cátedra):
    1. Divide por secciones ``##`` (nivel 2) — cada sección es un chunk.
    2. Si una sección excede ``rag_chunk_size`` caracteres (~500 tokens),
       subdivide por párrafos (doble salto de línea).
    3. Cada chunk conserva metadatos: fuente, sección.

    Args:
        filepath: Ruta al archivo .md.

    Returns:
        Lista de diccionarios con ``text`` y ``metadata``.
    """
    text = filepath.read_text(encoding="utf-8")
    chunks: list[dict] = []

    # 1. Dividir por headings de nivel 2 (## )
    sections = re.split(r'\n(?=##\s)', text)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split('\n')
        heading = ""
        for line in lines:
            if line.startswith('## '):
                heading = line.replace('## ', '').strip()
                break

        # Remover la(s) línea(s) de heading del contenido
        content_lines = [l for l in lines if not l.startswith('## ')]
        content = '\n'.join(content_lines).strip()

        if not content:
            continue

        # 2. Si entra en un solo chunk, lo dejamos así
        if len(content) <= settings.rag_chunk_size:
            chunks.append(_make_chunk(content, filepath, heading))
        else:
            # 3. Subdividir por párrafos (doble salto de línea)
            paragraphs = re.split(r'\n\n+', content)
            current = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if not current:
                    current = para
                elif len(current) + len(para) + 2 <= settings.rag_chunk_size:
                    current += "\n\n" + para
                else:
                    chunks.append(_make_chunk(current, filepath, heading))
                    current = para
            if current:
                chunks.append(_make_chunk(current, filepath, heading))

    return chunks


def _make_chunk(text: str, filepath: Path, seccion: str) -> dict:
    """Crea un diccionario de chunk con metadatos."""
    fuente = filepath.stem
    return {
        "text": text,
        "metadata": {
            "fuente": fuente,
            "seccion": seccion or fuente,
        },
    }


# ─── Ingesta principal ───────────────────────────────────────────


def _init_logging() -> None:
    """Configura logging con formato prolijo para la terminal."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Silenciar logs muy verbosos de librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


def _find_documents() -> list[Path]:
    """Busca archivos .md en el directorio de documentos.

    Returns:
        Lista de rutas a archivos .md.

    Raises:
        SystemExit: si el directorio no existe o no hay archivos.
    """
    if not DOCS_DIR.exists():
        logger.error("El directorio de documentos no existe: %s", DOCS_DIR)
        sys.exit(1)

    md_files = sorted(DOCS_DIR.rglob("*.md"))
    if not md_files:
        logger.warning("No se encontraron archivos .md en %s", DOCS_DIR)
        sys.exit(0)

    logger.info("📄 Documentos encontrados: %d", len(md_files))
    for f in md_files:
        logger.info("   • %s", f.relative_to(_PROJECT_ROOT))
    return md_files


def _chunk_documents(md_files: list[Path]) -> list[dict]:
    """Chunkifica todos los documentos.

    Returns:
        Lista plana de chunks.

    Raises:
        SystemExit: si no se genera ningún chunk.
    """
    all_chunks: list[dict] = []
    for fpath in md_files:
        try:
            chunks = chunk_markdown(fpath)
            logger.info("   • %s → %d chunks", fpath.name, len(chunks))
            all_chunks.extend(chunks)
        except Exception as e:
            logger.error("Error al procesar %s: %s", fpath.name, e)

    logger.info("🧩 Total chunks generados: %d", len(all_chunks))
    if not all_chunks:
        logger.warning("No se generaron chunks — nada que indexar.")
        sys.exit(0)
    return all_chunks


def _load_embedding_model():
    """Carga el modelo de Sentence Transformers.

    Returns:
        Instancia del modelo.

    Raises:
        SystemExit: si falla la carga.
    """
    logger.info(
        "🧠 Cargando modelo de embeddings: %s ...",
        settings.embedding_model_name,
    )
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(settings.embedding_model_name)
        dim = model.get_embedding_dimension()
        logger.info(
            "✅ Modelo cargado (dimensión=%d, device=%s)",
            dim, model.device,
        )
        return model
    except Exception as e:
        logger.error("❌ Error al cargar el modelo de embeddings: %s", e)
        sys.exit(1)


def _generate_embeddings(
    model, texts: list[str],
) -> list[list[float]]:
    """Genera embeddings normalizados para una lista de textos."""
    logger.info("🔢 Generando embeddings para %d chunks...", len(texts))
    try:
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
        logger.info("✅ Embeddings generados")
        return embeddings.tolist()
    except Exception as e:
        logger.error("❌ Error al generar embeddings: %s", e)
        sys.exit(1)


def _upload_to_qdrant(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    """Sube los chunks con sus embeddings a Qdrant.

    La estrategia es **reemplazar** todo el contenido de la colección
    (delete + recreate) para garantizar consistencia.
    """
    client = get_sync_client()

    # Verificar conectividad con Qdrant
    try:
        client.get_collections()
    except Exception as e:
        logger.error("❌ No se puede conectar con Qdrant: %s", e)
        sys.exit(1)

    # Asegurar que la colección existe
    ensure_collection_sync(client)

    # Eliminar puntos existentes y re-subir
    logger.info("🧹 Limpiando colección '%s'...", settings.qdrant_collection_name)
    try:
        existing_count = client.count(collection_name=settings.qdrant_collection_name).count
        if existing_count > 0:
            client.delete_collection(settings.qdrant_collection_name)
            logger.info("   Colección eliminada (%d puntos previos)", existing_count)
            ensure_collection_sync(client)
    except Exception as e:
        logger.warning("   No se pudo limpiar la colección previa: %s", e)
        # Si falló, intentamos seguir; la colección ya está asegurada

    # Construir puntos
    points = [
        PointStruct(
            id=i + 1,
            vector=embeddings[i],
            payload={
                "text": chunks[i]["text"],
                "fuente": chunks[i]["metadata"]["fuente"],
                "seccion": chunks[i]["metadata"]["seccion"],
            },
        )
        for i in range(len(chunks))
    ]

    # Subir en batches
    batch_size = 64
    logger.info(
        "📤 Subiendo %d puntos a Qdrant (batch_size=%d)...",
        len(points), batch_size,
    )
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        try:
            client.upsert(
                collection_name=settings.qdrant_collection_name,
                points=batch,
            )
            logger.info(
                "   ✅ %d / %d puntos subidos",
                min(i + batch_size, len(points)),
                len(points),
            )
        except Exception as e:
            logger.error(
                "❌ Error al subir batch %d: %s",
                i // batch_size, e,
            )
            sys.exit(1)

    # Verificación final
    try:
        final_count = client.count(
            collection_name=settings.qdrant_collection_name,
        ).count
        logger.info(
            "   📊 Colección '%s' ahora tiene %d puntos",
            settings.qdrant_collection_name,
            final_count,
        )
    except Exception:
        pass

    client.close()


# ─── Entry point ─────────────────────────────────────────────────


def main() -> None:
    """Ejecuta el pipeline completo de ingesta.

    Flujo:
        1. Encontrar documentos .md
        2. Chunkificar
        3. Cargar modelo de embeddings
        4. Generar embeddings
        5. Subir a Qdrant (reemplazando contenido previo)
    """
    _init_logging()
    logger.info("=" * 60)
    logger.info("  🚀 INGESTA RAG — Asistente Financiero")
    logger.info("=" * 60)

    md_files = _find_documents()
    chunks = _chunk_documents(md_files)
    model = _load_embedding_model()

    texts = [c["text"] for c in chunks]
    embeddings = _generate_embeddings(model, texts)

    _upload_to_qdrant(chunks, embeddings)

    logger.info("=" * 60)
    logger.info("  ✅ Ingesta completada exitosamente")
    logger.info("  📦 %d chunks indexados en '%s'", len(chunks), settings.qdrant_collection_name)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
