"""
Cliente HTTP para consumir las APIs financieras del backend Spring Boot.

Cada función construye el payload JSON, lo envía al endpoint
correspondiente y retorna la respuesta decodificada.

Todas las funciones son async y manejan errores de conexión/HTTP
para evitar que excepciones no capturadas lleguen al loop del agente.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 30


async def filtrar_transacciones(
    workspace_id: str,
    mes: int | None = None,
    anio: int | None = None,
    motivo: str | None = None,
    contacto: str | None = None,
    page: int | None = None,
    size: int | None = None,
) -> dict:
    """Llama a POST /api/internal/transaccion/buscar en el backend.

    Usa el endpoint interno (sin JWT) porque se ejecuta dentro de la red
    Docker, donde el agente ya fue autenticado por el frontend.

    Args:
        workspace_id: UUID del espacio de trabajo (obligatorio).
        mes, anio, motivo, contacto, page, size: filtros opcionales.

    Returns:
        Diccionario con la respuesta JSON del backend (estructura PaginatedResponse).

    Raises:
        ValueError: si el backend responde con error o hay problemas de conexión.
    """
    url = f"{settings.backend_url}/api/internal/transaccion/buscar"

    # Construir payload solo con campos no-None
    payload: dict = {"idEspacioTrabajo": workspace_id}
    if mes is not None:
        payload["mes"] = mes
    if anio is not None:
        payload["anio"] = anio
    if motivo is not None:
        payload["motivo"] = motivo
    if contacto is not None:
        payload["contacto"] = contacto
    if page is not None:
        payload["page"] = page
    if size is not None:
        payload["size"] = size



    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            return data
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error %s al llamar a transaccion/buscar: %s", e.response.status_code, e.response.text)
        raise ValueError(
            f"Error del backend al buscar transacciones (código {e.response.status_code}): "
            f"{e.response.text}"
        ) from e
    except httpx.RequestError as e:
        logger.error("Error de conexión al llamar a transaccion/buscar: %s", str(e))
        raise ValueError(
            f"No se pudo conectar con el backend para buscar transacciones: {e}"
        ) from e


async def filtrar_compras_credito(
    workspace_id: str,
    mes: int | None = None,
    anio: int | None = None,
    motivo: str | None = None,
    contacto: str | None = None,
    page: int | None = None,
    size: int | None = None,
) -> dict:
    """Llama a POST /api/internal/comprascredito/buscar en el backend.

    Usa el endpoint interno (sin JWT) porque se ejecuta dentro de la red
    Docker, donde el agente ya fue autenticado por el frontend.

    Args:
        workspace_id: UUID del espacio de trabajo (obligatorio).
        mes, anio, motivo, contacto, page, size: filtros opcionales.

    Returns:
        Diccionario con la respuesta JSON del backend (estructura PaginatedResponse).

    Raises:
        ValueError: si el backend responde con error o hay problemas de conexión.
    """
    url = f"{settings.backend_url}/api/internal/comprascredito/buscar"

    payload: dict = {"idEspacioTrabajo": workspace_id}
    if mes is not None:
        payload["mes"] = mes
    if anio is not None:
        payload["anio"] = anio
    if motivo is not None:
        payload["motivo"] = motivo
    if contacto is not None:
        payload["contacto"] = contacto
    if page is not None:
        payload["page"] = page
    if size is not None:
        payload["size"] = size



    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            return data
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error %s al llamar a comprascredito/buscar: %s", e.response.status_code, e.response.text)
        raise ValueError(
            f"Error del backend al buscar compras a crédito (código {e.response.status_code}): "
            f"{e.response.text}"
        ) from e
    except httpx.RequestError as e:
        logger.error("Error de conexión al llamar a comprascredito/buscar: %s", str(e))
        raise ValueError(
            f"No se pudo conectar con el backend para buscar compras a crédito: {e}"
        ) from e
