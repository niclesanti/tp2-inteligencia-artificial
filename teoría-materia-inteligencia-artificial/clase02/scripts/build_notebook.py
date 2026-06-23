"""
Genera clase02/clase2_slides.ipynb a partir de la estructura definida acá.

Es la "fuente única" de la clase. Para cambiar slides, editá este archivo
y volvé a correrlo:

    python clase02/scripts/build_notebook.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # clase02/
OUT = ROOT / "clase2_slides.ipynb"

# CSS reutilizable del notebook anterior
CSS = """<style>
.reveal table { font-size: 0.72em; width: 100%; table-layout: fixed; word-wrap: break-word; }
.reveal table td, .reveal table th { padding: 5px 8px; overflow-wrap: break-word; word-break: break-word; }
.reveal code { font-size: 0.82em; word-break: break-all; }
.reveal blockquote { font-size: 0.65em; margin-top: 0.6em; padding: 6px 12px; background: rgba(127,119,221,0.06); border-left: 3px solid #7F77DD; width: 100%; box-sizing: border-box; }
.reveal h2 { font-size: 1.4em !important; }
.reveal h3 { font-size: 1.0em !important; }
.reveal .slides section { overflow-x: hidden; }
.reveal img { max-height: 64vh; object-fit: contain; }
.reveal .slide-figure { width: 88%; display: block; margin: 0 auto; }
</style>
"""


def fig(name: str, alt: str = "", w: str = "88%") -> str:
    """Devuelve el snippet HTML para incrustar una figura SVG con el estilo de la clase."""
    return (
        f'<img src="figures/{name}" alt="{alt}" '
        f'class="slide-figure" style="width: {w};"/>'
    )


def md_slide(slide_id: str, content: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": slide_id,
        "metadata": {"slideshow": {"slide_type": "slide"}},
        "source": [line + "\n" for line in content.splitlines()],
    }


def raw_skip(cell_id: str, content: str) -> dict:
    return {
        "cell_type": "raw",
        "id": cell_id,
        "metadata": {"slideshow": {"slide_type": "skip"}},
        "source": [line + "\n" for line in content.splitlines()],
    }


cells = []

# ─────────────────────────────────────────────────────────────────────────────
# CSS global
cells.append(raw_skip("css-global-c2", CSS))

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 0 — Apertura
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-title", """\
# LLMs — Arquitectura, Ciclo de Vida y Prompting

### UTN-FRSF · Ingeniería en Sistemas de Información · Inteligencia Artificial
**Dr. Jorge Roa · Dra. María de los Milagros Gutiérrez**

---

*De qué está hecho un LLM, cómo aprende, cómo se le habla.*"""))


cells.append(md_slide("slide-recap", """\
## Recap Clase 1 → de qué partimos

```
  Texto      ──▶  Tokenización  ──▶  Embeddings  ──▶  LLM  ──▶  Output
  (crudo)          (subpalabras)      (vectores)        ↑hoy
```

| Lo que ya tenemos de Clase 1 | Lo que abrimos hoy |
|---|---|
| Tokenizers (BPE, WordPiece) | Esos mismos en GPT, Llama, Qwen |
| Embeddings de 384 dimensiones | Cómo el Transformer los procesa |
| BoW / TF-IDF como baseline | Por qué attention los supera |"""))


cells.append(md_slide("slide-modo", """\
## Hoy hablamos con un LLM **por código**, no por UI

- ChatGPT, Claude, Gemini son apps. Lo que está abajo es un modelo.
- En este curso vamos a tratarlo como una **API** que se invoca desde Python.
- Eso permite: scripting, integración, control fino, prompts reproducibles.

> Cuando deployás IA en una empresa, casi nunca usás la UI. Usás el modelo desde código."""))


cells.append(md_slide("slide-demo-groq", """\
## Demo: hola Groq desde un notebook

Vamos a abrir un Colab y conectarnos a Groq con tres consultas progresivas:

1. **Hola simple** — confirmar que la conexión funciona.
2. **Mismo prompt con `temperature=0` y `temperature=1`** — ver qué cambia.
3. **System prompt "respondé como un pirata"** — introducir roles.

📓 **Notebook**: [`clase02/notebooks/01_groq_intro.ipynb`](notebooks/01_groq_intro.ipynb)
   Tiene un botón "Open in Colab" arriba. Abrilo y seguilo en paralelo.

> No vamos a leer el código en clase, lo ejecutamos."""))


cells.append(md_slide("slide-roadmap", f"""\
## Recorrido de la clase

{fig("roadmap.svg", "Roadmap de los 7 bloques de la clase, con dos cortes intermedios", w="92%")}

Vamos primero a entender **qué es** un LLM (bloques 1–4), después a **usarlo bien** (bloque 5), y finalmente a **operarlo en producción** (bloque 6). Cerramos conectando con Clase 3."""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 1 — ¿Qué es un LLM? (Karpathy core)
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b1-section", """\
# Bloque 1
## ¿Qué es un LLM?

---

*Karpathy, "Intro to LLMs" — la intuición más limpia que existe.*"""))


cells.append(md_slide("slide-two-files", f"""\
## Un LLM, en disco, son dos archivos

{fig("two_files.svg", "Un LLM = parameters (140GB) + run.c (~500 líneas), corriendo offline en una MacBook")}

Para correr un modelo open weight como **Llama 2 70B** alcanza con un blob de **parámetros** (~140 GB) y un programa que sabe **multiplicar matrices**. Toda la inteligencia vive en los 140 GB."""))


cells.append(md_slide("slide-inference", f"""\
## Inferencia: 100% local, sin internet

{fig("inference_macbook.svg", "Una MacBook ejecutando un LLM offline, sin WiFi y sin API key")}

Una vez que tenés los pesos, el modelo es tuyo. No hay servicio externo en el medio. Esto es lo que cambia con los modelos open weight."""))


cells.append(md_slide("slide-training-compression", f"""\
## Entrenar = comprimir un trozo de internet

{fig("training_compression.svg", "10 TB de texto → cluster de 6.000 GPUs durante 12 días → 140 GB de pesos")}

Los 140 GB no salen de la nada: son una **compresión con pérdida** de billones de tokens del scraping de internet. Ratio aproximado: **70:1**.

> 📖 *Touvron, H., et al. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models.*"""))


cells.append(md_slide("slide-next-word", f"""\
## La red predice la próxima palabra

{fig("next_word_prediction.svg", "Una red neuronal recibe el contexto 'cat sat on a' y predice 'mat' con 97% de probabilidad")}

El objetivo de entrenamiento es **brutalmente simple**: dado un contexto, ¿qué token sigue?

Pero ese objetivo, repetido sobre billones de tokens, **fuerza** a la red a aprender un montón de cosas sobre el mundo."""))


cells.append(md_slide("slide-world-knowledge", f"""\
## Predecir tokens fuerza a aprender el mundo

{fig("world_knowledge.svg", "Un artículo de Wikipedia con hechos clave subrayados: fechas, lugares, personas, relaciones", w="76%")}

Para predecir cada palabra subrayada, la red tiene que **saber** un hecho del mundo: fechas, lugares, relaciones de parentesco, causalidad histórica, gramática, formato Wikipedia."""))


cells.append(md_slide("slide-dreams", f"""\
## La red alucina documentos

{fig("network_dreams.svg", "Tres documentos inventados por la red: código Java, ficha de Amazon, artículo de Wikipedia")}

Si dejás al modelo generar libre, **inventa** documentos plausibles: código que compila, fichas de productos con ISBN coherentes, artículos de Wikipedia bien estructurados.

**Ninguno existe.** Esto es la **alucinación**: por arquitectura, el modelo siempre genera el documento más plausible que puede, exista o no en la realidad."""))


cells.append(md_slide("slide-inscrutable", f"""\
## ¿Cómo funciona por dentro? Casi nadie lo sabe

{fig("inscrutable.svg", "Diagrama Transformer simplificado a la izquierda; ejemplo del 'reversal curse' Obama/Stanley Ann Dunham a la derecha")}

Sabemos **ajustar** los parámetros para que prediga mejor. No sabemos cómo **colaboran** los miles de millones de parámetros para hacerlo.

> 📖 *Berglund, L., et al. (2023). The Reversal Curse: LLMs trained on "A is B" fail to learn "B is A".*"""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 2 — Transformer
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b2-section", """\
# Bloque 2
## Transformer a grandes rasgos

---

*Lo que hay adentro de la red, sin entrar en la matemática.*"""))


cells.append(md_slide("slide-rnn-vs-transformer", f"""\
## De RNN secuencial a Transformer en paralelo

{fig("rnn_vs_transformer.svg", "Comparativa: RNN procesa una palabra a la vez en secuencia; Transformer mira todas a la vez con atención global")}

> 📖 *Vaswani, A., et al. (2017). Attention Is All You Need. NeurIPS 2017. https://arxiv.org/abs/1706.03762*"""))


cells.append(md_slide("slide-transformer-arch", f"""\
## La arquitectura Transformer original

{fig("transformer_architecture.svg", "Arquitectura completa del Transformer: encoder a la izquierda, decoder a la derecha, conectados por cross-attention", w="80%")}

Vaswani et al. (2017) la propusieron para **traducción**. La idea: el encoder "lee y entiende" la entrada, el decoder genera la salida token a token, y el cross-attention los conecta.

> A partir de acá la familia se dividió: la mayoría de los LLMs modernos usan **solo el decoder** — lo vemos en el próximo slide."""))


cells.append(md_slide("slide-encoder-decoder", f"""\
## Encoder vs Decoder — las dos mitades por separado

{fig("encoder_decoder.svg", "Encoder con atención bidireccional (BERT) vs Decoder con atención causal (GPT, Llama, Claude)")}

> En este curso usamos modelos **decoder-only**. Son los que generan respuestas token a token."""))


cells.append(md_slide("slide-token-mira", f"""\
## ¿Qué significa que un token "mira" a otro?

{fig("token_mira.svg", "El vector de 'banco' se actualiza absorbiendo información de 'quebró', desambiguando su sentido")}

Cada token entra al Transformer como un **vector** de números. "Mirar" es una metáfora: el vector del token se **actualiza absorbiendo información** de los otros tokens, ponderada por un **peso de atención**.

Esto es lo que **resuelve la polisemia**: la misma palabra (*banco*, *gato*, *llama*) toma significados distintos según con qué tokens se conecte. Los pesos los calcula el mecanismo **Query / Key / Value**."""))


cells.append(md_slide("slide-qkv", f"""\
## Query, Key, Value — la metáfora del buscador

{fig("qkv.svg", "Tres cajas Q/K/V con la metáfora 'qué busco / qué tengo / qué devuelvo'")}

Para cada token, el modelo genera tres vectores. **Match(Q, K) → pesos · V** te da una nueva representación que absorbe contexto.

Es un buscador interno, hecho por la red, que se entrena solo."""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 3 — Ciclo de vida
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b3-section", """\
# Bloque 3
## De base model a ChatGPT

---

*¿Cómo pasa un modelo de "completar texto" a "seguir instrucciones"?*"""))


cells.append(md_slide("slide-lifecycle-overview", f"""\
## El ciclo de vida de un LLM, de un vistazo

{fig("lifecycle_overview.svg", "Tres etapas en línea: Pretraining produce un base model, SFT lo convierte en assistant, RLHF/DPO lo alinea con preferencias humanas", w="92%")}

Vamos a recorrer cada etapa con ejemplos. La idea es que entiendan **qué cambia** entre una y otra: los datos, el objetivo, el costo, y qué modelo sale al final."""))


cells.append(md_slide("slide-base-model", f"""\
## Stage 1 — Qué te queda después del pretraining

{fig("base_model_capabilities.svg", "Dos columnas: lo que un base model sí sabe (completar, imitar estilo, hechos del mundo) y lo que NO sabe (seguir instrucciones, detenerse, decir 'no sé', mantener un rol)", w="68%")}

```
  Prompt:  "La capital de Francia es"

  base model →  "París, y también Roma es la capital de Italia,
                 mientras que Berlín lo es de Alemania. Las capitales
                 europeas suelen ser ciudades..."
```

Sabe la respuesta (París), pero **no se detiene**: sigue completando como si fuera un artículo de internet."""))


cells.append(md_slide("slide-training-assistant", f"""\
## Entrenar al assistant: cambiar el dataset

{fig("training_assistant.svg", "Dataset de ~100K conversaciones USER/ASSISTANT escritas por humanos, usado para SFT")}

Misma arquitectura, mismo objetivo (predecir el próximo token). Pero los datos cambian: ahora son **conversaciones de alta calidad** escritas por personas siguiendo guías estrictas.

A esto se le llama **SFT** (Supervised Fine-Tuning)."""))


cells.append(md_slide("slide-after-finetuning", f"""\
## Antes vs después del fine-tuning

{fig("after_finetuning.svg", "Comparativa: el base model genera más preguntas; el assistant detecta el bug y responde útil")}

El base model y el assistant son la **misma red neuronal**. Cambia solo en qué se la entrenó al final."""))


cells.append(md_slide("slide-comparisons", f"""\
## Recolectar preferencias humanas

{fig("comparisons_paperclips.svg", "Tres commits candidatos para el mismo diff; el humano elige el mejor", w="78%")}

Para que el modelo se alinee con lo que **prefieren** las personas, primero hay que medir esa preferencia. La forma más escalable: pedirle al humano que **elija** entre respuestas, en vez de pedirle que **escriba** la perfecta."""))


cells.append(md_slide("slide-rlhf", f"""\
## RLHF: el camino largo

{fig("rlhf_pipeline.svg", "Tres pasos: 1) recolectar comparaciones, 2) entrenar un reward model que las imita, 3) usar PPO para que el LLM maximice ese reward", w="86%")}

**Política** = el modelo cuando lo pensamos como un decisor (dada una situación, qué token genera). **PPO** actualiza la política con un freno: si los nuevos pesos cambian la distribución de tokens demasiado respecto del SFT, lo penaliza. Sin ese freno, el modelo se desvía y deja de generar texto coherente.

> 📖 *Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback (InstructGPT).*"""))


cells.append(md_slide("slide-dpo", f"""\
## DPO: el atajo

{fig("dpo_pipeline.svg", "DPO se saltea el reward model y el loop de PPO. Usa las comparaciones para optimizar el LLM directamente con una función de pérdida que sube la probabilidad del ganador y baja la del perdedor", w="86%")}

> 📖 *Rafailov, R., et al. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model.*"""))


cells.append(md_slide("slide-base-vs-instruct", """\
## Base vs Instruct en la práctica

| Modelo | Variante | Uso típico |
|---|---|---|
| `Qwen3-8B` | base | fine-tuning propio, research |
| `Qwen3-8B-Instruct` | instruct | **el que usamos en este curso** |
| `Llama-3.1-8B` | base | continued pretraining |
| `Llama-3.1-8B-Instruct` | instruct | chatbots, asistentes |

> Cuando bajes un modelo, fijate siempre el sufijo. Si te da respuestas raras o no responde, probablemente bajaste el base model."""))


cells.append(md_slide("slide-quiz-lifecycle", """\
## Quiz — LLMs y su ciclo de vida

*¿Verdadero o falso?*

1. Un LLM moderno consiste en dos archivos: los parámetros del modelo (~140 GB para uno de 70B) y un programa relativamente corto que los ejecuta. <span class="fragment">**Verdadero**</span>

2. Cuando un LLM "alucina" (genera información falsa con seguridad), es un bug que se puede arreglar con mejores datos de entrenamiento. <span class="fragment">**Falso** — es consecuencia de cómo está construido: siempre genera el documento más plausible que puede.</span>

3. En el Transformer, la atención causal del decoder permite que cada token mire tanto los anteriores como los siguientes en la secuencia. <span class="fragment">**Falso** — la atención causal solo mira los tokens anteriores.</span>

4. El base model y el modelo Instruct comparten la misma arquitectura y los mismos parámetros iniciales. La diferencia está en la última etapa de entrenamiento. <span class="fragment">**Verdadero**</span>

5. DPO necesita entrenar una segunda red (el *reward model*) antes de poder ajustar el LLM con las preferencias humanas. <span class="fragment">**Falso** — eso lo hace RLHF; DPO se saltea ese paso.</span>"""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 4 — Scaling laws + ecosistema
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b4-section", """\
# Bloque 4
## Scaling y estado del arte (2026)

---

*Por qué los modelos siguen creciendo, qué cambió en los últimos años, y qué hay en el mercado.*"""))


cells.append(md_slide("slide-scaling-laws", f"""\
## La era Chinchilla: "más N, más D, mejor modelo"

*Chinchilla = paper de DeepMind (2022) que mostró que la receta óptima es ~20 tokens por parámetro.*

{fig("scaling_laws.svg", "Curvas de loss vs tamaño del modelo, una por cada nivel de compute. Todas bajan, sin techo aparente. Pero la slide marca esto como histórico (~2022)", w="80%")}

> 📖 *Hoffmann, J., et al. (2022). Training Compute-Optimal Large Language Models (Chinchilla).*"""))


cells.append(md_slide("slide-data-wall", f"""\
## Pero algo cambió: el data wall y los nuevos ejes

{fig("data_wall.svg", "Izquierda: la oferta de texto público se aplana mientras la demanda de los LLMs sube; cruce ~2026-2028. Derecha: tres ejes nuevos donde escalar (post-training, test-time compute, synthetic data)", w="86%")}

> 📖 *Villalobos, P., et al. (2024). Will we run out of data? Limits of LLM scaling based on human-generated data. https://arxiv.org/abs/2211.04325*
>
> 📖 *OpenAI (2024). Learning to Reason with LLMs. https://openai.com/index/learning-to-reason-with-llms/*"""))


cells.append(md_slide("slide-post-training", f"""\
## Eje 1 — Post-training scaling

{fig("post_training_scaling.svg", "Progresión SFT → RLHF/DPO → RLVR/GRPO, con un callout sobre DeepSeek-R1 como ejemplo concreto del cambio", w="80%")}

**Las siglas:**
- **SFT** — Supervised Fine-Tuning. **RLHF** — RL from Human Feedback. **DPO** — Direct Preference Optimization. **RLVR** — RL with Verifiable Rewards. **GRPO** — Group Relative Policy Optimization (variante eficiente de PPO usada por DeepSeek-R1).

> 📖 *DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.*"""))


cells.append(md_slide("slide-test-time", f"""\
## Eje 2 — Test-time compute

{fig("test_time_compute.svg", "Modelo clásico que responde directo (rápido, errores) vs modelo de razonamiento que muestra un bloque de thinking antes de responder (más lento, más correcto)", w="86%")}

> 📖 *Snell, C., et al. (2024). Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters.*"""))


cells.append(md_slide("slide-sparks-agi", f"""\
## El salto razonador vs clásico (2026)

{fig("sparks_agi.svg", "Cuatro benchmarks (AIME, GPQA, SWE-Bench, Codeforces). En cada uno, el modelo razonador supera al clásico por 30-80 puntos porcentuales", w="86%")}

> Misma generación, mismo año. La diferencia es cómo se entrenó **después** del pretraining."""))


cells.append(md_slide("slide-ecosystem", """\
## Ecosistema 2026 — un mapa rápido

| Categoría | Modelos relevantes |
|---|---|
| **Closed source** (top calidad) | GPT-5.4 (OpenAI), Claude Opus 4.6 (Anthropic), Gemini 3.1 Pro (Google), Grok 4 (xAI) |
| **Closed source** (balance) | Claude Sonnet 4.6, GPT-5.4-mini |
| **Open weight** (densos) | Llama 4 Scout (Meta), Qwen3 / Qwen3.5 (Alibaba), Mistral Small 4 |
| **Open weight** (MoE) | **Kimi K2.5** (Moonshot, 1T total / 32B activos), DeepSeek-R1 |
| **Razonadores** (open) | DeepSeek-R1, Qwen QwQ, Kimi K2.5 |
| **Para correr local** | Gemma 4, Qwen3-4B, Llama 3.2-3B (vía Ollama) |"""))


cells.append(md_slide("slide-huggingface", f"""\
## ¿Dónde viven los modelos open weight?

{fig("huggingface.svg", "Los tres pilares de HuggingFace: el Hub (repositorio de modelos y datasets), las librerías Python (transformers, datasets, trl, peft), y Spaces / Inference Endpoints", w="88%")}

> 🔗 https://huggingface.co/"""))


cells.append(md_slide("slide-course-stack", """\
## Para este curso

Usamos **Groq** como provider principal de inferencia:

- **Gratis** con cuotas generosas para desarrollo.
- **Muy rápido** (Groq corre inferencia en hardware especializado).
- En las notebooks podés cambiar la constante `MODEL` por cualquier modelo disponible en Groq (Llama, Qwen3, DeepSeek-R1, Gemma, etc.).

```bash
pip install groq
export GROQ_API_KEY="..."
```

Alternativa local opcional: **Ollama**."""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 5 — Prompting (antes Bloque 6)
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b5-section", """\
# Bloque 5
## Prompting como ingeniería

---

*El prompt es la única interfaz. Usarla bien hace toda la diferencia.*"""))


cells.append(md_slide("slide-prompt-structure", f"""\
## Estructura de una llamada a un LLM

{fig("prompt_structure.svg", "Tres bloques: SYSTEM (define rol/restricciones), USER (la pregunta), ASSISTANT (la respuesta)")}

Toda la "ingeniería de prompts" es jugar con estos tres campos."""))


cells.append(md_slide("slide-sampling-params", f"""\
## Output params: temperature, top-K, top-P

{fig("sampling_params.svg", "Tres distribuciones de probabilidad mostrando cómo cambian con temperature baja/alta y con top-K/top-P")}

- **Temperature**: alta = creativo / diverso. Baja = predecible / factual.
- **Top-K**: corta a los K tokens más probables.
- **Top-P**: corta cuando la suma de probabilidades alcanza P.

> Bug clásico: con `temperature=0` o `top-K=1`, el modelo entra en **repetition loop**."""))


cells.append(md_slide("slide-sampling-link", """\
## Probá los parámetros vos mismo

📓 **Notebook**: [`clase02/notebooks/03_sampling_params.ipynb`](notebooks/03_sampling_params.ipynb)

Generá el mismo poema con `temperature=0.1` y `temperature=0.9`. Compará."""))


cells.append(md_slide("slide-system-role-context", """\
## System / Role / Contextual prompting

**System prompt** — define el rol y las restricciones del modelo.
```
Sos un ingeniero de software experto en Python.
Respondés conciso, técnico, solo en español.
```

**Role prompting** — asignás explícitamente un rol dentro del prompt.
```
Actuá como un profesor universitario que enseña con ejemplos prácticos.
Explicame qué es un decorador en Python.
```

**Contextual prompting** — proveés información que el modelo necesita para resolver.
```
Ley de Ohm: V = I × R
Pregunta: si I=2A y R=3Ω, ¿cuál es V?
```

> Los tres se pueden combinar."""))


cells.append(md_slide("slide-shot-spectrum", f"""\
## Zero / one / few-shot

{fig("shot_spectrum.svg", "Tres tarjetas comparando zero-shot (sin ejemplos), one-shot (un ejemplo), few-shot (varios ejemplos)")}

> 📖 *Brown, T., et al. (2020). Language Models are Few-Shot Learners (GPT-3).*"""))


cells.append(md_slide("slide-prompting-link", """\
## Probá zero-shot vs few-shot

📓 **Notebook**: [`clase02/notebooks/04_prompting_techniques.ipynb`](notebooks/04_prompting_techniques.ipynb)

Clasificá reseñas con un prompt zero-shot. Después con few-shot. Compará la calidad."""))


cells.append(md_slide("slide-cot", """\
## Chain of Thought — "pensemos paso a paso"

```
PROBLEMA:
Cuando tenía 3 años, mi pareja tenía 3 veces mi edad.
Ahora tengo 20. ¿Cuántos años tiene mi pareja?

❌ Sin CoT (responde de una): "26"  (a veces se equivoca)

✓ Con CoT ("pensá paso a paso"):
  1. A los 3 años, mi pareja tenía 9.
  2. Diferencia de edad: 6 años.
  3. Hoy tengo 20 → mi pareja tiene 26.

  Respuesta: 26.
```

**Conexión con Karpathy**: el modelo necesita **tokens para pensar**. Si lo forzás a una respuesta corta, le sacás esa capacidad.

> 📖 *Wei, J., et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in LLMs.*"""))


cells.append(md_slide("slide-structured-output", """\
## Structured output — JSON para integrar con código

```python
SYSTEM = '''
Analizás requerimientos. Respondés SOLO JSON con esta estructura:
{
  "tipo": "funcional" | "no_funcional" | "restriccion",
  "prioridad": "alta" | "media" | "baja",
  "componente": string,
  "resumen": string (max 15 palabras)
}
No incluyas nada más que el JSON.
'''

USER = "El sistema debe responder en <200ms al 95% de las requests."
```

```json
{"tipo": "no_funcional", "prioridad": "alta",
 "componente": "API", "resumen": "Latencia p95 menor a 200ms bajo carga normal"}
```

> Tip: usá `json-repair` para tolerar JSON parcialmente roto."""))


cells.append(md_slide("slide-prompt-variables", f"""\
## Prompt como código: variables y templating

{fig("prompt_variables.svg", "Comparativa: a la izquierda, el prompt hardcodeado dentro de una función; a la derecha, un template separado con variables {{ review }} que el código solo renderea con Jinja", w="86%")}

> 📖 *LangChain `PromptTemplate`, Jinja2, Mirascope, Promptfoo — todos los frameworks serios separan prompt de código.*"""))


cells.append(md_slide("slide-prompt-eval", f"""\
## Iteración: ¿cómo sé si mi prompt mejoró?

{fig("prompt_evaluation.svg", "Tres pasos: armar dataset de tests, correr ambos prompts (v1 y v2), comparar accuracy. Abajo, una nota sobre cómo medir según la tarea (clasificación, generación, código, latencia)", w="86%")}"""))


cells.append(md_slide("slide-playground", """\
## Práctica abierta — diseñá tu propio prompt

🌐 https://console.groq.com/playground · o desde el notebook 04.

**Tarea (15–20 min, en parejas):**

1. **Elegí** un caso de uso real para tu vida o tu trabajo: clasificar emails, extraer datos de un PDF, resumir reuniones, generar SQL desde lenguaje natural, etc.
2. **Armá 5 casos de prueba** con input + output esperado (esto es tu mini dataset).
3. **Escribí v1** del prompt: simple, zero-shot. Corré los 5 casos.
4. **Iterá a v2**: agregá rol + un par de ejemplos few-shot + restringí formato (JSON si aplica). Corré los 5 casos.
5. **Compará**: ¿cuántos casos pasan v1? ¿cuántos v2? Si empata, ¿cuál es más corto / barato?
6. **Reportá** el caso de uso, los dos prompts, y el accuracy de cada uno.

> El playground es para iterar rápido. La API + dataset de tests es para producción."""))


cells.append(md_slide("slide-best-practices", """\
## Mejores prácticas (resumen)

- **Específico** > genérico. "Resumí en 3 bullets" > "resumí".
- **Ejemplos** > descripciones. Few-shot beat zero-shot cuando podés.
- **Instrucciones positivas** > restricciones. "Hacé X" > "no hagas Y".
- **Estructura clara**: usá tags (XML, JSON, markdown) para delimitar.
- **Iterá**: cambiá una cosa por vez. Documentá qué probaste.
- **Temperatura baja** para tareas factuales, alta para creatividad.
- **CoT** para razonamiento, **structured output** para integración con código.
- **Variables y templating** desde el día 1: el prompt es código, versionalo en git.
- **Iterá con dataset de tests** si la tarea importa. "Probé una vez y anduvo" no escala."""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 6 — Evals y monitoreo
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b6-section", """\
# Bloque 6
## Evals y monitoreo: del prompt al producto

---

*El prompt ya está bien diseñado. Ahora viene producción.*"""))


cells.append(md_slide("slide-evals-offline-online", f"""\
## Evals offline vs online

{fig("evals_offline_online.svg", "Dos paneles lado a lado: eval offline (antes del deploy, dataset estático, en CI) vs eval online (en producción, tráfico real, continuo)", w="86%")}"""))


cells.append(md_slide("slide-monitoring", f"""\
## Qué loggear en producción

{fig("monitoring_pipeline.svg", "Pipeline App → LLM → Logger middleware → Storage → Dashboard. Abajo, los 4 datos clave: input completo, output completo, latencia/costo, señal de calidad", w="86%")}"""))


cells.append(md_slide("slide-drift", f"""\
## Drift: lo que cambia con el tiempo

{fig("drift_detection.svg", "Cuatro tipos de drift: input drift, quality drift, cost drift, abuse drift. Abajo, un mini-dashboard mostrando accuracy bajando y costo subiendo a lo largo de 3 meses, con alerta disparada", w="86%")}

> Tu sistema fue bueno el día del deploy. Tres meses después, no necesariamente."""))


cells.append(md_slide("slide-tools-landscape", f"""\
## Herramientas (mayo 2026)

{fig("tools_landscape.svg", "Tres columnas: evals offline (Promptfoo, Braintrust, DeepEval, OpenAI Evals, Inspect AI), evals de RAG (Ragas, preview Clase 3), monitoreo (Langfuse, LangSmith, Arize Phoenix, Helicone, TruLens). Una caja con 'por dónde empezar' según el caso", w="86%")}"""))


cells.append(md_slide("slide-feedback-loop", f"""\
## El loop completo: prompt → producto → mejora

{fig("feedback_loop.svg", "Ciclo de 6 nodos: diseño → eval offline → producción → eval online → análisis → feedback → vuelve al diseño. En el centro: 'PROMPT LIFECYCLE'", w="86%")}

> Igual que el código, el prompt nunca está "terminado". Evoluciona con feedback de la realidad."""))


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 7 — Cierre (antes Bloque 6)
# ─────────────────────────────────────────────────────────────────────────────

cells.append(md_slide("slide-b7-section", """\
# Bloque 7
## Cierre y puente a Clase 3

---

*Lo que aprendimos hoy nos lleva directo al próximo problema.*"""))


cells.append(md_slide("slide-context-window", f"""\
## Context window: el límite que motiva RAG

{fig("context_window.svg", "Una barra apilada que muestra cómo SYSTEM + historial + documentos + USER compiten por el espacio del context window")}"""))


cells.append(md_slide("slide-two-limits", """\
## Las dos limitaciones que motivan Clase 3

Volvemos al hook del inicio. Vimos:

**1. El modelo alucina** (Bloque 1) — siempre genera el documento más plausible, exista o no. Sin grounding en datos reales, inventa con confianza.

**2. El context window es finito** (recién vimos) — y aunque sea de 10M tokens, **tu base de conocimiento no entra**.

```
                    ╔══════════════════════════════════╗
                    ║                                  ║
   Alucina ───────▶║   ¿Cómo le damos al modelo       ║
                    ║   conocimiento propio,           ║
   Context  ───────▶║   sin reentrenarlo?              ║
   limits           ║                                  ║
                    ╚══════════════╤═══════════════════╝
                                   │
                                   ▼
                              RAG (Clase 3)
```"""))


cells.append(md_slide("slide-recap-cierre", """\
## Lo que vimos hoy

| Bloque | Concepto clave |
|---|---|
| 1 — ¿Qué es un LLM? | Two files. Compresión de internet. Alucina por arquitectura. |
| 2 — Transformer | Attention en paralelo. Encoder vs decoder. Q/K/V. |
| 3 — Ciclo de vida | Pretrain → SFT → RLHF/DPO. Base vs Instruct. |
| 4 — Scaling 2026 | El pretraining se aplana; el eje hoy es post-training y test-time compute. |
| 5 — Prompting | System / few-shot / CoT / structured output / variables / iteración. |
| 6 — Evals y monitoreo | Eval offline + online. Logging. Drift. Loop de mejora continua. |

**Notebooks que quedaron para ejecutar:** `01_groq_intro`, `03_sampling_params`, `04_prompting_techniques`."""))


cells.append(md_slide("slide-preview", """\
## Clase 3 — ¿qué viene?

Hoy aprendimos a **hablarle** a un LLM. En Clase 3 vemos cómo darle **conocimiento propio** sin reentrenarlo.

---

- **¿Por qué RAG?** — alucinación, knowledge cutoff, context limits.
- **Pipeline RAG naive** — chunking → embeddings → vector store → retrieval → augmentation.
- **Hybrid search** — BM25 (Clase 1) + búsqueda semántica (Clase 1) combinados.
- **RAG avanzado** — reranking, HyDE, parent-child chunks.
- **Práctica** — RAG funcional sobre documentos propios con ChromaDB + Ollama."""))


cells.append(md_slide("slide-bibliografia", """\
## 📚 Bibliografía

### Charla central
- **Karpathy, A. (2023). Intro to Large Language Models.**
  🔗 https://www.youtube.com/watch?v=zjkBMFhNj_g
  *La charla en la que se basa el grueso de los Bloques 1, 3, 4, 5.*

### Papers fundacionales
- Vaswani, A., et al. (2017). *Attention Is All You Need.* https://arxiv.org/abs/1706.03762
- Devlin, J., et al. (2018). *BERT.* https://arxiv.org/abs/1810.04805
- Brown, T., et al. (2020). *Language Models are Few-Shot Learners.* https://arxiv.org/abs/2005.14165
- Ouyang, L., et al. (2022). *Training language models to follow instructions with human feedback (InstructGPT).* https://arxiv.org/abs/2203.02155
- Wei, J., et al. (2022). *Chain-of-Thought Prompting.* https://arxiv.org/abs/2201.11903
- Hoffmann, J., et al. (2022). *Training Compute-Optimal LLMs (Chinchilla).* https://arxiv.org/abs/2203.15556
- Rafailov, R., et al. (2023). *Direct Preference Optimization.* https://arxiv.org/abs/2305.18290
- Berglund, L., et al. (2023). *The Reversal Curse.* https://arxiv.org/abs/2309.12288
- Hubinger, E., et al. (2024). *Sleeper Agents.* https://arxiv.org/abs/2401.05566

### Libros
- Jurafsky, D. & Martin, J. H. (2024). *Speech and Language Processing* (3rd ed. draft). https://web.stanford.edu/~jurafsky/slp3/
- Tunstall, L., von Werra, L. & Wolf, T. (2022). *NLP with Transformers.* O'Reilly."""))


# ─────────────────────────────────────────────────────────────────────────────
# Notebook envelope
# ─────────────────────────────────────────────────────────────────────────────

notebook = {
    "cells": cells,
    "metadata": {
        "celltoolbar": "Slideshow",
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False))
print(f"✓ Wrote {OUT}")
print(f"  {len(cells)} cells total ({sum(1 for c in cells if c['cell_type']=='markdown')} slides)")
