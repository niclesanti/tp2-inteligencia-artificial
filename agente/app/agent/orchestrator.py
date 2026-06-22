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
from app.tools.finance_api import (
    filtrar_compras_credito,
    filtrar_transacciones,
)

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
        logger.error("tool_filtrar_transacciones | error: %s", str(e))
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
        logger.error("tool_filtrar_compras_credito | error: %s", str(e))
        return f"Error al consultar compras a crédito: {e}"


# ── Tool de recuperación RAG ─────────────────────────────────────


@agent.tool
async def tool_recuperacion_RAG(
    ctx: RunContext[Deps],
    consulta: str,
) -> str:
    """Recupera información de la base de conocimiento de educación financiera.

    Usá esta herramienta SOLO cuando el usuario pida:
    - Consejos de ahorro o educación financiera personal
    - Información sobre el contexto macroeconómico argentino
      (inflación, IPC, salarios, INDEC)
    - Explicaciones sobre productos financieros
      (plazos fijos, cuentas remuneradas, FCI Money Market, Dólar MEP, CEDEARs)
    - Marco regulatorio y derechos del consumidor financiero
      (BCRA, CNV, Ley de Tarjetas de Crédito 25.065, Transferencias 3.0)
    - Estrategias de cobertura contra la inflación
    - Capacidad de endeudamiento y gestión de deudas
    - Cualquier tema de finanzas personales que requiera fundamentos teóricos

    NO uses esta herramienta para consultas sobre transacciones, gastos,
    ingresos o balances del usuario — esas van a las tools de filtrado.

    Args:
        consulta: La pregunta o tema sobre el cual se necesita
                  información financiera detallada.

    Returns:
        Texto con los fragmentos más relevantes de la base de conocimiento,
        incluyendo fuente y sección de origen para que el usuario pueda
        identificar el origen de la información.
    """
    logger.info("tool_recuperacion_RAG | consulta='%s'", consulta)

    # ── Validación temprana: rechazar consultas triviales/no financieras ──
    consulta_stripped = consulta.strip().lower()
    saludos = {"hola", "hola como estas", "como estas", "buenos dias",
               "buenas tardes", "buenas noches", "que tal", "hello",
               "hi", "hey", "gracias", "muchas gracias", "chau", "adios",
               "bye", "nos vemos", "saludos"}
    if consulta_stripped in saludos or len(consulta_stripped) < 5:
        logger.info(
            "tool_recuperacion_RAG | consulta trivial ignorada: '%s'",
            consulta[:60],
        )
        return (
            "Esta herramienta es solo para consultas de educación "
            "financiera. Para saludos o conversación general, "
            "respondé directamente sin usar herramientas."
        )

    try:
        contexto = await ctx.deps.retriever.retrieve(consulta)
        if not contexto:
            logger.info(
                "tool_recuperacion_RAG | sin resultados para: %s",
                consulta[:80],
            )
            return (
                "No se encontró información relevante en la base de "
                "conocimiento financiera para esa consulta."
            )
        logger.info(
            "tool_recuperacion_RAG | OK (%d caracteres)",
            len(contexto),
        )
        return contexto
    except Exception as e:
        logger.error(
            "tool_recuperacion_RAG | error: %s", str(e), exc_info=True
        )
        return f"Error al recuperar información financiera: {e}"


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


    try:
        resultado = calcular(
            data_json=data_json,
            operacion=operacion,
            filtro_categoria=filtro_categoria,
            filtro_tipo=filtro_tipo,
        )

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
