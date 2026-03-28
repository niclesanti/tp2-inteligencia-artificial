# Prompt Diario (Ultra-Compacto)

Usar con `Tech-Lead-Orchestrator` en modo Plan.

```md
Feature: [describir feature]
Scope: [incluye] | Excluye: [excluye]
Aceptación: [3 criterios verificables]

Flujo requerido:
1) Generar plan por paquetes (backend/frontend/integración).
2) Delegar backend a Backend-Lead y frontend a Frontend-Lead.
3) Pedir confirmación solo en decisiones no obvias.
4) Implementar end-to-end tras mi OK.

Validaciones mínimas:
- Backend: compile + tests + backend-health al final.
- Frontend: typecheck + build + tests relevantes.
- Integración: contrato DTO/API alineado.

Aplicar triage de revisión:
- Small: review final opcional.
- Medium/Large o seguridad/contratos: review final con Code-Reviewer-Lead.

Entrega final: archivos modificados, validaciones ejecutadas, riesgos pendientes.
Responder siempre en español.
```

# Prompt Extendido (Solo Features Grandes)

```md
# Contexto
Nueva feature en ProyectoGastos.

## Objetivo funcional
[qué debe lograr]

## Alcance
- Incluye: [módulos/pantallas/endpoints/entidades]
- Excluye: [fuera de alcance]
- Prioridad: [alta/media/baja]

## Requisitos funcionales
1. [RF1]
2. [RF2]
3. [RF3]

## Criterios de aceptación
1. [CA1]
2. [CA2]
3. [CA3]

## Plan y ejecución solicitados
1. Diseñar plan por paquetes y dependencias.
2. Separar backend/frontend/integración.
3. Marcar decisiones que requieran mi input.
4. Implementar de forma autónoma tras aprobación.

## Validación obligatoria
- Backend: compile + tests + backend-health.
- Frontend: typecheck + build + tests.
- Integración: verificar contratos DTO/API y flujos críticos.

## Cierre
Reportar: archivos, evidencias de validación, riesgos y próximos pasos.
Responder siempre en español.
```

# Uso recomendado

1. Para tareas diarias usa siempre el Prompt Diario (menos tokens).
2. Usa el Prompt Extendido solo para features cross-stack grandes.
3. Si falla algo, pedir: "iterar hasta verde manteniendo alcance".
