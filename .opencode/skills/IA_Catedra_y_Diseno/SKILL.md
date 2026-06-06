---
name: IA_Catedra_y_Diseno
description: >
  Use ONLY when you need to validate generated code against the theoretical
  guidelines of the IA course (UTN-FRSF, Dr. Jorge Roa & Dra. Milagros Gutierrez)
  and/or against the design decisions of the 'Asistente de Consulta Analitica e
  Inteligencia Financiera' agent. This skill indexes ALL Jupyter notebooks from
  the 4 classes (tokenization, LLMs, RAG, evaluation, agents) plus the agent
  design document. It serves as the exclusive RAG source for conformance checking
  — do NOT rely on general knowledge when this skill is loaded.
---

# IA_Catedra_y_Diseno — Base de Conocimiento RAG

## Fuentes indexadas

| # | Archivo | Descripcion |
|---|---------|-------------|
| 1 | `teoria-materia-inteligencia-artificial/clase01/vectores_slides.ipynb` | Tokenizacion y Vectorizacion en NLP y LLMs |
| 2 | `teoria-materia-inteligencia-artificial/clase02/clase2_slides.ipynb` | LLMs: Arquitectura, Ciclo de Vida y Prompting |
| 3 | `teoria-materia-inteligencia-artificial/clase02/notebooks/01_groq_intro.ipynb` | Practica: primera llamada a LLM via Groq |
| 4 | `teoria-materia-inteligencia-artificial/clase02/notebooks/03_sampling_params.ipynb` | Practica: temperature, top_p, top_k |
| 5 | `teoria-materia-inteligencia-artificial/clase02/notebooks/04_prompting_techniques.ipynb` | Practica: zero-shot, one-shot, few-shot |
| 6 | `teoria-materia-inteligencia-artificial/clase03/clase3_slides.ipynb` | RAG: Retrieval Augmented Generation |
| 7 | `teoria-materia-inteligencia-artificial/clase03/clase3b_slides.ipynb` | Evaluacion, monitoreo y benchmarks de sistemas LLM |
| 8 | `teoria-materia-inteligencia-artificial/clase03/notebooks/01_arize_eval_handson.ipynb` | Practica: eval + monitoring con Arize AX |
| 9 | `teoria-materia-inteligencia-artificial/clase03/notebooks/rag/practica_completa.ipynb` | Practica: pipeline RAG naive punta a punta |
| 10 | `teoria-materia-inteligencia-artificial/clase03/notebooks/rag/practica_legal.ipynb` | Practica: RAG legal sobre Ley 21.526 (hybrid + reranker) |
| 11 | `teoria-materia-inteligencia-artificial/clase04/clase4_slides.ipynb` | Agentes, Multiagentes y Deep Agents |
| 12 | `teoria-materia-inteligencia-artificial/clase04/notebooks/react_tools_scratch.ipynb` | Practica 1: ReAct desde cero + LangGraph |
| 13 | `teoria-materia-inteligencia-artificial/clase04/notebooks/multiagente_langgraph.ipynb` | Practica 2: Multiagente con LangGraph (orquestador) |
| 14 | `teoria-materia-inteligencia-artificial/clase04/notebooks/deepagents_harness.ipynb` | Practica 3: Deep agent con deepagents (Tier 2 harness) |
| 15 | `diseno-agente.md` | Documento de diseno del Asistente de Consulta Analitica e Inteligencia Financiera |
| 16 | `teoria-materia-inteligencia-artificial/README.md` | README del repositorio de catedra |

---

## Contenido indexado

### Clase 1 — Tokenizacion y Vectorizacion

**Archivo:** `clase01/vectores_slides.ipynb`

**Conceptos clave:**
- El problema fundamental: las maquinas no entienden texto crudo; debe convertirse a numeros.
- **Tokenizacion**: character-level, word-level, subword-level (gana en la practica).
- **Algoritmos subword**: BPE (GPT, Llama, Mistral), WordPiece (BERT), SentencePiece (T5, Llama 2).
- **Byte-level BPE**: opera sobre bytes, nunca falla en ningun caracter/emoji (desde GPT-2+).
- **Tiktoken**: implementacion de BPE de OpenAI (cl100k_base, o200k_base).
- **One-hot encoding**: limitaciones (sin similaridad semantica, sparse, vectores grandes).
- **Bag of Words (BoW)**: documento como vector de conteos, pierde orden de palabras.
- **TF-IDF**: pondera hacia abajo palabras comunes, hacia arriba terminos distintivos.
- **Word embeddings** (Word2Vec, GloVe, FastText): vectores densos, analogias semanticas (`king - man + woman = queen`).
- **Limitacion de embeddings estaticos**: un vector por palabra sin importar contexto (problema de polisemia).
- **Sentence Transformers**: embeddings contextuales, un vector por oracion (Siamese BERT), construidos sobre Transformer.
- **Metricas de similaridad**: coseno (default en NLP), producto punto (igual al coseno si normalizado), Euclidea/L2 (menos adecuada para texto).
- **Vector stores**: ChromaDB, FAISS, Pinecone, Milvus, pgvector — indexacion HNSW, busqueda ANN.

---

### Clase 2 — LLMs

**Archivo:** `clase02/clase2_slides.ipynb`

**Conceptos clave:**
- Un LLM son **dos archivos en disco**: un blob de parametros (~140 GB para 70B) + un programa corto que multiplica matrices.
- **Training = compresion**: ~10 TB de texto comprimidos en ~140 GB de pesos (proporcion 70:1 con perdida).
- **Prediccion del siguiente token**: objetivo simple que fuerza a la red a aprender gramatica, hechos, razonamiento, formato.
- **La alucinacion es arquitectural**: el modelo siempre genera la continuacion mas plausible, exista o no en la realidad.
- **Arquitectura Transformer** (Vaswani et al., 2017): encoder-decoder para traduccion; los LLMs modernos son decoder-only.
- **Mecanismo de atencion**: el vector de cada token se actualiza absorviendo informacion ponderada de otros tokens (resuelve polisemia).
- **QKV (Query/Key/Value)**: el "buscador" dentro de la red — match(Q,K) da pesos, suma ponderada de V produce nueva representacion.
- **Ciclo de vida del modelo**: Pretraining (base model) -> SFT (supervised fine-tuning on conversations) -> RLHF o DPO (alignment).
- **RLHF**: pipeline de 3 pasos (recoger comparaciones -> entrenar reward model -> optimizacion PPO con penalidad KL).
- **DPO**: optimizacion directa desde preferencias, salteando el reward model.
- **Scaling laws**: el rendimiento mejora predeciblemente con mas parametros, mas datos, mas computo.
- **Test-time compute**: chain-of-thought, razonamiento extendido en inferencia.
- **Prompt engineering**: roles system/user, temperatura, top_p, top_k, zero/one/few-shot.

**Practicas:**
- `01_groq_intro.ipynb`: Primera llamada a LLM via Groq API. Efecto de temperature, efecto del system prompt.
- `03_sampling_params.ipynb`: Sampling con temperature, top_p, top_k. Mismo prompt con Llama, Qwen, DeepSeek, Gemma en Groq.
- `04_prompting_techniques.ipynb`: Zero-shot, one-shot y few-shot para clasificacion de sentimiento y triaje de tickets de soporte. **Leccion clave**: few-shot no ensena a clasificar al modelo (ya sabe), sino que fija el formato exacto, resuelve ambiguedad de clases y ancla el vocabulario.

---

### Clase 3 — RAG (Retrieval Augmented Generation)

**Archivo:** `clase03/clase3_slides.ipynb`

**Conceptos clave:**
- **Tres problemas que RAG resuelve**: knowledge cutoff, alucinaciones, limites de ventana de contexto.
- **Pipeline RAG**: Index (chunk -> embed -> store) -> Retrieve (query -> embed -> search) -> Augment (context + query -> prompt) -> Generate.
- **Estrategias de chunking**: tamano fijo, por oracion, por parrafo, recursive (default de LangChain).
- **Trade-offs de chunk size**: chico (64-128 tokens) para alta precision; medio (256-512) como sweet spot; grande (1024+) para legal/tecnico.
- **Seleccion del embedding**: mismo modelo para chunks y queries, multilingual vs especifico, dimensionalidad.
- **Busqueda hibrida (Hybrid search)**: BM25 (keyword) + dense (semantico) combinados con RRF (Reciprocal Rank Fusion).
- **Reranking**: cross-encoder reranker re-ordena top-k para precision (agrega valor en corpus tecnicos/legales).
- **RAG Avanzado**: HyDE (hypothetical document embedding), parent-child chunking, GraphRAG, multi-hop retrieval.
- **Diseno del prompt de aumentacion**: restringir LLM al contexto solo, numerar chunks para citas, colocar query al final (recency bias).

**Practicas:**
- `practica_completa.ipynb`: RAG naive de punta a punta sobre el programa de la catedra (5 docs). Corpus -> chunking -> ChromaDB -> retrieval -> augmentation -> generation. Prueba con 3 queries (lookup directo, multi-fact, edge case).
- `practica_legal.ipynb`: Naive vs Hybrid (BM25+dense+RRF) + reranker sobre Ley 21.526 de Entidades Financieras (~91k chars, 67 articulos). **Regla de oro**: Empeza por dense solo. Si funciona en TU corpus con TUS queries, deja asi. Subi a hybrid cuando el dominio tenga terminos tecnicos. Subi al reranker solo cuando una metrica concreta te diga que vale la pena.

---

### Clase 3b — Evaluacion, monitoreo y benchmarks

**Archivo:** `clase03/clase3b_slides.ipynb`

**Conceptos clave:**
- **Por que el eval de LLMs difiere del ML clasico**: output abierto, subjetividad, no-determinismo, alucinacion confiada.
- **Metricas reference-based**: BLEU, ROUGE, METEOR, BERTScore (necesitan ground truth).
- **Metricas reference-free**: exact match, regex, LLM-as-judge, faithfulness, relevance.
- **Deteccion de alucinaciones**: SelfCheckGPT, citation-based, faithfulness-via-NLI, token-level uncertainty.
- **Tracing y observabilidad**: OpenTelemetry spans, traces end-to-end (retrieve -> rerank -> generate).
- **Pre-deploy eval**: golden datasets, LLM-as-judge, RAGAS, safety/red-teaming, custom benchmarks.
- **Patrones de deploy**: A/B testing, shadow deployment, canary releases, prompt versioning.
- **Monitoreo en produccion**: cost/latency tracking, drift detection (data drift, label drift, concept drift), feedback loops.
- **Ciclo de vida del eval**: design -> offline eval -> production -> online eval -> analysis -> feedback -> iterate.

**Practica:**
- `01_arize_eval_handson.ipynb`: End-to-end con Arize AX. Build Q&A chatbot, create golden dataset, LLM-as-judge eval, instrument with OpenTelemetry, dashboards, simulate drift.

---

### Clase 4 — Agentes, Multiagentes y Deep Agents

**Archivo:** `clase04/clase4_slides.ipynb`

**Conceptos clave:**
- **Agente = LLM + tools + memory + loop**: el LLM dirige, no solo responde.
- **Diferencia clave LLM vs Agente**: prompt->text (one-shot) vs objective->sequence of actions (iterativo).
- **Agent loop**: Perceive -> Reason -> Act -> Observe (mas re-perceive for exogenous changes).
- **Anatomy de un agente**: LLM (cerebro), memory (short/long term), tools (manos), planner, control module (seguridad).
- **Patron ReAct** (Yao et al., 2022): razonamiento y accion intercalados en loop explicito Thought/Action/Observation.
- **Tool calling**: los modelos retornan nativamente JSON estructurado para invocacion de funciones (no parsing de texto).
- **MCP (Model Context Protocol)**: estandar abierto de Anthropic (2024); transforma integraciones MxN en M+N; "USB-C para tools de agente".
- **Patrones multi-agente**: Sequential (prompt chaining), Router (classify+delegate), Orchestrator (plan+delegate+aggregate), Parallel, Hierarchical.
- **A2A (Agent-to-Agent)**: protocolo de Google (2025, ahora Linux Foundation); descubrimiento via Agent Cards, comunicacion task-based sobre HTTP+JSON-RPC+SSE.
- **MCP + A2A son complementarios**: MCP conecta agentes a tools; A2A conecta agentes a otros agentes.
- **Tier 1 vs Tier 2**: Frameworks (LangGraph, smolagents, LlamaIndex, CrewAI, **PydanticAI**) donde construis el loop vs Deep-agent harnesses (deepagents, Claude Agent SDK, opencode) que proveen loop opinado con planner, subagentes y filesystem out-of-the-box.
- **2026 state of the art**: OpenClaw, Hermes Agent (self-improving loop), OpenHands (autonomous software engineering).
- **Limites actuales**: reliability (errores compuestos), cost (multiplicacion de llamadas al LLM), latency (segundos a minutos), security (necesita human-in-the-loop, sandboxing).
- **RAG se convierte en una tool**: el sistema RAG de la Clase 3 es una herramienta mas dentro del toolset del agente (alimenta directamente el proyecto integrador).

**Practicas:**
- `react_tools_scratch.ipynb`: **Parte A** — Loop ReAct a mano en Python (~30 lineas). Parseo de texto `Thought/Action/Observation`. El LLM NO ejecuta las herramientas, solo genera texto; nuestro codigo parsea, ejecuta la funcion Python, y devuelve el `Observation`. **Parte B** — Lo mismo con LangGraph (`StateGraph` + `ToolNode` + `tools_condition`). Tools: `calculadora` y `buscar_web`.
- `multiagente_langgraph.ipynb`: Patron **Orquestador** con LangGraph. Manager que recibe tarea, delega en Investigador, Redactor, Revisor y agrega resultados. Corre en Colab con Groq.
- `deepagents_harness.ipynb`: Misma tarea pero con **deepagents** (Tier 2 harness de LangChain). Planner, subagentes, filesystem virtual vienen de fabrica. Corre con Groq, busqueda web real opcional con Tavily.

---

### Documento de Diseno del Agente

**Archivo:** `diseno-agente.md`

#### 1. Definicion del Problema

Plataforma web de gestion de finanzas personales existente (Spring Boot + React). Se identifica oportunidad para agregar un **componente de software autonomo con capacidades de razonamiento** que interprete contexto contable, ejecute calculos matematicos precisos bajo demanda y personalice la experiencia del usuario.

#### 2. Objetivo del Agente

**Asistente de Consulta Analitica e Inteligencia Financiera.** Interactua via lenguaje natural para resolver consultas analiticas sobre historial de transacciones, ejecutar operaciones aritmeticas precisas y proyectar escenarios financieros.

**Dos dimensiones complementarias:**
1. **Cuantitativa (accion y razonamiento logico)**: motor de consulta dinámico que recupera, filtra y procesa registros contables, delegando calculos numericos a herramientas deterministicas.
2. **Cualitativa (grounding y soporte pedagogico)**: inyecta contexto teorico con recomendaciones pedagogicas y consejos de salud financiera basados en normativas y literatura pre-indexada.

#### 3. Especificacion del Ambiente (PEAS)

| Propiedad | Valor |
|-----------|-------|
| **Parcialmente observable** | Solo conoce informacion cargada explicitamente en la BD |
| **Estocastico** | Comportamiento de consumo introduce incertidumbre en proyecciones |
| **Secuencial** | Decisiones previas y consultas influyen en estado futuro |
| **Estatico** | Backend no cambia durante el ciclo de razonamiento |
| **Discreto** | Entidades financieras con valores y estados bien delimitados |

#### 4. Percepciones y Acciones (Tools)

| Percepciones (Inputs) | Acciones (Outputs / Tools) |
|----------------------|---------------------------|
| Mensajes en lenguaje natural desde UI de chat | `tool_filtrar_transacciones`: consulta endpoints del Backend |
| Historial de conversacion persistido (Contexto) | `tool_filtrar_compras_credito`: recupera consumos con tarjeta |
| Estructuras JSON de API del Backend (Transacciones y Creditos) | `tool_calculadora_estadistica`: modulo deterministico para agrupar, sumar, promediar, proyectar |
| Fragmentos de RAG (base de conocimiento financiera) | `tool_recuperacion_RAG`: busquedas de similaridad vectorial |
| | Mensaje Final: respuestas estructuradas combinando analisis cuantitativo y cualitativo |

#### 5. Arquitectura del Agente

Arquitectura desacoplada: **microservicio de IA en Python**, comunicandose bidireccionalmente con infraestructura Java/React via REST APIs.

**Modulos internos:**
1. **Capa de interfaz y orquestacion (loop del agente)**: Controla el flujo con estrategia **ReAct** (Reasoning and Acting). Recibe prompt, evalua que herramientas activar, procesa respuestas y decide respuesta final.
2. **Modulo de memoria contextual (persistencia)**: Almacena session_id e historico de mensajes. Short-Term memory en ventana de contexto para co-referencia.
3. **Modulo RAG (Retrieval-Augmented Generation)**: Indexador de documentos financieros + motor de busqueda vectorial para marco conceptual educativo.

#### 6. Stack Tecnologico

| Componente | Tecnologia | Justificacion |
|-----------|-----------|---------------|
| **Framework de agentes** | **Pydantic AI** (Python) | Code-first, tipado estatico estricto sobre DTOs de tools y respuestas. Mitiga fallos de formato JSON hacia Spring Boot. |
| **Core LLM** | **Llama-3.3-70b-versatile** (via Groq API) | Pesos abiertos, razonamiento logico, Function Calling, sin costo transaccional. |
| **Base vectorial (RAG)** | **Qdrant** (Dockerizado externo) | Persistente via volumenes, busquedas por distancia coseno, filtrado por metadatos. |
| **Memoria conversacional** | **Redis** | Sesiones indexadas por `session_id`, recuperacion secuencial de ultimos turnos. |
| **Conectividad** | **REST API (JSON/HTTP)** | Microservicio Python desacoplado del backend Spring Boot. Contenedor consume endpoints dedicados con `workspace_id`. |

---

## Reglas de validacion para codigo generado

Al generar o revisar codigo para este proyecto, valida contra:

1. **Stack tecnologico**: El agente DEBE usar Pydantic AI (no LangGraph, no CrewAI, no smolagents). El LLM DEBE ser Llama-3.3-70b via Groq. Qdrant para vectores. Redis para memoria. REST API para conectividad.
2. **Estrategia ReAct**: El loop del agente DEBE seguir el patron Thought/Action/Observation de ReAct. NO usar agentes puramente basados en grafos.
3. **Tools deterministicas**: Los calculos numericos (sumas, promedios, proyecciones) DEBEN delegarse a `tool_calculadora_estadistica` — NUNCA confiar en el LLM para matematicas.
4. **RAG como tool**: El sistema RAG es UNA herramienta dentro del toolset del agente, no el agente completo.
5. **Arquitectura desacoplada**: El microservicio de IA en Python se comunica con Spring Boot via REST. No compartir capa de datos ni duplicar logica de acceso a PostgreSQL.
6. **Memoria conversacional**: Usar Redis con `session_id`. La memoria es short-term (ultimos turnos), no una base de conocimiento persistente.
7. **Formato estricto**: Los DTOs de herramientas y respuestas deben tener tipado estatico estricto (Pydantic) para cumplir contratos REST con Spring Boot.
8. **Evaluacion**: Antes de producir, evaluar con golden dataset + LLM-as-judge. Usar RAGAS para RAG. Monitorear drift en produccion.
9. **RAG pipeline**: Empezar con dense solo. Subir a hybrid (BM25+dense+RRF) si el dominio tiene terminologia tecnica. Agregar reranker solo si metricas lo justifican.
