# Graph Report - TNDCJewelryHouse  (2026-11-15)

## Corpus Check
- 125 files · ~55,229 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .avif 4, .css 3)

## Summary
- 1089 nodes · 3221 edges · 36 communities (31 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `43421380`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Currency
- languageContext.tsx
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
- order_service.py
- types/index.ts
- tsconfig.json
- cart_service.py
- useLanguage
- admin_catalog_service.py
- cartApi.ts
- test_admin_catalog.py
- package.json
- orderApi.ts
- request
- ProductImage
- seed.py
- cartContext.tsx
- test_cart.py
- import_products.py
- test_catalog_api.py
- admin_catalog_service.py

## God Nodes (most connected - your core abstractions)
1. `Currency` - 45 edges
2. `useLanguage()` - 44 edges
3. `ProductVariant` - 37 edges
4. `Product` - 36 edges
5. `Base` - 34 edges
6. `Category` - 31 edges
7. `checkout()` - 29 edges
8. `import_product()` - 29 edges
9. `VariantPrice` - 28 edges
10. `_setup()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `Rejestr ryzyk (najważniejsze)` --references--> `LanguageProvider()`  [INFERRED]
  docs/plans/roadmap.pl.md → web/src/context/languageContext.tsx
- `3. Кошик — фронт` --references--> `Item`  [INFERRED]
  docs/plans/m4-tasks.uk.md → web/src/types/item.ts
- `0. Підготовка` --references--> `VariantPrice`  [INFERRED]
  docs/plans/m4-tasks.uk.md → api/app/models/catalog.py

## Import Cycles
- None detected.

## Communities (36 total, 5 thin omitted)

### Community 0 - "Currency"
Cohesion: 0.07
Nodes (37): _database_url(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), upgrade(), Base, ProductEmbedding (+29 more)

### Community 1 - "languageContext.tsx"
Cohesion: 0.14
Nodes (19): M3 — Katalog + i18n (2–3 tygodnie), M3 — Каталог + i18n (2–3 тижні), Реєстр ризиків (топ), react, react-router-dom, CartLine(), ImageSliderOnHover(), useCart() (+11 more)

### Community 2 - "Kamienie milowe"
Cohesion: 0.04
Nodes (45): 1. Міграція, 2. Кошик — бекенд, 3. Кошик — фронт, 4. Замовлення — бекенд, 5. Checkout — фронт (без оплати), 7. Закриття M4, M4 — задачі (кошик, замовлення, платежі), Поза M4 (свідомо) (+37 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, vite (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.04
Nodes (42): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+34 more)

### Community 5 - "user_repository.py"
Cohesion: 0.05
Nodes (87): Settings, create_access_token(), decode_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), _pepper(), _verify() (+79 more)

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
Cohesion: 0.06
Nodes (33): get_current_user(), get_db(), get_optional_user(), conflict_handler(), health(), invalid_image_handler(), log_event(), not_found_handler() (+25 more)

### Community 11 - "CLAUDE.md"
Cohesion: 0.20
Nodes (9): 1. Code Comments (CRITICAL), 3. Security, Architecture & Design Guidelines, Development & Execution Commands, Docker (Preferred Runtime), File Access & Environment Restrictions, Navigation & Project Context Rules, Non-Negotiable Rules & Standards (+1 more)

### Community 12 - "API — baza danych i migracje (Milestone 1)"
Cohesion: 0.33
Nodes (5): API — baza danych i migracje (Milestone 1), Decyzje odzwierciedlone w schemacie, Kolejność migracji, Lista kontrolna dla wygenerowanej migracji `0002`, Uruchomienie

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "order_service.py"
Cohesion: 0.05
Nodes (64): send_email(), Order, OrderStatus, get_active_shipping_method(), get_order(), list_active_shipping_methods(), list_order_items(), list_orders() (+56 more)

### Community 15 - "types/index.ts"
Cohesion: 0.13
Nodes (29): getProductBySlug(), listCategories(), listProducts(), toItem(), toQuery(), ItemCard(), Categories(), COLORS (+21 more)

### Community 20 - "cart_service.py"
Cohesion: 0.09
Nodes (41): Cart, CartItem, CartStatus, add_item(), delete_item(), get_active_cart(), get_item(), get_item_by_variant() (+33 more)

### Community 21 - "useLanguage"
Cohesion: 0.17
Nodes (15): App(), Footer(), Header(), useAuth(), CartProvider(), useLanguage(), About(), Account() (+7 more)

### Community 22 - "admin_catalog_service.py"
Cohesion: 0.11
Nodes (33): MetalColor, add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant() (+25 more)

### Community 23 - "cartApi.ts"
Cohesion: 0.15
Nodes (18): addCartItem(), cartRequest(), clearCartSession(), getCart(), getCartSession(), ownerRequest(), readSession(), removeCartItem() (+10 more)

### Community 25 - "test_admin_catalog.py"
Cohesion: 0.15
Nodes (12): require_role(), PriceHistory, Role, image_paths(), process_image(), _auth(), _png(), test_admin_forbidden_for_regular_user() (+4 more)

### Community 26 - "package.json"
Cohesion: 0.67
Nodes (3): dependencies, typescript@^7.0.2, typescript

### Community 27 - "orderApi.ts"
Cohesion: 0.16
Nodes (17): cancelOrder(), createOrder(), getOrder(), listOrders(), listShippingMethods(), Checkout(), handleSubmit(), POINT_PROVIDERS (+9 more)

### Community 28 - "request"
Cohesion: 0.32
Nodes (11): extractErrorMessage(), forgotPassword(), login(), logout(), me(), refresh(), register(), request() (+3 more)

### Community 29 - "ProductImage"
Cohesion: 0.39
Nodes (6): ProductImage, clear_primary_image(), get_price(), list_image_keys(), upsert_category_translation(), upsert_product_translation()

### Community 30 - "seed.py"
Cohesion: 0.15
Nodes (24): Category, CategoryTranslation, Gemstone, ProductGemstone, ProductTranslation, _decode_cursor(), _encode_cursor(), get_product_by_slug() (+16 more)

### Community 31 - "cartContext.tsx"
Cohesion: 0.32
Nodes (5): CartContext, EMPTY_CART, Cart, CartLine, CartContextValue

### Community 32 - "test_cart.py"
Cohesion: 0.23
Nodes (21): _add(), _guest(), _lines(), _login(), _register_and_login(), test_add_item_uses_server_price(), test_add_over_free_stock_returns_409(), test_add_where_sum_exceeds_stock_returns_409() (+13 more)

### Community 33 - "import_products.py"
Cohesion: 0.18
Nodes (6): get_session(), _by_slug(), GemstoneFile, main(), ProductFile, VariantFile

### Community 34 - "test_catalog_api.py"
Cohesion: 0.37
Nodes (10): _category(), _now(), _product(), _slugs(), test_category_filter_includes_subcategories(), test_cursor_pages_do_not_overlap(), test_cursor_pagination_by_price(), test_price_filter_uses_active_sale_price() (+2 more)

### Community 36 - "admin_catalog_service.py"
Cohesion: 0.20
Nodes (26): Product, ProductVariant, add_gemstone(), _apply(), _check_parent(), _check_variant_of(), ConflictError, create_category() (+18 more)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `M4 — задачі (кошик, замовлення, платежі)` connect `Kamienie milowe` to `Currency`, `user_repository.py`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Should `Currency` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Why does `3. Кошик — фронт` connect `Kamienie milowe` to `types/index.ts`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `useLanguage()` (e.g. with `M3 — Katalog + i18n (2–3 tygodnie)` and `M3 — Каталог + i18n (2–3 тижні)`) actually correct?**
  _`useLanguage()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `languageContext.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.13655761024182078 - nodes in this community are weakly interconnected._
- **Why does `Item` connect `types/index.ts` to `languageContext.tsx`, `Kamienie milowe`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._