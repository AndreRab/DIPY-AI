# Scenario chat export

Run the four question chains with `openai/gpt-oss-120b` through the existing
workflow, including model-selected tool bundles and RAG:

```bash
uv run python scripts/generate_scenario_chats.py --dry-run
uv run python scripts/generate_scenario_chats.py
```

The script reads the exact user questions from `outputs/20b-model/` and writes
`B.json`, `Z.json`, `R.json`, and `P.json` to `outputs/120b-model/`. Each file
contains only `role` and `content`, with four user/assistant pairs. Previous
20B answers are not supplied to the model. Existing output files require
`--overwrite` to replace them. Failed scenarios do not publish partial files;
already completed scenario files remain available.

Each question gets up to **5 attempts total** (the initial attempt plus four
retries). If the workflow raises an error or returns an empty answer, the
script waits **60 seconds** before trying the same question again. Only
successful answers enter the conversation history. After the fifth failure,
the script stops and reports the error, with no additional wait.

Use the normal project environment from `make setup` and configure
`GROQ_API_KEY`, `GOOGLE_EMBEDDING_API_KEY`, simulation CSVs, and RAG PDFs/index
as described in the root README. Generation uses the configured remote Groq
endpoint and Google embeddings. The dry run only validates questions and
replays CSV data; it makes no provider calls and writes no output files.

Each scenario starts with fresh conversation history and a separate seeded
simulator. Modes are B=`clean`, Z=`laser_failure`,
R=`laser_failure_sensor_and_melt_pool`, and P=`position_noise`. By default,
each replay advances exactly ten samples and stays frozen for all four
questions. The script uses the current anomaly thresholds and system prompts.
It does not start the application, change its configuration, or write chat
history to its database.

To select a different frozen sample or run only selected scenarios:

```bash
uv run python scripts/generate_scenario_chats.py --steps 20 --seed 42 --scenarios B R
```

`--data-folder`, `--input-dir`, and `--output-dir` also accept custom paths;
relative paths resolve against the repository root. The original screenshot
runs advanced between some questions, and their complete tool inputs were
not archived. This script reproduces the questions and export format using
new, controlled inputs; it cannot establish an identical-input comparison
with those historical 20B answers.

Offline checks (no model or embedding calls):

```bash
uv run python -m unittest discover -s scripts/tests -v
```
