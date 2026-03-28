import { apiClient } from '@/lib/api-client'
import type {
  CompraCreditoDTORequest,
  CompraCredito,
  CompraCreditoDTOResponse,
  ResumenTarjetaDTOResponse,
  PaginatedResponse,
  CompraCreditoBusquedaDTO,
} from '@/types'

export const compraCreditoService = {
  async registrarCompraCredito(compra: CompraCreditoDTORequest): Promise<CompraCredito> {
    const { data } = await apiClient.post<CompraCredito>('/comprascredito/registrar', compra)
    return data
  },

  async listarComprasPendientes(idEspacioTrabajo: string, page?: number, size?: number): Promise<PaginatedResponse<CompraCreditoDTOResponse>> {
    const params = new URLSearchParams()
    if (page !== undefined) params.append('page', page.toString())
    if (size !== undefined) params.append('size', size.toString())
    
    const url = `/comprascredito/pendientes/${idEspacioTrabajo}${params.toString() ? `?${params.toString()}` : ''}`
    const { data } = await apiClient.get<PaginatedResponse<CompraCreditoDTOResponse>>(url)
    return data
  },

  async buscarComprasCredito(busqueda: CompraCreditoBusquedaDTO): Promise<PaginatedResponse<CompraCreditoDTOResponse>> {
    const { data } = await apiClient.post<PaginatedResponse<CompraCreditoDTOResponse>>('/comprascredito/buscar', busqueda)
    return data
  },

  async removerCompraCredito(id: number): Promise<void> {
    await apiClient.delete(`/comprascredito/${id}`)
  },

  async listarResumenesPorTarjeta(idTarjeta: number): Promise<ResumenTarjetaDTOResponse[]> {
    const { data } = await apiClient.get<ResumenTarjetaDTOResponse[]>(`/comprascredito/resumenes/tarjeta/${idTarjeta}`)
    return data
  },

  async pagarResumenTarjeta(request: {
    idResumen: number
    fecha: string // formato 'yyyy-MM-dd'
    monto: number
    nombreCompletoAuditoria: string
    idEspacioTrabajo: string  // UUID
    idCuentaBancaria?: number
  }): Promise<void> {
    await apiClient.post('/comprascredito/pagar-resumen', request)
  },
}
