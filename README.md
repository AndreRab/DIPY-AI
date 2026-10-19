# DIPy-AI

DIPy-AI is a modular AI architecture for industrial sensor-data processing, with a focus on metal additive manufacturing and Laser Powder Bed Fusion (LPBF).

The project explores how raw and model-processed manufacturing data can be transformed into useful information, domain knowledge, and operator-facing guidance. The current focus is Layer 3: the knowledge and reasoning layer that works with structured outputs from lower-level data and ML components.

For package-specific documentation, see [`src/dipy_ai/README.md`](src/dipy_ai/README.md).

## Architecture

DIPy-AI is organised as a three-layer pipeline:

```text
L1 — Sensor layer
     sensor-specific validation, calibration, and preprocessing
          |
          v
L2 — ML / information layer
     models convert sensor data into structured information
          |
          v
L3 — Knowledge layer
     context, retrieval, reasoning, explanation, and guidance
```

The Layer 3 direction is a controlled LLM pipeline: an incoming question or event is classified, mapped to a predefined set of tools, converted into a structured evidence package, and then synthesised into an explanation or recommendation. The aim is to keep the system predictable, grounded, and transferable across sensors and industrial contexts.

## Project materials

- [Layer 3 research and architecture proposal](docs/dipy-ai-layer-3-research-and-proposal.md) — related work, architectural decisions, and proposed tool bundles.
- [Model acceptance tests](docs/model-acceptance-tests.md) — test criteria, corruption scenarios, and prompt/expected-result chains.
- [Data overview notebook](data/data_overview.ipynb) — notes on the LPBF datasets, their fields, and possible uses.
- [NIST AMS 100-69 dataset](https://data.nist.gov/od/id/mds2-3761) — the main example dataset currently used for exploration.

The attached project documents provide background and research direction. The repository will collect implementation notes, experiments, datasets, and additional research documents as the work develops.

## Repository layout

```text
.
├── data/             # NIST CSV data, RAG source PDFs, and local vector index
├── docs/             # research, design notes, and model acceptance tests
├── frontend/         # React / Vite web application
├── scripts/dev.py    # starts and stops both development servers
├── src/dipy_ai/      # FastAPI, workflow agent, domain tools, and simulators
├── .env.example      # environment template (copy to .env)
├── Makefile          # setup and dev commands
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting started

Use Python 3.13 or newer, uv, Node.js with npm, and Make. The frontend's locked
frontend dependencies require a compatible Node.js version; use Node.js 22.13+
within the 22.x release line, or Node.js 24+.
Run all commands below from the repository root.

For the complete web application setup, follow **Running application** below.
To explore the data notebook after installing dependencies:

```bash
uv run jupyter lab data/data_overview.ipynb
```

## Running application

### 1. Install dependencies

```bash
make setup
```

This runs `uv sync` (creates/updates `.venv` and installs the Python package)
and `npm --prefix frontend ci` (installs the locked frontend dependencies).
You do not need to activate `.venv` when using the Make commands.

### 2. Copy and configure environment variables

If `.env` does not exist, copy the template into the repository root:

```bash
cp .env.example .env
```

If you already have `.env`, edit it instead of overwriting your keys. Replace
the placeholder values in **the root `.env`**, not in `.env.example` or a
frontend file:

```dotenv
GROQ_API_KEY=your_real_groq_api_key
GOOGLE_EMBEDDING_API_KEY=your_real_google_embedding_api_key
SIMULATION_DATA_FOLDER=data/AMS_NIST/part01
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
SIMULATOR_SEED=42
```

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Groq credential for request routing and answer generation. The configured model is `openai/gpt-oss-20b`. |
| `GOOGLE_EMBEDDING_API_KEY` | Google credential for RAG document/query embeddings using the configured `gemini-embedding-2` model. Required by the RAG tool constructed at backend startup. |
| `SIMULATION_DATA_FOLDER` | Directory containing the NIST CSV files; relative paths resolve from the repository root. |
| `FRONTEND_URL` | Vite bind address and FastAPI allowed CORS origin. Open this exact origin in the browser. |
| `BACKEND_URL` | Uvicorn bind address and API origin used by the frontend. |
| `SIMULATOR_SEED` | Integer seed for reproducible corruption decisions; default `42`. |

Both provider credentials must have access to the configured models. Keys stay
on the backend; `.env` is Git-ignored. Existing shell environment variables
override `.env`, so check exported values if your changes seem ineffective.

Optional variables supported by `src/dipy_ai/config.py`:

```dotenv
RAG_DATA_FOLDER=data/RAG_data/
RAG_CHROMA_DB=data/RAG_chroma/
CORRUPTION_MODE=laser_failure_sensor_only
```

`CORRUPTION_MODE` configures initial simulator construction. Select the mode for
an actual run in the Simulation panel. Supported IDs are `clean`,
`laser_failure_sensor_only`, `laser_failure_sensor_and_melt_pool`,
`laser_failure`, and `position_noise`.

### 3. Prepare simulation data and RAG documents

- Place compatible NIST AMS 100-69 CSV files directly inside
  `SIMULATION_DATA_FOLDER`. Use the dataset linked under Project materials.
  The reader uses the positional `COLUMN_NAMES` schema in
  `src/dipy_ai/simulation/nis_ams_100_69_simulator/nist_ams_100_69_simulator.py`
  and reads headerless CSV rows; arbitrary CSV schemas are not supported.
- Place at least one readable PDF with extractable text directly inside
  `RAG_DATA_FOLDER`. These documents supply the knowledge used in answers.
- Ensure `RAG_CHROMA_DB` is writable. On the first start, PDFs are split,
  embedded through Google, and stored in a local Chroma collection. Startup
  can take longer and requires network access to the embedding service.

The backend checks for CSVs and PDFs during startup, even before you start a
simulation. An existing nonempty Chroma collection is reused, so replacing
PDFs does not automatically refresh it. To index changed documents, stop the
application, set `RAG_CHROMA_DB` to a new empty directory, and restart.

### 4. Start the application

```bash
make dev
```

The runner reads the root `.env`, starts FastAPI with Uvicorn reload and the
Vite development server, and prints their URLs:

- Application: http://localhost:5173
- Interactive API docs: http://localhost:8000/docs
- Simulation snapshot: http://localhost:8000/simulation

These are the default addresses; use your configured URLs if you changed them.
Both URLs must be HTTP origins without paths, queries, or credentials, for
example `http://localhost:8001`. Use different free ports for the two servers.
Restart `make dev` after environment changes.

### 5. Start a simulation and ask questions

1. Open the frontend. The simulation initially waits for **Start**.
2. In **Simulation**, select a corruption mode (begin with **Clean**) and a
   step interval between 50 and 2000 ms, then press **Start**.
3. Wait for telemetry, inspect the commanded/measured laser path and expand a
   state row to see measurements.
4. Ask: `What is the current machine state? Report commanded and measured
   laser power and any evaluated anomalies.`
5. Press **Stop** to freeze telemetry for repeatable questions. **Resume**
   continues the same run; **Start** creates a fresh run and clears its
   telemetry history. Stop the run before selecting another mode.

Selecting a historical row changes the displayed inspection; chat tools still
read the simulator's latest state. The UI retains the last 100 states, while
the workflow's history tool supplies the last 10. The backend currently keeps
one shared agent conversation; starting a simulation does not clear that chat.
For independent acceptance cases, restart the backend to reset conversation
context. Follow the [model acceptance tests](docs/model-acceptance-tests.md)
for prompt chains and expected results.

Press `Ctrl+C` in the terminal running `make dev` to stop both servers.

### Troubleshooting

| Symptom | What to check |
| --- | --- |
| `Missing .env` or missing variables | Create the root `.env` and fill in the keys and both URLs. The runner explicitly checks Groq and URLs; embedding configuration is checked later by the RAG dependency. |
| `No CSV files found` / `No PDF files found` | Check the configured folder, file extension, and that files are directly inside it. Run from the repository root. |
| Authentication, model access, or embedding errors | Check the relevant provider key, model access, network connection, and quota. Both providers are needed. |
| Port already in use | Stop the other process or change the affected URL in `.env`, then restart. Vite uses a strict port. |
| Frontend cannot reach backend / CORS error | Confirm backend startup completed and `BACKEND_URL` is correct. Open the frontend at exactly `FRONTEND_URL` (including hostname and port). |
| No telemetry | Press Start and inspect backend logs for CSV parsing errors. |
| Answers use old PDF content | Restart with a fresh `RAG_CHROMA_DB` directory to rebuild the index. |

For the terminal alternative:

```bash
uv run python -m dipy_ai.main
```

Enter `exit` or `quit` to stop the terminal chat. See the
[package README](src/dipy_ai/README.md) and [frontend README](frontend/README.md)
for component details.

## Related implementation reference

The Dante example is intended to serve as a reference for implementation patterns and project organisation. Its integration into this repository will be documented here when the relevant code or link is added.

## Safety

This is a research project. Outputs are intended for analysis and operator support, not for direct autonomous control of manufacturing equipment. Any operational recommendation should remain subject to human review.
