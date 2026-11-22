# Graph Report - TNDCJewelryHouse  (2026-11-22)

## Corpus Check
- 160 files · ~62,530 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .avif 4, .css 3)

## Summary
- 1332 nodes · 4046 edges · 71 communities (62 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 416 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `666fe768`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- str
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
- Categories.tsx
- tsconfig.json
- cart_service.py
- useLanguage
- routers/admin_catalog.py
- cartApi.ts
- test_admin_catalog.py
- package.json
- orderApi.ts
- request
- engine.py
- Currency
- types/index.ts
- test_cart.py
- config.py
- test_catalog_api.py
- dependencies.py
- admin_catalog_service.py
- test_recommendations_api.py
- auth_service.py
- test_auth_flows.py
- test_consents.py
- post
- test_checkout.py
- sqlalchemy_orm
- security.py
- UserEvent
- config.py
- order.py
- trackingContext.tsx
- Currency
- test_payment.py
- telemetry_service.py
- test_tracking_flows.py
- import_products.py
- get_by_email
- _setup
- EventType
- Milestones
- create_access_token
- Product.tsx
- Diploma roadmap — TNDC Jewelry House
- Diploma roadmap — TNDC Jewelry House
- M4 — задачі (кошик, замовлення, платежі)
- create_order
- ingest_events
- dependencies.py
- recommendation_repository.py
- enums.py
- admin_catalog_repository.py
- get_order

## God Nodes (most connected - your core abstractions)
1. `Currency` - 53 edges
2. `EventType` - 46 edges
3. `useLanguage()` - 46 edges
4. `Product` - 43 edges
5. `ProductVariant` - 42 edges
6. `_setup()` - 37 edges
7. `Category` - 36 edges
8. `Base` - 34 edges
9. `checkout()` - 34 edges
10. `VariantPrice` - 32 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Schemat bazy i migracje (1–2 tygodnie)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.pl.md → api/app/models/enums.py
- `M1 — Схема БД і міграції (1–2 тижні)` --references--> `CartStatus`  [INFERRED]
  docs/plans/roadmap.uk.md → api/app/models/enums.py
- `1. Репозиторій` --references--> `load_product_features()`  [INFERRED]
  docs/plans/m6-tasks.uk.md → api/app/repositories/recommendation_repository.py
- `Rejestr ryzyk (najważniejsze)` --references--> `LanguageProvider()`  [INFERRED]
  docs/plans/roadmap.pl.md → web/src/context/languageContext.tsx
- `Architektura (skrót)` --references--> `useTracking()`  [INFERRED]
  docs/plans/roadmap.pl.md → web/src/context/trackingContext.tsx

## Import Cycles
- None detected.

## Communities (71 total, 9 thin omitted)

### Community 0 - "str"
Cohesion: 0.18
Nodes (8): PaymentProvider, PaymentStatus, InvalidSignature, PaymentGateway, WebhookEvent, 6. Платежі (sandbox) — ⏸ перенесено, M4 — Koszyk, zamówienia, płatności (3–4 tygodnie), M4 — Кошик, замовлення, платежі (3–4 тижні)

### Community 1 - "languageContext.tsx"
Cohesion: 0.22
Nodes (9): react, react-router-dom, CartLine(), useCart(), Language, LanguageContext, LanguageContextValue, LANGUAGES (+1 more)

### Community 2 - "Kamienie milowe"
Cohesion: 0.20
Nodes (10): Kamienie milowe, M0 — Stabilizacja (1–2 dni), M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle), M1 — Schemat bazy i migracje (1–2 tygodnie), M2 — FastAPI i własne uwierzytelnianie (2–3 tygodnie), M5 — Telemetria UX + RODO (1–2 tygodnie), M6 — Algorytmy klasyczne (2–3 tygodnie), M7 — Wyszukiwanie semantyczne e5 + pgvector (2–3 tygodnie, równolegle z M4/M6) (+2 more)

### Community 3 - "package.json"
Cohesion: 0.08
Nodes (33): oxlint, react-dom, tailwindcss, @tailwindcss/vite, @types/node, @types/react, @types/react-dom, vite (+25 more)

### Community 4 - "Architecture Workshop (Student-Owned)"
Cohesion: 0.04
Nodes (42): 10. Open questions, 11. Decisions D1–D5, 1. Problem statement & scope, 2. Context diagram, 3. Containers, 4. Responsibility matrix, 5.1 Cart rules (decided), 5.2 Auth & profile (decided — D1) (+34 more)

### Community 5 - "user_repository.py"
Cohesion: 0.21
Nodes (21): EmailVerificationToken, PasswordResetToken, RefreshToken, UserProfile, create_email_verification_token(), create_password_reset_token(), get_by_phone_number(), get_email_verification_token() (+13 more)

### Community 6 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, allowJs, erasableSyntaxOnly, jsx, lib, module (+12 more)

### Community 7 - "postgres"
Cohesion: 0.04
Nodes (47): build, container_name, depends_on, environment, ports, restart, volumes, context (+39 more)

### Community 8 - "catalog_service.py"
Cohesion: 0.06
Nodes (31): _database_url(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), upgrade(), upgrade(), get_product() (+23 more)

### Community 9 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 10 - "main.py"
Cohesion: 0.12
Nodes (9): conflict_handler(), health(), invalid_image_handler(), log_event(), not_found_handler(), ready(), request_context(), RequestIdFilter (+1 more)

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
Cohesion: 0.14
Nodes (26): send_email(), Order, OrderItem, OrderStatus, get_active_shipping_method(), get_order(), list_active_shipping_methods(), list_order_items() (+18 more)

### Community 15 - "Categories.tsx"
Cohesion: 0.20
Nodes (14): listCategories(), listProducts(), toItem(), ItemCard(), Categories(), COLORS, EMPTY_FILTERS, FINENESS (+6 more)

### Community 20 - "cart_service.py"
Cohesion: 0.11
Nodes (37): Cart, CartItem, CartStatus, add_item(), delete_item(), get_active_cart(), get_item(), get_item_by_variant() (+29 more)

### Community 21 - "useLanguage"
Cohesion: 0.13
Nodes (23): M3 — Katalog + i18n (2–3 tygodnie), M3 — Каталог + i18n (2–3 тижні), Реєстр ризиків (топ), App(), ConsentBanner(), Footer(), Header(), CartProvider() (+15 more)

### Community 22 - "routers/admin_catalog.py"
Cohesion: 0.11
Nodes (32): add_gemstone(), create_category(), create_product(), create_variant(), delete_image(), delete_product(), delete_variant(), remove_gemstone() (+24 more)

### Community 23 - "cartApi.ts"
Cohesion: 0.18
Nodes (16): addCartItem(), cartRequest(), clearCartSession(), getCart(), getCartSession(), ownerRequest(), readSession(), removeCartItem() (+8 more)

### Community 25 - "test_admin_catalog.py"
Cohesion: 0.24
Nodes (13): Role, test_events_by_day_counts_new_events(), test_query_limits_validated(), test_requires_admin_role(), test_top_products_counts_and_orders(), _today_count(), _auth(), _png() (+5 more)

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
Cohesion: 0.07
Nodes (36): Settings, score(), build_vectors(), cosine(), _normalize(), profile_vector(), similar(), for_you() (+28 more)

### Community 30 - "Currency"
Cohesion: 0.13
Nodes (42): Base, Category, CategoryTranslation, Gemstone, PriceHistory, Product, ProductEmbedding, ProductGemstone (+34 more)

### Community 31 - "types/index.ts"
Cohesion: 0.15
Nodes (22): AuthContext, CartContext, EMPTY_CART, AuthContextValue, AuthResult, User, Cart, CartLine (+14 more)

### Community 32 - "test_cart.py"
Cohesion: 0.23
Nodes (21): _add(), _guest(), _lines(), _login(), _register_and_login(), test_add_item_uses_server_price(), test_add_over_free_stock_returns_409(), test_add_where_sum_exceeds_stock_returns_409() (+13 more)

### Community 34 - "test_catalog_api.py"
Cohesion: 0.37
Nodes (10): _category(), _now(), _product(), _slugs(), test_category_filter_includes_subcategories(), test_cursor_pages_do_not_overlap(), test_cursor_pagination_by_price(), test_price_filter_uses_active_sale_price() (+2 more)

### Community 35 - "dependencies.py"
Cohesion: 0.21
Nodes (6): require_role(), events_by_day(), top_products(), EventBatchIn, EventCountOut, TopProductOut

### Community 36 - "admin_catalog_service.py"
Cohesion: 0.16
Nodes (26): add_gemstone(), _apply(), _check_parent(), _check_variant_of(), ConflictError, create_category(), create_product(), create_variant() (+18 more)

### Community 37 - "test_recommendations_api.py"
Cohesion: 0.33
Nodes (10): _event(), _product(), test_counts_split_into_two_windows(), test_history_keeps_only_recent_product_events(), _fan_history(), _get(), test_guest_without_history_gets_popularity(), test_history_changes_the_order() (+2 more)

### Community 38 - "auth_service.py"
Cohesion: 0.23
Nodes (22): generate_refresh_token(), hash_refresh_token(), UserStatus, User, is_locked(), UserResponse, AuthError, delete_account() (+14 more)

### Community 39 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 40 - "test_consents.py"
Cohesion: 0.33
Nodes (9): tracking_allowed(), test_consent_creates_missing_profile(), test_consent_defaults_to_false(), test_consent_requires_token_and_bool(), test_grant_consent_persists_and_sets_timestamp(), test_repeated_same_value_keeps_timestamp(), test_tracking_allowed_rule(), test_withdrawal_anonymises_events() (+1 more)

### Community 41 - "post"
Cohesion: 0.20
Nodes (22): delete_me(), forgot_password(), login(), logout(), me(), refresh(), register(), reset_password() (+14 more)

### Community 42 - "test_checkout.py"
Cohesion: 0.20
Nodes (16): checkout(), test_only_one_buyer_gets_the_last_unit(), buyer_a(), buyer_b(), _form(), test_allowed_transitions_cover_every_status(), test_cancel_releases_reserve_and_sets_cancelled_at(), test_cancel_twice_is_rejected() (+8 more)

### Community 43 - "sqlalchemy_orm"
Cohesion: 0.24
Nodes (6): CartOwner, get_cart(), get_cart_owner(), for_you(), similar(), RecommendationOut

### Community 44 - "security.py"
Cohesion: 0.27
Nodes (10): decode_access_token(), hash_password(), _pepper(), _verify(), verify_legacy_password(), verify_password(), test_hash_is_peppered(), test_legacy_hash_is_upgraded_on_login() (+2 more)

### Community 45 - "UserEvent"
Cohesion: 0.24
Nodes (10): SearchQuery, UserEvent, anonymize_older_than(), anonymize_user_events(), bulk_insert_events(), count_events_by_day(), existing_ids(), link_guest_events() (+2 more)

### Community 46 - "config.py"
Cohesion: 0.36
Nodes (7): _login(), _register(), test_account_locks_after_max_failed_attempts(), test_login_sqli_in_password_does_not_bypass_auth(), test_refresh_with_expired_token_is_rejected(), test_refresh_with_revoked_token_is_rejected(), test_successful_login_resets_failed_attempts()

### Community 47 - "order.py"
Cohesion: 0.19
Nodes (7): CheckoutIn, OrderItemOut, ShippingMethodOut, test_courier_address_instead_of_point_is_accepted(), test_invalid_checkout_is_rejected(), test_line_total_is_computed(), test_valid_checkout_is_accepted_and_trimmed()

### Community 48 - "trackingContext.tsx"
Cohesion: 0.19
Nodes (12): EventType, sendEvents(), TrackEvent, TRACKING_HEADER, setAnalyticsConsent(), Consent, readGuestConsent(), TrackingContext (+4 more)

### Community 49 - "Currency"
Cohesion: 0.23
Nodes (8): DeliveryProvider, ShippingMethod, UserAddress, _check_delivery_details(), _shipping_amount(), last_unit(), _method(), test_lists_only_active_methods_cheapest_first()

### Community 50 - "test_payment.py"
Cohesion: 0.26
Nodes (6): _decode_cursor(), _encode_cursor(), signed(), test_duplicate_webhook_no_double_stock(), test_invalid_signature_400(), test_valid_webhook_marks_paid()

### Community 51 - "telemetry_service.py"
Cohesion: 0.25
Nodes (6): EventType, EventIn, events_by_day(), record_events(), _since(), top_products()

### Community 52 - "test_tracking_flows.py"
Cohesion: 0.32
Nodes (12): _checkout(), _events(), _guest_event(), _login(), test_cart_line_has_product_id(), test_guest_checkout_with_consent_records_purchase(), test_guest_checkout_without_consent_records_nothing(), test_login_does_not_link_without_account_consent() (+4 more)

### Community 53 - "import_products.py"
Cohesion: 0.15
Nodes (6): _by_slug(), GemstoneFile, import_all(), main(), ProductFile, VariantFile

### Community 54 - "get_by_email"
Cohesion: 0.40
Nodes (10): get_by_email(), _payload(), test_register_creates_pending_user(), test_register_duplicate_email_does_not_create_a_second_user(), test_register_duplicate_email_is_case_insensitive(), test_register_issues_email_verification_token(), test_register_never_stores_plaintext_password(), test_register_rejects_invalid_email() (+2 more)

### Community 55 - "_setup"
Cohesion: 0.42
Nodes (9): _setup(), _payload(), test_cancel_via_api_and_foreign_cancel_is_404(), test_empty_cart_returns_400(), test_guest_can_fill_a_new_cart_after_checkout(), test_guest_creates_and_reads_own_order(), test_logged_in_user_owns_order_guest_token_and_other_user_do_not(), test_other_guest_gets_404_for_foreign_order() (+1 more)

### Community 56 - "EventType"
Cohesion: 0.33
Nodes (6): _category(), _events(), test_guest_batch_is_stored(), test_link_guest_events(), test_unknown_product_dropped_without_500(), test_validation_rejects_bad_batches()

### Community 57 - "Milestones"
Cohesion: 0.20
Nodes (10): M0 — Стабілізація (1–2 дні), M10 — Впровадження і документація (3–4 тижні, паралельно), M1 — Схема БД і міграції (1–2 тижні), M2 — FastAPI і власна автентифікація (2–3 тижні), M5 — Телеметрія UX + RODO (1–2 тижні), M6 — Класичні алгоритми (2–3 тижні), M7 — Семантичний пошук e5 + pgvector (2–3 тижні, паралельно з M4/M6), M8 — Персоналізація в UI (2 тижні) (+2 more)

### Community 58 - "create_access_token"
Cohesion: 0.21
Nodes (16): create_access_token(), create_user(), create_user_profile(), get_by_id(), register(), _delete(), test_delete_removes_user_anonymises_events_keeps_orders(), test_token_rejected_after_deletion() (+8 more)

### Community 59 - "Product.tsx"
Cohesion: 0.31
Nodes (8): getProductBySlug(), ImageSliderOnHover(), addToCart(), gemstoneName(), Product(), handleAdd(), T, variantLabel()

### Community 60 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.25
Nodes (8): Context, Diploma roadmap — TNDC Jewelry House, Verification, Архітектура (скорочено), Опційні таблиці (лише якщо лишиться час), Перші кроки після затвердження, Порядок і залежності, Прийняті рішення

### Community 61 - "Diploma roadmap — TNDC Jewelry House"
Cohesion: 0.22
Nodes (9): Architektura (skrót), Diploma roadmap — TNDC Jewelry House, Kolejność i zależności, Kontekst, Pierwsze kroki, Przyjęte decyzje, Rejestr ryzyk (najważniejsze), Tabele opcjonalne (tylko jeśli zostanie czas) (+1 more)

### Community 62 - "M4 — задачі (кошик, замовлення, платежі)"
Cohesion: 0.17
Nodes (8): 1. Міграція, 2. Кошик — бекенд, 3. Кошик — фронт, 4. Замовлення — бекенд, 5. Checkout — фронт (без оплати), 7. Закриття M4, M4 — задачі (кошик, замовлення, платежі), Поза M4 (свідомо)

### Community 63 - "create_order"
Cohesion: 0.19
Nodes (6): create_order(), CheckoutError, DeliveryDetailsError, EmptyCartError, OutOfStockError, ShippingMethodNotFoundError

### Community 65 - "dependencies.py"
Cohesion: 0.21
Nodes (5): get_current_user(), get_db(), get_optional_user(), client(), db_session()

### Community 66 - "recommendation_repository.py"
Cohesion: 0.39
Nodes (6): _distinct_array(), event_counts(), _owner(), purchased_product_ids(), user_events_for(), test_history_without_owner_is_empty()

### Community 69 - "admin_catalog_repository.py"
Cohesion: 0.39
Nodes (5): clear_primary_image(), get_price(), list_image_keys(), upsert_category_translation(), upsert_product_translation()

### Community 70 - "get_order"
Cohesion: 0.38
Nodes (3): get_order(), list_orders(), list_shipping_methods()

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CartStatus` connect `cart_service.py` to `str`, `test_cart.py`, `Kamienie milowe`, `enums.py`, `test_checkout.py`, `order_service.py`, `Milestones`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.07563025210084033 - nodes in this community are weakly interconnected._
- **Why does `M4 — задачі (кошик, замовлення, платежі)` connect `M4 — задачі (кошик, замовлення, платежі)` to `str`, `security.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `EventType` (e.g. with `UserEvent` and `event_counts()`) actually correct?**
  _`EventType` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Should `Architecture Workshop (Student-Owned)` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._
- **Why does `3. Кошик — фронт` connect `M4 — задачі (кошик, замовлення, платежі)` to `Categories.tsx`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._