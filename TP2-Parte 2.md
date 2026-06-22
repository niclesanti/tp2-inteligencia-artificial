# 2º Entrega — Avances en la Implementación del Asistente de Consulta Analítica e Inteligencia Financiera

## 1. Introducción

En la primera etapa del Trabajo Práctico se definió el diseño conceptual del agente inteligente: su objetivo como Asistente de Consulta Analítica e Inteligencia Financiera, las percepciones y acciones (tools) que lo componen, la caracterización del ambiente en el que se desenvuelve y la arquitectura general del sistema. Sobre esa base, se procedió a la implementación completa del agente, integrando los distintos módulos definidos en el diseño y desplegando la infraestructura necesaria para su funcionamiento dentro del ecosistema existente de la plataforma de gestión de finanzas personales.

El presente informe documenta los avances de la segunda etapa, describiendo la implementación de cada componente: desde el aprovisionamiento de servicios auxiliares en Docker Compose hasta la orquestación del agente con Pydantic AI, pasando por las herramientas financieras determinísticas, el módulo de memoria conversacional, el pipeline de Retrieval-Augmented Generation (RAG), la estrategia de razonamiento ReAct y el sistema de observabilidad basado en Langfuse.

## 2. Infraestructura de servicios

Para que el agente opere de forma autónoma y desacoplada del backend Java existente, se incorporaron tres servicios adicionales al archivo `docker-compose.yml` del proyecto.

En primer lugar, se agregó **Qdrant** como base de datos vectorial para el módulo RAG. Qdrant se ejecuta en su propia imagen Docker oficial y persiste los embeddings de la base de conocimiento financiera en un volumen dedicado. Se eligió Qdrant por su capacidad de realizar búsquedas de similitud por distancia coseno de forma eficiente y por su soporte nativo de filtrado por metadatos, lo que permite acompañar los fragmentos recuperados con información estructurada sobre su fuente y sección temática.

En segundo lugar, se incorporó **Redis** como almacenamiento de memoria conversacional de corto plazo. Redis persiste los mensajes de cada sesión de chat indexados por `session_id`. Se optó por Redis por su velocidad de lectura y escritura, su capacidad de expiración automática de claves (TTL) y su idoneidad para manejo de datos transaccionales de alta frecuencia, que es precisamente el patrón de acceso que requiere la memoria de contexto del agente durante una conversación.

En tercer lugar, se definió el servicio **agente** propiamente dicho, que corresponde al microservicio Python que aloja toda la lógica del agente conversacional. Este servicio se construye a partir del Dockerfile ubicado en el directorio `agente/`, expone el puerto 8000 y depende de los servicios `backend` (para obtener datos financieros del usuario), `qdrant` (para búsqueda vectorial) y `redis` (para memoria de sesión). Las variables de entorno necesarias para su funcionamiento (como la clave de API de Groq, las direcciones de los servicios dependientes y las credenciales de Langfuse para trazabilidad) se inyectan a través del archivo de entorno del proyecto.

Paralelamente, se crearon endpoints internos en el backend Spring Boot bajo la ruta `/api/internal/` que el agente consume sin necesidad de autenticación JWT, dado que dichas comunicaciones ocurren exclusivamente dentro de la red interna de Docker. La seguridad de estos endpoints se delegó al aislamiento de red, mientras que el frontend se comunica con el agente a través de un proxy configurado en Vite que redirige las rutas `/api/agente` al microservicio Python y el resto de las rutas `/api` al backend Java.

## 3. Arquitectura del agente

El agente se implementó como un microservicio Python utilizando el framework **Pydantic AI** con el modelo de lenguaje **Llama-3.3-70b-versatile** provisto a través de la API de inferencia de **Groq**. La elección de Pydantic AI responde a su enfoque code-first con tipado estricto mediante Pydantic, lo que permite definir contratos precisos para las herramientas y las respuestas del agente, mitigando los errores de formato que los modelos de lenguaje suelen introducir en las invocaciones a funciones.

La estructura del microservicio sigue una organización modular clara. El punto de entrada es una aplicación FastAPI que expone dos endpoints principales para el chat: uno síncrono mediante POST y otro asíncrono mediante Server-Sent Events (SSE) que permite recibir la respuesta del modelo token por token en tiempo real, ofreciendo una experiencia conversacional fluida similar a la de los asistentes modernos. Adicionalmente, se implementó un endpoint de verificación de salud y un endpoint raíz informativo.

El núcleo del agente reside en el módulo de orquestación, que configura el modelo de lenguaje, define el prompt de sistema con las reglas de comportamiento y registra las cuatro herramientas disponibles. El prompt de sistema delimita estrictamente el ámbito de actuación del agente a las finanzas personales del usuario dentro de la plataforma, la educación financiera respaldada por la base de conocimiento RAG y las consultas sobre el uso de la aplicación, instruyendo al modelo a rechazar educadamente cualquier pregunta fuera de ese dominio.

## 4. Herramientas del agente

El agente dispone de cuatro herramientas que le permiten interactuar con el mundo externo de forma determinística. Todas ellas fueron implementadas siguiendo el principio de que el LLM nunca debe realizar cálculos aritméticos por sí mismo, sino delegar toda operación numérica a herramientas diseñadas para tal fin.

La primera herramienta, `tool_filtrar_transacciones`, permite recuperar registros de ingresos y gastos corrientes (efectivo/débito) desde el backend Spring Boot. Acepta filtros opcionales de mes, año, motivo (categoría) y contacto, y devuelve una estructura JSON paginada con los datos solicitados. La segunda herramienta, `tool_filtrar_compras_credito`, funciona de manera análoga pero orientada a consumos realizados con tarjeta de crédito, incluyendo información sobre montos totales, cantidad de cuotas, cuotas pagadas y datos del comercio.

La tercera herramienta, `tool_calculadora_estadistica`, constituye el módulo determinístico de cálculo matemático del agente. Opera sobre los datos devueltos por las dos herramientas anteriores y ofrece nueve operaciones distintas: sumar, promediar, contar, mínimo, máximo, agrupar por categoría (con cálculo de porcentajes), balance (total de ingresos menos total de gastos), distribución porcentual completa y proyección de crédito (cálculo de cuotas pendientes y monto restante). Esta herramienta es invocada obligatoriamente por el LLM cada vez que necesita realizar alguna operación numérica, garantizando así la precisión matemática que el modelo de lenguaje no puede asegurar por sí mismo.

La cuarta herramienta, `tool_recuperacion_RAG`, ejecuta búsquedas semánticas sobre la base de conocimiento financiero indexada en Qdrant. Esta herramienta genera un embedding de la pregunta utilizando el modelo Sentence Transformer `paraphrase-multilingual-MiniLM-L12-v2`, busca los fragmentos más relevantes en la base vectorial y devuelve el contenido junto con metadatos de fuente, sección y nivel de relevancia.

Todas las herramientas incluyen manejo robusto de excepciones: capturan errores de conexión HTTP, errores de validación de parámetros y errores de procesamiento interno, elevando excepciones descriptivas que el orquestador del agente puede interpretar para generar respuestas informativas ante fallos.

## 5. Memoria conversacional

La memoria de corto plazo del agente se implementó mediante Redis como almacén de mensajes. Por cada sesión de chat identificada por un `session_id`, se persiste el listado completo de mensajes intercambiados entre el usuario y el asistente en formato JSON, con un tiempo de expiración configurable mediante variable de entorno (por defecto, 1800 segundos). Esto permite que el agente mantenga coherencia conversacional a lo largo de los turnos de diálogo, pudiendo resolver correferencias gramaticales como "en el mes anterior" o "en esa categoría" sin perder el contexto de interacciones previas.

La implementación utiliza el sistema de tipos de Pydantic AI para serializar y deserializar los mensajes del modelo, garantizando que la estructura de datos almacenada sea exactamente la que el framework espera al reconstruir el historial en cada invocación. El módulo `RedisModelMessageStore` encapsula la lógica de lectura y escritura, operando de forma asíncrona sobre el cliente Redis.

## 6. Pipeline de Retrieval-Augmented Generation

El módulo RAG sigue el pipeline completo de indexación y recuperación. La indexación se realiza mediante un script de ingesta que lee los documentos Markdown ubicados en el directorio `docs RAG/`, los segmenta en fragmentos utilizando una estrategia que combina división por encabezados de nivel 2 y subdivisión por párrafos, genera embeddings para cada fragmento utilizando el modelo multilingüe `paraphrase-multilingual-MiniLM-L12-v2` y los almacena en la colección `guias_financieras` de Qdrant con vectores de 384 dimensiones y distancia coseno.

La base de conocimiento indexada consiste en un documento titulado "Guía de Finanzas Personales en la Argentina", que abarca temas como contexto macroeconómico argentino (inflación, salarios), planificación financiera, gestión de liquidez transaccional (normativas del BCRA, interoperabilidad QR, protección contra fraudes), estrategias de cobertura (cuentas remuneradas, fondos comunes de inversión money market, plazos fijos tradicionales y UVA), financiación y endeudamiento (Costo Financiero Total, Ley de Tarjetas de Crédito, capacidad de endeudamiento sostenible), y diversificación e inversiones (dólar MEP, CEDEARs). Esta guía fue elaborada específicamente para el contexto argentino, con datos actualizados y referencias a normativas vigentes.

El motor de recuperación implementa carga diferida del modelo de embeddings para no bloquear el inicio del servidor, realizando la precarga de forma eager durante el ciclo de vida de la aplicación pero con la capacidad de inicializarse bajo demanda en un hilo separado para no interferir con el bucle de eventos asíncrono.

## 7. Estrategia de razonamiento ReAct

El agente implementa el patrón **Reasoning and Acting (ReAct)** como estrategia de razonamiento, provisto de forma nativa por el framework Pydantic AI. Este patrón permite que el modelo de lenguaje razone de forma iterativa: recibe el mensaje del usuario, evalúa si necesita invocar alguna herramienta para obtener información o realizar cálculos, ejecuta la herramienta correspondiente, analiza el resultado y decide si debe continuar el ciclo con otra herramienta o si cuenta con la información suficiente para formular la respuesta final.

Un aspecto central de la implementación es que el prompt de sistema instruye al modelo a no invocar herramientas para saludos, presentaciones, agradecimientos o despedidas, respondiendo directamente de forma cordial y breve en esos casos. Para consultas analíticas, en cambio, el modelo debe necesariamente recurrir a las herramientas de filtrado y cálculo, siguiendo una secuencia lógica: primero recupera los datos del usuario mediante las herramientas de consulta al backend, luego procesa esos datos mediante la calculadora estadística y, finalmente, si corresponde, enriquece la respuesta con contenido educativo recuperado vía RAG.

## 8. Integración con el frontend

La interfaz de usuario del agente se integró completamente en la aplicación React existente. Se agregó una ruta protegida `/agente-ia` que despliega una página de chat conversacional. La página cuenta con componentes específicos: una pantalla de bienvenida que saluda al usuario por su nombre, un área de mensajes con desplazamiento automático, burbujas de mensaje que distinguen visualmente al usuario del asistente y renderizan el contenido del asistente en Markdown, y un campo de entrada de texto con validación de longitud máxima y envío mediante Enter.

La comunicación en tiempo real se implementó mediante Server-Sent Events (SSE). Cuando el usuario envía un mensaje, el frontend establece una conexión EventSource contra el endpoint `/api/agente/chat/stream` del microservicio Python, pasando el mensaje, el identificador de sesión y el token JWT del usuario como parámetros de consulta. El servidor valida el token contra el backend Spring Boot, ejecuta el agente con el historial recuperado de Redis y transmite cada token de la respuesta como un evento SSE. El frontend reconstruye el mensaje token por token, mostrando un indicador de escritura mientras el agente está procesando. Al finalizar, se transmiten metadatos como las funciones invocadas y la cantidad de tokens utilizados, que se muestran junto al mensaje del asistente.

## 9. Observabilidad y logging

Para garantizar la trazabilidad del comportamiento del agente, se implementó un sistema de observabilidad basado en **Langfuse** con **OpenTelemetry** como protocolo de instrumentación. La inicialización de la telemetría ocurre al arranque del microservicio, verificando la presencia de credenciales de Langfuse en el entorno. Cuando están configuradas, se autentica el cliente Langfuse y se activa la instrumentación automática de todos los agentes de Pydantic AI mediante `Agent.instrument_all()`, lo que captura de forma estructurada cada prompt enviado al LLM, cada invocación de herramienta con sus argumentos de entrada y salida, y cada respuesta generada.

Langfuse proporciona una interfaz web donde es posible inspeccionar sesiones completas de conversación, analizar el costo y la latencia de cada llamada al modelo, y examinar los caminos de razonamiento que siguió el agente para llegar a una respuesta determinada. Esto resulta fundamental para diagnosticar respuestas incorrectas, ya sea por alucinaciones del modelo, errores en el parsing de herramientas o fallos en la recuperación de contexto.

Adicionalmente, se implementó logging estructurado en Python para registrar eventos relevantes durante la ejecución del agente, proporcionando una capa adicional de diagnóstico para el desarrollo y la evaluación offline.

## 10. Pruebas

Se desarrollaron pruebas unitarias para la calculadora estadística, que cubren las nueve operaciones matemáticas con distintos escenarios: datos de transacciones mixtas (ingresos y gastos), datos de compras a crédito, datos vacíos, filtrado por categoría, filtrado por tipo (ingreso/gasto), y casos de error como JSON inválido, operaciones no soportadas o tipos de datos incompatibles. Las pruebas verifican no solo la corrección numérica de los resultados sino también el manejo adecuado de situaciones límite, garantizando la robustez del componente determinístico del agente.

## 11. Conclusión

La implementación realizada materializa el diseño definido en la primera etapa del trabajo práctico, integrando un agente conversacional basado en LLM dentro del ecosistema existente de la plataforma de gestión de finanzas personales. Se optó por una arquitectura desacoplada con un microservicio Python independiente que se comunica con el backend Spring Boot mediante APIs internas y con el frontend React mediante Server-Sent Events para una experiencia conversacional en tiempo real. La infraestructura se completa con Qdrant como base vectorial para el módulo RAG y Redis como almacén de memoria conversacional, todo orquestado mediante Docker Compose. Las herramientas determinísticas de cálculo financiero, la estrategia de razonamiento ReAct y el sistema de observabilidad con Langfuse conforman un agente capaz de asistir al usuario en el análisis de sus finanzas personales con precisión matemática y fundamento conceptual.
