# DIPy-AI

DIPy-AI is a modular Python package for experimenting with AI-assisted
industrial sensor-data processing, with an initial focus on metal additive
manufacturing and Laser Powder Bed Fusion (LPBF).

The current implementation combines a conversational LLM agent with a small
simulation layer. It is a foundation for the Layer 3 knowledge and reasoning
system described in the project research documents.

## Package structure

```text
dipy_ai/
├── agent/
│   ├── base_agent.py          # Agent interface and UserMessage
│   ├── one_step_llm_agent.py  # OpenAI-compatible chat agent
│   └── workflow_agent.py      # Tool-routed workflow agent
├── api/
│   └── app.py                 # FastAPI application used by the frontend
├── simulation/
│   ├── base_simulator.py      # Simulator interface and State
│   ├── nist_ams_100_69_simulator.py # NIST CSV data simulator
│   └── simulation_runner.py   # Background simulation loop
├── tools/
│   ├── base_tool.py           # Base interface for domain tools
│   └── anomaly_tool.py        # Command-to-measurement deviation analysis
├── config.py                  # Environment-backed configuration
└── main.py                    # Interactive terminal application
```

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm for the web frontend
- A Groq API key for the default LLM configuration

## Installation with uv

From the repository root, install the project and its locked dependencies:

```bash
uv sync
```

`uv sync` creates or updates `.venv` and installs the package in editable
mode. You can run commands through `uv run`, or activate the environment:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Configuration

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_api_key_here
SIMULATION_DATA_FOLDER=data/AMS_NIST/part01
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

The current defaults in `config.py` are:

- API endpoint: `https://api.groq.com/openai/v1`
- Model: `openai/gpt-oss-20b`

The simulation data folder is resolved relative to the current working
directory; run the backend from the repository root. Anomaly thresholds are
configured in `config.py` with the keys `x_position` and `y_position` (mm),
`laser_power` (W), and `scan_speed` (mm/s). Set validated absolute tolerances
for the signals you want evaluated. Any threshold left unset is reported as
`not_evaluated`.

## Start the frontend and FastAPI backend

From the repository root, create `.env` from `.env.example` if needed, add your
Groq API key, and install the Python and frontend dependencies once:

```bash
[ -f .env ] || cp .env.example .env
make setup
```

Start both servers together:

```bash
make dev
```

The Makefile runner reads `FRONTEND_URL` and `BACKEND_URL` from the root `.env`
and uses them to bind Vite and Uvicorn. FastAPI reads the same `FRONTEND_URL`
for CORS, and Vite reads `BACKEND_URL` for its `/invoke` request. The API docs
are available at `BACKEND_URL/docs` (normally
<http://localhost:8000/docs>). Press `Ctrl+C` to stop both servers.

See the [frontend README](../../frontend/README.md) for frontend-specific
details.

## Start the terminal application

To use the terminal chat instead of the web frontend, run from the repository
root:

```bash
uv run python -m dipy_ai.main
```

The application starts the NIST simulation runner and opens a terminal chat.
Enter `exit` or `quit` to stop it.

## Main components

### `dipy_ai.agent`

Defines the base agent contract, the `UserMessage` data object, and
`OneStepLLMAgent`, which sends each user message to an OpenAI-compatible chat
completion endpoint.

### `dipy_ai.simulation`

Defines the simulator contract, the NIST AMS 100-69 CSV simulator, and a
background `SimulationRunner`.

### `dipy_ai.tools`

Provides the base interface for tools that can expose structured domain
operations to the knowledge layer.

## Project direction

DIPy-AI is organised around a three-layer pipeline:

```text
L1 — Sensor layer       validation, calibration, and preprocessing
          |
          v
L2 — ML / information   conversion of sensor data into structured information
          |
          v
L3 — Knowledge layer     context, retrieval, reasoning, explanation, guidance
```

See the [Layer 3 research and architecture proposal](../../docs/dipy-ai-layer-3-research-and-proposal.md)
for the broader design, research context, and planned tool bundles.
