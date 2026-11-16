# Shared

Code that both the **API** and the **worker** need. It exists so that the two processes use exactly the same database models, settings and error types instead of keeping copies.

`shared/` is the lowest layer. It does not import from `api/` or `worker/`.

## What is in here

```
shared/
├── config.py                 settings, read from environment variables and .env
├── database.py               async and sync SQLAlchemy engines, session factories, Base
├── core/
│   └── exceptions.py         exceptions used by both sides
└── modules/                  SQLAlchemy models, one folder per table
    ├── user/model.py         users
    ├── document/             documents (model.py, exceptions.py)
    └── chunk/model.py        chunks
```

### `config.py`

One `Settings` class that everyone imports.

- Required: `ENVIRONMENT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_PORT`, `DB_NAME`, `DB_HOST`. The app does not start without them.
- Optional with defaults: pool settings, `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`, `COOKIE_SECURE`, `FRONTEND_URL`, and the JWT settings.
- `DATABASE_URL` and `DATABASE_ASYNC_URL` are built from the parts.

The full list with descriptions is in the root README under *Environment Variables*. A new setting goes here first.

### `database.py`

Two ways to talk to the same PostgreSQL database:

| | Used by | Driver | Session |
|---|---|---|---|
| Async | API | `asyncpg` | `AsyncSessionLocal`, handed to routes through `get_db()` |
| Sync | worker | `psycopg2` | `SyncSessionLocal` |

It also defines `Base`, the parent class of every model.

### `modules/`

The SQLAlchemy models. Alembic reads `Base.metadata` from here, so **a model must be imported in `alembic/env.py`** to be seen by `alembic revision --autogenerate`.

| Table | Model | Main columns |
|---|---|---|
| `users` | `User` | email (unique), full name, hashed password, hashed refresh token, active and superuser flags, last login |
| `documents` | `Document` | user, title, file name, storage path, size, type, `content_hash` (unique), `status`, error message, chunk count |
| `chunks` | `Chunk` | document, user, chunk index, text, token count |

### `core/exceptions.py`

Plain exception classes without any web code: `DatabaseException`, `InputError`, `NotFoundException`, `StorageException`,
`QdrantException`, `OllamaException`, `OpenaiException`. 
