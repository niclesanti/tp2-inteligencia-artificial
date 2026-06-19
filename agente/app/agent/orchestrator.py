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
from app.tools.calculator import calcular
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


# ── Tool de cálculo determinístico ───────────────────────────────


@agent.tool
async def tool_calculadora_estadistica(
    ctx: RunContext[Deps],
    data_json: str,
    operacion: str,
    filtro_categoria: str | None = None,
    filtro_tipo: str | None = None,
) -> str:
    """Ejecuta cálculos matemáticos y estadísticos determinísticos sobre datos financieros.

    NO intentes hacer cálculos aritméticos por tu cuenta. Usá SIEMPRE esta
    herramienta para sumar, promediar, contar o cualquier operación numérica.
    Solo suma montos de un mismo tipo de dato.

    Args:
        data_json: JSON string obtenido de ``tool_filtrar_transacciones``
                   o ``tool_filtrar_compras_credito``. Debe contener el campo
                   ``content`` con la lista de transacciones o compras.
        operacion: Operación a realizar. Valores válidos:
                   - "sumar": suma todos los montos.
                   - "promedio": promedio de los montos.
                   - "contar": cantidad de elementos.
                   - "minimo": elemento de menor monto.
                   - "maximo": elemento de mayor monto.
                   - "agrupar_por_categoria": total, cantidad y % por categoría.
                   - "balance": total ingresos, gastos y neto (solo transacciones).
                   - "porcentaje": % de una categoría sobre el total.
                   - "proyeccion_credito": cuotas pendientes y próximo pago (solo crédito).
        filtro_categoria: Opcional. Filtra por nombre de categoría/motivo
                          (ej: "Alimentación", "Servicios"). No diferencia
                          mayúsculas/minúsculas.
        filtro_tipo: Opcional. Filtra por tipo de transacción. Solo aplica a
                     transacciones. Valores: "INGRESO" o "GASTO".

    Returns:
        JSON string con el resultado estructurado del cálculo.
        Incluye siempre los campos ``operacion`` y ``moneda``.
    """
    logger.info(
        "tool_calculadora_estadistica | op=%s cat=%s tipo=%s",
        operacion,
        filtro_categoria,
        filtro_tipo,
    )

    try:
        resultado = calcular(
            data_json=data_json,
            operacion=operacion,
            filtro_categoria=filtro_categoria,
            filtro_tipo=filtro_tipo,
        )
        logger.info("tool_calculadora_estadistica | OK")
        return resultado
    except Exception as e:
        logger.error(
            "tool_calculadora_estadistica | error: %s", str(e), exc_info=True
        )
        return json.dumps(
            {
                "error": f"Error inesperado en la calculadora: {e}",
                "operacion": operacion,
            },
            ensure_ascii=False,
        )
