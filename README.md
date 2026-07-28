# TNDC Jewelry House

Family jewelry e-commerce — diploma thesis and portfolio project.

## Stack (planned)

TypeScript · React · Next.js · Tailwind · Node.js · Supabase · Docker · Git

Phase 1 UI currently uses **Vite + React + TypeScript** with CSS tokens (Tailwind optional later).

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
