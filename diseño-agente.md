1. INTRODUCCIÓN Y DEFINICIÓN DEL PROBLEMA

1.1. Descripción general del problema

Actualmente, contamos con una plataforma web de gestión de finanzas personales que
ofrece una solución centralizada y básica para el registro operativo de ingresos, gastos
corrientes y consumos con tarjetas de crédito. Si bien el sistema actual procesa y expone
métricas descriptivas e indicadores estadísticos básicos mediante tableros visuales
tradicionales, la interpretación profunda de estos datos sigue recayendo enteramente en el
esfuerzo cognitivo del usuario.
El problema radica en que los datos consolidados y estructurados en una base de datos
relacional son desaprovechados debido a que el usuario común carece del tiempo o de la
formación analítica para correlacionar datos.
Por lo tanto, se identifica una oportunidad para añadir valor al ecosistema de la aplicación
mediante la introducción de un componente de software autónomo y dotado de capacidades
de razonamiento. Este agente inteligente será capaz de interpretar el contexto contable del
usuario, ejecutar cálculos matemáticos precisos bajo demanda mediante interfaces
conversacionales en lenguaje natural y personalizar la experiencia del usuario,
transformando los datos crudos en conocimiento.

1.2. Definición del objetivo del agente

El objetivo del agente inteligente es consolidarse como un Asistente de Consulta Analítica
e Inteligencia Financiera. Su propósito principal es interactuar con el usuario mediante una
interfaz conversacional en lenguaje natural para resolver consultas analíticas específicas
sobre su información histórica de transacciones, ejecutar operaciones aritméticas precisas
sobre sus registros y proyectar escenarios financieros inmediatos a partir de los datos
existentes en la plataforma.
Para alcanzar este fin de manera balanceada, el agente perseguirá dos objetivos
específicos complementarios:

1.  Dimensión cuantitativa (acción y razonamiento lógico): Actuar como un motor de
consulta dinámico capaz de recuperar, filtrar y procesar registros contables
específicos (ingresos, gastos corrientes y cuotas de crédito), delegando los cálculos
numéricos a herramientas determinísticas para asegurar precisión matemática.
2.  Dimensión cualitativa (grounding y soporte pedagógico): Enriquecer las respuestas

analíticas inyectando contexto teórico contextualizado. El agente complementará los
datos duros del usuario con recomendaciones pedagógicas y consejos de salud
financiera, fundamentados rigurosamente en normativas vigentes, guías de buenas
prácticas y literatura de educación financiera pre-indexada.

2. ESPECIFICACIÓN DEL AGENTE

Para formalizar el diseño del sistema, se definen las dimensiones del ambiente,
percepciones y acciones del agente.

2.1. Especificación del ambiente de desenvolvimiento

El ambiente en el cual el agente opera posee las siguientes características:

●  Parcialmente observable: El agente sólo conoce la información que el usuario ha

cargado explícitamente en la base de datos (transacciones y tarjetas) y los
documentos de texto indexados; no tiene visibilidad de movimientos externos no
registrados.

●  Estocástico: El comportamiento de consumo del usuario en el mundo real introduce

un grado de incertidumbre en las proyecciones a futuro.

●  Secuencial: Las decisiones de gasto y las consultas previas influyen en el estado de

las cuentas y en la memoria del contexto conversacional para futuras interacciones.

●  Estático: El ambiente financiero del backend no cambia drásticamente mientras el
agente realiza un ciclo de razonamiento (el procesamiento de datos ocurre sobre
fotos fijas de la API).

●  Discreto: Las entidades financieras (transacciones, cuotas, categorías, fechas)

operan con valores y estados bien delimitados.

2.2. Identificación de percepciones y acciones (Tools)

Dimensión

Descripción técnica

Percepciones (Inputs)

Acciones (Outputs / Tools)

Mensajes en lenguaje natural enviados por
el usuario desde la UI de chat .Historial de
la conversación persistido en memoria
(Contexto). Estructuras de datos JSON
devueltas por la API del Backend
(Transacciones y Compras con Crédito).
Fragmentos de texto recuperados de la
base de conocimiento financiera (Vía RAG).

tool_filtrar_transacciones: Consulta
endpoints del Backend para recuperar
transacciones en efectivo/débito aplicando
filtros de fechas o categorías.
tool_filtrar_compras_credito: Recupera
consumos hechos con tarjeta de crédito,
con información sobre montos, cantidad de
cuotas pendientes y pagadas, fechas,
comercio.
tool_calculadora_estadistica: Módulo
determinístico encargado de agrupar por
categoría, sumar totales, calcular
promedios y proyectar saldos netos
basados en los JSON obtenidos (mitigando
fallas matemáticas del LLM).
tool_recuperacion_RAG: Ejecuta
búsquedas de similitud vectorial para
extraer recomendaciones teóricas de
ahorro ante desvíos de presupuesto.
Mensaje Final: Respuestas estructuradas al
usuario combinando el análisis cuantitativo
y cualitativo.

3. Definición de la arquitectura del agente: módulos, tecnologías y
componentes

Se propone una arquitectura desacoplada basada en un microservicio de Inteligencia
Artificial en Python, comunicándose bidireccionalmente con la infraestructura Java/React
existente mediante APIs REST.
3.1. Diagrama de componentes conceptuales

´´´plantuml
@startuml Diagrama_Componentes_FinanzasBot_Gateway

skinparam componentStyle uml2
skinparam backgroundColor white
skinparam handwritten false

skinparam Rectangle {
    BackgroundColor<<Infra>> #F1F5F9
    BorderColor<<Infra>> #94A3B8
}

skinparam Component {
    BackgroundColor<<App>> #E0F2FE
    BorderColor<<App>> #0284C7
    BackgroundColor<<Agent>> #F0FDF4
    BorderColor<<Agent>> #16A34A
    BackgroundColor<<Data>> #FEF3C7
    BorderColor<<Data>> #D97706
}

package "Capa de Presentación (UI)" {
    [Frontend (React / TS)] <<App>> as FE
}

package "Capa de Enrutamiento y Seguridad" {
    [API Gateway] <<App>> as GW
}

package "Capa de Negocio e Infraestructura Existente" {
    [Backend (Spring Boot API)] <<App>> as BE
    database "PostgreSQL\n(Datos Financieros)" <<Data>> as DB
}

package "Microservicio de IA (Python)" <<Agente>> {
    component "Orquestador del Agente\n(Pydantic AI + LLM)" <<Agent>> as Core
    
    package "Componentes Internos del Agente" {
        [Memoria Corto Plazo] <<Agent>> as ST_Mem
        [Tools] <<Agent>> as Tools
        [RAG] <<Agent>> as RAG
    }
    database "Qdrant Vector Store\n(Educación Financiera)" <<Data>> as VectorDB
    database "Redis Session Store\n(Memoria Contextual)" <<Data>> as Redis
}

' ---- FLUJOS Y COMUNICACIÓN ----

' El Frontend solo conoce al Gateway
FE --> GW : 1. Peticiones HTTP / Mensajes de Chat

' El Gateway redirige según el Endpoint
GW --> BE : [/api/*]\nRedirige operaciones comunes
GW --> Core : [/api/agente/*]\nRedirige flujo conversacional

' Persistencia tradicional y de contexto
BE --> DB : Consulta/Guarda estados financieros
Core <--> Redis : Consulta/Actualiza historial de chat

' Funcionamiento interno y percepción del Agente
Core <--> ST_Mem : Mantiene contexto del diálogo
Core --> Tools : Planifica acciones cuantitativas
Tools --> BE : 2. Consume Datos Crudos (Filtros de Transacciones/Crédito)
Core --> RAG : Dispara consulta pedagógica
RAG <--> VectorDB : Búsqueda por similitud semántica

@enduml
´´´

3.2. Módulos internos de la arquitectura del agente

1.  Capa de interfaz y orquestación (loop del agente): Controla el flujo de ejecución

del agente utilizando la estrategia ReAct (Reasoning and Acting). Recibe el prompt
del usuario, evalúa qué herramientas necesita activar, procesa las respuestas de las
herramientas y decide cuándo formular la respuesta final.

2.  Módulo de memoria contextual (persistencia): Almacena de forma persistente los
identificadores de sesión y el histórico de mensajes del chat. Garantiza la coherencia
conversacional para resolver la co-referencia en preguntas subsecuentes
(Short-Term memory en la ventana de contexto).

3.  Módulo RAG (Retrieval-Augmented Generation): Compuesto por un indexador de
documentos financieros y un motor de búsqueda vectorial que provee el marco
conceptual educativo para las recomendaciones analíticas del agente.

3.3. Justificación del stack tecnológico propuesto

Framework de agentes: Pydantic AI (Python)
Justificación: Se selecciona Pydantic AI debido a su enfoque "code-first". Al operar en un
dominio financiero y analítico, se requiere un control estricto y tipado estático sobre los
DTOs de entrada y salida de las herramientas (Tools) y las respuestas finales del agente.
Este framework mitiga los fallos de formato comunes en los LLMs, asegurando que las
estructuras JSON enviadas hacia el backend de Spring Boot cumplan estrictamente con los
contratos de la API REST sin requerir capas pesadas de orquestación basadas en grafos.

Modelo de lenguaje (Core LLM): Llama-3.3-70b-versatile (vía Groq API)
Justificación: En conformidad con las restricciones presupuestarias y operativas, se adopta
Llama-3.3-70b provisto por la infraestructura de inferencia de ultra alta velocidad de Groq.
Este modelo de pesos abiertos ofrece capacidades de razonamiento lógico, planificación
intermedio y Function Calling equivalentes a modelos comerciales cerrados, garantizando
un procesamiento eficiente de instrucciones conversacionales complejas y un seguimiento
estricto del contexto sin costo transaccional de tokens.

Base de datos vectorial (RAG): Qdrant (Servicio Dockerizado Externo)
Justificación: Para alinearse con la arquitectura de la plataforma, se descartan las
soluciones vectoriales embebidas en memoria no persistentes. Se opta por Qdrant
levantado de forma independiente mediante Docker Compose. Qdrant permite almacenar
los embeddings de las guías de salud financiera de manera persistente a través de
volúmenes, soportando búsquedas de similitud semántica por distancia coseno a nivel de
base de datos y facilitando el filtrado por metadatos estructurados de forma aislada y
eficiente.

Persistencia de memoria conversacional: Redis
Justificación: Para dar cumplimiento al requisito obligatorio de memoria conversacional, se
implementa un almacenamiento de sesiones indexado por `session_id`. Se opta por Redis
para actuar como la memoria de corto plazo del agente. Este componente permite recuperar
de forma secuencial los últimos turnos de diálogo del usuario antes de cada inferencia. Esto
dota al modelo de la capacidad de resolver co-referencias gramaticales y mantener la
coherencia del contexto analítico durante toda la sesión interactiva, aislando este flujo
transaccional veloz de la base de datos vectorial del RAG.

Conectividad entre sistemas: REST API (JSON / HTTP)
Justificación: El microservicio del agente inteligente se desacopla completamente del
backend principal de la aplicación mediante interfaces REST. El contenedor de Python
consume endpoints dedicados expuestos por Spring Boot para leer el historial transaccional
del usuario pasando el identificador de contexto correspondiente (`workspace_id`). Esto
preserva la modularidad del sistema, respeta el principio de única responsabilidad para este
microservicio y evita la duplicación innecesaria de la lógica de acceso a datos de
PostgreSQL en múltiples lenguajes de programación.

