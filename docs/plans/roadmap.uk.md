# Diploma roadmap — TNDC Jewelry House

> Мови: **Українська** (цей файл) · [Polski](roadmap.pl.md)

## Context

Диплом (inż., Informatyka, promotor K. Łapa, R-WIiSI-D.460): *Projekt i implementacja sklepu internetowego z algorytmami personalizacji UX na przykładzie sklepu z biżuterią*. Aspekt badawczy: nie dotyczy → критерій = працююча реалізація + якісний опис алгоритмів; оцінка (M9) інженерна, не наукова.

Поточний стан: фронтенд (Vite/React/TS) не запускається, бекенду немає. Мета плану — послідовність M0–M10 з фіксованими рішеннями D1–D8, щоб на неї спиратись.

Цей файл — канонічна версія плану в репозиторії; польська версія: [roadmap.pl.md](roadmap.pl.md).

## Прийняті рішення

| # | Рішення |
|---|---|
| D1 | Автентифікація власна у FastAPI (argon2id, JWT 15 хв + refresh з ротацією, lockout). Не Supabase Auth. RLS — не межа безпеки |
| D2 | Postgres 16 + pgvector у Docker Compose; Supabase/Neon — опційно для prod |
| D3 | Два ринки: UA (основний: UAH, uk, Нова Пошта, Monobank/LiqPay) і PL (PLN, pl, InPost, Przelewy24/PayU/BLIK, Stripe fallback). Сутність `markets` з першого дня, без `if country ==` |
| D4 | i18n через `product_translations` / `category_translations` |
| D5 | Embeddings: `multilingual-e5-small`, 384d, версіонування (`model_name`, `locale`, `embedding_version`) |
| **D6 (нове)** | **Ціни**: PLN-ціна генерується з курсу (`exchange_rates`) + націнка (на ринок), з можливістю ручного перебиття в `variant_prices` (`is_manual_override`). Ручне значення не перезаписується перерахунком |
| **D7 (нове)** | **Перемикання ринку посеред сесії**: створюється новий кошик на новому ринку, старий лишається `abandoned`/зберігається; без перерахунку |
| **D8 (нове)** | **Мови: UK + PL + EN** (EN обов'язкова). Наслідок: 3 локалі в `product_translations` і до 3 embeddings на товар (M7); seed і переклади ×3 |

Фронтенд ніколи не звертається до БД напряму; весь доступ через FastAPI.

## Архітектура (скорочено)

React/TS (authContext JWT-in-memory + httpOnly refresh cookie, `useTracking`) → FastAPI (Auth, Catalog, Cart/Order, Payment, EventIngestion, Recommendation, SemanticSearch) → Postgres16+pgvector (core, events, vectors/HNSW); окремий `embedder` воркер (e5-small); Object Storage для зображень.

## Порядок і залежності

M0 → M1 → M2 → M3 → {M4, M5, M7 паралельно} ; M5 → M6 ; M6+M7 → M8 → M9 (+M4) → M10.
M7 залежить лише від M3 і може йти паралельно з M4/M6.

## Milestones

### M0 — Стабілізація (1–2 дні)
- Фікс запуску `web/`: відсутній `index.css` у `web/src/main.tsx`; імпорт `cartContext.jsx`→`.tsx` в `web/src/components/ItemCard/ItemCard.jsx`; `useContext(CartContext)` у `web/src/context/cartContext.tsx`.
- `web/src/context/authContext.jsx` — заглушка без Supabase (перепишеться в M2).
- Записати D1–D8 в `docs/architecture.md`; замінити згадки Node.js на FastAPI; оновити `README.md`.
- Експорт DBML → PNG/SVG.
- **DoD**: `cd web && npm run dev` без помилок у консолі на всіх маршрутах; architecture.md актуальний.

### M1 — Схема БД і міграції (1–2 тижні)
- Compose: `postgres` (pgvector), `CREATE EXTENSION vector`; Alembic з першого дня.
- SQLAlchemy-моделі + міграції з DBML, з правками: `markets`, `shipping_methods`, `exchange_rates` (обов'язкова), `variant_prices` (+ `is_manual_override`, `markup_percent` на ринку — D6), `product_translations` (uk/pl/en), `refresh_tokens`, `email_verification_tokens`, `password_reset_tokens`, `user_events`, `search_queries`; `product_embeddings` з PK `(product_id, locale, model_name)`; `products.search_vector` + GIN.
- Узагальнення `user_addresses` (`delivery_provider` enum, `provider_point_id`, `market_id`), `carts.market_id`, `orders` (`market_id`, `shipping_method_id`, `exchange_rate_used`, `session_token`, `locale`, timestamps, `recommendation_influenced`), `order_items.product_id`, `cart_items.unit_price_at_add`, `product_variants.length_mm/reserved_quantity`, `product_gemstones.is_center_stone`, `product_images.alt_text/width/height/storage_key`, enum `Status`→`CartStatus`.
- Всі `*_at` — `DateTime(timezone=True)`. `users.email` — partial unique index `WHERE deleted_at IS NULL` (case-insensitive); те саме для інших unique з soft delete.
- ON DELETE: CASCADE для залежних каталожних/кошикових таблиць; RESTRICT для orders/order_items/payments; SET NULL для nullable `orders.user_id`.
- Тригер `set_updated_at()`; CHECK: stock>=0, price>0, quantity>0, fineness IN (375,500,585,750,875,925,958,999).
- Seed: 2 ринки, категорії, 20–40 товарів, варіанти, ціни UAH + PLN (PLN через D6), камені, переклади uk/pl/en, admin + тестові юзери (Faker + кілька реальних товарів).
- **DoD**: `alembic upgrade head` з нуля; `downgrade -1` працює; seed достатній для демо обох ринків.
- **Deliverable**: розділ «Projekt bazy danych».

### M2 — FastAPI і власна автентифікація (2–3 тижні)
- Структура `api/`: routers, services, repositories, models, schemas, core; Pydantic Settings, `.env.example`; health/readiness, CORS whitelist, structured logging + request-id, глобальний exception handler.
- Auth: argon2id; access JWT 15 хв; refresh з ротацією в `refresh_tokens`; верифікація email; reset через окрему таблицю; lockout (5 спроб + `locked_until`) + rate limit на `/auth/*`; ролі User/Manager/Admin.
- Фронт: `authContext` під власний API (login/register/logout/refresh), access у пам'яті, refresh у httpOnly cookie, protected `/account`.
- **DoD**: реєстрація з верифікацією, вхід/вихід, автоrefresh після reload, lockout, жодних секретів у бандлі.
- **Ризик (високий)**: вразливості → перевірені бібліотеки, OWASP ASVS L1, негативні тести.
- **Deliverable**: «Bezpieczeństwo i uwierzytelnianie» (sequence diagram, argon2, brute force).

### M3 — Каталог + i18n + ринки (2–3 тижні)
- API: `GET /products` (cursor pagination, фільтри: категорія/метал/колір/проба/ціна/камінь/наявність, сортування), `GET /products/{slug}`, `GET /categories` (дерево), admin CRUD + upload зображень (WebP, кілька розмірів).
- i18n: `Accept-Language` + fallback на мову ринку; **PL + UK + EN**; ринок: перемикач у хедері, дефолт з Accept-Language/геолокації, збереження в cookie і `user_profiles.preferred_market_id`.
- Ціни у валюті ринку з `variant_prices`; сервіс перерахунку PLN = UAH-база × курс × (1+націнка), пропускає рядки з `is_manual_override` (D6). Курси: НБУ/НБП.
- Фронт: Categories з API (прибрати `web/src/mockProducts/data.json`), `/products/:slug` з вибором варіанта, Home — нові надходження.
- **DoD**: моки видалені; фільтр «біле золото 585, перстень, до 3000» коректний; зображення оптимізовані.
- **Deliverable**: модуль каталогу + обґрунтування варіантів.

### M4 — Кошик, замовлення, платежі (3–4 тижні)
- Кошик: `session_token` для гостя, `user_id` для залогіненого; merge при вході (кількості сумуються, гостьовий → converted); cartContext на API, у localStorage лише session_token. **Зміна ринку → новий кошик (D7)**.
- Замовлення: snapshot-паттерн; транзакційне зменшення stock з `SELECT … FOR UPDATE` (або `stock_reservations` з TTL); `exchange_rate_used`, статуси з мітками часу.
- Платежі: лише sandbox, жодних карт у БД; абстракція `PaymentProvider` + реєстр доступності за ринком; повністю реалізувати **по одному провайдеру на ринок** (UA: LiqPay/Monobank + Нова Пошта; PL: Przelewy24/PayU + InPost), решта — інтерфейси; webhook з перевіркою підпису; `idempotency_key`.
- **DoD**: гість→реєстрація→кошик злито; замовлення зменшує stock і шле email; sandbox-оплата → Processing; UA = UAH+НП, PL = PLN+InPost, змішати неможливо.
- **Deliverable**: діаграма станів, платежі, ідемпотентність.

### M5 — Телеметрія UX + RODO (1–2 тижні)
- Таблиці `user_events`, `search_queries`; `POST /events` (батч, валідація, throttling); `GET /admin/analytics/*`.
- Фронт: `useTracking()` з батчингом (interval + beforeunload); гість = той самий `session_token`, що й кошик; consent banner **до** трекінгу.
- RODO: використання `consent_*` у `user_profiles`; retention-анонімізація (user_id→NULL); видалення акаунта анонімізує події.
- **DoD**: сесія дає послідовність подій; реєстрація прив'язує попередні події; без згоди трекінгу немає.
- **Deliverable**: «Zbieranie danych o zachowaniu użytkownika».

### M6 — Класичні алгоритми (2–3 тижні)
`api/services/recommendation/`: `content_based.py` (one-hot + нормалізація + cosine), `behavior.py` (ваги view=1, search=1, click_reco=2, fav=3, cart=4, purchase=6; згасання `w·exp(−λ·days)`), `popularity.py` (7/30 днів, нормалізація на вік), `hybrid.py` (`a·behavior + b·content + c·popularity + d·novelty`, коефіцієнти з env), `engine.py`. Бізнес-правила: не показувати відсутнє, вже куплене, різноманітність.
- Ендпоінти: `/recommendations/similar/{product_id}`, `/recommendations/for-you`.
- **DoD**: гість → popularity, користувач з історією → інший результат; коефіцієнти задокументовані.
- **Deliverable**: «Algorytmy klasyczne» (псевдокод, складність, ваги).

### M7 — Семантичний пошук e5 + pgvector (2–3 тижні, паралельно з M4/M6)
- Passage-текст по товару × **3 локалі (uk/pl/en)** з префіксами `query: ` / `passage: `, вербалізація числових характеристик + SQL-фільтри; L2-нормалізація; HNSW `vector_cosine_ops (m=16, ef_construction=64)`, оператор `<=>`; `content_hash` для інкрементного перерахунку.
- `GET /search?q=` — lexical (tsvector+unaccent), semantic, hybrid (RRF, k≈60); кросмовність (запит PL → опис UK).
- «Схожі» з двох джерел (CBF vs vector) — перемикач прапорцем.
- `api/scripts/build_embeddings.py`; embedder як окремий сервіс у Compose; кеш query embedding у `search_queries`; прапорець вимкнення семантики.
- **DoD**: описовий запит релевантний без збігу слів; build перераховує лише змінене; порівняння 3 варіантів задокументовано.
- **Ризики**: RAM 400–600 МБ, латентність 20–80 мс, числа в embedding.
- **Deliverable**: «Wyszukiwanie semantyczne i podobieństwo wektorowe».

### M8 — Персоналізація в UI (2 тижні)
Секції «Polecane dla Ciebie», «Podobne produkty», «Ostatnio przeglądane», «Inni oglądali też»; персоналізований порядок у категоріях; пошук у хедері з autocomplete; `recommendation_cache` з TTL; прапорець `algorithm=cbf|vector|hybrid`; `click_recommendation` з ідентифікатором алгоритму; skeleton-стани.
- **DoD**: гість і користувач з історією бачать різну головну; кожен клік має algorithm id; без layout shift.
- **Deliverable**: інтеграція в UX + скріншоти до/після.

### M9 — Тести, оцінка, аудит (2–3 тижні)
- pytest: юніт (детерміновані ранкінги), інтеграційні (TestClient + тестова БД), негативні auth (протухлий/відкликаний токен, lockout, SQLi), smoke на фронті.
- Оцінка: генератор синтетичних сесій (персони), Precision/Recall/nDCG@K, Coverage, Diversity; popularity vs CBF vs vector vs hybrid + варіанти коефіцієнтів; latency p50/p95.
- Аудит: OWASP Top 10, pip-audit/npm audit, відсутність PII/секретів у логах.
- CI (GitHub Actions): lint + mypy + pytest на push.
- **DoD**: `docs/evaluation.md`; покриття критичних шляхів; CI зелений.
- **Deliverable**: «Testy», «Ewaluacja algorytmów».

### M10 — Впровадження і документація (3–4 тижні, паралельно)
- Deploy: фронт Netlify/Vercel; API+embedder Docker (Railway/Render/Fly/VPS); керований Postgres з pgvector; storage+CDN; HTTPS, домен, бекапи з перевіреним restore; health + моніторинг помилок.
- Юридичні сторінки по ринку: PL детально (regulamin, polityka prywatności, cookies, 14 днів, ціни brutto, RODO-форма), UA оглядово (оферта, політика, повернення).
- Документація ~60–80 стор.: Wstęp; Analiza; Wymagania; Architektura; Implementacja; Algorytmy; Wyszukiwanie semantyczne; Testy; Bezpieczeństwo i RODO; Podsumowanie.
- **DoD**: публічне демо + тег `v1.0-diploma`; README; інструкції user/admin; 10-хв демо-сценарій.
- Правило: 1–2 сторінки чернетки після кожного milestone, скріншоти/діаграми одразу.

## Опційні таблиці (лише якщо лишиться час)
`recommendation_cache` (потрібна для M8), `stock_reservations` (за вибором в M4), `audit_log`, `product_reviews`, `coupons`+`coupon_redemptions`, `product_collections`, `ab_experiments`.

## Реєстр ризиків (топ)
- Надмірний обсяг (висока/високий) → жорсткий MVP на milestone, лише sandbox, coupons/reviews/ab — по залишку часу.
- Подвійна складність двох ринків + 3 мов (висока/високий) → `markets` з першого дня; PL «мінімально повний».
- Відкладання тексту роботи (висока/високий) → чернетки після кожного milestone.
- Розходження коду/схеми → Alembic, без ручних правок.
- Власна auth (середня/високий) → бібліотеки, ASVS, негативні тести.
- RODO для телеметрії → consent, анонімізація, retention.
- Overselling → FOR UPDATE / резервації.
- Холодний старт → popularity + семантичний fallback + синтетичні сесії.

## Перші кроки після затвердження
1. M0: `index.css`, імпорт/`useContext` cartContext, заглушка authContext.
2. Записати D1–D8 в `docs/architecture.md`, оновити `README.md`; скопіювати цей план в `docs/roadmap.md`.
3. Оновити DBML (markets, variant_prices + override, shipping_methods, exchange_rates, delivery_provider, translations uk/pl/en).
4. Старт M1: compose з pgvector, Alembic, перша міграція (markets/users/user_profiles/categories/products/product_variants/variant_prices).

## Verification
- M0: `npm run dev`, пройти всі маршрути, консоль чиста.
- Для кожного milestone — DoD вище; наскрізно: `alembic upgrade head && alembic downgrade -1`, `pytest`, CI зелений, демо-сценарій M10.
