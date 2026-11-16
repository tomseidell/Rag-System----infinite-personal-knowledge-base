# Contributing

Thanks for your interest in Second Brain. Bug reports, ideas and pull requests are welcome. This page explains how to
get a change from your machine into `main`.

## Report a bug or suggest something

Open a [GitHub Issue](https://github.com/tomseidell/fastApi/issues). Check first that nobody has reported the same thing.
For a bug, please include:

- what you did and what you expected
- what happened instead (error message, status code, log output of `docker compose logs api`)
- how you run the project (Docker or local) and your `ENVIRONMENT`

If you found a security problem, do not open a public issue. Contact the maintainer directly instead.

## Make a change

1. **Set up the project** as described in [Start the project](README.md#start-the-project).
2. **Create a branch from `main`**, named by type: `dev/short-description` for features, `fix/short-description` for bug fixes.
3. **Keep the change focused.** One topic per pull request, no unrelated refactoring.
4. **Follow the structure.** A feature lives in `api/modules/<feature>/` and is split into router → service → repository. Routers only handle HTTP, services hold the logic, repositories talk to the database.
5. **Write tests** next to the code in the module's `tests/` folder. Mock external services (database, Redis, Qdrant, LLMs). More in [Testing](README.md#testing).
6. **Add a migration** if you changed a SQLAlchemy model:
   ```bash
   docker compose exec api alembic revision --autogenerate -m "change description"
   docker compose exec api alembic upgrade head
   ```
   See the generated file in `alembic/versions/` before you commit it.
7. **Document it.** New or changed endpoints belong into the [API reference](api/README.md).
