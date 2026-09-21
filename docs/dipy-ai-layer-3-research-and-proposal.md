# DIPy-AI Layer 3: Related Work and Architecture Proposal

## Five related research works

### 1. Halder and Mojumder — Agentic AI for WAAM monitoring

**Paper:** [In-situ process monitoring for defect detection in wire-arc additive manufacturing: an agentic AI approach](https://arxiv.org/abs/2604.09889)

**Core idea:** Separate agents analyse different process signals. A processing agent uses current and voltage data, while a monitoring agent uses acoustic data. Their ML tools detect porosity, and an orchestrator combines the results.

**Architecture:**

```text
Process signals -> 1D/2D CNN tools -> specialist agents
                -> parallel reports -> orchestrator -> defect decision
```

This is the clearest example of tools wrapped by specialist agents and then combined by a central orchestrator.

### 2. Gautam et al. — IIoT digital twin with LLM agents

**Paper:** [IIoT-enabled digital twin for legacy and smart factory machines with LLM integration](https://doi.org/10.1016/j.jmsy.2025.03.022)

**Core idea:** A digital twin exposes real-time and historical machine data to a supervisor agent. The supervisor routes each request to a suitable specialist, such as machine expertise, visualisation, or fault diagnosis.

**Architecture:**

```text
Machines -> MTConnect / IIoT platform -> digital twin
          -> supervisor agent -> specialist agent -> operator
```

This work is close to an industrial operator copilot with dynamic routing.

### 3. Jazi and Ameri — Semantic digital twin with RAG

**Paper:** [Large Language Model-Augmented Semantic Digital Twins for Real-Time Fault Diagnosis and Closed-Loop Control](https://doi.org/10.1115/1.4071805)

**Core idea:** Real-time machine data is mapped into an ontology and knowledge graph. RAG retrieves only the relevant faults, rules, causes, and corrective actions. The LLM then produces an explanation or an action command.

**Architecture:**

```text
Telemetry -> semantic mapping -> ontology / knowledge graph
          -> targeted RAG -> LLM -> explanation or action
```

The important lesson is to give the LLM relevant structured context, not all raw telemetry.

### 4. Li et al. — AM-Agent for data and knowledge fusion

**Paper:** [Data-Driven Meets Knowledge-Driven: An LLM-Agent Framework for Quality Control in Metal Additive Manufacturing](https://doi.org/10.1016/j.jii.2026.101182)

**Core idea:** Two independent evidence sources are used for LPBF quality control. A Data-driven Prediction Service provides material-specific ML predictions. A Knowledge Service uses RAG and Asset Administration Shell (AAS) context. Their outputs are combined with a reliability-weighted Linear Opinion Pool.

**Architecture:**

```text
                         -> ML prediction service -\
Supervisor LLM -> tool calls                         -> weighted fusion -> decision
                         -> RAG + AAS knowledge --/
```

This shows how a forecast or prediction model can be combined with domain knowledge. The probability fusion should be deterministic, not left to the final LLM.

### 5. Williams et al. — Digital twin predictive maintenance

**Paper:** [Cross-domain digital twin architecture for predictive maintenance via machine learning and Large Language Models](https://doi.org/10.1016/j.cie.2026.111914)

**Core idea:** Sensor streams are sent through MQTT to a Random Forest fault classifier. The predicted fault state is then sent to an edge LLM, which creates short maintenance guidance for the operator.

**Architecture:**

```text
Sensors -> MQTT -> Random Forest -> predicted fault
        -> MQTT -> edge LLM -> maintenance guidance
```

This is the simplest sequential pattern: detect, classify, explain, and recommend.

## Proposal for DIPy-AI Layer 3

The proposed Layer 3 combines the useful ideas from all five works while keeping the execution predictable and low-latency.

```text
Operator query or L2 event
          |
          v
Fast intent / classification model
          |
          v
Predefined tool bundle
          |
          +--> tools run in parallel
          |
          v
Structured evidence package
          |
          v
Fast final synthesis LLM
          |
          v
Status, explanation, or recommendation for the operator
```

The classification layer decides the task, not an arbitrary sequence of tools. Each task maps to a deterministic, predefined bundle. Tools should return structured results such as current state, anomaly severity, history, forecast probability, or retrieved evidence.

Use a low-latency Flash/fast model for intent classification. Use a fast model for final synthesis when the task is routine and the evidence is already structured. A stronger model can be added only for difficult or high-risk cases.

For forecast tasks, a specialised `forecast_model` should produce the numeric prediction. If ML and knowledge evidence must be reconciled, use a deterministic `evidence_fusion` step before the final LLM. The LLM should explain the result, not perform the probability arithmetic.

## Scenario-to-tool bundles

| Scenario | Exact tool bundle | Output |
|---|---|---|
| Current Situation | `current_state`, `anomaly_context` | Current status and active deviations |
| Anomaly Analysis | `current_state`, `anomaly_context`, `history`, `RAG` | Anomaly meaning, severity, and likely effects |
| Root Cause | `current_state`, `anomaly_context`, `history`, `RAG`, `machine_context` | Ranked possible causes and supporting evidence |
| Historical Comparison | `current_state`, `history` | Comparison with previous layers, builds, or events |
| Forecast | `current_state`, `history`, `forecast_model`, `RAG` | Prediction, horizon, uncertainty, and explanation |
| Domain QA | `RAG`, `machine_context` | Grounded answer from manuals, papers, and process knowledge |
| Recommendation | `current_state`, `anomaly_context`, `history`, `RAG`, `machine_context` | Operator checks and recommended next action |

This design is a controlled hybrid: it supports sequential flows, specialist tools, targeted RAG, and ML-plus-knowledge fusion without requiring an open-ended agent loop.
