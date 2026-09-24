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
│   └── one_step_llm_agent.py  # OpenAI-compatible chat agent
├── simulation/
│   ├── base_simulator.py      # Simulator interface and State
│   ├── mock_simulator.py      # Minimal simulator implementation
│   └── simulation_runner.py   # Background simulation loop
├── tools/
│   └── base_tool.py           # Base interface for domain tools
├── config.py                  # Environment-backed configuration
└── main.py                    # Interactive application entry point
```

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
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
```

The current defaults in `config.py` are:

- API endpoint: `https://api.groq.com/openai/v1`
- Model: `openai/gpt-oss-20b`

## Start the application

Run the interactive application from the repository root:

```bash
uv run python -m dipy_ai.main
```

The application starts the mock simulation runner and opens a terminal chat.
Enter `exit` or `quit` to stop the simulation and close the application.

## Main components

### `dipy_ai.agent`

Defines the base agent contract, the `UserMessage` data object, and
`OneStepLLMAgent`, which sends each user message to an OpenAI-compatible chat
completion endpoint.

### `dipy_ai.simulation`

Defines the simulator contract and a background `SimulationRunner`. The
current `MockSimulator` is intentionally minimal and can be replaced with a
domain-specific simulator as the project develops.

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
