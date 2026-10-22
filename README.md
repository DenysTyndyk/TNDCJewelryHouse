# TNDC Jewelry House

Family jewelry e-commerce — diploma thesis and portfolio project.

## Stack

TypeScript · React (Vite) · FastAPI · PostgreSQL 16 + pgvector · Docker · Git

Two markets: Ukraine (primary — UAH, `uk`) and Poland (PLN, `pl`). Supabase Auth is not used; authentication will live in the FastAPI API. Decisions: [`docs/architecture.md`](./docs/architecture.md).

The storefront in `web/` is **Vite + React + TypeScript** with CSS tokens. Auth on the client is a stub until that API exists.

## Web UI (Phase 1)

```bash
cd web
npm install
npm run dev
```

Details and Phase 1 checklist: [`web/README.md`](./web/README.md).

## Repository map

| Path | Purpose |
|------|---------|
| [`web/`](./web/) | React storefront UI (Phase 1) |
| [`design/`](./design/) | Brand tokens + static HTML mocks |
| [`docs/`](./docs/) | Architecture notes + workshop |
| [`.cursor/rules/learning-mode.mdc`](./.cursor/rules/learning-mode.mdc) | AI teaching mode (hints first) |
| [`plan.md`](./plan.md) | Phase 1 task breakdown |

## Preview the static design

```bash
npx --yes serve design
```

Open `/mocks/home.html` (also `category`, `cart`, `about`, `contact`).
