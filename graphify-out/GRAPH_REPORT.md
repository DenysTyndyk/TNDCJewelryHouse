# Graph Report - TNDCJewelryHouse  (2026-11-03)

## Corpus Check
- 67 files · ~32,312 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 5, .avif 4, .css 3)

## Summary
- 463 nodes · 894 edges · 21 communities (15 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 49 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37e8638f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Base
- App.tsx
- Kamienie milowe
- package.json
- Architecture Workshop (Student-Owned)
- user_repository.py
- compilerOptions
- postgres
- System Architecture — TNDC Jewelry House
- compilerOptions
- main.py
- CLAUDE.md
- API — baza danych i migracje (Milestone 1)
- .oxlintrc.json
- tsconfig.json
- routers/auth.py

## God Nodes (most connected - your core abstractions)
1. `Base` - 34 edges
2. `compilerOptions` - 19 edges
3. `Currency` - 15 edges
4. `compilerOptions` - 15 edges
5. `User` - 14 edges
6. `App()` - 13 edges
7. `Architecture Workshop (Student-Owned)` - 13 edges
8. `seed_products()` - 12 edges
9. `System Architecture — TNDC Jewelry House` - 12 edges
10. `Kamienie milowe` - 12 edges

## Surprising Connections (you probably didn't know these)
- `M4 — Koszyk, zamówienia, płatności (3–4 tygodnie)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M4 — Кошик, замовлення, платежі (3–4 тижні)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `5.2 Auth & profile (decided — D1)` --references--> `User`  [INFERRED]
  docs/architecture.md → api/app/models/user.py
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `Currency`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `Currency`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py

## Import Cycles
- None detected.

## Communities (21 total, 6 thin omitted)

### Community 0 - "Base"
Cohesion: 0.09
Nodes (48): Base, get_session(), Category, CategoryTranslation, Gemstone, PriceHistory, Product, ProductEmbedding (+40 more)

### Community 1 - "App.tsx"
Cohesion: 0.10
Nodes (26): react, react-router-dom, App(), Footer(), Header(), navLinks, CartLine(), ImageSliderOnHover() (+18 more)

### Community 2 - "Kamienie milowe"
Cohesion: 0.05
Nodes (40): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kamienie milowe, Kolejność i zależności, Kontekst, M0 — Stabilizacja (1–2 dni), M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle), M2 — FastAPI i własne uwierzytelnianie (2–3 tygodnie) (+32 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, typescript (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.07
Nodes (24): A. Context & goals, Architecture Workshop (Student-Owned), B. System context, C. Containers (high-level deployable pieces), D. Responsibility split checklist, E. Data, F. Key flows (sequences), G. Next.js routing map (App Router) (+16 more)

### Community 5 - "user_repository.py"
Cohesion: 0.14
Nodes (25): Settings, create_access_token(), decode_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), verify_password(), RefreshToken (+17 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "postgres"
Cohesion: 0.06
Nodes (35): build, container_name, depends_on, environment, ports, restart, volumes, postgres (+27 more)

### Community 8 - "System Architecture — TNDC Jewelry House"
Cohesion: 0.11
Nodes (18): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+10 more)

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "main.py"
Cohesion: 0.06
Nodes (14): _database_url(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), get_current_user(), get_db(), require_role() (+6 more)

### Community 11 - "CLAUDE.md"
Cohesion: 0.20
Nodes (9): 1. Code Comments (CRITICAL), 3. Security, Architecture & Design Guidelines, Development & Execution Commands, Docker (Preferred Runtime), File Access & Environment Restrictions, Navigation & Project Context Rules, Non-Negotiable Rules & Standards (+1 more)

### Community 12 - "API — baza danych i migracje (Milestone 1)"
Cohesion: 0.33
Nodes (5): API — baza danych i migracje (Milestone 1), Decyzje odzwierciedlone w schemacie, Kolejność migracji, Lista kontrolna dla wygenerowanej migracji `0002`, Uruchomienie

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 20 - "routers/auth.py"
Cohesion: 0.23
Nodes (11): login(), logout(), me(), refresh(), register(), _set_refresh_cookie(), LoginRequest, RegisterRequest (+3 more)

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `user_repository.py` to `Base`, `System Architecture — TNDC Jewelry House`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `Base` be split into smaller, more focused modules?**
  _Cohesion score 0.09292854498333951 - nodes in this community are weakly interconnected._
- **Why does `5.2 Auth & profile (decided — D1)` connect `System Architecture — TNDC Jewelry House` to `user_repository.py`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `Role` and `UserStatus`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `App.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.09764309764309764 - nodes in this community are weakly interconnected._
- **Should `Kamienie milowe` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._