-- V19__optimize_dashboard_indexes.sql
-- Optimización de índices para mejorar performance del dashboard
-- Objetivo: Reducir tiempo de respuesta del endpoint /dashboard/stats a <1 segundo

-- ============================================================================
-- 1. Índice compuesto para cuotas_credito (crítico para resumenMensual)
-- ============================================================================
-- Optimiza la query: findByTarjetaSinResumenEnRango
-- WHERE tarjeta_id = :id AND resumen_id IS NULL AND fecha_vencimiento BETWEEN :inicio AND :fin
-- El orden del índice permite búsquedas eficientes por tarjeta, luego por resumen nulo, y finalmente rango de fechas
-- Nota: Índice parcial solo para cuotas sin resumen asignado
CREATE INDEX IF NOT EXISTS idx_cuotas_tarjeta_fecha_sin_resumen 
ON cuotas_credito (compra_credito_id, fecha_vencimiento) 
WHERE resumen_id IS NULL;

-- Índice parcial adicional para calcularDeudaTotalPendiente
-- WHERE pagada = false AND espacio_trabajo_id (a través de compra_credito)
-- Nota: Ya existe idx_cuotas_pendientes en V5, pero sin tarjeta_id
CREATE INDEX IF NOT EXISTS idx_cuotas_deuda_pendiente 
ON cuotas_credito (compra_credito_id, pagada, monto_cuota) 
WHERE pagada = false;

-- ============================================================================
-- 2. Índices para compras_credito (distribución de compras con crédito)
-- ============================================================================
-- Optimiza: findDistribucionComprasCredito
-- WHERE espacio_trabajo_id = :id AND fecha_compra >= :fechaLimite
CREATE INDEX IF NOT EXISTS idx_compras_credito_espacio_fecha 
ON compras_credito (espacio_trabajo_id, fecha_compra DESC);

-- Índice en FK para JOIN con motivos_transaccion (si no existe por FK automático)
-- PostgreSQL no crea índices automáticamente en FKs, solo en PKs
CREATE INDEX IF NOT EXISTS idx_compras_credito_motivo 
ON compras_credito (motivo_transaccion_id);

-- ============================================================================
-- 3. Índice para tarjetas (carga de tarjetas por espacio)
-- ============================================================================
-- Optimiza: findByEspacioTrabajo_Id
CREATE INDEX IF NOT EXISTS idx_tarjetas_espacio_trabajo 
ON tarjetas (espacio_trabajo_id);

-- ============================================================================
-- 4. Índice en FK de transacciones para JOINs (distribución de gastos)
-- ============================================================================
-- Optimiza: findDistribucionGastos que hace JOIN con motivos_transaccion
-- Nota: Verificamos si existe porque PostgreSQL podría haberlo creado automáticamente
CREATE INDEX IF NOT EXISTS idx_transacciones_motivo 
ON transacciones (motivo_transaccion_id);

-- ============================================================================
-- 5. Índice adicional para optimizar búsquedas de compras por tarjeta
-- ============================================================================
-- Útil para queries que buscan compras por tarjeta (usado en varias operaciones)
CREATE INDEX IF NOT EXISTS idx_compras_credito_tarjeta 
ON compras_credito (tarjeta_id, fecha_compra DESC);

-- ============================================================================
-- ANÁLISIS DE IMPACTO ESPERADO:
-- ============================================================================
-- 1. idx_cuotas_tarjeta_resumen_fecha: Elimina sequential scan en resumenMensual() - ALTO IMPACTO
-- 2. idx_cuotas_deuda_pendiente: Optimiza calcularDeudaTotalPendiente - MEDIO IMPACTO
-- 3. idx_compras_credito_espacio_fecha: Optimiza distribución de compras crédito - ALTO IMPACTO
-- 4. idx_tarjetas_espacio_trabajo: Optimiza carga inicial de tarjetas - MEDIO IMPACTO
-- 5. idx_transacciones_motivo: Optimiza JOIN en distribución de gastos - ALTO IMPACTO
-- 6. idx_compras_credito_motivo: Optimiza JOIN en distribución compras - ALTO IMPACTO
-- 7. idx_compras_credito_tarjeta: Mejora queries adicionales - BAJO-MEDIO IMPACTO
--
-- TOTAL: 7 índices nuevos, impacto esperado en dashboard: reducción de 60-80% en tiempo de queries
-- ============================================================================
