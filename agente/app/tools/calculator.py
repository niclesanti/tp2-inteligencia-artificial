"""
Módulo matemático/estadístico determinístico para el agente financiero.

Recibe datos JSON crudos (obtenidos de las tools de filtrado) y ejecuta
operaciones numéricas precisas, mitigando las debilidades aritméticas del LLM.

Todas las funciones de cálculo son síncronas y determinísticas.
"""

import json
import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)

# ─── Constantes ──────────────────────────────────────────────────

MONEDA = "ARS"

OPERACIONES_VALIDAS: set[str] = {
    "sumar",
    "promedio",
    "contar",
    "minimo",
    "maximo",
    "agrupar_por_categoria",
    "balance",
    "porcentaje",
    "proyeccion_credito",
}

# ─── Parseo y detección ──────────────────────────────────────────


def _extraer_items(data_json: str) -> list[dict[str, Any]]:
    """Parsea el JSON y extrae la lista de elementos del campo ``content``.

    Args:
        data_json: JSON string devuelto por una tool de filtrado.

    Returns:
        Lista de diccionarios con los items.

    Raises:
        ValueError: si el JSON es inválido, no tiene ``content``,
                    o ``content`` no es una lista.
    """
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear el JSON de entrada: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("El JSON de entrada debe ser un objeto (dict), no una lista")

    content = data.get("content")
    if content is None:
        raise ValueError("El JSON de entrada no contiene el campo 'content' con los datos")

    if not isinstance(content, list):
        raise ValueError("El campo 'content' debe ser una lista")

    return content


def _detectar_tipo(items: list[dict[str, Any]]) -> Literal["transacciones", "compras_credito"]:
    """Detecta automáticamente el tipo de dato financiero.

    Si los items tienen ``montoTotal`` y ``cantidadCuotas`` → crédito.
    Si tienen ``monto`` y ``tipo`` → transacciones.
    Si la lista está vacía, retorna transacciones como default.
    """
    if not items:
        return "transacciones"

    first = items[0]
    if "montoTotal" in first and "cantidadCuotas" in first:
        return "compras_credito"
    if "monto" in first and "tipo" in first:
        return "transacciones"

    # Fallback: intentar inferir por campo único presente
    if "montoTotal" in first:
        return "compras_credito"
    if "monto" in first:
        return "transacciones"


    return "transacciones"


def _get_monto(item: dict[str, Any], tipo_dato: str) -> float:
    """Extrae el monto del item según su tipo financiero."""
    key = "montoTotal" if tipo_dato == "compras_credito" else "monto"
    try:
        return float(item.get(key, 0))
    except (TypeError, ValueError):
        logger.warning("Valor no numérico en '%s' para item %s", key, item.get("id", "?"))
        return 0.0


def _get_categoria(item: dict[str, Any]) -> str:
    """Extrae el nombre de la categoría/motivo del item."""
    return item.get("nombreMotivo") or "Sin categoría"


def _aplicar_filtros(
    items: list[dict[str, Any]],
    tipo_dato: str,
    filtro_categoria: str | None = None,
    filtro_tipo: str | None = None,
) -> list[dict[str, Any]]:
    """Aplica filtros opcionales a la lista de items.

    - ``filtro_categoria``: filtra por ``nombreMotivo`` (case-insensitive, substring match).
    - ``filtro_tipo``: solo para transacciones, filtra por ``tipo`` (INGRESO/GASTO).
    """
    if filtro_categoria:
        fc = filtro_categoria.lower()
        items = [
            it
            for it in items
            if fc in (it.get("nombreMotivo") or "").lower()
        ]


    if filtro_tipo and tipo_dato == "transacciones":
        ft = filtro_tipo.upper()
        items = [
            it
            for it in items
            if it.get("tipo", "").upper() == ft
        ]


    return items


# ─── Operaciones individuales ────────────────────────────────────


def _sumar(items: list[dict[str, Any]], tipo_dato: str) -> dict[str, Any]:
    """Suma los montos de todos los items."""
    total = sum(_get_monto(it, tipo_dato) for it in items)
    return {
        "operacion": "sumar",
        "tipo_dato": tipo_dato,
        "total": round(total, 2),
        "cantidad": len(items),
        "moneda": MONEDA,
    }


def _promedio(items: list[dict[str, Any]], tipo_dato: str) -> dict[str, Any]:
    """Calcula el promedio de los montos."""
    if not items:
        return {
            "operacion": "promedio",
            "tipo_dato": tipo_dato,
            "total": 0,
            "cantidad": 0,
            "moneda": MONEDA,
        }
    total = sum(_get_monto(it, tipo_dato) for it in items)
    return {
        "operacion": "promedio",
        "tipo_dato": tipo_dato,
        "total": round(total / len(items), 2),
        "cantidad": len(items),
        "moneda": MONEDA,
    }


def _contar(items: list[dict[str, Any]], tipo_dato: str) -> dict[str, Any]:
    """Cuenta la cantidad de items."""
    return {
        "operacion": "contar",
        "tipo_dato": tipo_dato,
        "total": len(items),
        "cantidad": len(items),
    }


def _minimo(items: list[dict[str, Any]], tipo_dato: str) -> dict[str, Any]:
    """Encuentra el item de menor monto."""
    if not items:
        return {
            "operacion": "minimo",
            "tipo_dato": tipo_dato,
            "total": 0,
            "cantidad": 0,
            "moneda": MONEDA,
        }
    min_item = min(items, key=lambda it: _get_monto(it, tipo_dato))
    return {
        "operacion": "minimo",
        "tipo_dato": tipo_dato,
        "total": _get_monto(min_item, tipo_dato),
        "cantidad": 1,
        "moneda": MONEDA,
        "item": {
            "categoria": _get_categoria(min_item),
            "descripcion": min_item.get("descripcion")
            or min_item.get("nombreComercio", ""),
        },
    }


def _maximo(items: list[dict[str, Any]], tipo_dato: str) -> dict[str, Any]:
    """Encuentra el item de mayor monto."""
    if not items:
        return {
            "operacion": "maximo",
            "tipo_dato": tipo_dato,
            "total": 0,
            "cantidad": 0,
            "moneda": MONEDA,
        }
    max_item = max(items, key=lambda it: _get_monto(it, tipo_dato))
    return {
        "operacion": "maximo",
        "tipo_dato": tipo_dato,
        "total": _get_monto(max_item, tipo_dato),
        "cantidad": 1,
        "moneda": MONEDA,
        "item": {
            "categoria": _get_categoria(max_item),
            "descripcion": max_item.get("descripcion")
            or max_item.get("nombreComercio", ""),
        },
    }


def _agrupar_por_categoria(
    items: list[dict[str, Any]], tipo_dato: str
) -> dict[str, Any]:
    """Agrupa items por categoría y calcula total, cantidad y porcentaje."""
    if not items:
        return {
            "operacion": "agrupar_por_categoria",
            "tipo_dato": tipo_dato,
            "total_general": 0,
            "cantidad_total": 0,
            "moneda": MONEDA,
            "grupos": [],
        }

    grupos: dict[str, dict[str, float | int]] = {}
    for it in items:
        cat = _get_categoria(it)
        monto = _get_monto(it, tipo_dato)
        if cat not in grupos:
            grupos[cat] = {"total": 0.0, "cantidad": 0}
        grupos[cat]["total"] += monto  # type: ignore[operator]
        grupos[cat]["cantidad"] += 1  # type: ignore[operator]

    total_general = float(sum(g["total"] for g in grupos.values()))

    grupos_list = [
        {
            "categoria": cat,
            "total": round(float(v["total"]), 2),
            "cantidad": int(v["cantidad"]),
            "porcentaje": (
                round((float(v["total"]) / total_general) * 100, 1)
                if total_general > 0
                else 0.0
            ),
        }
        for cat, v in sorted(
            grupos.items(), key=lambda x: float(x[1]["total"]), reverse=True
        )
    ]

    return {
        "operacion": "agrupar_por_categoria",
        "tipo_dato": tipo_dato,
        "total_general": round(total_general, 2),
        "cantidad_total": sum(int(v["cantidad"]) for v in grupos.values()),
        "moneda": MONEDA,
        "grupos": grupos_list,
    }


def _balance(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula total ingresos, total gastos y balance neto.

    Solo aplica a transacciones (tipo INGRESO/GASTO).
    """
    ingresos = sum(
        float(it.get("monto", 0))
        for it in items
        if it.get("tipo", "").upper() == "INGRESO"
    )
    gastos = sum(
        float(it.get("monto", 0))
        for it in items
        if it.get("tipo", "").upper() == "GASTO"
    )
    neto = ingresos - gastos

    return {
        "operacion": "balance",
        "tipo_dato": "transacciones",
        "total_ingresos": round(ingresos, 2),
        "total_gastos": round(gastos, 2),
        "balance_neto": round(neto, 2),
        "cantidad_ingresos": sum(
            1 for it in items if it.get("tipo", "").upper() == "INGRESO"
        ),
        "cantidad_gastos": sum(
            1 for it in items if it.get("tipo", "").upper() == "GASTO"
        ),
        "moneda": MONEDA,
    }


def _porcentaje(
    items: list[dict[str, Any]],
    tipo_dato: str,
    filtro_categoria: str | None = None,
) -> dict[str, Any]:
    """Calcula el porcentaje que representa una categoría sobre el total.

    Si se especifica ``filtro_categoria``, calcula el % de esa categoría puntual.
    Si no, devuelve la distribución completa de % por categoría.
    """
    if not items:
        return {
            "operacion": "porcentaje",
            "tipo_dato": tipo_dato,
            "total_general": 0,
            "moneda": MONEDA,
            "detalle": [],
        }

    total_general = sum(_get_monto(it, tipo_dato) for it in items)

    if filtro_categoria:
        # % de una categoría específica
        fc = filtro_categoria.lower()
        items_filtrados = [
            it for it in items if fc in _get_categoria(it).lower()
        ]
        total_categoria = sum(
            _get_monto(it, tipo_dato) for it in items_filtrados
        )
        pct = (
            round((total_categoria / total_general) * 100, 1)
            if total_general > 0
            else 0.0
        )
        return {
            "operacion": "porcentaje",
            "tipo_dato": tipo_dato,
            "categoria": filtro_categoria,
            "total_categoria": round(total_categoria, 2),
            "total_general": round(total_general, 2),
            "porcentaje": pct,
            "moneda": MONEDA,
        }

    # Distribución completa
    categorias: dict[str, float] = {}
    for it in items:
        cat = _get_categoria(it)
        categorias[cat] = categorias.get(cat, 0) + _get_monto(it, tipo_dato)

    detalle = [
        {
            "categoria": cat,
            "total": round(v, 2),
            "porcentaje": (
                round((v / total_general) * 100, 1) if total_general > 0 else 0.0
            ),
        }
        for cat, v in sorted(
            categorias.items(), key=lambda x: x[1], reverse=True
        )
    ]

    return {
        "operacion": "porcentaje",
        "tipo_dato": tipo_dato,
        "total_general": round(total_general, 2),
        "moneda": MONEDA,
        "detalle": detalle,
    }


def _proyeccion_credito(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Proyecta el estado de pagos de compras a crédito.

    Calcula:
    - Total original de todas las compras
    - Total pagado hasta ahora
    - Total restante a pagar
    - Cantidad de cuotas pendientes
    - Estimación del próximo pago (suma de 1 cuota por cada compra activa)
    """
    if not items:
        return {
            "operacion": "proyeccion_credito",
            "tipo_dato": "compras_credito",
            "total_original": 0,
            "total_pagado": 0,
            "total_restante": 0,
            "cuotas_pendientes": 0,
            "estimado_proxima_cuota": 0,
            "compras_activas": 0,
            "cantidad_compras": 0,
            "moneda": MONEDA,
        }

    total_original = 0.0
    total_pagado = 0.0
    total_restante = 0.0
    cuotas_pendientes = 0
    estimado_proxima = 0.0
    compras_activas = 0

    for it in items:
        monto_total = float(it.get("montoTotal", 0))
        cantidad_cuotas = int(it.get("cantidadCuotas", 1))
        cuotas_pagadas = int(it.get("cuotasPagadas", 0))

        if cantidad_cuotas <= 0:
            continue

        monto_por_cuota = monto_total / cantidad_cuotas
        total_original += monto_total
        total_pagado += cuotas_pagadas * monto_por_cuota

        restantes = cantidad_cuotas - cuotas_pagadas
        if restantes > 0:
            total_restante += restantes * monto_por_cuota
            cuotas_pendientes += restantes
            estimado_proxima += monto_por_cuota
            compras_activas += 1

    return {
        "operacion": "proyeccion_credito",
        "tipo_dato": "compras_credito",
        "total_original": round(total_original, 2),
        "total_pagado": round(total_pagado, 2),
        "total_restante": round(total_restante, 2),
        "cuotas_pendientes": cuotas_pendientes,
        "estimado_proxima_cuota": round(estimado_proxima, 2),
        "compras_activas": compras_activas,
        "cantidad_compras": len(items),
        "moneda": MONEDA,
    }


# ─── Dispatcher principal ────────────────────────────────────────


def calcular(
    data_json: str,
    operacion: str,
    filtro_categoria: str | None = None,
    filtro_tipo: str | None = None,
) -> str:
    """Función principal: orquesta el cálculo solicitado sobre los datos.

    Args:
        data_json: JSON string con datos de transacciones o compras a crédito
                   (devuelto por ``tool_filtrar_transacciones`` o
                   ``tool_filtrar_compras_credito``).
        operacion: Operación a realizar.
                   Valores válidos: sumar, promedio, contar, minimo, maximo,
                   agrupar_por_categoria, balance, porcentaje, proyeccion_credito.
        filtro_categoria: Opcional. Filtra por nombre de categoría/motivo
                          (case-insensitive, búsqueda parcial).
        filtro_tipo: Opcional. Filtra por tipo de transacción (INGRESO o GASTO).
                     Solo aplica a transacciones (efectivo/débito).

    Returns:
        JSON string con el resultado estructurado del cálculo.

    Examples:
        >>> calcular(data_json, "sumar", filtro_tipo="GASTO")
        '{"operacion": "sumar", "total": 35000.0, ...}'
    """


    # 1. Validar operación
    op = operacion.lower().strip()
    if op not in OPERACIONES_VALIDAS:
        ops_str = ", ".join(sorted(OPERACIONES_VALIDAS))
        error_msg = (
            f"Operación '{operacion}' no válida. "
            f"Operaciones disponibles: {ops_str}"
        )
        logger.warning("calcular | %s", error_msg)
        return json.dumps(
            {"error": error_msg, "operacion": operacion}, ensure_ascii=False
        )

    # 2. Extraer items del JSON
    try:
        items = _extraer_items(data_json)
    except ValueError as e:
        logger.error("calcular | error extrayendo items: %s", str(e))
        return json.dumps(
            {"error": str(e), "operacion": operacion}, ensure_ascii=False
        )

    # 3. Detectar tipo de dato
    tipo_dato = _detectar_tipo(items)


    # 4. Validar compatibilidad operación ↔ tipo_dato
    #    (se saltea si la lista está vacía, ya que no podemos
    #    determinar el tipo real de datos vacíos)
    if items:
        if op == "balance" and tipo_dato != "transacciones":
            msg = (
                "La operación 'balance' solo está disponible para transacciones "
                "(efectivo/débito), no para compras a crédito."
            )
            logger.warning("calcular | %s", msg)
            return json.dumps(
                {"error": msg, "operacion": operacion}, ensure_ascii=False
            )

        if op == "proyeccion_credito" and tipo_dato != "compras_credito":
            msg = (
                "La operación 'proyeccion_credito' solo está disponible para "
                "compras a crédito."
            )
            logger.warning("calcular | %s", msg)
            return json.dumps(
                {"error": msg, "operacion": operacion}, ensure_ascii=False
            )

    # 5. Aplicar filtros comunes antes de la operación.
    #    NOTA: porcentaje y agrupar_por_categoria manejan el filtro
    #    de categoría internamente, porque necesitan el total GENERAL
    #    para calcular porcentajes correctos.
    if op in ("porcentaje", "agrupar_por_categoria"):
        # Solo aplicar filtro_tipo, NO filtro_categoria (lo maneja la función)
        items = _aplicar_filtros(items, tipo_dato, filtro_categoria=None, filtro_tipo=filtro_tipo)
    else:
        items = _aplicar_filtros(items, tipo_dato, filtro_categoria, filtro_tipo)

    # 6. Ejecutar operación
    operaciones_map: dict[str, Any] = {
        "sumar": lambda: _sumar(items, tipo_dato),
        "promedio": lambda: _promedio(items, tipo_dato),
        "contar": lambda: _contar(items, tipo_dato),
        "minimo": lambda: _minimo(items, tipo_dato),
        "maximo": lambda: _maximo(items, tipo_dato),
        "agrupar_por_categoria": lambda: _agrupar_por_categoria(items, tipo_dato),
        "balance": lambda: _balance(items),
        "porcentaje": lambda: _porcentaje(items, tipo_dato, filtro_categoria),
        "proyeccion_credito": lambda: _proyeccion_credito(items),
    }

    try:
        resultado = operaciones_map[op]()

        return json.dumps(resultado, ensure_ascii=False)
    except Exception as e:
        logger.error(
            "calcular | error en operacion %s: %s", op, str(e), exc_info=True
        )
        return json.dumps(
            {
                "error": f"Error interno al ejecutar '{op}': {e}",
                "operacion": op,
            },
            ensure_ascii=False,
        )
