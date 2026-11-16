# AGENTS.md

Development rules for Second Brain (Python, FastAPI) on the `main` branch.
Every contributor, human or AI agent, should read this before working on the repository.
Setup and commands are in [README.md](README.md), the contribution flow is in [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository

- Work on a branch (`dev/<topic>` or `fix/<topic>`), never directly on `main`. Pull requests go to `main`.
- Never commit secrets: `.env`, `*.tfvars`, Terraform state and credential files are in `.gitignore` and stay out of Git.
- Do not run `terraform apply`, the **CD** workflow or the **Migrate** workflow.
- Do not commit one-off scripts, logs, generated reports or local caches (`venv/`, `.coverage`, `.pytest_cache/`, `.ruff_cache/`).

## Structure

| Folder | Owns |
|---|---|
| `api/` | the FastAPI app: routers, services, repositories, clients, middleware |
| `worker/` | the Celery app and the tasks `read_pdf` and `embed_document` |
| `shared/` | settings, database setup, SQLAlchemy models, shared exceptions |
| `alembic/` | database migrations |
| `tests/` | integration and end-to-end tests (unit tests live next to the code) |
| `frontend/` | the React app, a separate project that consumes the API |
| `infra/` | Terraform for AWS |

- Every feature is a module in `api/modules/<feature>/` built from the same files: `router.py`, `service.py`, `repository.py`, `schemas.py`, `dependencies.py`, `exceptions.py` and `tests/`. A module only has the files it needs (`chat` has no repository, `chunk` has no router).
- **Router** handles HTTP only (parameters, status codes, response models). **Service** holds the logic. **Repository** is the only place that talks to the database. No logic in routers, no SQL in services.
- Dependencies are wired in `dependencies.py` with FastAPI's `Depends`. Clients for Qdrant, Redis, storage and the LLMs are singletons (`@lru_cache`) in `api/clients/`.
- Models and settings used by both API and worker belong in `shared/`. `worker/` never imports from `api/`. The only link in the other direction is `api` importing `worker.celery_app` to send tasks, keep it that way.
- Name modules for what they own. No `utils` or `common` dumping grounds for new code.

## Style

- Follow the surrounding code. Type hints on function signatures, Pydantic schemas for every request and response body.
- The API is **async** (`AsyncSession`, `await`). The worker is **sync** (`SyncSessionLocal`).
- New configuration goes into `shared/config.py` with a default if possible and they should be added to the Environment Variables table in the README.
- Raise domain exceptions (`NotFoundException`, `InputError`, `DocumentNotFoundException`, ...) from services and add or reuse a handler in `api/exception_handlers.py`. Do not return error dicts from services.
- No `print` for diagnostics in new code, use `logging`.

## Tests and checks

- A bug fix needs a regression test that fails without the fix.
- Put unit tests in the module's `tests/` folder and mock all external services (database, Redis, Qdrant, LLMs, storage). Repository tests mock the session or use in-memory SQLite.
- Do not add tests for static values. One focused test per behaviour change.
- Tests must not need network access or a running stack, except `tests/e2e/`, which is not part of CI.
- Before every pull request, run what CI runs:

```bash
ruff check api/ shared/ worker/ infra/
pytest -v --ignore=tests/e2e
```

CI (`.github/workflows/ci-backend.yml`) runs lint, tests and `pip-audit`. All three must pass.

## Database changes

- Change the model in `shared/modules/<feature>/model.py`, then create a migration with `alembic revision --autogenerate`. Read the generated file before you commit it.
- Never edit a migration that is already on `main`. Add a new one.
- Migrations on the deployed database are applied by the **Migrate** workflow, not locally.

## Surface contract (do not change without agreement)

The frontend and the documentation depend on these, so changing them is a breaking change:

- Endpoint paths and methods listed in [api/README.md](api/README.md), including `/document/` and `/chat/`.
- Auth through the `access_token` and `refresh_token` cookies, not through a token in the response body.
- Chat response format: server-sent events with answer parts, then one JSON array of sources, then `data: [DONE]`.
- Document status values: `reading_pdf`, `chunking`, `embedding`, `completed`, `failed`.
- Celery task names (`read_pdf`, `embed_document`) and queue names (`pdf_read`, `embed`). The API, the workers and `docker-compose.yaml` must agree on them.
- The Qdrant collection `second_brain` and its dense and sparse vector configuration.

If you change one of these, update the code, the tests, `api/README.md` and the frontend in the same pull request.

## Reliability

- Background work must be safe to retry. Tasks use `acks_late`, `autoretry_for` and exponential backoff, so a task can run more than once. Writes in tasks must be idempotent.
- Every task reports progress through `set_status` in Redis and ends in `completed` or `failed`. Never leave a document stuck in a processing state.
- Delete operations use Postgres, Qdrant and storage together. Commit the database change only after the other two succeeded, as `delete_document` does.
- Keep the user's data separated: every query for documents, chunks and vectors is filtered by `user_id`.
- No stubs, no `TODO` code paths in merged work, no silently ignored errors.
