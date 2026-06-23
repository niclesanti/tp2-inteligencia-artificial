## 🏗️ Propuesta de Estructura de Directorios para `/agente`

Dado que están trabajando en un **monorepo**, el objetivo es que el microservicio de IA en Python sea completamente autocontenido y respetuoso de la arquitectura desacoplada que plantearon en su informe.

Aquí tienen la estructura recomendada para el nuevo directorio `/agente`:

```text
/agente
│── .env.example                  # Variables de entorno (Groq API Key, DB URLs, etc.)
│── Dockerfile                    # Dockerización del microservicio de IA
│── requirements.txt              # Dependencias (pydantic-ai, fastapi, qdrant-client, redis, etc.)
│
├── app/
│   │── __init__.py
│   │── main.py                   # Punto de entrada (FastAPI / Uvicorn)
│   │
│   ├── core/                     # Configuración central y variables globales
│   │   │── config.py             # Lectura de variables de entorno con Pydantic Settings
│   │   └── security.py           # Validaciones de seguridad iniciales
│   │
│   ├── agent/                    # El corazón del Agente Inteligente
│   │   │── __init__.py
│   │   │── orchestrator.py       # Definición del Agent de Pydantic AI y el loop ReAct
│   │   │── prompts.py            # System Prompts, Directrices Financieras y Persona
│   │   └── dependencies.py       # Dependencias inyectadas al contexto del agente (banco, etc.)
│   │
│   ├── tools/                    # Herramientas determinísticas del agente (Acciones)
│   │   │── __init__.py
│   │   │── finance_api.py        # Clientes HTTP para consumir el Backend de Spring Boot
│   │   │── calculator.py         # Módulo matemático/estadístico determinístico
│   │   └── schemas.py            # Modelos Pydantic (DTOs) para inputs/outputs de las tools
│   │
│   ├── rag/                      # Pipeline de Recuperación y Conocimiento
│   │   │── __init__.py
│   │   │── connection.py         # Conector con la base de datos vectorial Qdrant
│   │   │── retriever.py          # Lógica de búsqueda semántica y filtrado por metadatos
│   │   └── ingester.py           # Script para chunking y carga de guías de salud financiera
│   │
│   ├── memory/                   # Gestión de persistencia de contexto
│   │   │── __init__.py
│   │   └── redis_store.py        # Manejo de sesiones e historial de chat en Redis
│   │
│   └── services/                 # Capa de servicios auxiliares o de observabilidad
│       └── logging_config.py     # Configuración de trazas/logs de llamadas a LLM y Tools
│
└── tests/                        # Set de pruebas (Happy path, límites, adversariales)
    │── __init__.py
    │── test_tools.py             # Pruebas unitarias determinísticas
    └── test_agent_responses.py   # Pruebas con LLM-as-a-judge o evaluaciones manuales

```

---

## 🔍 Desglose Metodológico de los Componentes Clave

Para asegurar el rigor académico que exige la cátedra, analicemos el "por qué" y el "cómo" de algunos de estos directorios bajo el marco teórico de los sistemas basados en agentes:

### 1. El corazón del Agente (`app/agent/`)

* 
**`orchestrator.py`**: Aquí instanciarán el objeto `Agent` de Pydantic AI. Utilizará el modelo `Llama-3.3-70b-versatile` a través de Groq. Este archivo manejará el bucle **ReAct (Reasoning and Acting)**.


* 
**`prompts.py`**: El *System Prompt* debe delimitar de manera estricta el alcance del agente. Debe incluir instrucciones explícitas para prohibir que el LLM intente hacer cálculos matemáticos por sí mismo, obligándolo a delegar esas tareas en la `tool_calculadora_estadistica`.



### 2. Dimensión Cuantitativa (`app/tools/`)

* 
**`finance_api.py`**: Dado que en esta primera fase el API Gateway no existe, este módulo se comunicará **directamente** con los endpoints que el backend de Spring Boot ya expone. Consumirá los JSON de transacciones y cuotas pasando el parámetro `workspace_id`.


* 
**`calculator.py`**: Recibe las estructuras JSON crudas de las transacciones. Al ser código Python nativo, garantiza un **comportamiento determinístico** para sumar totales, promediar gastos o proyectar saldos, mitigando por completo las debilidades aritméticas de los modelos de lenguaje.



### 3. Dimensión Cualitativa (`app/rag/`)

* 
**`retriever.py`**: Cuando el agente detecte que el usuario necesita educación financiera (por ejemplo, ante desvíos de presupuesto), invocará la herramienta de RAG. Qdrant resolverá la búsqueda por similitud semántica empleando distancia coseno y devolverá los fragmentos teóricos más relevantes para inyectarlos en el contexto del LLM.



---

## 🐳 Ajustes en el Entorno Docker del Monorepo

Para que este microservicio coexista armónicamente con `/frontend` y `/backend`, deberán actualizar sus archivos de Docker Compose en la raíz del proyecto. Deberán añadir:

1. El servicio propio de la app de Python (`/agente`).
2. La base de datos vectorial **Qdrant**.


3. El almacén de datos en memoria **Redis** para la memoria a corto plazo.

