"""
Orquestador del agente financiero.

Define la instancia central del Agent de Pydantic AI y
registra todas las tools que el LLM puede invocar durante
el loop ReAct (Reasoning and Acting).
"""

import json
import logging
import os

import httpx
from groq import AsyncGroq
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Instrumentation
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from app.agent.dependencies import Deps
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.calculator import calcular
from app.tools import finance_api

logger = logging.getLogger(__name__)

# ── Modelo y agente ──────────────────────────────────────────────

# Cliente HTTP personalizado con timeout generoso (180s) para evitar
# que los retries automáticos del SDK de Groq disparen demoras de
# ~3 minutos cuando el LLM tarda en decidir el siguiente paso del
# loop ReAct. Además, max_retries=0 desactiva los reintentos internos.
_groq_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(180.0, connect=30.0),
)
_groq_client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    http_client=_groq_http_client,
    max_retries=0,
    timeout=httpx.Timeout(180.0),
)
_groq_provider = GroqProvider(groq_client=_groq_client)

model = GroqModel("llama-3.3-70b-versatile", provider=_groq_provider)

agent: Agent[Deps] = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=Deps,
    capabilities=[Instrumentation()],
)


# ── Tools de consulta al backend ─────────────────────────────────

# NOTA: No usar `int | None = None` ni `Optional[int]` como parámetros
# de tool. Pydantic AI 2.0.0 tiene un bug que impide ejecutar la tool
# cuando el parámetro usa type union con None. Usar `int = 0` como
# default para parámetros opcionales (0 no es un valor válido para
# mes/anio/page/size).


def _filtrar_por_tipo(items: list[dict], filtro_tipo: str) -> list[dict]:
    if not filtro_tipo:
        return items
    ft = filtro_tipo.upper()
    return [it for it in items if it.get("tipo", "").upper() == ft]


def _filtrar_por_categoria(items: list[dict], filtro_categoria: str) -> list[dict]:
    if not filtro_categoria:
        return items
    fc = filtro_categoria.lower()
    return [it for it in items if fc in (it.get("nombreMotivo") or "").lower()]


@agent.tool
async def filtro_transacciones(
    ctx: RunContext[Deps],
    mes: int = 0,
    anio: int = 0,
    motivo: str = "",
    contacto: str = "",
    page: int = 0,
    size: int = 0,
    filtro_tipo: str = "",
    filtro_categoria: str = "",
) -> str:
    """Filtra y recupera transacciones (ingresos/gastos en efectivo o débito) del usuario.

    Aplica filtros opcionales como mes, año, motivo, contacto, tipo o categoría.

    Args:
        mes: Número de mes (1=enero, ..., 12=diciembre). Si se usa, el año es OBLIGATORIO.
        anio: Año (ej: 2024, 2025). Puede usarse sin mes.
        motivo: Texto para filtrar por motivo de la transacción.
        contacto: Texto para filtrar por nombre del contacto.
        page: Número de página (0-based). Omite para usar la primera página.
        size: Cantidad de resultados por página. Omite para usar el valor por defecto.
        filtro_tipo: Opcional. Filtra por tipo de transacción. Valores: "INGRESO" o "GASTO".
        filtro_categoria: Opcional. Filtra por nombre de categoría/motivo.

    Returns:
        JSON string con la lista paginada de transacciones.
    """
    if mes and not anio:
        logger.warning("filtro_transacciones llamada con mes=%s pero sin año", mes)
        return (
            "Error: Si especificas el mes, el año también es obligatorio. "
            "Por favor, indica también el año (ej: 2025) para poder realizar la búsqueda."
        )

    try:
        data = await finance_api.filtrar_transacciones(
            workspace_id=ctx.deps.workspace_id,
            mes=mes,
            anio=anio,
            motivo=motivo,
            contacto=contacto,
            page=page,
            size=size,
        )
        items = data.get("content", [])
        items = _filtrar_por_tipo(items, filtro_tipo)
        items = _filtrar_por_categoria(items, filtro_categoria)
        data["content"] = items
        data["totalElements"] = len(items)
        return json.dumps(data, default=str, ensure_ascii=False)
    except ValueError as e:
        logger.error("filtro_transacciones | error: %s", str(e))
        return f"Error al consultar transacciones: {e}"


@agent.tool
async def filtro_compras_credito(
    ctx: RunContext[Deps],
    mes: int = 0,
    anio: int = 0,
    motivo: str = "",
    contacto: str = "",
    page: int = 0,
    size: int = 0,
    filtro_tipo: str = "",
    filtro_categoria: str = "",
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
        filtro_tipo: Opcional. Filtra por tipo. Solo aplica si la data tiene campo tipo.
        filtro_categoria: Opcional. Filtra por nombre de categoría/motivo.

    Returns:
        JSON string con la lista paginada de compras a crédito.
    """
    if mes and not anio:
        logger.warning("filtro_compras_credito llamada con mes=%s pero sin año", mes)
        return (
            "Error: Si especificas el mes, el año también es obligatorio. "
            "Por favor, indica también el año (ej: 2025) para poder realizar la búsqueda."
        )

    try:
        data = await finance_api.filtrar_compras_credito(
            workspace_id=ctx.deps.workspace_id,
            mes=mes,
            anio=anio,
            motivo=motivo,
            contacto=contacto,
            page=page,
            size=size,
        )
        items = data.get("content", [])
        items = _filtrar_por_tipo(items, filtro_tipo)
        items = _filtrar_por_categoria(items, filtro_categoria)
        data["content"] = items
        data["totalElements"] = len(items)
        return json.dumps(data, default=str, ensure_ascii=False)
    except ValueError as e:
        logger.error("filtro_compras_credito | error: %s", str(e))
        return f"Error al consultar compras a crédito: {e}"


# ── Tool de cálculo determinístico ───────────────────────────────


@agent.tool
async def calculadora_estadistica(
    ctx: RunContext[Deps],
    data_json: str,
    operacion: str,
    filtro_categoria: str = "",
    filtro_tipo: str = "",
) -> str:
    """Ejecuta cálculos matemáticos y estadísticos determinísticos sobre datos financieros.

    NO intentes hacer cálculos aritméticos por tu cuenta. Usá SIEMPRE esta
    herramienta para sumar, promediar, contar o cualquier operación numérica.
    Solo suma montos de un mismo tipo de dato.

    Args:
        data_json: JSON string obtenido de ``filtro_transacciones``
                   o ``filtro_compras_credito``. Debe contener el campo
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


    try:
        resultado = calcular(
            data_json=data_json,
            operacion=operacion,
            filtro_categoria=filtro_categoria or None,
            filtro_tipo=filtro_tipo or None,
        )

        return resultado
    except Exception as e:
        logger.error(
            "calculadora_estadistica | error: %s", str(e), exc_info=True
        )
        return json.dumps(
            {
                "error": f"Error inesperado en la calculadora: {e}",
                "operacion": operacion,
            },
            ensure_ascii=False,
        )
