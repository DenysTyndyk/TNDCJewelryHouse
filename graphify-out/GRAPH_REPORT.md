# Graph Report - TNDCJewelryHouse  (2026-11-14)

## Corpus Check
- 109 files · ~50,326 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .avif 4, .css 3)

## Summary
- 942 nodes · 2654 edges · 37 communities (30 shown, 7 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f7f777fe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- enums.py
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
- cart_service.py
- test_auth_flows.py
- admin_catalog_service.py
- Diploma roadmap — TNDC Jewelry House
- test_admin_catalog.py
- package.json
- sqlalchemy
- Diploma roadmap — TNDC Jewelry House
- Currency
- test_cart.py
- seed.py
- test_catalog_api.py
- Category
- models/catalog.py

## God Nodes (most connected - your core abstractions)
1. `useLanguage()` - 38 edges
2. `Currency` - 36 edges
3. `Base` - 34 edges
4. `Product` - 30 edges
5. `ProductVariant` - 29 edges
6. `import_product()` - 29 edges
7. `Category` - 27 edges
8. `VariantPrice` - 24 edges
9. `_variant()` - 21 edges
10. `ProductImage` - 20 edges

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

## Communities (37 total, 7 thin omitted)

### Community 0 - "enums.py"
Cohesion: 0.14
Nodes (17): Base, ProductEmbedding, Favorite, Order, OrderItem, Payment, DeliveryProvider, EventType (+9 more)

### Community 1 - "App.tsx"
Cohesion: 0.05
Nodes (85): 3. Кошик — фронт, M3 — Katalog + i18n (2–3 tygodnie), Rejestr ryzyk (najważniejsze), M3 — Каталог + i18n (2–3 тижні), react, react-router-dom, extractErrorMessage(), forgotPassword() (+77 more)

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
Cohesion: 0.06
Nodes (73): create_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), _pepper(), _verify(), verify_legacy_password(), verify_password() (+65 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "postgres"
Cohesion: 0.04
Nodes (47): build, container_name, depends_on, environment, ports, restart, volumes, context (+39 more)

### Community 8 - "catalog_service.py"
Cohesion: 0.14
Nodes (22): get_product(), list_categories(), list_products(), CategoryNode, GemstoneOut, ImageOut, ProductDetail, ProductFilter (+14 more)

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "main.py"
Cohesion: 0.05
Nodes (35): Settings, decode_access_token(), get_current_user(), get_db(), get_optional_user(), require_role(), conflict_handler(), health() (+27 more)

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
Cohesion: 0.25
Nodes (8): 1. Міграція, 2. Кошик — бекенд, 4. Замовлення — бекенд, 5. Checkout — фронт (без оплати), 6. Платежі (sandbox), 7. Закриття M4, M4 — задачі (кошик, замовлення, платежі), Поза M4 (свідомо)

### Community 20 - "cart_service.py"
Cohesion: 0.09
Nodes (40): Cart, CartItem, CartStatus, add_item(), delete_item(), get_active_cart(), get_item(), get_item_by_variant() (+32 more)

### Community 21 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 22 - "admin_catalog_service.py"
Cohesion: 0.07
Nodes (62): upsert_category_translation(), add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant() (+54 more)

### Community 23 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.25
Nodes (8): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kolejność i zależności, Kontekst, Pierwsze kroki, Przyjęte decyzje, Tabele opcjonalne (tylko jeśli zostanie czas), Weryfikacja

### Community 25 - "test_admin_catalog.py"
Cohesion: 0.15
Nodes (11): PriceHistory, Role, image_paths(), _auth(), _png(), test_admin_forbidden_for_regular_user(), test_manager_builds_product_end_to_end(), test_process_image_makes_three_webp_sizes_without_exif() (+3 more)

### Community 26 - "package.json"
Cohesion: 0.67
Nodes (3): dependencies, typescript@^7.0.2, typescript

### Community 27 - "sqlalchemy"
Cohesion: 0.20
Nodes (6): _database_url(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), upgrade()

### Community 28 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.22
Nodes (9): Context, Diploma roadmap — TNDC Jewelry House, Verification, Архітектура (скорочено), Опційні таблиці (лише якщо лишиться час), Перші кроки після затвердження, Порядок і залежності, Прийняті рішення (+1 more)

### Community 30 - "Currency"
Cohesion: 0.19
Nodes (20): CategoryTranslation, ProductGemstone, ProductImage, ProductTranslation, VariantPrice, Currency, clear_primary_image(), get_price() (+12 more)

### Community 32 - "test_cart.py"
Cohesion: 0.23
Nodes (21): _add(), _guest(), _lines(), _login(), _register_and_login(), test_add_item_uses_server_price(), test_add_over_free_stock_returns_409(), test_add_where_sum_exceeds_stock_returns_409() (+13 more)

### Community 33 - "seed.py"
Cohesion: 0.21
Nodes (10): get_session(), ShippingMethod, UserProfile, save_image(), main(), seed_categories(), seed_gemstones(), seed_image() (+2 more)

### Community 34 - "test_catalog_api.py"
Cohesion: 0.37
Nodes (10): _category(), _now(), _product(), _slugs(), test_category_filter_includes_subcategories(), test_cursor_pages_do_not_overlap(), test_cursor_pagination_by_price(), test_price_filter_uses_active_sale_price() (+2 more)

### Community 35 - "Category"
Cohesion: 0.29
Nodes (9): Category, Gemstone, import_all(), main(), _count(), _folder(), _png(), test_import_creates_then_updates_without_duplicates() (+1 more)

### Community 36 - "models/catalog.py"
Cohesion: 0.47
Nodes (6): Product, ProductVariant, MetalColor, MetalType, _product(), test_dod_filter_white_gold_585_ring_under_3000()

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `M4 — задачі (кошик, замовлення, платежі)` connect `M4 — задачі (кошик, замовлення, платежі)` to `App.tsx`, `user_repository.py`, `roadmap.uk.md`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `useLanguage()` (e.g. with `M3 — Katalog + i18n (2–3 tygodnie)` and `M3 — Каталог + i18n (2–3 тижні)`) actually correct?**
  _`useLanguage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `enums.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13940256045519203 - nodes in this community are weakly interconnected._
- **Why does `3. Кошик — фронт` connect `App.tsx` to `M4 — задачі (кошик, замовлення, платежі)`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `App.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.050243719535058115 - nodes in this community are weakly interconnected._
- **Are the 13 inferred relationships involving `Product` (e.g. with `get_purchasable_variant()` and `list_cart_lines()`) actually correct?**
  _`Product` has 13 INFERRED edges - model-reasoned connections that need verification._