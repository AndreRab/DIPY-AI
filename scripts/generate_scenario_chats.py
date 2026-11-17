from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODEL = "openai/gpt-oss-20b"
MAX_ATTEMPTS = 5
RETRY_DELAY_SECONDS = 60
SCENARIO_MODES = {
    "B": "clean",
    "Z": "laser_failure",
    "R": "laser_failure_sensor_and_melt_pool",
    "P": "position_noise",
}


def repository_path(value: str | Path) -> Path:
    path = Path(value)
    return (ROOT / path).resolve()


def load_questions(path: Path) -> list[str]:
    messages = json.loads(path.read_text(encoding="utf-8"))
    roles = ["user", "assistant"] * 4
    if not isinstance(messages, list) or len(messages) != len(roles):
        raise ValueError(f"{path}: expected four user/assistant pairs")
    for message, role in zip(messages, roles, strict=True):
        if (
            not isinstance(message, dict)
            or message.get("role") != role
            or not isinstance(message.get("content"), str)
            or not message["content"].strip()
        ):
            raise ValueError(f"{path}: invalid {role} message")
    return [message["content"] for message in messages[::2]]


@contextmanager
def frozen_simulator(data_folder: Path, mode: str, seed: int, steps: int):
    from dipy_ai.simulation import NIST_AMS_100_69_CorruptModeSimulator

    simulator = NIST_AMS_100_69_CorruptModeSimulator(
        data_folder=data_folder, corruption_mode=mode, seed=seed,
    )
    try:
        for _ in range(steps):
            simulator.step()
        yield simulator
    finally:
        simulator.data.close()


def build_agent(simulator: Any, config: Any):
    """Use the application's actual routing, tools, retrieval, and prompts."""
    from dipy_ai.agent import WorkflowAgent
    from dipy_ai.tools import generate_tool_bundles

    return WorkflowAgent(
        api_key=config.API_KEY,
        base_url=config.BASE_URL,
        model_name=MODEL,
        system_prompt_final_answer=config.SYSTEM_PROMPT_FINAL_ANSWER,
        system_prompt_tool_selection=config.SYSTEM_PROMPT_TOOL_SELECTION,
        tool_bundles=generate_tool_bundles(simulator, config.ANOMALY_THRESHOLDS),
    )


def run_scenario(agent: Any, questions: list[str], name: str) -> list[dict[str, str]]:
    from dipy_ai.agent.base_agent import UserMessage

    history: list[dict[str, str]] = []
    for number, question in enumerate(questions, 1):
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(
                f"  {name}{number:02d}: generating answer (attempt {attempt}/{MAX_ATTEMPTS})...",
                flush=True,
            )
            try:
                answer = agent.handle_message(
                    UserMessage(question), history=[dict(message) for message in history],
                )
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError(f"{name}{number:02d}: model returned an empty answer")
            except Exception as error:
                print(
                    f"  {name}{number:02d}: attempt {attempt}/{MAX_ATTEMPTS} failed "
                    f"({type(error).__name__}).",
                    flush=True,
                )
                if attempt == MAX_ATTEMPTS:
                    raise
                print(f"  Retrying in {RETRY_DELAY_SECONDS} seconds...", flush=True)
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                break
        history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
    return history


def save_transcript(path: Path, messages: list[dict[str, str]], *, overwrite: bool):
    """Publish only a complete transcript; preserve existing files by default."""
    payload = json.dumps(messages, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
        if overwrite:
            os.replace(temporary_path, path)
        else:
            # Linking fails atomically if another run has already created path.
            os.link(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=repository_path, default=ROOT / "outputs/20b-model")
    parser.add_argument("--output-dir", type=repository_path, default=ROOT / "outputs/120b-model")
    parser.add_argument("--scenarios", nargs="+", choices=SCENARIO_MODES, default=list(SCENARIO_MODES))
    parser.add_argument("--steps", type=int, default=10, help="Freeze each replay after this many samples (minimum: 10).")
    parser.add_argument("--seed", type=int, help="Override SIMULATOR_SEED from config/.env.")
    parser.add_argument("--data-folder", type=repository_path, help="Override SIMULATION_DATA_FOLDER; paths are relative to the repository.")
    parser.add_argument("--dry-run", action="store_true", help="Check questions and replay inputs without model/embedding calls or file writes.")
    parser.add_argument("--overwrite", action="store_true", help="Replace completed output transcripts from an earlier run.")
    args = parser.parse_args(argv)
    if args.steps < 10:
        parser.error("--steps must be at least 10 so history tools have ten samples")
    if args.input_dir.resolve() == args.output_dir.resolve():
        parser.error("--output-dir must differ from --input-dir")
    if len(args.scenarios) != len(set(args.scenarios)):
        parser.error("--scenarios must not contain duplicates")

    # Config and RAG use repository-relative paths, as in `make dev`.
    os.chdir(ROOT)
    from dipy_ai import config

    data_folder = args.data_folder or repository_path(config.SIMULATION_DATA_FOLDER)
    seed = config.SIMULATOR_SEED if args.seed is None else args.seed
    questions = {name: load_questions(args.input_dir / f"{name}.json") for name in args.scenarios}
    if not args.dry_run:
        for key, value in [("GROQ_API_KEY", config.API_KEY), ("GOOGLE_EMBEDDING_API_KEY", config.GOOGLE_EMBEDDING_API_KEY)]:
            if not value:
                parser.error(f"Missing {key}; configure it in the environment or root .env")
        for name in args.scenarios:
            path = args.output_dir / f"{name}.json"
            if path.exists() and not args.overwrite:
                parser.error(f"{path} already exists; use --overwrite or another --output-dir")

    print(f"Model: {MODEL}; seed: {seed}; samples per scenario: {args.steps}", flush=True)
    print("Same questions and JSON format; original screenshot tool inputs are not replayed.", flush=True)
    # Prepare every replay before making provider calls, catching data errors first.
    with ExitStack() as stack:
        simulators = {
            name: stack.enter_context(frozen_simulator(data_folder, SCENARIO_MODES[name], seed, args.steps))
            for name in args.scenarios
        }
        if args.dry_run:
            for name, simulator in simulators.items():
                print(f"\n{name}: mode={SCENARIO_MODES[name]}; output={args.output_dir / (name + '.json')}")
                print("Frozen state: " + json.dumps(asdict(simulator.get_current_state()), allow_nan=False))
                for number, question in enumerate(questions[name], 1):
                    print(f"  {name}{number:02d}: {question}")
            print("\nDry run complete: no provider calls or output files.")
            return 0

        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, simulator in simulators.items():
            print(f"\n{name}: {SCENARIO_MODES[name]}", flush=True)
            agent = build_agent(simulator, config)
            messages = run_scenario(agent, questions[name], name)
            path = args.output_dir / f"{name}.json"
            save_transcript(path, messages, overwrite=args.overwrite)
            print(f"  Saved {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
