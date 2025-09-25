# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI app (entry: `app/main.py`).
  - `app/api/endpoints/`: Route handlers (e.g., `auth.py`).
  - `app/models/`: SQLAlchemy models (e.g., `user.py`).
  - `app/crud/`: DB access helpers.
  - `app/schemas/`: Pydantic models for requests/responses.
  - `app/services/`: Domain services (auth, mail).
  - `app/config/`: DB/Redis/settings configuration.
- `sql/schema.sql`: MySQL DDL for core tables.
- `README.md`, `README.en.md`: Product and setup docs.
- `.kiro/`: Internal specs and plans.

## Build, Test, and Development Commands
- Create env: `python -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r backend/requirements.txt`
- Run API (dev): `cd backend && uvicorn app.main:app --reload`
- Apply DB schema (MySQL): `mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB < sql/schema.sql`
- Environment: create `backend/.env` with at least `MYSQL_*`, `REDIS_*`, `JWT_SECRET_KEY`, `MAIL_*` (see `app/config/settings.py`).

## Coding Style & Naming Conventions
- Python, PEP 8, 4‑space indentation, type hints required.
- Modules/variables/functions: `snake_case`; classes: `PascalCase`.
- Endpoints live under `app/api/endpoints/` and return unified JSON via `app/utils/response.py`.
- Keep business logic in `app/services/`; DB access in `app/crud/`.
- Optional tooling (recommended): `black backend`, `ruff check backend`.

## Testing Guidelines
- Framework: `pytest` (add as dev dependency if missing).
- Location: `backend/tests/` mirroring package layout; files as `test_*.py`.
- Use FastAPI `TestClient`/HTTPX for API tests; seed data via factories.
- Aim for ≥80% coverage on changed lines; include negative tests for auth flows.
- Run: `pytest -q` from repo root or `backend/`.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- One logical change per PR; keep diffs focused.
- PRs must include: clear description, linked issue, testing notes, and API examples (sample `curl` or request/response snippets). Update `sql/` or env docs if relevant.
- Ensure local run works (`uvicorn`), DB schema applied, and CI/tests (if present) pass.

## Security & Configuration Tips
- Never commit secrets; keep them in `backend/.env`.
- Use a strong `JWT_SECRET_KEY`; rotate if leaked.
- Prefer MySQL via `app/config/mysql_config.py` in real environments; `app/config/database.py` is for local/dev.

## 重要提示
在每次和用户交互，完成用户的编程任务之前，你都需要先给出规划，待用户确认后，再执行具体的操作。
