# IA · UTN-FRSF

Material de la asignatura **Inteligencia Artificial** de la
Universidad Tecnológica Nacional, Facultad Regional Santa Fe.

**Docentes:** Dr. Jorge Roa · Dra. Milagros Gutiérrez

---

## Contenido

### Clase 1 — Tokenización y Vectorización

- `clase01/vectores_slides.ipynb` — slides de la clase en formato Jupyter (reveal.js).
- `clase01/figures/` — recursos gráficos.

### Clase 2 — LLMs

- `clase02/clase2_slides.ipynb` — slides de la clase en formato Jupyter (reveal.js).
- `clase02/figures/` — figuras SVG.
- `clase02/notebooks/` — notebooks de práctica para Colab (Groq):
  - `01_groq_intro.ipynb` — primera llamada al LLM.
  - `03_sampling_params.ipynb` — temperature, top_p, top_k.
  - `04_prompting_techniques.ipynb` — zero/one/few-shot.
- `clase02/scripts/` — generadores: `build_notebook.py` (slides) y `build_colabs.py` (notebooks).

### Clase 3 — RAG (Retrieval Augmented Generation)

- `clase03/clase3_slides.ipynb` — slides conceptuales (reveal.js).
- `clase03/figures/` — figuras SVG.
- `clase03/notebooks/rag/` — notebooks de práctica para Colab:
  - `practica_completa.ipynb` — RAG naive de punta a punta sobre el
    programa real de la Cátedra IA UTN-FRSF 2026 (5 documentos).
    Cubre corpus → chunking → embeddings → ChromaDB → retrieval →
    augmentation → generation. Cierra probando el pipeline con tres
    queries (lookup directo, multi-fact, edge case) para ver dónde
    naive alcanza y dónde se queda corto.
  - `practica_legal.ipynb` — naive vs hybrid usando LangChain sobre un
    corpus real y extenso: la Ley argentina 21.526 de Entidades
    Financieras (67 artículos, ~91k chars). Dos casos: dense alcanza
    (vocabulario natural) y hybrid rescata (jerga técnica). Sección de
    exploración para que los alumnos investiguen reranker / pesos /
    embeddings.
  - `ley21526.pdf` — el corpus de `practica_legal.ipynb` bundleado en
    el repo para que la notebook funcione offline / sin depender del
    servidor de origen.

Pipeline RAG paso a paso (naive desde cero), búsqueda híbrida con RRF
en LangChain, y exploración guiada del impacto de reranking sobre un
corpus jurídico real.

### Clase 3b — Evaluación, monitoreo y benchmarks de sistemas LLM

- `clase03/clase3b_slides.ipynb` — slides (reveal.js).
- `clase03/notebooks/` — notebook de práctica para Colab:
  - `01_arize_eval_handson.ipynb` — end-to-end eval + monitoring de un
    chatbot Q&A con Arize AX (OpenTelemetry tracing, LLM-as-judge,
    dashboards, drift simulation).

Cinco fases del ciclo de vida (Fundamentos → Pre-deploy → Deploy →
Producción → Cierre) cubriendo LLM-as-judge, RAGAS, safety + red-teaming,
benchmarks propios, A/B/shadow/canary, drift detection, feedback loops.

### Próximas clases

- Clase 4 — Agentes

---

## Generar las slides

Las notebooks están pensadas para presentarse como reveal.js. Para exportar a HTML:

```bash
cd claseXX
jupyter nbconvert --to slides <archivo>.ipynb
```

Esto genera `<archivo>.slides.html`, que se abre en cualquier navegador y se navega con flechas (← → para slides; ↓ ↑ para subslides opcionales).

Para servirlas en localhost:

```bash
jupyter nbconvert --to slides <archivo>.ipynb --post serve
```

### Clase 2 — pipeline de generación

La notebook de slides y las notebooks de Colab se regeneran desde scripts:

```bash
cd clase02
python scripts/build_notebook.py    # regenera clase2_slides.ipynb
python scripts/build_colabs.py      # regenera las notebooks de Colab
jupyter nbconvert clase2_slides.ipynb --to slides --no-input
```

### Clase 3 y 3b — pipeline de generación

Las slides de clase 3 (RAG) contienen celdas de código visibles (demos),
las de clase 3b (eval/monitoring) son todas markdown. Las dos se regeneran
sin `--no-input`:

```bash
cd clase03
jupyter nbconvert clase3_slides.ipynb --to slides
jupyter nbconvert clase3b_slides.ipynb --to slides
```

Los notebooks de Colab se editan directamente (no hay build script todavía).

### Dependencias mínimas

Recomendamos un entorno virtual aislado para no contaminar el Python del
sistema:

```bash
python3 -m venv venv
source venv/bin/activate    # en Windows: venv\Scripts\activate
pip install jupyter nbconvert
```

El directorio `venv/` está en `.gitignore`. Para salir del entorno:
`deactivate`.

---

## Estructura del repositorio

```
.
├── clase01/
│   ├── vectores_slides.ipynb
│   └── figures/
├── clase02/
│   ├── clase2_slides.ipynb
│   ├── clase2_slides.slides.html
│   ├── figures/
│   ├── notebooks/
│   └── scripts/
├── clase03/
│   ├── clase3_slides.ipynb              # Clase 3: RAG
│   ├── clase3_slides.slides.html
│   ├── clase3b_slides.ipynb             # Clase 3b: Eval / monitoring / benchmarks
│   ├── clase3b_slides.slides.html
│   ├── figures/
│   └── notebooks/
│       ├── 01_arize_eval_handson.ipynb  # práctica de clase 3b
│       └── rag/                          # prácticas de clase 3
│           ├── practica_completa.ipynb   # naive desde cero → LangChain
│           ├── practica_legal.ipynb      # caso real sobre Ley 21.526
│           └── ley21526.pdf              # corpus de practica_legal
├── CITATION.cff
├── LICENSE
└── README.md
```

---

## Licencia

Este material se distribuye bajo la licencia
[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).

Sos libre de compartir, adaptar y reusar el material para cualquier
propósito, incluso comercial, siempre que cites a los autores. Si
querés citar este repo en un trabajo académico, usá el archivo
[`CITATION.cff`](CITATION.cff).
