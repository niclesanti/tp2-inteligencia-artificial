"""
Esquemas Pydantic para las tools del agente financiero.

Reflejan los DTOs del backend Spring Boot para garantizar
contratos REST tipados y evitar alucinaciones del LLM en la
estructura de datos.
"""

from pydantic import BaseModel
from typing import Any, Optional


# ─── Transacciones (cuentas corrientes: efectivo/débito) ───

class TransaccionResponse(BaseModel):
    """Refleja TransaccionDTOResponse del backend (versión mínima)."""
    fecha: str
    monto: float
    tipo: str                     # INGRESO | GASTO
    nombreMotivo: Optional[str] = None
    nombreContacto: Optional[str] = None
    descripcion: Optional[str] = None


# ─── Compras a crédito (tarjetas de crédito) ───

class CompraCreditoResponse(BaseModel):
    """Refleja CompraCreditoDTOResponse del backend (versión mínima)."""
    fechaCompra: str
    montoTotal: float
    cantidadCuotas: int
    cuotasPagadas: int
    nombreMotivo: Optional[str] = None
    nombreComercio: Optional[str] = None
    numeroTarjeta: Optional[str] = None
    descripcion: Optional[str] = None


# ─── Respuesta paginada (wrapper genérico) ───

class PaginatedResponse(BaseModel):
    """Refleja PaginatedResponse<T> del backend Spring Boot."""
    content: list[Any]
    totalElements: int
    totalPages: int
    currentPage: int
    pageSize: int
    first: bool
    last: bool
    hasPrevious: bool
    hasNext: bool


# ─── Inputs para las tools del agente ───

class FiltrarTransaccionesInput(BaseModel):
    """Parámetros que acepta filtrar_transacciones.
    
    NOTA: mes solo puede usarse si también se proporciona anio.
    """
    workspace_id: str
    mes: Optional[int] = None      # 1-12
    anio: Optional[int] = None     # 2000-2100
    motivo: Optional[str] = None
    contacto: Optional[str] = None
    page: Optional[int] = None
    size: Optional[int] = None


class FiltrarComprasCreditoInput(BaseModel):
    """Parámetros que acepta filtrar_compras_credito.
    
    NOTA: mes solo puede usarse si también se proporciona anio.
    """
    workspace_id: str
    mes: Optional[int] = None
    anio: Optional[int] = None
    motivo: Optional[str] = None
    contacto: Optional[str] = None
    page: Optional[int] = None
    size: Optional[int] = None
