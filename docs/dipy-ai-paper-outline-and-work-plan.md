# DIPy-AI: preliminary paper outline and work plan

Draft for discussion, 2 November 2026. This is a proposed study and manuscript skeleton; results are not yet available. Literature claims in the supplied documents have not been independently reverified for this outline.

## 1. Central direction

**Working title:** DIPy-AI: A Brain-Inspired Layered Architecture and Modular Implementation Framework for Industrial Sensor Intelligence.

**Scope:** present the DIPy-AI architectural principles, operationalize them through explicit interfaces and a controlled orchestration framework, and evaluate an LPBF demonstrator. The contribution should center on modular implementation, adaptation effort, operator-facing evidence, and feasibility of local deployment.

DIPy-AI already appears in the supplied BICA manuscripts. The new paper must credit that architectural foundation and identify its extension: executable interfaces, implemented orchestration, and measured evidence of the architecture's benefits. Confirm the manuscripts' publication status and relationship before deciding whether to describe the architecture as newly proposed, extended, or implemented.

**Draft positioning paragraph:**

> Building on the brain-inspired DIPy-AI architecture, this work develops a modular implementation framework for industrial sensor intelligence. Sensor-specific preprocessing, information extraction, and application-specific knowledge interpretation are separated through explicit interfaces. A controlled orchestration workflow connects process evidence and domain knowledge to operator-facing explanations. An LPBF replay demonstrator is used to investigate functional reliability, component replacement effort, and the feasibility of operation with locally hosted language and embedding models.

[TODO: final title, venue, authors, relationship to earlier DIPy-AI work.]

## 2. What the supplied materials establish

| Material | Role in this paper | Important distinction |
| --- | --- | --- |
| `BICA_Paper_DiyPY-6.pdf`, pp. 4–6 | Three-layer architectural foundation; wrappers, heterogeneity, human feedback; thalamus-inspired preprocessing | Architectural proposal; described benefits still require evaluation |
| `BICA_Paper_DiyPY (3).pdf` | Closely overlapping version of the same three-layer manuscript | Extracted text differs mainly in author/affiliation block and pagination; do not treat as independent evidence |
| `BICA_Paper_DiyPY-5.pdf`, sections III–IV | Broader connectivity → digital thread → ML/MLOps → MCP/assistant stack | A different four-layer decomposition, not simply another numbering of our L1–L3 |
| `Industrial LLM Project.pdf`, pp. 1–3 | Layer 3 project brief: replay, fault injection, event wrapper, situational awareness and evaluation | Earlier ambition includes control recommendations; proposed study uses operator-reviewed guidance |
| Existing research review and acceptance protocol | Related-work map, conservative claims, scenarios and evaluation ideas | Planning material, not completed experiments |
| Repository implementation | Executable starting point for the demonstrator | Prototype coverage is narrower than the complete architectural vision |

## 3. Architecture and terminology

Use one canonical three-layer diagram throughout the paper:

**Sensors / replay → L1 preprocessing and data packaging → L2 information extraction → structured evidence wrapper → L3 orchestration and knowledge interpretation → operator.**

A human-reviewed feedback path can describe requested changes to goals, configuration or component selection. Mark unimplemented feedback paths explicitly as proposed.

| Component | Responsibility | Interface placeholder |
| --- | --- | --- |
| L1: sensor-dependent processing | Validation, units, calibration metadata, optional calibration/compression | [Sensor record schema and adapter contract] |
| L2: information extraction | Features, anomaly signals or model outputs; exchangeable implementations | [Information/event schema with time, source, quality and model version] |
| Inter-layer wrappers | Isolate source formats and domain-specific translations | [Minimal input/output example and validation rules] |
| L3: knowledge interpretation | Intent routing, bounded tool execution, evidence assembly, explanation | [Bundle registry, evidence contract, answer format] |
| Operator feedback | Review hypotheses and guidance; request a new goal or configuration | [One human-reviewed adaptation example] |

“Brain-inspired” describes functional inspiration: staged abstraction, heterogeneous inputs, contextual interpretation and feedback. The BICA document specifically associates preprocessing with the thalamus. It is not evidence of biological fidelity or a causal explanation for improved software performance. Measure modularity and adaptation directly.

Use Data–Information–Knowledge as the implemented three-layer mapping. Explain the DIKW origin while avoiding an unsupported additional implemented “wisdom” layer. “Sensor-agnostic L2” should mean standardized interfaces and replaceable processing components; models can still require sensor-specific features or retraining.

Agents at each layer are an optional extension. Define their actual responsibilities and allowed operations before adding them. The current LangGraph workflow does not establish that independent agents operate across all three layers.

## 4. Current implementation versus proposed work

| Capability | Current evidence | Work needed |
| --- | --- | --- |
| LPBF replay and synthetic faults | NIST CSV simulator and corruption modes | Freeze cases; preserve reference values and provenance |
| L1 calibration/compression | Part of architectural proposal | Implement only what is in study scope; label the rest conceptual |
| L2 processing | Deterministic deviation analysis is available | Specify its role; distinguish it from a validated learned defect detector |
| L3 orchestration | Six predefined bundles; parallel tools; final synthesis | Add reproducible routing/evidence/latency traces and defined failure behavior |
| Domain retrieval | PDF retrieval with Chroma | Return source/page metadata; freeze corpus and index version |
| Local operation | Current generation uses Groq; embeddings use Google | Configure local generation AND local embeddings, including index creation |
| Plug-in adaptability | Existing tool and simulator abstractions | Specify stable contracts and perform a component replacement experiment |
| Industrial collaboration | Architectural motivation and named partners in source manuscripts | Confirm actual participation; demonstrate module ownership/integration if available |
| Cross-industry transfer | Intended architectural benefit | Keep as future work unless evaluated in another setting |
| Multi-layer agents / adaptive feedback | Architectural extension | Optional demonstrator after core study, not a prerequisite |

## 5. Approximate manuscript outline

### Abstract

[Problem: heterogeneous industrial sensing and costly adaptation.]
[Approach: brain-inspired layered architecture + implementation framework.]
[Demonstrator: NIST LPBF replay, controlled faults, local configuration.]
[Evaluation: reliability, adaptation effort, runtime and hardware.]
[Results: insert measured findings only after experiments.]

### 1. Introduction

- Industrial problem: changing sensors, analytical models, operator goals and organizational ownership.
- Motivation for staged abstraction, explicit interfaces and locally deployable components.
- Scope and relationship to the earlier DIPy-AI architecture.
- Contributions: (C1) specified modular architecture/interfaces, (C2) executable framework, (C3) evaluated LPBF case study and adaptation/local-deployment experiments.

[TODO: precise contribution statements and reference to original DIPy-AI publication/manuscript.]

### 2. Background and related work

- DIKW and brain-inspired cognitive architectures.
- Modular industrial sensing, digital twins and interoperability.
- Industrial LLM assistants and evidence-grounded orchestration.
- Locally hosted models and industrial data boundaries.

[Table: closest approach, architectural scope, interface modularity, deployment, evaluation.]
[TODO: verify relevant full texts and bibliographic status; reuse existing review as a starting map.]

### 3. DIPy-AI architecture and design requirements

- Three layers and their responsibilities.
- Wrappers, data contracts, provenance and component lifecycle.
- Human feedback and module ownership across collaborators.
- Deployment boundary and intended agent roles.

[Figure 1: three-layer architecture, wrappers, operator and feedback.]
[Table 1: requirements → mechanisms → tests.]
[Example 1: sensor measurement → information event → operator explanation.]

### 4. Implementation framework

- Adapter, simulator, processing and tool interfaces.
- Intent classification → predefined bundle → parallel execution → evidence → synthesis.
- Six implemented use cases; model/embedding provider configuration.
- API, UI, conversation history and reproducibility logging.
- Implemented versus proposed components.

[Figure 2: implementation workflow and local deployment boundary.]
[Table 2: module inventory and replacement points.]
[TODO: schema snippets, software versions, configuration.]

### 5. LPBF demonstrator and experimental protocol

- NIST data subset, replay assumptions, physical quantities and units.
- Clean and synthetic-fault scenarios; missing data and boundary cases.
- Fixed question episodes and expected answers.
- Component replacement and operator-goal change tasks.
- Local inference configuration, hardware and external-service dependencies.

[Table 3: scenarios, evidence oracle and expected behavior.]
[TODO: independent episodes, annotation, repeated runs, hardware, models.]

### 6. Results

- Functional grounding and routing reliability.
- Adaptation effort and integration regressions.
- Local deployment feasibility, latency, memory and output quality.
- Failures and uncertainty handling.

[Table 4: factual accuracy, unsupported claims, routing and failure rates.]
[Table 5: files/modules changed, effort and regressions per adaptation task.]
[Figure 3: latency distribution and quality/resource trade-off.]
[TODO: measured results, uncertainty intervals and representative failures.]

### 7. Discussion and limitations

- What evidence supports modularity and collaboration, and at what scale.
- Functional brain inspiration versus demonstrated engineering effects.
- Local deployment trade-offs and the actual data boundary.
- Replay and synthetic faults versus production deployment and physical diagnosis.
- Limited sensor/domain coverage; optional MCP, multi-layer agents and feedback extensions.

### 8. Conclusion and future work

[Answer research questions using results.]
[Next steps: new sensors, partner integration, validated L2 models and broader transfer.]

## 6. Research questions and minimal experiments

| Question | Minimum experiment | Evidence to collect |
| --- | --- | --- |
| RQ1: Can the framework generate grounded operator explanations from layered evidence? | Frozen normal/fault/missing-data episodes and manual acceptance chains | Field accuracy, unsupported claims, routing trace, abstention and failures |
| RQ2: How much work is required to change a sensor source, processing component or operator goal? | Replace one input adapter, one L2 processor, and add/change one task bundle separately | Engineering time, files/modules changed, core changes, integration errors and regressions |
| RQ3: Can the complete pipeline operate within a declared local boundary with useful performance? | Same frozen episodes with locally hosted generation and embeddings | Quality, p50/p95 latency, RAM/VRAM, hardware, model/quantization, dependency and outbound-call audit |
| RQ4: Does bounded orchestration provide a useful trade-off? | Compare fixed all-tools bundle and task-selected bundle; add unrestricted agent if feasible | Quality, latency, tokens, tool calls and failures under matched evidence access |

For RQ2, record a baseline task using direct source-specific integration or an existing coupled implementation if feasible. Without a comparable baseline, report observed adaptation effort rather than a reduction. Specify task acceptance criteria before timing. If a second developer/team is available, use a documented module handoff to test collaboration; otherwise assess interface usability only.

Start with a small pilot suite, then decide sample size from task coverage, variance and available independent episodes. Do not count correlated replay rows as independent builds. Keep synthetic faults separate from measured defects. Use a dedicated forecasting model only if forecasting enters the evaluated scope.

## 7. Proposed work sequence

| Stage | Main work | Deliverable / completion criterion |
| --- | --- | --- |
| A. Align scope | Confirm canonical layers, earlier-paper relationship, contribution and demonstrator boundary | Agreed 1-page scope and architecture diagram |
| B. Specify contracts | Define sensor, event and evidence schemas; module responsibilities and examples | Small interface specification and worked example |
| C. Make prototype observable | Add traces, retrieval provenance, consistent episode snapshots, explicit errors | Reproducible run with inspectable evidence and routing |
| D. Establish baseline | Freeze data/questions and run the existing acceptance protocol | Recorded baseline results and failure list |
| E. Test adaptation | Swap adapter/processor and change a goal through documented extension points | Change log, effort record and regression outcomes |
| F. Validate local pipeline | Replace remote inference and embedding dependencies; repeat matched cases | Local configuration, hardware report, boundary verification and performance results |
| G. Evaluate and write | Run comparisons, analyze failures, fill results placeholders | Tables/figures, limitations and completed manuscript draft |

Stages are ordered by dependencies, not promised calendar dates. Draft sections 1–5 while implementing; finalize abstract, claims and conclusion after results. Keep MCP, full MLOps infrastructure, autonomous reconfiguration and agents in every layer outside the minimum study unless a research question requires them.

## 8. Decisions to settle during the first review

1. Is the target an architecture/framework paper with an LPBF validation case, and what venue/length fits it?
2. Which BICA manuscript is the authoritative prior version, and has any version been published?
3. Which hardware and model budget are available for fully local inference and embeddings?
4. Which component swap best represents a real partner need, and can another developer perform the integration?
5. Are partner data and participation available, or should the first study explicitly remain NIST-only?

These decisions refine the study; the outline can proceed with NIST replay, the three-layer architecture, and local deployment as an experimental objective.
