# Graph Report - TNDCJewelryHouse  (2026-11-11)

## Corpus Check
- 97 files · ~46,719 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .avif 4, .css 3)

## Summary
- 822 nodes · 2142 edges · 28 communities (21 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 180 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b4a402b5`
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
- resolve_locale
- compilerOptions
- main.py
- CLAUDE.md
- API — baza danych i migracje (Milestone 1)
- .oxlintrc.json
- tsconfig.json
- routers/auth.py
- test_auth_flows.py
- admin_catalog_service.py
- Moduł katalogu (M3)
- test_admin_catalog.py
- package.json
- env.py

## God Nodes (most connected - your core abstractions)
1. `useLanguage()` - 38 edges
2. `Base` - 34 edges
3. `Currency` - 29 edges
4. `Category` - 20 edges
5. `Product` - 20 edges
6. `ProductVariant` - 20 edges
7. `User` - 19 edges
8. `compilerOptions` - 19 edges
9. `_tx()` - 18 edges
10. `_get()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `M4 — Koszyk, zamówienia, płatności (3–4 tygodnie)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M4 — Кошик, замовлення, платежі (3–4 тижні)` --references--> `PaymentProvider`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `2.1. `GET /products` — lista z filtrami` --references--> `ProductFilter`  [INFERRED]
  docs/catalog.md → api/app/schemas/catalog.py

## Import Cycles
- None detected.

## Communities (28 total, 7 thin omitted)

### Community 0 - "Base"
Cohesion: 0.05
Nodes (85): downgrade(), upgrade(), Base, get_session(), Category, CategoryTranslation, Gemstone, PriceHistory (+77 more)

### Community 1 - "App.tsx"
Cohesion: 0.05
Nodes (79): react, react-router-dom, extractErrorMessage(), forgotPassword(), login(), logout(), me(), refresh() (+71 more)

### Community 2 - "Kamienie milowe"
Cohesion: 0.05
Nodes (44): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kamienie milowe, Kolejność i zależności, Kontekst, M0 — Stabilizacja (1–2 dni), M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle), M1 — Schemat bazy i migracje (1–2 tygodnie) (+36 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, vite (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.04
Nodes (42): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+34 more)

### Community 5 - "user_repository.py"
Cohesion: 0.06
Nodes (70): Settings, create_access_token(), decode_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), verify_password(), get_current_user() (+62 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "postgres"
Cohesion: 0.04
Nodes (46): build, container_name, depends_on, environment, ports, restart, volumes, context (+38 more)

### Community 8 - "resolve_locale"
Cohesion: 0.22
Nodes (7): get_product(), list_categories(), resolve_locale(), test_accept_language_used(), test_fallback_uk(), test_query_locale_wins(), test_tree_hides_children_of_inactive_parent()

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "main.py"
Cohesion: 0.08
Nodes (12): get_db(), conflict_handler(), health(), invalid_image_handler(), log_event(), not_found_handler(), ready(), request_context() (+4 more)

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
Cohesion: 0.21
Nodes (18): forgot_password(), login(), logout(), me(), refresh(), register(), reset_password(), _set_refresh_cookie() (+10 more)

### Community 21 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 22 - "admin_catalog_service.py"
Cohesion: 0.08
Nodes (56): add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant(), remove_gemstone() (+48 more)

### Community 23 - "Moduł katalogu (M3)"
Cohesion: 0.17
Nodes (11): 1. Zakres, 2.1. `GET /products` — lista z filtrami, 2.2. Paginacja kursorowa, 2.3. `GET /products/{slug}` i `GET /categories`, 2. Publiczne API, 3. Wielojęzyczność (UK / PL / EN), 4. Ceny, 5. Zdjęcia (+3 more)

### Community 25 - "test_admin_catalog.py"
Cohesion: 0.21
Nodes (10): require_role(), Role, process_image(), _auth(), _png(), test_admin_forbidden_for_regular_user(), test_manager_builds_product_end_to_end(), test_process_image_makes_three_webp_sizes_without_exif() (+2 more)

### Community 26 - "package.json"
Cohesion: 0.67
Nodes (3): dependencies, typescript@^7.0.2, typescript

### Community 27 - "env.py"
Cohesion: 0.47
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `useLanguage()` connect `App.tsx` to `Kamienie milowe`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `useLanguage()` (e.g. with `M3 — Katalog + i18n (2–3 tygodnie)` and `M3 — Каталог + i18n (2–3 тижні)`) actually correct?**
  _`useLanguage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Base` be split into smaller, more focused modules?**
  _Cohesion score 0.052999047921294826 - nodes in this community are weakly interconnected._
- **Are the 16 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `App.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.05330578512396694 - nodes in this community are weakly interconnected._
- **Are the 7 inferred relationships involving `Category` (e.g. with `get_product_by_slug()` and `list_categories()`) actually correct?**
  _`Category` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `Kamienie milowe` be split into smaller, more focused modules?**
  _Cohesion score 0.0463768115942029 - nodes in this community are weakly interconnected._