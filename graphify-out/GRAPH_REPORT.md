# Graph Report - TNDCJewelryHouse  (2026-11-12)

## Corpus Check
- 102 files · ~48,042 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .avif 4, .css 3)

## Summary
- 849 nodes · 2296 edges · 32 communities (24 shown, 8 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 200 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f83c8099`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- seed.py
- App.tsx
- Kamienie milowe
- package.json
- Architecture Workshop (Student-Owned)
- user_repository.py
- compilerOptions
- postgres
- catalog_service.py
- compilerOptions
- main.py
- CLAUDE.md
- API — baza danych i migracje (Milestone 1)
- .oxlintrc.json
- Milestones
- M4 — задачі (кошик, замовлення, платежі)
- tsconfig.json
- routers/auth.py
- test_auth_flows.py
- admin_catalog_service.py
- Diploma roadmap — TNDC Jewelry House
- test_admin_catalog.py
- package.json
- env.py
- Diploma roadmap — TNDC Jewelry House

## God Nodes (most connected - your core abstractions)
1. `useLanguage()` - 38 edges
2. `Base` - 34 edges
3. `Currency` - 29 edges
4. `import_product()` - 29 edges
5. `Category` - 25 edges
6. `Product` - 25 edges
7. `ProductVariant` - 24 edges
8. `ProductImage` - 20 edges
9. `User` - 19 edges
10. `compilerOptions` - 19 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `6. Платежі (sandbox)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/m4-tasks.uk.md → api/app/models/enums.py
- `M4 — Koszyk, zamówienia, płatności (3–4 tygodnie)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M4 — Кошик, замовлення, платежі (3–4 тижні)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py

## Import Cycles
- None detected.

## Communities (32 total, 8 thin omitted)

### Community 0 - "seed.py"
Cohesion: 0.06
Nodes (74): downgrade(), upgrade(), Base, get_session(), Category, CategoryTranslation, Gemstone, PriceHistory (+66 more)

### Community 1 - "App.tsx"
Cohesion: 0.05
Nodes (84): M3 — Katalog + i18n (2–3 tygodnie), M3 — Каталог + i18n (2–3 тижні), Реєстр ризиків (топ), react, react-router-dom, extractErrorMessage(), forgotPassword(), login() (+76 more)

### Community 2 - "Kamienie milowe"
Cohesion: 0.18
Nodes (11): Kamienie milowe, M0 — Stabilizacja (1–2 dni), M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle), M1 — Schemat bazy i migracje (1–2 tygodnie), M2 — FastAPI i własne uwierzytelnianie (2–3 tygodnie), M4 — Koszyk, zamówienia, płatności (3–4 tygodnie), M5 — Telemetria UX + RODO (1–2 tygodnie), M6 — Algorytmy klasyczne (2–3 tygodnie) (+3 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, vite (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.04
Nodes (42): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+34 more)

### Community 5 - "user_repository.py"
Cohesion: 0.07
Nodes (68): create_access_token(), decode_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), _pepper(), _verify(), verify_legacy_password() (+60 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "postgres"
Cohesion: 0.04
Nodes (46): build, container_name, depends_on, environment, ports, restart, volumes, context (+38 more)

### Community 8 - "catalog_service.py"
Cohesion: 0.14
Nodes (22): get_product(), list_categories(), list_products(), CategoryNode, GemstoneOut, ImageOut, ProductDetail, ProductFilter (+14 more)

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "main.py"
Cohesion: 0.06
Nodes (20): Settings, get_db(), conflict_handler(), health(), invalid_image_handler(), log_event(), not_found_handler(), ready() (+12 more)

### Community 11 - "CLAUDE.md"
Cohesion: 0.20
Nodes (9): 1. Code Comments (CRITICAL), 3. Security, Architecture & Design Guidelines, Development & Execution Commands, Docker (Preferred Runtime), File Access & Environment Restrictions, Navigation & Project Context Rules, Non-Negotiable Rules & Standards (+1 more)

### Community 12 - "API — baza danych i migracje (Milestone 1)"
Cohesion: 0.33
Nodes (5): API — baza danych i migracje (Milestone 1), Decyzje odzwierciedlone w schemacie, Kolejność migracji, Lista kontrolna dla wygenerowanej migracji `0002`, Uruchomienie

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "Milestones"
Cohesion: 0.18
Nodes (11): M0 — Стабілізація (1–2 дні), M10 — Впровадження і документація (3–4 тижні, паралельно), M1 — Схема БД і міграції (1–2 тижні), M2 — FastAPI і власна автентифікація (2–3 тижні), M4 — Кошик, замовлення, платежі (3–4 тижні), M5 — Телеметрія UX + RODO (1–2 тижні), M6 — Класичні алгоритми (2–3 тижні), M7 — Семантичний пошук e5 + pgvector (2–3 тижні, паралельно з M4/M6) (+3 more)

### Community 15 - "M4 — задачі (кошик, замовлення, платежі)"
Cohesion: 0.22
Nodes (9): 1. Міграція, 2. Кошик — бекенд, 3. Кошик — фронт, 4. Замовлення — бекенд, 5. Checkout — фронт (без оплати), 6. Платежі (sandbox), 7. Закриття M4, M4 — задачі (кошик, замовлення, платежі) (+1 more)

### Community 20 - "routers/auth.py"
Cohesion: 0.21
Nodes (19): forgot_password(), login(), logout(), me(), refresh(), register(), reset_password(), _set_refresh_cookie() (+11 more)

### Community 21 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 22 - "admin_catalog_service.py"
Cohesion: 0.06
Nodes (65): add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant(), remove_gemstone() (+57 more)

### Community 23 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.22
Nodes (9): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kolejność i zależności, Kontekst, Pierwsze kroki, Przyjęte decyzje, Rejestr ryzyk (najważniejsze), Tabele opcjonalne (tylko jeśli zostanie czas) (+1 more)

### Community 25 - "test_admin_catalog.py"
Cohesion: 0.29
Nodes (9): require_role(), Role, _auth(), _png(), test_admin_forbidden_for_regular_user(), test_manager_builds_product_end_to_end(), test_process_image_makes_three_webp_sizes_without_exif(), test_process_image_never_upscales() (+1 more)

### Community 26 - "package.json"
Cohesion: 0.67
Nodes (3): dependencies, typescript@^7.0.2, typescript

### Community 27 - "env.py"
Cohesion: 0.47
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 28 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.25
Nodes (8): Context, Diploma roadmap — TNDC Jewelry House, Verification, Архітектура (скорочено), Опційні таблиці (лише якщо лишиться час), Перші кроки після затвердження, Порядок і залежності, Прийняті рішення

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `M4 — задачі (кошик, замовлення, платежі)` connect `M4 — задачі (кошик, замовлення, платежі)` to `user_repository.py`, `roadmap.uk.md`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `useLanguage()` (e.g. with `M3 — Katalog + i18n (2–3 tygodnie)` and `M3 — Каталог + i18n (2–3 тижні)`) actually correct?**
  _`useLanguage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `seed.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06088154269972452 - nodes in this community are weakly interconnected._
- **Why does `3. Кошик — фронт` connect `M4 — задачі (кошик, замовлення, платежі)` to `App.tsx`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `App.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.050793650793650794 - nodes in this community are weakly interconnected._
- **Why does `0. Підготовка` connect `user_repository.py` to `seed.py`, `M4 — задачі (кошик, замовлення, платежі)`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._