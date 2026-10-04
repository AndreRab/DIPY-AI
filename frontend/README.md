# DIPy-AI Frontend

The frontend is a React and TypeScript application served by Vite. It sends
prompts to the FastAPI backend at `${BACKEND_URL}/invoke`, using `BACKEND_URL`
from the repository root `.env` file.

## Requirements

- Node.js and npm
- [uv](https://docs.astral.sh/uv/)
- A root `.env` file with `GROQ_API_KEY`, `FRONTEND_URL`, and `BACKEND_URL`

## Install and run

From the repository root, create `.env` from the example only if it does not
already exist, then install dependencies once:

```bash
[ -f .env ] || cp .env.example .env
make setup
```

Add your Groq API key to `.env`, then start both the frontend and backend with:

```bash
make dev
```

The frontend reads `BACKEND_URL` from the root `.env`; the backend reads
`FRONTEND_URL` there for CORS. `make dev` uses both URLs to choose the bind
addresses. Press `Ctrl+C` to stop both servers.

The Vite dev server uses the configured `FRONTEND_URL`, normally
<http://localhost:5173>.

## Other commands

Run these from the `frontend/` directory:

```bash
npm run build  # type-check and create a production build in dist/
npm run lint   # run ESLint
```
