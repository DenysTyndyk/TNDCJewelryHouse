# Graph Report - api  (2026-11-11)

## Corpus Check
- 37 files · ~11,022 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .ini 1, .mako 1)

## Summary
- 310 nodes · 939 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b4a402b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- user_repository.py
- Base
- enums.py
- main.py
- catalog_service.py
- routers/auth.py
- test_auth_flows.py
- test_auth_negative.py
- get_by_email
- env.py
- API — baza danych i migracje (Milestone 1)

## God Nodes (most connected - your core abstractions)
1. `Base` - 34 edges
2. `Currency` - 20 edges
3. `User` - 17 edges
4. `hash_refresh_token()` - 14 edges
5. `list_products()` - 14 edges
6. `get_by_email()` - 14 edges
7. `login()` - 12 edges
8. `seed_products()` - 12 edges
9. `login()` - 11 edges
10. `ProductFilter` - 11 edges

## Surprising Connections (you probably didn't know these)
- `seed_users()` --uses--> `Role`  [INFERRED]
  scripts/seed.py → app/models/enums.py
- `seed_users()` --uses--> `UserStatus`  [INFERRED]
  scripts/seed.py → app/models/enums.py
- `test_refresh_reuse_outside_grace_window_revokes_all_sessions()` --uses--> `RefreshToken`  [INFERRED]
  tests/test_auth_flows.py → app/models/user.py
- `test_register_issues_email_verification_token()` --uses--> `EmailVerificationToken`  [INFERRED]
  tests/test_auth_register.py → app/models/user.py
- `test_refresh_reuse_outside_grace_window_revokes_all_sessions()` --calls--> `hash_refresh_token()`  [EXTRACTED]
  tests/test_auth_flows.py → app/core/security.py

## Import Cycles
- None detected.

## Communities (15 total, 4 thin omitted)

### Community 0 - "user_repository.py"
Cohesion: 0.12
Nodes (41): create_access_token(), decode_access_token(), generate_refresh_token(), hash_password(), hash_refresh_token(), verify_password(), EmailVerificationToken, PasswordResetToken (+33 more)

### Community 1 - "Base"
Cohesion: 0.14
Nodes (34): Base, get_session(), Category, CategoryTranslation, Gemstone, PriceHistory, Product, ProductEmbedding (+26 more)

### Community 2 - "enums.py"
Cohesion: 0.10
Nodes (17): downgrade(), upgrade(), require_role(), Payment, CartStatus, DeliveryProvider, EventType, OrderStatus (+9 more)

### Community 3 - "main.py"
Cohesion: 0.07
Nodes (10): get_current_user(), get_db(), health(), log_event(), ready(), request_context(), RequestIdFilter, unhandled_exception_handler() (+2 more)

### Community 4 - "catalog_service.py"
Cohesion: 0.13
Nodes (23): MetalColor, MetalType, get_product(), list_categories(), list_products(), CategoryNode, ImageOut, ProductDetail (+15 more)

### Community 5 - "routers/auth.py"
Cohesion: 0.22
Nodes (17): forgot_password(), login(), logout(), me(), refresh(), register(), reset_password(), _set_refresh_cookie() (+9 more)

### Community 6 - "test_auth_flows.py"
Cohesion: 0.23
Nodes (11): _extract_token_from_log(), _login(), _register(), test_login_is_rate_limited(), test_me_returns_current_user(), test_refresh_reuse_outside_grace_window_revokes_all_sessions(), test_refresh_rotates_the_token_and_issues_a_new_access_token(), test_reset_password_changes_password_and_revokes_sessions() (+3 more)

### Community 7 - "test_auth_negative.py"
Cohesion: 0.23
Nodes (8): Settings, _login(), _register(), test_account_locks_after_max_failed_attempts(), test_login_sqli_in_password_does_not_bypass_auth(), test_refresh_with_expired_token_is_rejected(), test_refresh_with_revoked_token_is_rejected(), test_successful_login_resets_failed_attempts()

### Community 8 - "get_by_email"
Cohesion: 0.40
Nodes (10): get_by_email(), _payload(), test_register_creates_pending_user(), test_register_duplicate_email_does_not_create_a_second_user(), test_register_duplicate_email_is_case_insensitive(), test_register_issues_email_verification_token(), test_register_never_stores_plaintext_password(), test_register_rejects_invalid_email() (+2 more)

### Community 9 - "env.py"
Cohesion: 0.47
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 10 - "API — baza danych i migracje (Milestone 1)"
Cohesion: 0.33
Nodes (5): API — baza danych i migracje (Milestone 1), Decyzje odzwierciedlone w schemacie, Kolejność migracji, Lista kontrolna dla wygenerowanej migracji `0002`, Uruchomienie

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Base` connect `Base` to `user_repository.py`, `env.py`, `enums.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Currency` (e.g. with `PriceHistory` and `VariantPrice`) actually correct?**
  _`Currency` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `user_repository.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11611030478955008 - nodes in this community are weakly interconnected._
- **Why does `User` connect `user_repository.py` to `get_by_email`, `Base`, `enums.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `User` (e.g. with `Role` and `UserStatus`) actually correct?**
  _`User` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `Base` be split into smaller, more focused modules?**
  _Cohesion score 0.14153561517113783 - nodes in this community are weakly interconnected._
- **Should `enums.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0966183574879227 - nodes in this community are weakly interconnected._