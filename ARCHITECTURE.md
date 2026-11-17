# Architecture

How Second Brain is built, as seen from the code. For setup see the [README](README.md), for details of the background processing see [worker/](worker/README.md), for AWS see [infra/](infra/README.md).

## Layers

Each feature (`user`, `document`, `chunk`, `chat`) in `api/modules/` has the same three layers. Every layer only talks to the one below it.

```mermaid
flowchart TB
    subgraph HTTP["HTTP layer (api/)"]
        MW["Middleware<br/>CORS, rate limit, metrics"]
        RT["Router<br/>parameters, status codes, auth cookie"]
    end
    subgraph LOGIC["Logic layer"]
        SV["Service<br/>rules, orchestration"]
    end
    subgraph DATA["Data layer"]
        RP["Repository<br/>the only place with database queries"]
        CL["Clients (api/clients/)<br/>Qdrant, Redis, storage, LLM"]
    end
    SH["shared/<br/>models, settings, exceptions"]
    WK["worker/<br/>Celery tasks"]

    MW --> RT --> SV
    SV --> RP
    SV --> CL
    SV -->|"send_task"| WK
    RP --> PG[("PostgreSQL")]
    CL --> QD[("Qdrant")]
    CL --> RD[("Redis")]
    CL --> S3[("S3 / MinIO")]
    CL --> LLM["Ollama / OpenAI"]
    RP -.-> SH
    WK -.-> SH
    SV -.->|"raises exceptions"| EH["exception_handlers.py<br/>turns them into JSON errors"]
```

`shared/` is used by the API and the worker and imports nothing from either of them.

## One request, start to end

```mermaid
flowchart LR
    C["Client"] --> M["Middleware<br/>CORS + rate limit<br/>(Redis counter)"]
    M -->|"over 100/min"| E429["429"]
    M --> R["Router"]
    R --> A{"access_token<br/>cookie valid?"}
    A -->|no| E401["401"]
    A -->|"yes: user_id"| V{"Body valid?<br/>(Pydantic)"}
    V -->|no| E422["422"]
    V -->|yes| S["Service"]
    S -->|"InputError, NotFound, ..."| H["Exception handler<br/>400, 404, 409, 500"]
    S --> D["Repository / clients"]
    D --> S
    S --> RES["Response"]
```

The `user_id` from the cookie is passed to every service call, so each query is limited to the signed-in user.

## Where the data lives

| Data | Stored in | Why there |
|---|---|---|
| users, documents, chunk text | PostgreSQL | relational data, migrations with Alembic |
| embeddings (dense and sparse) | Qdrant | similarity search, which Postgres cannot do well |
| the PDF files | S3 / MinIO | large binary files |
| processing status, chat cache, rate-limit counters, Celery messages | Redis | short-lived and fast, expires on its own |

## Main design decisions

- **Slow work leaves the request.** An upload only validates and queues a task. Two Celery workers read the PDF and create the embeddings, so the API stays fast.
- **Two worker types.** The embed worker holds the large embedding model, the PDF worker is light. They scale separately.
- **Hybrid search.** Dense vectors capture meaning, sparse vectors catch exact words. Qdrant merges both rankings (RRF).
- **One interface for the language models.** The service code does not care whether Ollama (development) or OpenAI answers.
- **Cookies instead of tokens in the body.** `HttpOnly` cookies keep the tokens out of reach of JavaScript.
