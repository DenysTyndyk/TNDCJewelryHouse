# TNDC Jewelry House — Web (Phase 1)

React + TypeScript + Vite UI for the jewelry storefront.

Brand styling uses CSS design tokens (`src/styles/tokens.css`) and `site.css` (same look as `design/mocks/`). Tailwind packages may exist in `package.json` but are not required for Phase 1.

## Run

```bash
cd web
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Local development |
| `npm run build` | Production build |
| `npm run preview` | Preview the production build |

## Routes

| Path | Page |
|------|------|
| `/` | Home |
| `/categories` | Categories |
| `/cart` | Cart |
| `/about` | About |
| `/contact` | Contact |

## Phase 1 — done when

- [x] `npm run dev` works from `web/`
- [x] 5 routes match the design IA
- [ ] Mock catalog + category filter (`mockProducts`)
- [ ] Guest cart in `localStorage` + header badge
- [x] No API / Supabase / Docker in this app yet

## Out of scope (later phases)

Auth against the FastAPI API, cart merge to Postgres, Docker, payment.
