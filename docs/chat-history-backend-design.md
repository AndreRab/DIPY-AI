# Conversation history: backend design

Status: implementation proposal for `origin/chat-history`.

## Goal and scope

The backend must persist conversations, expose their messages so the UI can reopen
them, and use those messages as model context when a conversation continues.
`conversation_id` identifies the same conversation in all three scenarios.

The database is the single persistent source of history. The agent has no shared
mutable conversation history between requests. Restarting the server preserves
context, and switching conversations never carries messages into another chat.

Frontend integration belongs to a separate PR. This change must complete the
backend contract regardless of whether the current UI sends conversation IDs.

Concrete functions and classes are sufficient for this project. Repository
interfaces, a Unit of Work, a separate domain layer, and abstractions around a
single storage implementation are unnecessary.

## Expected structure

```text
src/dipy_ai/
├── main.py                       # existing console entry point
├── config.py                     # existing settings plus database location
├── agent/
│   ├── base_agent.py             # agent contract and message types
│   └── workflow_agent.py         # graph with fresh state for each invocation
└── api/
    ├── __init__.py
    ├── app.py                    # FastAPI assembly and resource lifecycle
    ├── infrastructure/
    │   ├── __init__.py
    │   ├── database.py           # Base, engine, sessions, table initialization
    │   └── models.py             # Conversation, Message, Role
    ├── routers/
    │   ├── __init__.py
    │   ├── conversations.py      # HTTP schemas and conversation routes
    │   └── simulation.py         # simulation schemas and routes
    └── services/
        ├── __init__.py
        ├── chat_service.py       # reading and continuing conversations
        └── nist_ams_mode_service.py  # simulation logic
```

There is no separate `schemas.py` yet. Request and response schemas live at the
start of `routers/conversations.py`, followed by routes. Extract them when their number
justifies a separate module. All HTTP handlers live in `routers/`; application logic lives in `services/`.
`app.py` assembles the application and manages resource lifetimes.

## File responsibilities

### `api/app.py`: application assembly

- Creates `FastAPI`, configures CORS, and includes the conversation and simulation routers.
- Initializes the database, simulator, tools, agent, and `ChatService` in `lifespan`.
- Holds application resources, for example in `app.state`.
- Closes simulation resources and disposes of the engine on shutdown.
- Contains no HTTP handlers; simulation endpoints live in `routers/simulation.py`.

The `/invoke` handler moves into the router. Table creation and external resource
initialization must not happen as side effects of importing modules.

### `main.py`: console entry point

This file currently runs the interactive CLI. The HTTP server starts through
`uvicorn dipy_ai.api.app:app`. These are separate entry points. HTTP routes do not
need to move into `main.py`; `scripts/dev.py` continues to start the existing app.

Adapt the CLI when the agent contract changes: it explicitly maintains its console
session history and passes it to the agent. Connecting the CLI to the database is
optional for this task. Put executable code in `main()` behind an
`if __name__ == "__main__"` guard.

### `api/infrastructure/database.py`: connection and sessions

- Declares the SQLAlchemy `Base`.
- Provides engine creation using `DATABASE_URL`.
- Provides `get_db`: one session per HTTP request, closed afterward.
- Provides explicit table initialization, called from `lifespan`.

Register ORM models before calling `Base.metadata.create_all()`. Import `models`
inside the initialization function to register them without a module-level import
cycle.

For this version, `create_all()` is sufficient. It creates missing tables but does
not migrate existing ones. Schema changes to a database that must retain its data
require an explicit migration; repeatedly calling `create_all()` does not solve
that problem.

The SQLite path must be stable and independent of the working directory. For
example, compute an absolute default path to `var/dipy_ai.db` relative to the
project root in configuration. Create the directory at startup and ignore `var/`
in Git. Preserve the existing local database before moving it; do not delete it
automatically. Remove `dipy_ai.db` from Git tracking.

### `api/infrastructure/models.py`: database records

Contains `Role`, `Conversation`, and `Message`. Separate packages for individual
classes are unnecessary. Use SQLAlchemy's `Mapped` / `mapped_column` style
consistently.

| Model | Fields |
| --- | --- |
| `Conversation` | `id`, `title`, `created_at`, `updated_at`, `messages` relationship |
| `Message` | `id`, `conversation_id`, `role`, `content`, `created_at` |

- Roles are `user` and `assistant`; the server assigns them.
- Messages are immutable, so `Message.updated_at` is unnecessary for now.
- Explicitly update `Conversation.updated_at` when saving a successful exchange.
- Timestamps represent UTC and are returned as ISO 8601 with a UTC offset.
  Explicitly restore UTC when reading SQLite timestamps: `DateTime(timezone=True)`
  alone does not guarantee preservation of timezone information.
- System instructions and intermediate tool results are not user conversation
  messages and are not stored in this table.

### `api/routers/conversations.py`: HTTP contract

Place these Pydantic schemas at the beginning of the file:

- `InvokeRequest`: `prompt`, optional `conversation_id`.
- `InvokeResponse`: `conversation_id`, `response`.
- `ConversationResponse`: `id`, `title`, `created_at`, `updated_at`.
- `MessageResponse`: `id`, `conversation_id`, `role`, `content`, `created_at`.

Trim the prompt and reject empty values. IDs must be positive. Attach response
schemas using `response_model` and use `from_attributes=True` when reading ORM
objects. This validates data and documents the API.

Routes below the schemas are thin handlers: receive input and dependencies, call
the service, and return its result. Translate service exceptions into HTTP errors
here. Handlers do not call the agent or issue SQLAlchemy queries directly.

### `api/services/chat_service.py`: conversation operations

Use one concrete `ChatService`. It can receive a session factory or use sessions
passed by routes, but choose one approach rather than supporting both. For this
project, passing the session from `get_db` into service methods is sufficient.
The service receives the agent during application initialization.

Methods:

- `list_conversations(db)`: order by `updated_at DESC, id DESC`.
- `get_messages(db, conversation_id)`: check that the conversation exists and
  return messages ordered by `id ASC`.
- `invoke(db, prompt, conversation_id)`: load context, generate, and persist.

The service does not depend on FastAPI or raise `HTTPException`. A few concrete
exceptions are sufficient: conversation not found, conversation busy, and
generation failed. A project-wide exception hierarchy is unnecessary.

### `agent/workflow_agent.py`: generation with explicit context

Instead of accumulating `self._current_state`, accept history explicitly. Example
contract, with the exact history type declared in the agent module:

```python
def handle_message(
    self,
    message: UserMessage,
    history: Sequence[ChatMessage],
) -> str:
    ...
```

`history` contains previous successful exchanges only; the new question is passed
separately. Build a local `WorkflowState` containing system instructions, previous
messages, the new question, and empty tool results. The graph returns a response,
but the agent neither retains history nor mutates the caller's list. The service
owns persistence.

The graph and model client can be reused. Check that other agent fields and tools
do not introduce shared mutable invocation state. Update the `BaseAgent` contract
and every affected implementation and caller.

Final generation receives the entire selected conversation history. Tool
selection must also consider earlier messages: a question such as “what about it
now?” cannot reliably be interpreted from its last line alone. For tools requiring
a standalone search query, resolve references using history instead of sending
an unresolved “it” into search.

Initially, pass the full stored conversation. Automatic history reduction is a
separate improvement. Exceeding the context window must produce an explicit error
rather than silently dropping messages.

## HTTP API

| Method and path | Behavior |
| --- | --- |
| `GET /conversations` | List conversations, most recently active first |
| `GET /conversations/{id}/messages` | Ordered messages; `404` if the conversation does not exist |
| `POST /invoke` | Start a conversation or continue an existing one |

First request:

```json
{"prompt": "What is happening with the process right now?"}
```

Response:

```json
{"conversation_id": 42, "response": "..."}
```

Continue after reopening this conversation:

```json
{"prompt": "Why did that happen?", "conversation_id": 42}
```

The response has the same format and ID. All previously saved messages from
conversation 42 enter the model context. There is no separate endpoint to activate
a conversation: the server has no global current chat, and clients send the ID
with each request.

Separate `POST /conversations` and `POST /conversations/{id}/messages` endpoints
are unnecessary for this workflow. A conversation is created on its first
successful exchange, and messages are written through generation only. History
import can be added later.

## `/invoke` sequence and errors

1. Validate input.
2. For an existing conversation, acquire its ID lock; return `409` if busy.
3. Check that the conversation exists; return `404` for an unknown ID.
4. Read messages into plain Python values and end the read transaction.
5. Call the agent with history and the new question, without an open database
   transaction.
6. In a short transaction, create the conversation if needed, save both messages,
   and update `updated_at`. Use `flush()` to obtain a new conversation ID, then
   commit the entire exchange once.
7. Return the ID and response. Release the lock in `finally` on every outcome.

Use the first 80 characters of the trimmed initial question as the conversation
title. An additional LLM call for the title is unnecessary.

Return `502` for generation failures and `504` for provider timeouts. Neither
message is saved on generation failure, and a failed first request does not leave
an empty conversation. A persistence failure rolls back the entire exchange and
returns a server error. Do not expose internal provider details in public errors.

This persistence policy means failed attempts do not appear when reopening a
conversation. The frontend shows an error on its unsaved message and offers retry.
Idempotency after a lost HTTP response following commit is not implemented yet:
retrying can create another exchange. Do not enable automatic POST retries on the
client; add request IDs later if needed.

## Concurrent requests

For the current single-process deployment, an ID-based lock registry in
`ChatService` is sufficient. A lock covers reading, generation, and writing.
Remove registry entries safely so the registry does not grow indefinitely. Two
requests for the same conversation must not generate from the same stale history.

Different conversations may run concurrently if the agent has no shared mutable
state. In-memory locks only work with one worker. Implement coordination across
processes before enabling multiple workers; SQLite alone does not protect the
“read → call LLM → write” sequence.

## Migration from the current branch

1. Merge `api/db/base.py` and `api/db/core.py` into `infrastructure/database.py`.
2. Merge `api/model/*` and `api/enum/role.py` into `infrastructure/models.py`.
3. Move schemas from `api/schemas/conversation.py` and routes from
   `api/router/conversations.py` into `routers/conversations.py`.
4. Move `/invoke` from `app.py` into the router and its workflow into `services/chat_service.py`.
5. Make agent state local to each invocation and adapt the CLI.
6. Initialize resources through `lifespan` and update imports.
7. Remove unnecessary empty packages and stop tracking the working database,
   preserving local data.

## Acceptance criteria

- The first successful request creates exactly one conversation and two messages,
  and returns the conversation ID.
- Continuation saves to the same conversation and passes previous messages to
  the agent.
- Reopening a conversation returns saved messages in a stable order.
- Conversations A and B never receive each other's history.
- Recreating the agent/application with the same database preserves context.
- Unknown IDs return `404`; empty prompts return `422`.
- Model failures leave neither half an exchange nor an empty new conversation.
- A second concurrent request for the same conversation receives `409`; locks
  are released on failure too. Different conversations do not unnecessarily
  block each other.
- `updated_at` changes after successful continuation, and the list order reflects it.
- Context informs both final generation and the interpretation of follow-up
  questions during tool selection.
- The CLI works with the updated agent contract.

Use temporary SQLite databases and a fake agent for the main checks. Real paid
LLM calls are unnecessary to verify persistence, isolation, and errors. Separately
verify message assembly inside the agent using a fake model client.

## Implementation and verification notes

Conversation locks are shared by request-scoped services within one process.
Run the backend with one worker; multiple workers require coordination across
processes before they can safely continue the same conversation concurrently.

New timestamps are stored and returned in UTC. Legacy SQLite timestamps have no
recorded timezone and are interpreted as UTC for compatibility; their original
local timezone cannot be recovered automatically. If old dates matter, migrate
them explicitly using the timezone of the server that originally wrote them.

Tool selection returns both the bundle and a standalone search query resolved
from conversation history, within the same model call.

Run the regression checks without external LLM calls:

```bash
uv run python -m unittest discover -s tests -v
```

### Router and service organization

`routers/simulation.py` owns simulation request schemas, HTTP dependencies, and
HTTP error mapping. It obtains the simulation service from `app.state` and does
not create a simulator. `services/nist_ams_mode_service.py` retains the existing
simulation behavior. The console entry point imports that service from its new
location.

`app.py` initializes the simulator, tools, and agent in `lifespan`, publishes them
through `app.state`, includes both routers, and closes resources at shutdown.
The public endpoint paths remain unchanged.
