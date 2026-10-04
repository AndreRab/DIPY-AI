import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]


def read_environment() -> dict[str, str]:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        raise SystemExit("Missing .env. Copy .env.example to .env and configure it first.")

    file_values = {
        key: value
        for key, value in dotenv_values(env_path).items()
        if key is not None and value is not None
    }
    # Match dotenv's default behavior: existing shell variables take precedence.
    env = {**file_values, **os.environ}

    missing = [key for key in ("FRONTEND_URL", "BACKEND_URL") if not env.get(key)]
    if missing:
        raise SystemExit(f"Missing {', '.join(missing)} in .env.")
    if not env.get("GROQ_API_KEY"):
        raise SystemExit("Missing GROQ_API_KEY in .env.")
    return env


def parse_local_http_url(env: dict[str, str], key: str) -> tuple[str, int]:
    value = env[key]
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or not parsed.hostname
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise SystemExit(
            f"{key} must be an http origin such as http://localhost:8000 (without a path)."
        )

    try:
        port = parsed.port if parsed.port is not None else 80
    except ValueError as error:
        raise SystemExit(f"Invalid port in {key}: {error}") from error
    if not 1 <= port <= 65535:
        raise SystemExit(f"Port in {key} must be between 1 and 65535.")
    return parsed.hostname, port


def stop_process(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> int:
    env = read_environment()
    backend_host, backend_port = parse_local_http_url(env, "BACKEND_URL")
    frontend_host, frontend_port = parse_local_http_url(env, "FRONTEND_URL")

    if shutil.which("npm") is None:
        raise SystemExit("npm was not found. Install Node.js and npm to run the frontend.")

    print(f"Backend:  {env['BACKEND_URL']}", flush=True)
    print(f"Frontend: {env['FRONTEND_URL']}", flush=True)
    processes: list[subprocess.Popen] = []
    exit_code = 0

    try:
        processes.append(subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "dipy_ai.api.app:app",
                "--reload",
                "--host",
                backend_host,
                "--port",
                str(backend_port),
            ],
            cwd=ROOT,
            env=env,
        ))
        processes.append(subprocess.Popen(
            [
                "npm",
                "run",
                "dev",
                "--",
                "--host",
                frontend_host,
                "--port",
                str(frontend_port),
                "--strictPort",
            ],
            cwd=ROOT / "frontend",
            env=env,
        ))

        while True:
            completed = [process.poll() for process in processes]
            if any(code is not None for code in completed):
                exit_code = next(code for code in completed if code is not None)
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping both development servers...", flush=True)
    finally:
        for process in processes:
            stop_process(process)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
