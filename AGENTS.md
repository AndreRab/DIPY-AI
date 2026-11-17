# DIPy-AI project instructions

## Project context

DIPy-AI is a modular architecture for industrial sensor intelligence. The
current demonstrator uses laser powder bed fusion (LPBF) data from NIST AMS
100-69. Its three layers are sensor-specific preprocessing (L1), information
extraction (L2), and application-specific knowledge interpretation (L3).

Before project work, read `README.md` and inspect the relevant implementation.
Read `src/dipy_ai/README.md` for backend work and `frontend/README.md` for UI
work. Check the working tree and preserve unrelated user changes.

The backend lives in `src/dipy_ai/` (FastAPI, LangGraph orchestration, domain
tools, simulation, and conversation persistence). The React/TypeScript/Vite
application lives in `frontend/`. Research and manuscript materials belong
in `docs/`; datasets and retrieval sources live in `data/`.

## Paper conversation trigger

If the first user message containing the actual task starts with the word
`paper` (case-insensitive, allowing leading whitespace and punctuation after
the word), treat the conversation as paper work. Ignore setup messages such
as pasted agent instructions when identifying that message. Keep this context
active for follow-up requests in the same conversation. Also use this workflow
when the user explicitly requests manuscript or abstract work without the prefix.

Before giving substantive paper advice or making manuscript edits, read these
project documents from `docs/`:

1. `dipy-ai-paper-outline-and-work-plan.md` — manuscript scope, contributions,
   relationship to earlier work, and evaluation roadmap.
2. `dipy-ai-layer-3-research-and-proposal.md` — Layer 3 design and tool bundles.
3. `dipy-ai-related-work-architecture-review-2026.md` — related work,
   positioning, candidate claims, and evaluation considerations.

Read additional primary project materials according to the request:

- Architecture, origin, or attribution: `BICA_Paper_DiyPY-6.pdf` and relevant
  sections of `BICA_Paper_DiyPY (3).pdf`. These are overlapping manuscript
  versions, not independent evidence. Use `BICA_Paper_DiyPY-5.pdf` when
  comparing the broader four-layer decomposition; do not conflate it with L1–L3.
- Project objectives and initial requirements: `Industrial LLM Project.pdf`
  and, where relevant, `industrial_llm_agent_report.docx`.
- Experiments and expected behavior: `model-acceptance-tests.md` and relevant
  simulator/tool code. Read `data/RAG_data/NIST.AMS.100-69.pdf` when dataset
  details are needed.
- Chat architecture or persistence claims: `chat-history-backend-design.md`
  and the current implementation.

Inspect `docs/` for new or renamed materials before relying on this list. Read
the relevant contents, not just filenames. Reuse documents already read in the
conversation unless changed; if a required source is unavailable, state the
gap and avoid inventing its contents.

## Live manuscript

When reviewing or editing the current paper, read the live DIPY-AI project
through Overleaf MCP if available. The known project ID is
`6ae8721d83d137e78a8dbd88` on `overleaf.com`; its main document is `main.tex`.
Verify the project and tree before use. The live manuscript is authoritative
for its current wording; local planning documents provide background and must
not silently override newer user decisions or manuscript changes.

Use exact text replacements for focused Overleaf edits and account for
collaborator changes. A review request alone does not authorize manuscript
changes. If Overleaf is disconnected, explain the access limitation and use
available sources without claiming to have read the latest manuscript.

## Scientific accuracy

- Verify implementation claims against current code rather than relying only
  on documentation. The current workflow selects a predefined tool bundle,
  executes tools, and synthesizes an answer; do not assume independent
  autonomous agents operate in every layer.
- Distinguish implemented features, planned experiments, and future extensions.
  Do not turn evaluation plans into results or invent measurements.
- Emphasize explicit interfaces, modularity, component replacement, tool
  extensibility, and operator support. Transfer to other datasets or industries
  is a design goal until evaluated.
- Credit earlier DIPy-AI architecture; verify publication status before making
  novelty or priority claims. Existing reviews are research notes, not a
  substitute for primary-source verification of literature claims.
- Distinguish replay and synthetic faults from production deployment and
  confirmed physical defects. Separate observations, model outputs, retrieved
  knowledge, and causal hypotheses.
- Local model deployment is not demonstrated merely because a remotely served
  model has open weights. Verify generation, embedding, retrieval, and measured
  hardware performance separately.
- Treat outputs as operator-facing guidance subject to human review.

## Implementation and validation

Keep changes focused and follow existing interfaces and conventions. Never
expose credentials or overwrite `.env`. Use the documented `make setup` and
`make dev` workflow when needed. For frontend changes, use the relevant
`npm --prefix frontend run build` and `npm --prefix frontend run lint` checks.
For backend changes, inspect the available tests and run checks appropriate to
the affected behavior. Documentation-only edits require a content/diff review,
not application startup or paid model calls. Report what was actually verified.
