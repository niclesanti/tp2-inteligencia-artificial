"""
Orquestador del agente financiero.

Define la instancia central del Agent de Pydantic AI y
registra todas las tools que el LLM puede invocar durante
el loop ReAct (Reasoning and Acting).
"""

import json
import logging

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel

from app.agent.dependencies import Deps
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.finance_api import (
    filtrar_compras_credito,
    filtrar_transacciones,
)

logger = logging.getLogger(__name__)

# ── Modelo y agente ──────────────────────────────────────────────

model = GroqModel("llama-3.3-70b-versatile")

agent: Agent[Deps] = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=Deps,
)


# ── Tools de consulta al backend ─────────────────────────────────

@agent.tool
async def tool_filtrar_transacciones(
    ctx: RunContext[Deps],
    mes: int | None = None,
    anio: int | None = None,
    motivo: str | None = None,
    contacto: str | None = None,
    page: int | None = None,
    size: int | None = None,
) -> str:
    """Filtra y recupera transacciones (ingresos/gastos en efectivo o débito) del usuario.

    Aplica filtros opcionales como mes, año, motivo o contacto.
    Los resultados se devuelven paginados (10 elementos por página por defecto).

    Args:
        mes: Número de mes (1=enero, ..., 12=diciembre). Si se usa, el año es OBLIGATORIO.
        anio: Año (ej: 2024, 2025). Puede usarse sin mes.
        motivo: Texto para filtrar por motivo de la transacción.
        contacto: Texto para filtrar por nombre del contacto.
        page: Número de página (0-based). Omite para usar la primera página.
        size: Cantidad de resultados por página. Omite para usar el valor por defecto.

    Returns:
        JSON string con la lista paginada de transacciones.
    """
    # Validación: mes requiere año
    if mes is not None and anio is None:
        logger.warning("tool_filtrar_transacciones llamada con mes=%s pero sin año", mes)
        return (
            "Error: Si especificas el mes, el año también es obligatorio. "
            "Por favor, indica también el año (ej: 2025) para poder realizar la búsqueda."
        )

    logger.info(
        "tool_filtrar_transacciones | workspace=%s mes=%s anio=%s motivo=%s contacto=%s page=%s size=%s",
        ctx.deps.workspace_id, mes, anio, motivo, contacto, page, size,
    )

    try:
        data = await filtrar_transacciones(
            workspace_id=ctx.deps.workspace_id,
            mes=mes,
            anio=anio,
            motivo=motivo,
            contacto=contacto,
            page=page,
            size=size,
        )
        return json.dumps(data, default=str, ensure_ascii=False)
    except ValueError as e:
        logger.error("Error en tool_filtrar_transacciones: %s", str(e))
        return f"Error al consultar transacciones: {e}"


@agent.tool
async def tool_filtrar_compras_credito(
    ctx: RunContext[Deps],
    mes: int | None = None,
    anio: int | None = None,
    motivo: str | None = None,
    contacto: str | None = None,
    page: int | None = None,
    size: int | None = None,
) -> str:
    """Filtra y recupera compras realizadas con tarjeta de crédito del usuario.

    Incluye información detallada: monto total, cantidad de cuotas, cuotas pagadas,
    datos de la tarjeta, comercio y fechas.

    Args:
        mes: Número de mes (1=enero, ..., 12=diciembre). Si se usa, el año es OBLIGATORIO.
        anio: Año (ej: 2024, 2025). Puede usarse sin mes.
        motivo: Texto para filtrar por motivo de la compra.
        contacto: Texto para filtrar por nombre del contacto/comercio.
        page: Número de página (0-based). Omite para usar la primera página.
        size: Cantidad de resultados por página. Omite para usar el valor por defecto.

    Returns:
        JSON string con la lista paginada de compras a crédito.
    """
    # Validación: mes requiere año
    if mes is not None and anio is None:
        logger.warning("tool_filtrar_compras_credito llamada con mes=%s pero sin año", mes)
        return (
            "Error: Si especificas el mes, el año también es obligatorio. "
            "Por favor, indica también el año (ej: 2025) para poder realizar la búsqueda."
        )

    logger.info(
        "tool_filtrar_compras_credito | workspace=%s mes=%s anio=%s motivo=%s contacto=%s page=%s size=%s",
        ctx.deps.workspace_id, mes, anio, motivo, contacto, page, size,
    )

    try:
        data = await filtrar_compras_credito(
            workspace_id=ctx.deps.workspace_id,
            mes=mes,
            anio=anio,
            motivo=motivo,
            contacto=contacto,
            page=page,
            size=size,
        )
        return json.dumps(data, default=str, ensure_ascii=False)
    except ValueError as e:
        logger.error("Error en tool_filtrar_compras_credito: %s", str(e))
        return f"Error al consultar compras a crédito: {e}"
