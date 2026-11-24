# Graph Report - TNDCJewelryHouse  (2026-11-23)

## Corpus Check
- 167 files · ~63,471 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 9, .avif 4, .css 3)

## Summary
- 1403 nodes · 4225 edges · 73 communities (60 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 421 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab2bee67`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- str
- languageContext.tsx
- Diploma roadmap — TNDC Jewelry House
- package.json
- Architecture Workshop (Student-Owned)
- order_repository.py
- compilerOptions
- web
- catalog_service.py
- compilerOptions
- app/main.py
- CLAUDE.md
- API — baza danych i migracje (Milestone 1)
- .oxlintrc.json
- order_service.py
- Categories.tsx
- tsconfig.json
- cart_service.py
- useLanguage
- admin_catalog_service.py
- cartApi.ts
- EventType
- package.json
- orderApi.ts
- request
- engine.py
- M7 — Семантичний пошук e5 + pgvector: план задач
- types/index.ts
- test_cart.py
- session.py
- test_catalog_api.py
- dependencies.py
- user_repository.py
- auth_service.py
- postgres
- test_auth_flows.py
- test_consents.py
- routers/auth.py
- api
- environment
- order.py
- jobs
- security.py
- trackingContext.tsx
- enums.py
- test_auth_negative.py
- telemetry_service.py
- FastAPI
- get_by_email
- healthcheck
- test_checkout.py
- create_access_token
- Kamienie milowe
- test_account_deletion.py
- Product.tsx
- Milestones
- embedder
- Diploma roadmap — TNDC Jewelry House
- ingest_events
- dependencies.py
- sqlalchemy
- Currency
- RequestIdFilter
- InvalidSignature

## God Nodes (most connected - your core abstractions)
1. `Currency` - 53 edges
2. `EventType` - 50 edges
3. `Product` - 46 edges
4. `useLanguage()` - 46 edges
5. `ProductVariant` - 43 edges
6. `_setup()` - 40 edges
7. `Category` - 36 edges
8. `UserEvent` - 36 edges
9. `checkout()` - 35 edges
10. `Base` - 34 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `Що вже є (не робити)` --references--> `SearchType`  [INFERRED]
  docs/plans/m7-tasks.uk.md → api/app/models/enums.py
- `T5. Скрипт `api/scripts/build_embeddings.py`` --references--> `load_product_features()`  [INFERRED]
  docs/plans/m7-tasks.uk.md → api/app/repositories/recommendation_repository.py
- `Реєстр ризиків (топ)` --references--> `LanguageProvider()`  [INFERRED]
  docs/plans/roadmap.uk.md → web/src/context/languageContext.tsx

## Import Cycles
- None detected.

## Communities (73 total, 13 thin omitted)

### Community 0 - "str"
Cohesion: 0.23
Nodes (6): PaymentProvider, PaymentStatus, PaymentGateway, WebhookEvent, M4 — Koszyk, zamówienia, płatności (3–4 tygodnie), M4 — Кошик, замовлення, платежі (3–4 тижні)

### Community 1 - "languageContext.tsx"
Cohesion: 0.22
Nodes (9): react, react-router-dom, CartLine(), useCart(), Language, LanguageContext, LanguageContextValue, LANGUAGES (+1 more)

### Community 2 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.20
Nodes (8): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kolejność i zależności, Kontekst, Pierwsze kroki, Przyjęte decyzje, Tabele opcjonalne (tylko jeśli zostanie czas), Weryfikacja

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, vite (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.04
Nodes (42): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+34 more)

### Community 5 - "order_repository.py"
Cohesion: 0.24
Nodes (14): Order, OrderItem, get_active_shipping_method(), get_order(), list_active_shipping_methods(), list_order_items(), list_orders(), lock_purchasable_variants() (+6 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "web"
Cohesion: 0.18
Nodes (11): context, dockerfile, VITE_API_URL, web, build, container_name, depends_on, environment (+3 more)

### Community 8 - "catalog_service.py"
Cohesion: 0.10
Nodes (28): get_product(), list_categories(), list_products(), for_you(), similar(), CategoryNode, GemstoneOut, ImageOut (+20 more)

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "app/main.py"
Cohesion: 0.13
Nodes (9): conflict_handler(), health(), invalid_image_handler(), log_event(), not_found_handler(), ready(), request_context(), unhandled_exception_handler() (+1 more)

### Community 11 - "CLAUDE.md"
Cohesion: 0.20
Nodes (9): 1. Code Comments (CRITICAL), 3. Security, Architecture & Design Guidelines, Development & Execution Commands, Docker (Preferred Runtime), File Access & Environment Restrictions, Navigation & Project Context Rules, Non-Negotiable Rules & Standards (+1 more)

### Community 12 - "API — baza danych i migracje (Milestone 1)"
Cohesion: 0.29
Nodes (6): API — baza danych i migracje (Milestone 1), Decyzje odzwierciedlone w schemacie, Kolejność migracji, Lista kontrolna dla wygenerowanej migracji `0002`, Uruchomienie, Zadania okresowe (serwis `jobs`)

### Community 13 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 14 - "order_service.py"
Cohesion: 0.10
Nodes (25): send_email(), OrderStatus, cancel_order(), create_order(), get_order(), list_orders(), list_shipping_methods(), OrderOut (+17 more)

### Community 15 - "Categories.tsx"
Cohesion: 0.20
Nodes (14): listCategories(), listProducts(), toItem(), ItemCard(), Categories(), COLORS, EMPTY_FILTERS, FINENESS (+6 more)

### Community 20 - "cart_service.py"
Cohesion: 0.10
Nodes (39): Cart, CartItem, CartStatus, add_item(), delete_item(), get_active_cart(), get_item(), get_item_by_variant() (+31 more)

### Community 21 - "useLanguage"
Cohesion: 0.13
Nodes (23): M3 — Katalog + i18n (2–3 tygodnie), Rejestr ryzyk (najważniejsze), M3 — Каталог + i18n (2–3 тижні), App(), ConsentBanner(), Footer(), Header(), CartProvider() (+15 more)

### Community 22 - "admin_catalog_service.py"
Cohesion: 0.06
Nodes (63): add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant(), remove_gemstone() (+55 more)

### Community 23 - "cartApi.ts"
Cohesion: 0.18
Nodes (16): addCartItem(), cartRequest(), clearCartSession(), getCart(), getCartSession(), ownerRequest(), readSession(), removeCartItem() (+8 more)

### Community 25 - "EventType"
Cohesion: 0.07
Nodes (54): EventType, Role, SearchQuery, UserEvent, anonymize_older_than(), anonymize_user_events(), bulk_insert_events(), count_events_by_day() (+46 more)

### Community 26 - "package.json"
Cohesion: 0.67
Nodes (3): dependencies, typescript@^7.0.2, typescript

### Community 27 - "orderApi.ts"
Cohesion: 0.18
Nodes (17): cancelOrder(), createOrder(), getOrder(), listShippingMethods(), useAuth(), Checkout(), handleSubmit(), POINT_PROVIDERS (+9 more)

### Community 28 - "request"
Cohesion: 0.29
Nodes (12): extractErrorMessage(), forgotPassword(), login(), logout(), me(), refresh(), register(), request() (+4 more)

### Community 29 - "engine.py"
Cohesion: 0.11
Nodes (22): score(), build_vectors(), cosine(), _normalize(), profile_vector(), similar(), for_you(), _popularity() (+14 more)

### Community 30 - "M7 — Семантичний пошук e5 + pgvector: план задач"
Cohesion: 0.09
Nodes (22): Settings, embed(), EmbedderUnavailable, test_embed_raises_when_service_down(), fake_post(), test_embed_returns_vectors(), M7 — Семантичний пошук e5 + pgvector: план задач, T10. Фронтенд (мінімум) (+14 more)

### Community 31 - "types/index.ts"
Cohesion: 0.15
Nodes (22): AuthContext, CartContext, EMPTY_CART, AuthContextValue, AuthResult, User, Cart, CartLine (+14 more)

### Community 32 - "test_cart.py"
Cohesion: 0.23
Nodes (21): _add(), _guest(), _lines(), _login(), _register_and_login(), test_add_item_uses_server_price(), test_add_over_free_stock_returns_409(), test_add_where_sum_exceeds_stock_returns_409() (+13 more)

### Community 33 - "session.py"
Cohesion: 0.33
Nodes (4): get_session(), main(), main(), main()

### Community 34 - "test_catalog_api.py"
Cohesion: 0.23
Nodes (16): score(), _category(), _now(), _product(), _slugs(), test_category_filter_includes_subcategories(), test_cursor_pages_do_not_overlap(), test_cursor_pagination_by_price() (+8 more)

### Community 35 - "dependencies.py"
Cohesion: 0.24
Nodes (5): events_by_day(), top_products(), EventBatchIn, EventCountOut, TopProductOut

### Community 36 - "user_repository.py"
Cohesion: 0.20
Nodes (22): UserStatus, EmailVerificationToken, PasswordResetToken, RefreshToken, User, UserProfile, create_email_verification_token(), create_password_reset_token() (+14 more)

### Community 37 - "auth_service.py"
Cohesion: 0.27
Nodes (16): generate_refresh_token(), hash_refresh_token(), get_by_id(), AuthError, delete_account(), forgot_password(), _issue_email_verification_token(), _issue_password_reset_token() (+8 more)

### Community 38 - "postgres"
Cohesion: 0.18
Nodes (11): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, TZ, container_name, environment, image, ports (+3 more)

### Community 39 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 40 - "test_consents.py"
Cohesion: 0.24
Nodes (15): create_user_profile(), get_profile(), UserResponse, get_me(), set_analytics_consent(), set_preferred_language(), tracking_allowed(), test_consent_creates_missing_profile() (+7 more)

### Community 41 - "routers/auth.py"
Cohesion: 0.20
Nodes (22): delete_me(), forgot_password(), login(), logout(), me(), refresh(), register(), reset_password() (+14 more)

### Community 42 - "api"
Cohesion: 0.20
Nodes (10): build, container_name, depends_on, ports, restart, volumes, postgres, depends_on (+2 more)

### Community 43 - "environment"
Cohesion: 0.25
Nodes (15): environment, ACCESS_TOKEN_EXPIRE_MINUTES, CORS_ORIGINS, DATABASE_URL, EMBEDDER_URL, EMBEDDING_MODEL, EMBEDDING_VERSION, JWT_ALGORITHM (+7 more)

### Community 45 - "order.py"
Cohesion: 0.20
Nodes (7): CheckoutIn, OrderItemOut, ShippingMethodOut, test_courier_address_instead_of_point_is_accepted(), test_invalid_checkout_is_rejected(), test_line_total_is_computed(), test_valid_checkout_is_accepted_and_trimmed()

### Community 46 - "jobs"
Cohesion: 0.18
Nodes (10): build, command, container_name, restart, volumes, services, jobs, volumes (+2 more)

### Community 47 - "security.py"
Cohesion: 0.30
Nodes (10): hash_password(), _pepper(), _verify(), verify_legacy_password(), verify_password(), is_locked(), login(), test_hash_is_peppered() (+2 more)

### Community 48 - "trackingContext.tsx"
Cohesion: 0.19
Nodes (12): EventType, sendEvents(), TrackEvent, TRACKING_HEADER, setAnalyticsConsent(), Consent, readGuestConsent(), TrackingContext (+4 more)

### Community 49 - "enums.py"
Cohesion: 0.21
Nodes (7): DeliveryProvider, pg_enum(), SearchType, ShippingMethod, last_unit(), _method(), test_lists_only_active_methods_cheapest_first()

### Community 50 - "test_auth_negative.py"
Cohesion: 0.35
Nodes (8): _login(), _register(), test_account_locks_after_max_failed_attempts(), test_login_sqli_in_password_does_not_bypass_auth(), test_refresh_with_expired_token_is_rejected(), test_refresh_with_revoked_token_is_rejected(), test_successful_login_resets_failed_attempts(), test_suspended_user_loses_access_and_refresh()

### Community 51 - "telemetry_service.py"
Cohesion: 0.24
Nodes (5): EventIn, events_by_day(), record_events(), _since(), top_products()

### Community 52 - "FastAPI"
Cohesion: 0.23
Nodes (5): embed(), EmbedIn, EmbedOut, health(), lifespan()

### Community 53 - "get_by_email"
Cohesion: 0.40
Nodes (10): get_by_email(), _payload(), test_register_creates_pending_user(), test_register_duplicate_email_does_not_create_a_second_user(), test_register_duplicate_email_is_case_insensitive(), test_register_issues_email_verification_token(), test_register_never_stores_plaintext_password(), test_register_rejects_invalid_email() (+2 more)

### Community 54 - "healthcheck"
Cohesion: 0.43
Nodes (7): healthcheck, interval, retries, start_period, test, timeout, healthcheck

### Community 55 - "test_checkout.py"
Cohesion: 0.24
Nodes (14): checkout(), test_only_one_buyer_gets_the_last_unit(), buyer_a(), buyer_b(), _form(), test_allowed_transitions_cover_every_status(), test_cancel_releases_reserve_and_sets_cancelled_at(), test_cancel_twice_is_rejected() (+6 more)

### Community 56 - "create_access_token"
Cohesion: 0.33
Nodes (8): create_access_token(), create_user(), test_logged_in_header_cannot_override_profile(), _headers(), test_me_returns_default_language(), test_patch_preferences_creates_missing_profile(), test_patch_preferences_persists_language(), test_patch_preferences_rejects_unknown_language()

### Community 57 - "Kamienie milowe"
Cohesion: 0.20
Nodes (10): Kamienie milowe, M0 — Stabilizacja (1–2 dni), M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle), M1 — Schemat bazy i migracje (1–2 tygodnie), M2 — FastAPI i własne uwierzytelnianie (2–3 tygodnie), M5 — Telemetria UX + RODO (1–2 tygodnie), M6 — Algorytmy klasyczne (2–3 tygodnie), M7 — Wyszukiwanie semantyczne e5 + pgvector (2–3 tygodnie, równolegle z M4/M6) (+2 more)

### Community 58 - "test_account_deletion.py"
Cohesion: 0.73
Nodes (5): _delete(), test_delete_removes_user_anonymises_events_keeps_orders(), test_token_rejected_after_deletion(), test_wrong_password_keeps_account(), _user()

### Community 59 - "Product.tsx"
Cohesion: 0.31
Nodes (8): getProductBySlug(), ImageSliderOnHover(), addToCart(), gemstoneName(), Product(), handleAdd(), T, variantLabel()

### Community 61 - "Milestones"
Cohesion: 0.20
Nodes (10): M0 — Стабілізація (1–2 дні), M10 — Впровадження і документація (3–4 тижні, паралельно), M1 — Схема БД і міграції (1–2 тижні), M2 — FastAPI і власна автентифікація (2–3 тижні), M5 — Телеметрія UX + RODO (1–2 тижні), M6 — Класичні алгоритми (2–3 тижні), M7 — Семантичний пошук e5 + pgvector (2–3 тижні, паралельно з M4/M6), M8 — Персоналізація в UI (2 тижні) (+2 more)

### Community 62 - "embedder"
Cohesion: 0.22
Nodes (9): build, container_name, environment, mem_limit, ports, restart, volumes, HF_HOME (+1 more)

### Community 63 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.22
Nodes (9): Context, Diploma roadmap — TNDC Jewelry House, Verification, Архітектура (скорочено), Опційні таблиці (лише якщо лишиться час), Перші кроки після затвердження, Порядок і залежності, Прийняті рішення (+1 more)

### Community 65 - "dependencies.py"
Cohesion: 0.16
Nodes (7): decode_access_token(), get_current_user(), get_db(), get_optional_user(), require_role(), client(), db_session()

### Community 68 - "sqlalchemy"
Cohesion: 0.14
Nodes (9): _database_url(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), upgrade(), upgrade(), downgrade() (+1 more)

### Community 69 - "Currency"
Cohesion: 0.06
Nodes (74): Base, Category, CategoryTranslation, Gemstone, PriceHistory, Product, ProductEmbedding, ProductGemstone (+66 more)

## Knowledge Gaps
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CartStatus` connect `cart_service.py` to `test_cart.py`, `Currency`, `order_service.py`, `enums.py`, `test_checkout.py`, `Kamienie milowe`, `Milestones`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.07563025210084033 - nodes in this community are weakly interconnected._
- **Why does `useLanguage()` connect `useLanguage` to `languageContext.tsx`, `Product.tsx`, `Categories.tsx`, `cartApi.ts`, `orderApi.ts`, `types/index.ts`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `EventType` (e.g. with `UserEvent` and `refresh_view_counts()`) actually correct?**
  _`EventType` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `Architecture Workshop (Student-Owned)` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._
- **Why does `Kamienie milowe` connect `Kamienie milowe` to `str`, `Diploma roadmap — TNDC Jewelry House`, `useLanguage`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._