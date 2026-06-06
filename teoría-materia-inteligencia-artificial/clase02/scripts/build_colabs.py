"""
Genera los 5 notebooks Colab de clase02/notebooks/.
Cada uno con badge "Open in Colab" apuntando a main.

Para regenerar:
    python clase02/scripts/build_colabs.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # clase02/
NB_DIR = ROOT / "notebooks"
NB_DIR.mkdir(exist_ok=True)

REPO = "jorgeroa/ia-utn-frsf"
BRANCH = "main"


def colab_badge(notebook_filename: str) -> str:
    path = f"clase02/notebooks/{notebook_filename}"
    return (
        f'<a href="https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/{path}" '
        f'target="_blank">'
        f'<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        f'alt="Open In Colab"/></a>'
    )


def md(content: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in content.splitlines()],
    }


def code(content: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [line + "\n" for line in content.splitlines()],
    }


def write_notebook(filename: str, cells: list):
    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {"provenance": []},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = NB_DIR / filename
    out.write_text(json.dumps(notebook, indent=1, ensure_ascii=False))
    print(f"OK {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 01 — Groq intro
# ─────────────────────────────────────────────────────────────────────────────

write_notebook("01_groq_intro.ipynb", [
    md(f"""\
# 01 — Hola Groq desde Python

{colab_badge("01_groq_intro.ipynb")}

**Objetivo.** Conectarse a un LLM por código (no por UI) y observar tres comportamientos básicos:
1. Una consulta simple.
2. El efecto de `temperature` en la respuesta.
3. El efecto de un `system` prompt en el comportamiento.

**Requisitos.**
- API key gratuita en https://console.groq.com (registrate con email).
- En Colab, guardá la key en el panel de "Secrets" con nombre `GROQ_API_KEY` (icono de la llave en la sidebar)."""),

    code("""\
%pip install --quiet groq"""),

    md("""\
## Setup

Si estás en Colab, esto lee la API key del panel de Secrets. Si estás local, exportá `GROQ_API_KEY` antes de abrir Jupyter."""),

    code("""\
import os
from groq import Groq

# En Colab:
try:
    from google.colab import userdata
    os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
except ImportError:
    # Local: asume que ya está exportada
    assert os.environ.get("GROQ_API_KEY"), "Exportá GROQ_API_KEY antes de correr."

client = Groq()
MODELS = {
    "llama_fast":   "llama-3.1-8b-instant",
    "llama_strong": "llama-3.3-70b-versatile",
    "qwen_reason":  "qwen/qwen3-32b",
    "deepseek":     "deepseek-r1-distill-llama-70b",
    "gemma":        "gemma2-9b-it",
}
MODEL = MODELS["llama_strong"]  # cambiá la clave para probar otros modelos

print("Cliente listo, modelo:", MODEL)"""),

    md("""\
## 1. Consulta simple

Mandamos un único mensaje del usuario y leemos la respuesta."""),

    code("""\
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explicame en 2 oraciones qué es un LLM."}],
)

print(resp.choices[0].message.content)"""),

    md("""\
## 2. Efecto de `temperature`

La misma pregunta, dos veces, con temperaturas distintas. Observá cómo cambia el estilo de la respuesta."""),

    code("""\
PROMPT = "Escribime un haiku sobre los lunes."

for temp in [0.1, 1.0]:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=temp,
    )
    print(f"--- temperature = {temp} ---")
    print(resp.choices[0].message.content)
    print()"""),

    md("""\
## 3. Cambiar el "carácter" con un `system` prompt

El system prompt define el rol del modelo antes de cualquier interacción del usuario."""),

    code("""\
PIRATA = "Sos un pirata del Caribe del siglo XVII. Hablás siempre en primera persona y usás expresiones piratas."

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": PIRATA},
        {"role": "user", "content": "¿Cómo declaro un array en Python?"},
    ],
    temperature=0.6,
)

print(resp.choices[0].message.content)"""),

    md("""\
## Para experimentar después

- Cambiá el `system` prompt: profesor de física, abogado, chef.
- Combiná `system` + `temperature` baja → asistente técnico predecible.
- Probá pasar varios mensajes en `messages` simulando una conversación.

> El próximo notebook (`03_sampling_params`) profundiza en `temperature`, `top_p` y los efectos del sampling."""),
])


# ─────────────────────────────────────────────────────────────────────────────
# 03 — Sampling params
# ─────────────────────────────────────────────────────────────────────────────

write_notebook("03_sampling_params.ipynb", [
    md(f"""\
# 03 — Sampling: temperature, top_p, top_k

{colab_badge("03_sampling_params.ipynb")}

**Objetivo.** Tocar los parámetros de sampling y ver cómo cambia el output. La idea es que después puedas elegirlos a conciencia para tu caso de uso.

**Requisitos.** API key de Groq en `GROQ_API_KEY`."""),

    code("""\
%pip install --quiet groq"""),

    code("""\
import os
from groq import Groq

try:
    from google.colab import userdata
    os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
except ImportError:
    assert os.environ.get("GROQ_API_KEY"), "Exportá GROQ_API_KEY."

client = Groq()
MODELS = {
    "llama_fast":   "llama-3.1-8b-instant",
    "llama_strong": "llama-3.3-70b-versatile",
    "qwen_reason":  "qwen/qwen3-32b",
    "deepseek":     "deepseek-r1-distill-llama-70b",
    "gemma":        "gemma2-9b-it",
}
MODEL = MODELS["llama_strong"]  # cambiá la clave para probar otros modelos

def generar(prompt, **kwargs):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    return resp.choices[0].message.content"""),

    md("""\
## 1. `temperature` — el termostato de la creatividad

Mismo prompt, distintas temperaturas. Observá la diferencia de tono y vocabulario."""),

    code("""\
PROMPT = "Escribime un poema corto (4 versos) sobre el otoño en Buenos Aires."

for temp in [0.0, 0.3, 0.7, 1.2]:
    print(f"--- temperature = {temp} ---")
    print(generar(PROMPT, temperature=temp))
    print()"""),

    md("""\
- `temperature=0` → el modelo elige siempre el token más probable. Determinista.
- Valores altos → distribución más plana, salidas diversas (y a veces incoherentes)."""),

    md("""\
## 2. Reproducibilidad: el bug del "siempre lo mismo"

Con temperatura baja, dos llamadas seguidas dan respuestas casi idénticas. Útil cuando necesitás determinismo (testing, código)."""),

    code("""\
PROMPT = "Listame 3 razones por las que se prefiere PostgreSQL sobre MySQL."

for i in range(2):
    print(f"--- Llamada {i+1} (temperature=0) ---")
    print(generar(PROMPT, temperature=0))
    print()"""),

    md("""\
## 3. `top_p` — nucleus sampling

Muestrea solo del conjunto de tokens cuya probabilidad acumulada llega a P. Recorta la "cola larga"."""),

    code("""\
PROMPT = "Inventame el nombre de una banda de rock progresivo argentina."

for p in [0.1, 0.5, 1.0]:
    print(f"--- top_p = {p} ---")
    for _ in range(3):
        print("  ·", generar(PROMPT, temperature=0.9, top_p=p))
    print()"""),

    md("""\
## Cuándo usar qué

| Caso | temperature | top_p |
|---|---|---|
| Código, factual, extracción | 0.0 – 0.3 | 1.0 |
| Conversación natural | 0.6 – 0.8 | 0.9 |
| Creatividad, brainstorming | 0.9 – 1.2 | 0.95 |
| Determinismo (tests) | 0.0 | 1.0 |"""),
])


# ─────────────────────────────────────────────────────────────────────────────
# 04 — Prompting techniques
# ─────────────────────────────────────────────────────────────────────────────

write_notebook("04_prompting_techniques.ipynb", [
    md(f"""\
# 04 — Zero-shot, one-shot, few-shot

{colab_badge("04_prompting_techniques.ipynb")}

**Objetivo.** Comparar las tres técnicas en una tarea concreta: clasificación de sentimiento. Vas a ver cómo unos pocos ejemplos cambian el comportamiento."""),

    code("""\
%pip install --quiet groq"""),

    code("""\
import os
from groq import Groq

try:
    from google.colab import userdata
    os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
except ImportError:
    assert os.environ.get("GROQ_API_KEY"), "Exportá GROQ_API_KEY."

client = Groq()
MODELS = {
    "llama_fast":   "llama-3.1-8b-instant",
    "llama_strong": "llama-3.3-70b-versatile",
    "qwen_reason":  "qwen/qwen3-32b",
    "deepseek":     "deepseek-r1-distill-llama-70b",
    "gemma":        "gemma2-9b-it",
}
MODEL = MODELS["llama_fast"]  # cambiá la clave para probar otros modelos

def clasificar(messages, temperature=0.1):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()"""),

    md("""\
## Reseñas de prueba

Mezclamos casos fáciles y ambiguos para ver dónde fallan las distintas técnicas."""),

    code("""\
RESEÑAS = [
    "El servicio fue impecable, vuelvo seguro.",                                 # claramente positiva
    "Pésimo, no me devolvieron la plata.",                                       # claramente negativa
    "Está OK, nada del otro mundo pero cumple.",                                 # neutral
    "El servicio fue lento pero la comida estuvo buena.",                        # ambiguo
    "Llegó a tiempo, eso es lo único bueno que puedo decir.",                    # sarcástico/negativo
    "Hace lo que promete, ni más ni menos.",                                     # neutral
]"""),

    md("""\
## Zero-shot

Solo le decimos qué hacer, sin ejemplos."""),

    code("""\
SYSTEM_ZS = "Sos un clasificador de sentimientos. Respondés SOLO con una palabra: POSITIVA, NEUTRAL o NEGATIVA."

print("ZERO-SHOT")
print("-" * 60)
for r in RESEÑAS:
    out = clasificar([
        {"role": "system", "content": SYSTEM_ZS},
        {"role": "user", "content": f"Reseña: {r}"},
    ])
    print(f"  {out:<10} <- {r}")"""),

    md("""\
## Few-shot

Le damos 3 ejemplos resueltos. Observá cómo mejora la consistencia en los casos ambiguos."""),

    code("""\
SYSTEM_FS = "Sos un clasificador de sentimientos. Respondés SOLO con: POSITIVA, NEUTRAL o NEGATIVA."

EJEMPLOS = '''Reseña: Excelente atención y precio justo.
Etiqueta: POSITIVA

Reseña: Lo recibí roto y nadie responde.
Etiqueta: NEGATIVA

Reseña: Cumple, pero tarda más que la competencia.
Etiqueta: NEUTRAL

'''

print("FEW-SHOT")
print("-" * 60)
for r in RESEÑAS:
    user = EJEMPLOS + f"Reseña: {r}\\nEtiqueta:"
    out = clasificar([
        {"role": "system", "content": SYSTEM_FS},
        {"role": "user", "content": user},
    ])
    print(f"  {out:<10} <- {r}")"""),

    md("""\
## Parte 2 — Cuando zero-shot ya no alcanza

El sentimiento de reseñas es una tarea **fácil**: el modelo conoce las clases (positivo / negativo / neutral) sin que se las definas. Por eso zero-shot ya anda muy bien.

Probemos algo más realista: **triaje de tickets de soporte con un esquema propio**, donde:

- Las etiquetas son **idiosincrásicas** del producto (no las podés googlear).
- Hay **clases ambiguas** (un mismo ticket podría caer en dos).
- Necesitás un **formato de salida estricto** para alimentar un sistema downstream."""),

    md("""\
## La tarea

Un ticket entra y queremos clasificarlo en una de **6 etiquetas internas**:

| Etiqueta | Significa |
|---|---|
| `BUG_BLOQUEANTE` | El usuario no puede operar (login caído, pago no procesa, error 500). |
| `BUG_VISUAL` | Algo se ve mal pero la funcionalidad anda (CSS roto, ícono cortado). |
| `FEATURE_REQUEST` | Pide algo que no existe todavía. |
| `DUDA_DOCS` | Duda que se resuelve leyendo la doc del producto. |
| `DUDA_BILLING` | Duda sobre planes, facturación, precios, suscripción. |
| `OUT_OF_SCOPE` | No es nuestro problema (consulta sobre otro producto, spam, queja sin acción posible). |"""),

    code("""\
TICKETS = [
    "Hace 2 horas que no puedo loguearme, me tira 'session expired' en loop.",
    "El logo de la barra se ve cortado a la mitad en Safari mobile.",
    "¿Tienen plan anual con descuento o solo mensual?",
    "Necesitaría poder exportar el reporte a Excel, no solo a PDF.",
    "No entiendo cómo configurar el webhook, leí la doc pero quedé igual.",
    "¿Hola? Me podés pasar el teléfono de Movistar?",
    "El pago me lo cobró dos veces, urgente.",
    "Sería genial poder customizar los colores del dashboard.",
]"""),

    md("""\
## Zero-shot

Le decimos al modelo qué tiene que hacer **en palabras**, sin ejemplos."""),

    code("""\
SYSTEM_ZS = '''Sos un sistema de triaje de tickets de soporte.
Clasificá cada ticket en exactamente una de estas etiquetas:
BUG_BLOQUEANTE, BUG_VISUAL, FEATURE_REQUEST, DUDA_DOCS, DUDA_BILLING, OUT_OF_SCOPE.

Respondé SOLO con la etiqueta, sin explicación.'''

print("ZERO-SHOT")
print("-" * 70)
zero_shot_results = []
for t in TICKETS:
    out = clasificar([
        {"role": "system", "content": SYSTEM_ZS},
        {"role": "user", "content": t},
    ])
    zero_shot_results.append(out)
    print(f"  {out:<25} <- {t[:60]}")"""),

    md("""\
**¿Qué pasa típicamente?**

- El modelo a veces inventa etiquetas (`BUG_CRITICO`, `bug_visual`, `Bug Bloqueante`) o las escribe distinto.
- Agrega texto extra ("Etiqueta: BUG_BLOQUEANTE", "Esta sería FEATURE_REQUEST porque...").
- En los casos ambiguos (consulta sobre billing vs duda general; bug visual vs feature request) elige distinto cada vez.

Eso pasa porque el modelo **no conoce tu esquema** — está adivinando."""),

    md("""\
## Few-shot

Le mostramos 5 ejemplos resueltos. Elegidos para cubrir los casos donde zero-shot suele fallar."""),

    code("""\
EJEMPLOS_FS = '''
Ticket: No me carga el dashboard, queda cargando infinito.
Etiqueta: BUG_BLOQUEANTE

Ticket: El botón "Guardar" aparece cortado en pantalla chica.
Etiqueta: BUG_VISUAL

Ticket: ¿Cuánto sale el plan empresa?
Etiqueta: DUDA_BILLING

Ticket: Necesito una forma de duplicar los proyectos.
Etiqueta: FEATURE_REQUEST

Ticket: Disculpá, era para otra empresa.
Etiqueta: OUT_OF_SCOPE

'''

SYSTEM_FS = '''Sos un sistema de triaje de tickets de soporte.
Clasificá cada ticket en exactamente una de estas etiquetas:
BUG_BLOQUEANTE, BUG_VISUAL, FEATURE_REQUEST, DUDA_DOCS, DUDA_BILLING, OUT_OF_SCOPE.

Respondé SOLO con la etiqueta, sin explicación.'''

print("FEW-SHOT")
print("-" * 70)
few_shot_results = []
for t in TICKETS:
    user = EJEMPLOS_FS + f"Ticket: {t}\\nEtiqueta:"
    out = clasificar([
        {"role": "system", "content": SYSTEM_FS},
        {"role": "user", "content": user},
    ])
    few_shot_results.append(out)
    print(f"  {out:<25} <- {t[:60]}")"""),

    md("""\
## Comparación lado a lado"""),

    code("""\
print(f"{'TICKET':<60} {'ZERO-SHOT':<22} {'FEW-SHOT':<22}")
print("-" * 104)
for t, z, f in zip(TICKETS, zero_shot_results, few_shot_results):
    short = (t[:55] + '...') if len(t) > 58 else t
    flag = "  ⚠" if z.strip() != f.strip() else ""
    print(f"{short:<60} {z:<22} {f:<22}{flag}")"""),

    md("""\
## El takeaway

El few-shot **no le enseña a clasificar** al modelo (Llama 3.3 ya entiende perfecto cada ticket). Lo que hace es:

1. **Fijar el formato exacto** — solo la etiqueta, sin texto extra, en MAYÚSCULAS exactas.
2. **Resolver ambigüedad de las clases** — qué cae en `DUDA_BILLING` vs `DUDA_DOCS`, qué es `BUG_VISUAL` vs `FEATURE_REQUEST`.
3. **Anclar el vocabulario** — el modelo no inventa `BUG_CRITICO` ni `bug_visual`.

Ese es el patrón general: **few-shot es para fijar formato y resolver tu esquema propio**, no para enseñarle al modelo lo que ya sabe."""),

    md("""\
## Para experimentar

- Cambiá los ejemplos del few-shot por casos más cercanos a tu dominio. Probablemente mejore más.
- Probá con 1 solo ejemplo (one-shot) y compará con few-shot.
- Pedí al modelo que devuelva además una **explicación** de por qué clasificó así. Esto es CoT, lo vemos en el próximo notebook.
- Probá con `temperature=0.7` en zero-shot — ¿se vuelve más inconsistente?
- Cambiá `MODEL` a `MODELS["llama_fast"]` (Llama 3.1 8B) y mirá cómo cae la calidad — los modelos chicos sufren más sin few-shot."""),
])




print()
print("Listo.")
