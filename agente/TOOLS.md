# Tools del Asistente Financiero

El agente dispone de 3 tools determinísticas para asistir al usuario. El
LLM **nunca** debe realizar cálculos aritméticos por sí mismo; siempre
debe delegarlos a `tool_calculadora_estadistica`.

---

## tool_filtrar_transacciones

**Propósito**: Recuperar ingresos y gastos registrados en cuentas corrientes
(efectivo/débito) del usuario.

**Filtros disponibles**:

| Parámetro  | Tipo   | Requerido | Descripción                              |
|------------|--------|-----------|------------------------------------------|
| `mes`      | int    | No        | Mes (1–12). Requiere `anio` si se usa.   |
| `anio`     | int    | No        | Año (ej: 2025).                          |
| `motivo`   | string | No        | Texto para filtrar por motivo/categoría. |
| `contacto` | string | No        | Nombre del contacto/comercio.            |
| `page`     | int    | No        | N° de página (0‑based).                  |
| `size`     | int    | No        | Resultados por página.                   |

**Salida**: JSON con lista paginada de transacciones (`content`).

---

## tool_filtrar_compras_credito

**Propósito**: Recuperar compras realizadas con tarjeta de crédito.

**Filtros disponibles**: mismos que `tool_filtrar_transacciones`.

**Salida**: JSON con lista paginada de compras. Cada item incluye:
`montoTotal`, `cantidadCuotas`, `cuotasPagadas`, datos de tarjeta,
comercio, motivo y fechas.

---

## tool_calculadora_estadistica

**Propósito**: Ejecutar cálculos matemáticos determinísticos sobre los
datos devueltos por las tools de filtrado. El LLM **siempre** debe usar
esta tool para cualquier operación numérica.

**Parámetros**:

| Parámetro         | Tipo   | Requerido | Descripción                                          |
|-------------------|--------|-----------|------------------------------------------------------|
| `data_json`       | string | Sí        | JSON devuelto por `tool_filtrar_transacciones` o `tool_filtrar_compras_credito`. |
| `operacion`       | string | Sí        | Ver operaciones disponibles abajo.                   |
| `filtro_categoria`| string | No        | Filtra por nombre de categoría/motivo.               |
| `filtro_tipo`     | string | No        | Filtra por tipo: `INGRESO` o `GASTO` (solo transacciones). |

**Operaciones disponibles**:

| Operación               | Data soportada    | Qué calcula                                                        |
|-------------------------|-------------------|--------------------------------------------------------------------|
| `sumar`                 | Transacc., Créd.  | Suma total de montos.                                              |
| `promedio`              | Transacc., Créd.  | Promedio de montos.                                                |
| `contar`                | Transacc., Créd.  | Cantidad de elementos.                                             |
| `minimo`                | Transacc., Créd.  | Elemento de menor monto (+ detalle).                               |
| `maximo`                | Transacc., Créd.  | Elemento de mayor monto (+ detalle).                               |
| `agrupar_por_categoria` | Transacc., Créd.  | Total, cantidad y **%** agrupado por categoría (`nombreMotivo`).   |
| `balance`               | Solo Transacc.    | Total ingresos, total gastos y neto.                               |
| `porcentaje`            | Transacc., Créd.  | % de una categoría específica o distribución completa.             |
| `proyeccion_credito`    | Solo Crédito      | Cuotas pendientes, monto restante y estimación del próximo pago.   |

**Salida**: JSON estructurado con resultados numéricos precisos.
Siempre incluye los campos `operacion`, `tipo_dato` y `moneda`.
