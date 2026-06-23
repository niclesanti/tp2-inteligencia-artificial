"""Tools determinísticas del agente financiero.

- ``calculator``: funciones de cálculo matemático/estadístico.
- ``finance_api``: clientes HTTP para consumir el backend Spring Boot.
"""

from app.tools.calculator import calcular

__all__ = ["calcular"]
