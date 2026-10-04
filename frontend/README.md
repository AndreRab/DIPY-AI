# DIPy-AI Frontend

The frontend is a React and TypeScript application served by Vite. It sends
prompts to the FastAPI backend at `http://localhost:8000/invoke`.

## Requirements

- Node.js and npm
- The backend running locally; see
  [`src/dipy_ai/README.md`](../src/dipy_ai/README.md#start-the-fastapi-backend)

## Install and run

From the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open the URL printed by Vite, normally <http://localhost:5173>. Keep the
backend running in a separate terminal. The backend's CORS configuration allows
the local Vite origin.

Press `Ctrl+C` in the frontend terminal to stop the development server.

## Other commands

Run these from the `frontend/` directory:

```bash
npm run build  # type-check and create a production build in dist/
npm run lint   # run ESLint
```
