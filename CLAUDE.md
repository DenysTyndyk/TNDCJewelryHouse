## Project Overview
TNDC Jewelry House — online jewelry store with UX personalization algorithms (engineering thesis, see `docs/plans/roadmap.uk.md` / `docs/plans/roadmap.pl.md`).
- **Frontend**: React + TypeScript (Vite), in `web/`
- **Backend**: Python, FastAPI, SQLAlchemy 2.0, Alembic, in `api/`
- **Database**: PostgreSQL 16 + pgvector (Docker Compose). The browser never talks to the database; FastAPI is the only DB client.
- **Environment**: Docker, Docker Compose
- **Market**: single market — Ukraine (D3). Prices only in UAH from `variant_prices`, no exchange-rate conversion (D6); there are no `markets` / `exchange_rates` tables.
- **Languages**: UI and catalog content in `uk` (primary), `pl`, `en` (D8) via `product_translations` / `category_translations`. Language is UI/content only, not a market.
- **Key Integrations**: payment sandboxes LiqPay / Monobank, Nova Poshta delivery, multilingual-e5-small embeddings (384 dims)
- **Decisions**: `docs/plans/roadmap.uk.md` (D1–D8, canonical), `docs/architecture.md`, `docs/schema.dbml` (schema source of truth)

## Architecture & Design Guidelines
- **API Style**: RESTful endpoints returning consistent JSON structures.
- **Authentication**: Own implementation in FastAPI (not Supabase Auth, D1): argon2id password hashing, access JWT (15 min) in an Authorization header, rotating refresh token in an httpOnly cookie, account lockout.
- **API Documentation**: Interactive OpenAPI / Swagger (`/docs`) must stay updated with every new endpoint.
- **Database Migrations**: Every schema update must include appropriate migration scripts.
- **Performance Constraint**: Database queries and standard API reads must complete within 500ms.
- **Manual Execution Only (CRITICAL)**: Do NOT execute bash commands, scripts, migrations, or database queries automatically. Provide all terminal commands and SQL queries as explicit, copy-pasteable instructions — the user will run them manually.
- **Database Access Control**: Claude has strictly no direct access to the database. All queries, inspection, schema updates, and seedings must be provided to the user to execute manually.
- **Documentation**: must be on Polish language 
## Non-Negotiable Rules & Standards

### 1. Code Comments (CRITICAL)
- **Language**: All inline comments, docstrings, and module descriptions **MUST be written in English** (as specified in NF-04).
- **Code identifiers**: Variable, function, and class names must remain in standard English (e.g., `calculate_balance()`, `UserWallet`).


### 3. Security
- Never store raw passwords. Always hash credentials with argon2id (`argon2-cffi`, D1).
- Never store card data (PCI-DSS): payments go through provider redirect/SDK only, sandbox only.
- Behaviour tracking requires user consent first (RODO).

## File Access & Environment Restrictions
- **Sensitive Files (STRICT)**: Never read, display, or log `.env`, `.env.local`, or any files containing private keys, credentials, or production tokens. Instead, only reference or update template files like `.env.example`.
- **Ignored Directories**: Do NOT read, search, or index heavy generated or dependency directories (e.g., `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `build/`, `dist/`, `.git/`, `.idea/`).
- **Heavy & Generated Files**: Do NOT inspect large lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`), binary assets, or database dump files (`.sql`, `.dump`). Focus exclusively on relevant source code.

# Navigation & Project Context Rules

Code Graph First (MUST): Before the first exploratory Glob/Grep/Read in a new task (searching for a module, "where is X defined", analyzing dependencies) — first run graphify explain "<module or file>" (graph: graphify-out/graph.json) to inspect its relationships, and only then open specific files using the discovered paths.
Not applicable when: The file path is already known directly (specified by the user or identified in a previous step of the task) — in this case, read it without querying the graph.
Fallback: If graphify-out/graph.json does not exist or is clearly outdated — state this directly (do not stay silent) and ask whether to run graphify update . to build/update the graph, rather than silently scanning the directory tree.
Index Refresh: If the task added new files/modules — upon completion, remind the user to run graphify update . (or run it yourself if permitted by project rules — see "Manual Execution Only").

## Development & Execution Commands

### Docker (Preferred Runtime)
```bash
# Start the database (repo root)
docker compose up -d postgres

# Stop environment
docker compose down

# Backend (run from api/)
pip install -r requirements.txt
alembic upgrade head
alembic downgrade -1
pytest

# Frontend (run from web/)
npm install
npm run dev
npm run lint
```
Migration details: `api/README.md`.