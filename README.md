# DIPy-AI

DIPy-AI is a modular AI architecture for industrial sensor-data processing, with a focus on metal additive manufacturing and Laser Powder Bed Fusion (LPBF).

The project explores how raw and model-processed manufacturing data can be transformed into useful information, domain knowledge, and operator-facing guidance. The current focus is Layer 3: the knowledge and reasoning layer that works with structured outputs from lower-level data and ML components.

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
- [Data overview notebook](data/data_overview.ipynb) — notes on the LPBF datasets, their fields, and possible uses.
- [NIST AMS 100-69 dataset](https://data.nist.gov/od/id/mds2-3761) — the main example dataset currently used for exploration.

The attached project documents provide background and research direction. The repository will collect implementation notes, experiments, datasets, and additional research documents as the work develops.

## Repository layout

```text
.
├── data/       # datasets and data-exploration notebooks
├── docs/       # research notes and architecture documents
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting started

The project uses Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
source .venv/bin/activate
```

To explore the data notebook:

```bash
cd data
uv run jupyter lab data_overview.ipynb
```

## Related implementation reference

The Dante example is intended to serve as a reference for implementation patterns and project organisation. Its integration into this repository will be documented here when the relevant code or link is added.

## Safety

This is a research project. Outputs are intended for analysis and operator support, not for direct autonomous control of manufacturing equipment. Any operational recommendation should remain subject to human review.
