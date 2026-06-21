"""
Inicializador central del subsistema de observabilidad.

Configura Langfuse como backend de trazas estructuradas vía OpenTelemetry,
y habilita la instrumentación automática de Pydantic AI para registrar
prompts, respuestas del LLM e invocaciones a tools con sus argumentos
y retornos JSON.
"""

import logging

logger = logging.getLogger(__name__)


def init_observability() -> None:
    """Inicializa el subsistema de observabilidad con Langfuse + Pydantic AI.

    1. Configura logging básico de Python.
    2. Inicializa el cliente Langfuse (lee credenciales de env vars).
    3. Habilita la instrumentación global de todos los agentes de Pydantic AI
       para que emitan spans OpenTelemetry capturados por Langfuse.

    Si las credenciales de Langfuse no están configuradas, la aplicación
    arranca normalmente pero sin observabilidad (fail-open).
    """
    # ── Logging básico de Python ─────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Verificar credenciales de Langfuse ───────────────────────
    from app.core.config import settings

    public_key = settings.langfuse_public_key
    secret_key = settings.langfuse_secret_key

    if not public_key or not secret_key:
        logger.warning(
            "LANGFUSE_PUBLIC_KEY y/o LANGFUSE_SECRET_KEY no están configuradas. "
            "La observabilidad con Langfuse está DESACTIVADA. "
            "El agente funcionará normalmente sin trazas."
        )
        return

    # ── Inicializar cliente Langfuse ─────────────────────────────
    try:
        from langfuse import get_client
        from pydantic_ai import Agent

        # get_client() lee automáticamente LANGFUSE_PUBLIC_KEY,
        # LANGFUSE_SECRET_KEY y LANGFUSE_BASE_URL de las env vars
        # y registra un span processor de OpenTelemetry internamente.
        langfuse_client = get_client()

        # Verificar autenticación con Langfuse
        if langfuse_client.auth_check():
            logger.info("✅ Langfuse: cliente autenticado correctamente")
        else:
            logger.warning(
                "⚠️ Langfuse: autenticación fallida. "
                "Verificá las credenciales en las variables de entorno."
            )
            return

        # ── Instrumentar todos los agentes de Pydantic AI ────────
        # Esto habilita la captura automática de:
        #   - Prompts de entrada del usuario
        #   - Llamadas internas del loop ReAct al LLM
        #   - Respuestas del modelo
        #   - Invocaciones a tools con argumentos JSON y retornos
        Agent.instrument_all()
        logger.info(
            "✅ Observabilidad: Pydantic AI instrumentado globalmente → Langfuse"
        )

    except ImportError as e:
        logger.warning(
            "No se pudieron importar las dependencias de observabilidad (%s). "
            "Instalá 'langfuse' y 'pydantic-ai' para habilitar trazas.",
            e,
        )
    except Exception as e:
        logger.error(
            "Error inesperado al inicializar la observabilidad: %s",
            e,
            exc_info=True,
        )
