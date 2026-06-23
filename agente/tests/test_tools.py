"""
Tests unitarios para las tools determinísticas del agente financiero.

Cubre la calculadora estadística con datos de transacciones y compras
a crédito, incluyendo casos borde (listas vacías, JSON inválido,
operaciones no aplicables, filtros).
"""

import json

import pytest

from app.tools.calculator import calcular, OPERACIONES_VALIDAS


# ─── Fixtures: datos de prueba ───────────────────────────────────


@pytest.fixture
def transacciones_json() -> str:
    """JSON de ejemplo con 5 transacciones mixtas (INGRESO + GASTO)."""
    data = {
        "content": [
            {
                "id": 1,
                "monto": 50000.0,
                "tipo": "INGRESO",
                "nombreMotivo": "Sueldo",
                "fecha": "2025-01-01",
                "descripcion": "Sueldo enero",
            },
            {
                "id": 2,
                "monto": 15000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Alimentación",
                "fecha": "2025-01-02",
                "descripcion": "Supermercado",
            },
            {
                "id": 3,
                "monto": 8000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Transporte",
                "fecha": "2025-01-03",
                "descripcion": "Sube",
            },
            {
                "id": 4,
                "monto": 12000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Alimentación",
                "fecha": "2025-01-05",
                "descripcion": "Restaurante",
            },
            {
                "id": 5,
                "monto": 25000.0,
                "tipo": "INGRESO",
                "nombreMotivo": "Freelance",
                "fecha": "2025-01-10",
                "descripcion": "Proyecto freelance",
            },
        ],
        "totalElements": 5,
        "totalPages": 1,
        "currentPage": 0,
        "pageSize": 10,
        "first": True,
        "last": True,
    }
    return json.dumps(data)


@pytest.fixture
def transacciones_solo_gastos_json() -> str:
    """JSON de ejemplo con solo gastos."""
    data = {
        "content": [
            {
                "id": 2,
                "monto": 15000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Alimentación",
                "fecha": "2025-01-02",
                "descripcion": "Supermercado",
            },
            {
                "id": 3,
                "monto": 8000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Transporte",
                "fecha": "2025-01-03",
                "descripcion": "Sube",
            },
            {
                "id": 4,
                "monto": 12000.0,
                "tipo": "GASTO",
                "nombreMotivo": "Alimentación",
                "fecha": "2025-01-05",
                "descripcion": "Restaurante",
            },
        ],
        "totalElements": 3,
        "totalPages": 1,
        "currentPage": 0,
        "pageSize": 10,
        "first": True,
        "last": True,
    }
    return json.dumps(data)


@pytest.fixture
def compras_credito_json() -> str:
    """JSON de ejemplo con 3 compras a crédito en distintos estados."""
    data = {
        "content": [
            {
                "id": 101,
                "montoTotal": 60000.0,
                "cantidadCuotas": 12,
                "cuotasPagadas": 3,
                "nombreMotivo": "Electrónica",
                "fechaCompra": "2024-10-15",
                "descripcion": "Notebook",
                "nombreComercio": "Tienda Tech",
            },
            {
                "id": 102,
                "montoTotal": 24000.0,
                "cantidadCuotas": 6,
                "cuotasPagadas": 6,
                "nombreMotivo": "Indumentaria",
                "fechaCompra": "2024-08-20",
                "descripcion": "Ropa",
                "nombreComercio": "Tienda Moda",
            },
            {
                "id": 103,
                "montoTotal": 12000.0,
                "cantidadCuotas": 3,
                "cuotasPagadas": 1,
                "nombreMotivo": "Salud",
                "fechaCompra": "2025-01-10",
                "descripcion": "Consulta médica",
                "nombreComercio": "Clínica Salud",
            },
        ],
        "totalElements": 3,
        "totalPages": 1,
        "currentPage": 0,
        "pageSize": 10,
        "first": True,
        "last": True,
    }
    return json.dumps(data)


@pytest.fixture
def empty_json() -> str:
    """JSON con lista vacía."""
    data = {"content": [], "totalElements": 0}
    return json.dumps(data)


# ═══════════════════════════════════════════════════════════════════
# Tests: Sumar
# ═══════════════════════════════════════════════════════════════════


class TestSumar:
    def test_sumar_todas(self, transacciones_json):
        """Suma todas las transacciones sin filtros."""
        result = json.loads(calcular(transacciones_json, "sumar"))
        assert result["operacion"] == "sumar"
        assert result["tipo_dato"] == "transacciones"
        assert result["total"] == 110000.0  # 50000+15000+8000+12000+25000
        assert result["cantidad"] == 5
        assert result["moneda"] == "ARS"

    def test_sumar_solo_gastos(self, transacciones_json):
        """Suma solo GASTO usando filtro_tipo."""
        result = json.loads(calcular(transacciones_json, "sumar", filtro_tipo="GASTO"))
        assert result["total"] == 35000.0  # 15000+8000+12000
        assert result["cantidad"] == 3

    def test_sumar_solo_ingresos(self, transacciones_json):
        """Suma solo INGRESO usando filtro_tipo."""
        result = json.loads(
            calcular(transacciones_json, "sumar", filtro_tipo="INGRESO")
        )
        assert result["total"] == 75000.0  # 50000+25000
        assert result["cantidad"] == 2

    def test_sumar_compras_credito(self, compras_credito_json):
        """Suma montos totales de compras a crédito."""
        result = json.loads(calcular(compras_credito_json, "sumar"))
        assert result["tipo_dato"] == "compras_credito"
        assert result["total"] == 96000.0  # 60000+24000+12000
        assert result["cantidad"] == 3

    def test_sumar_lista_vacia(self, empty_json):
        """Suma con lista vacía debe retornar total 0."""
        result = json.loads(calcular(empty_json, "sumar"))
        assert result["total"] == 0
        assert result["cantidad"] == 0


# ═══════════════════════════════════════════════════════════════════
# Tests: Promedio
# ═══════════════════════════════════════════════════════════════════


class TestPromedio:
    def test_promedio_transacciones(self, transacciones_json):
        """Promedio de todas las transacciones."""
        result = json.loads(calcular(transacciones_json, "promedio"))
        assert result["operacion"] == "promedio"
        assert result["total"] == 22000.0  # 110000 / 5
        assert result["cantidad"] == 5

    def test_promedio_gastos(self, transacciones_json):
        """Promedio solo de gastos."""
        result = json.loads(
            calcular(transacciones_json, "promedio", filtro_tipo="GASTO")
        )
        assert result["total"] == pytest.approx(11666.67, rel=0.01)
        assert result["cantidad"] == 3

    def test_promedio_lista_vacia(self, empty_json):
        """Promedio con lista vacía debe retornar 0."""
        result = json.loads(calcular(empty_json, "promedio"))
        assert result["total"] == 0
        assert result["cantidad"] == 0


# ═══════════════════════════════════════════════════════════════════
# Tests: Contar
# ═══════════════════════════════════════════════════════════════════


class TestContar:
    def test_contar_transacciones(self, transacciones_json):
        """Cuenta todas las transacciones."""
        result = json.loads(calcular(transacciones_json, "contar"))
        assert result["total"] == 5
        assert result["cantidad"] == 5

    def test_contar_solo_ingresos(self, transacciones_json):
        """Cuenta solo ingresos."""
        result = json.loads(
            calcular(transacciones_json, "contar", filtro_tipo="INGRESO")
        )
        assert result["total"] == 2

    def test_contar_lista_vacia(self, empty_json):
        """Contar con lista vacía debe retornar 0."""
        result = json.loads(calcular(empty_json, "contar"))
        assert result["total"] == 0


# ═══════════════════════════════════════════════════════════════════
# Tests: Mínimo y Máximo
# ═══════════════════════════════════════════════════════════════════


class TestMinimo:
    def test_minimo_transacciones(self, transacciones_json):
        """Encuentra la transacción de menor monto."""
        result = json.loads(calcular(transacciones_json, "minimo"))
        assert result["total"] == 8000.0
        assert result["item"]["categoria"] == "Transporte"

    def test_minimo_lista_vacia(self, empty_json):
        """Mínimo con lista vacía."""
        result = json.loads(calcular(empty_json, "minimo"))
        assert result["total"] == 0


class TestMaximo:
    def test_maximo_transacciones(self, transacciones_json):
        """Encuentra la transacción de mayor monto."""
        result = json.loads(calcular(transacciones_json, "maximo"))
        assert result["total"] == 50000.0
        assert result["item"]["categoria"] == "Sueldo"

    def test_maximo_lista_vacia(self, empty_json):
        """Máximo con lista vacía."""
        result = json.loads(calcular(empty_json, "maximo"))
        assert result["total"] == 0


# ═══════════════════════════════════════════════════════════════════
# Tests: Agrupar por Categoría
# ═══════════════════════════════════════════════════════════════════


class TestAgruparPorCategoria:
    def test_agrupar_transacciones(self, transacciones_json):
        """Agrupa transacciones por categoría con porcentajes."""
        result = json.loads(
            calcular(transacciones_json, "agrupar_por_categoria")
        )
        assert result["operacion"] == "agrupar_por_categoria"
        assert result["total_general"] == 110000.0
        assert result["cantidad_total"] == 5

        categorias = {g["categoria"]: g for g in result["grupos"]}
        assert "Alimentación" in categorias
        assert "Sueldo" in categorias
        assert "Transporte" in categorias
        assert "Freelance" in categorias

        # Alimentación: 27000 / 110000 = 24.5%
        assert categorias["Alimentación"]["porcentaje"] == pytest.approx(24.5, rel=0.1)
        assert categorias["Alimentación"]["cantidad"] == 2

    def test_agrupar_solo_gastos(self, transacciones_json):
        """Agrupa solo gastos."""
        result = json.loads(
            calcular(
                transacciones_json,
                "agrupar_por_categoria",
                filtro_tipo="GASTO",
            )
        )
        assert result["total_general"] == 35000.0
        assert len(result["grupos"]) == 2  # Alimentación, Transporte

    def test_agrupar_lista_vacia(self, empty_json):
        """Agrupar con lista vacía."""
        result = json.loads(calcular(empty_json, "agrupar_por_categoria"))
        assert result["total_general"] == 0
        assert result["grupos"] == []

    def test_agrupar_compras_credito(self, compras_credito_json):
        """Agrupa compras a crédito por categoría."""
        result = json.loads(
            calcular(compras_credito_json, "agrupar_por_categoria")
        )
        assert result["tipo_dato"] == "compras_credito"
        assert result["total_general"] == 96000.0
        categorias = {g["categoria"]: g for g in result["grupos"]}
        assert "Electrónica" in categorias
        assert "Indumentaria" in categorias
        assert categorias["Electrónica"]["porcentaje"] == 62.5  # 60000/96000


# ═══════════════════════════════════════════════════════════════════
# Tests: Balance
# ═══════════════════════════════════════════════════════════════════


class TestBalance:
    def test_balance_transacciones(self, transacciones_json):
        """Balance: debe separar ingresos y gastos correctamente."""
        result = json.loads(calcular(transacciones_json, "balance"))
        assert result["operacion"] == "balance"
        assert result["total_ingresos"] == 75000.0
        assert result["total_gastos"] == 35000.0
        assert result["balance_neto"] == 40000.0
        assert result["cantidad_ingresos"] == 2
        assert result["cantidad_gastos"] == 3

    def test_balance_con_filtro_categoria(self, transacciones_json):
        """Balance filtrado por categoría."""
        result = json.loads(
            calcular(
                transacciones_json,
                "balance",
                filtro_categoria="Alimentación",
            )
        )
        assert result["total_gastos"] == 27000.0  # 15000+12000
        assert result["total_ingresos"] == 0.0

    def test_balance_lista_vacia(self, empty_json):
        """Balance con lista vacía."""
        result = json.loads(calcular(empty_json, "balance"))
        assert result["total_ingresos"] == 0
        assert result["total_gastos"] == 0
        assert result["balance_neto"] == 0

    def test_balance_no_aplica_credito(self, compras_credito_json):
        """Balance sobre datos de crédito debe dar error."""
        result = json.loads(calcular(compras_credito_json, "balance"))
        assert "error" in result


# ═══════════════════════════════════════════════════════════════════
# Tests: Porcentaje
# ═══════════════════════════════════════════════════════════════════


class TestPorcentaje:
    def test_porcentaje_categoria_especifica(self, transacciones_json):
        """% de una categoría específica."""
        result = json.loads(
            calcular(
                transacciones_json,
                "porcentaje",
                filtro_categoria="Alimentación",
            )
        )
        assert result["categoria"] == "Alimentación"
        assert result["total_categoria"] == 27000.0
        assert result["total_general"] == 110000.0
        assert result["porcentaje"] == pytest.approx(24.5, rel=0.1)

    def test_porcentaje_distribucion_completa(self, transacciones_json):
        """Distribución completa de % sin filtro de categoría."""
        result = json.loads(calcular(transacciones_json, "porcentaje"))
        assert "detalle" in result
        assert len(result["detalle"]) == 4
        assert result["total_general"] == 110000.0

    def test_porcentaje_lista_vacia(self, empty_json):
        """Porcentaje con lista vacía."""
        result = json.loads(calcular(empty_json, "porcentaje"))
        assert result["detalle"] == []


# ═══════════════════════════════════════════════════════════════════
# Tests: Proyección Crédito
# ═══════════════════════════════════════════════════════════════════


class TestProyeccionCredito:
    def test_proyeccion_completa(self, compras_credito_json):
        """Proyección de crédito con compras mixtas (activas y pagadas)."""
        result = json.loads(calcular(compras_credito_json, "proyeccion_credito"))
        assert result["operacion"] == "proyeccion_credito"
        assert result["tipo_dato"] == "compras_credito"
        # Total original: 60000+24000+12000 = 96000
        assert result["total_original"] == 96000.0
        # Compra 1: 60000/12=5000/cuota, 3 pagadas=15000
        # Compra 2: 24000/6=4000/cuota, 6 pagadas=24000 (total pagado)
        # Compra 3: 12000/3=4000/cuota, 1 pagada=4000
        # Total pagado: 15000+24000+4000 = 43000
        assert result["total_pagado"] == 43000.0
        # Restante: 96000-43000 = 53000
        assert result["total_restante"] == 53000.0
        # Cuotas pendientes: (12-3)+(6-6)+(3-1) = 9+0+2 = 11
        assert result["cuotas_pendientes"] == 11
        # Próxima cuota: 5000+4000 = 9000 (solo compras activas)
        assert result["estimado_proxima_cuota"] == 9000.0
        # Compras activas: 2 (compra 2 ya está pagada)
        assert result["compras_activas"] == 2

    def test_proyeccion_lista_vacia(self, empty_json):
        """Proyección con lista vacía."""
        result = json.loads(calcular(empty_json, "proyeccion_credito"))
        assert result["total_original"] == 0
        assert result["total_restante"] == 0

    def test_proyeccion_no_aplica_transacciones(self, transacciones_json):
        """Proyección sobre transacciones debe dar error."""
        result = json.loads(
            calcular(transacciones_json, "proyeccion_credito")
        )
        assert "error" in result


# ═══════════════════════════════════════════════════════════════════
# Tests: Casos borde y errores
# ═══════════════════════════════════════════════════════════════════


class TestErrores:
    def test_json_invalido(self):
        """JSON malformado debe retornar error."""
        result = json.loads(calcular("esto no es json", "sumar"))
        assert "error" in result

    def test_json_sin_content(self):
        """JSON sin campo content debe retornar error."""
        result = json.loads(calcular(json.dumps({"foo": "bar"}), "sumar"))
        assert "error" in result

    def test_operacion_invalida(self, transacciones_json):
        """Operación no reconocida debe retornar error con lista de válidas."""
        result = json.loads(
            calcular(transacciones_json, "operacion_inexistente")
        )
        assert "error" in result
        assert "Operación" in result["error"]

    def test_operacion_case_insensitive(self, transacciones_json):
        """La operación debe ser case-insensitive."""
        result = json.loads(calcular(transacciones_json, "SUMAR"))
        assert result["operacion"] == "sumar"
        assert result["total"] == 110000.0

    def test_filtro_categoria_parcial(self, transacciones_json):
        """Filtro de categoría con substring debe funcionar."""
        result = json.loads(
            calcular(transacciones_json, "sumar", filtro_categoria="Aliment")
        )
        assert result["total"] == 27000.0
        assert result["cantidad"] == 2

    def test_filtro_categoria_case_insensitive(self, transacciones_json):
        """Filtro de categoría debe ser case-insensitive."""
        result = json.loads(
            calcular(transacciones_json, "sumar", filtro_categoria="alimentación")
        )
        assert result["total"] == 27000.0

    def test_filtro_tipo_invalido_no_elimina(self, transacciones_json):
        """Filtro_tipo con valor no reconocido no debe romper (filtro sin efecto)."""
        result = json.loads(
            calcular(transacciones_json, "contar", filtro_tipo="OTRO")
        )
        assert result["total"] == 0  # ninguno coincide

    def test_todas_las_operaciones_tienen_test(self):
        """Verifica que todas las operaciones definidas estén cubiertas."""
        # Este test es informativo - verifica que OPERACIONES_VALIDAS tenga
        # al menos las operaciones documentadas
        esperadas = {
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
        assert esperadas.issubset(OPERACIONES_VALIDAS)
