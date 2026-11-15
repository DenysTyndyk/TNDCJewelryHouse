# M5 — задачі (телеметрія UX + RODO)

> Детальний опис milestone: [roadmap.uk.md](roadmap.uk.md#m5--телеметрія-ux--rodo-12-тижні). Виконувати по порядку; кожна задача — окремий коміт.

## Вже є (не робити повторно)

- Таблиці `user_events`, `search_queries` з індексами (міграція `0002`), моделі в [telemetry.py](../../api/app/models/telemetry.py), enum `EventType`.
- `user_events.user_id` → `ON DELETE SET NULL`, тож видалення акаунта вже відв'язує події.
- Гостьовий `session_token` = `X-Cart-Session`, власник запиту — `get_cart_owner` у [cart.py](../../api/app/routers/cart.py#L32).
- Throttling — `limiter` (slowapi) у [limiter.py](../../api/app/core/limiter.py).

## Рішення (зафіксувати перед стартом)

- **Окрема згода на аналітику.** `consent_personal_data` — це згода на обробку даних для замовлення/акаунта, а трекінг для персоналізації — інша мета (RODO, art. 6/7: окрема, добровільна, відкликувана). Тому нова колонка `consent_analytics`.
- **Хто вирішує, чи можна трекати:**
  - залогінений → `user_profiles.consent_analytics` (джерело правди, з `consent_updated_at`);
  - гість → заголовок `X-Tracking-Consent: granted`, який фронт шле лише після згоди в банері.
- **Без згоди подій не буде взагалі** — ні в черзі на фронті, ні в БД. Не «збираємо, а потім фільтруємо».
- **`Purchase` пише бекенд** у `order_service.checkout()` (не фронт): так подія достовірна. Поки немає оплати (перенесено в M8) — це момент створення замовлення.
- **`created_at` ставить сервер**, час клієнта не довіряємо.
- `Search` і `search_queries` — у M7 (там з'явиться пошук), `ClickRecommendation` — у M8, `AddToFavorites` — коли з'являться обрані.

## 1. Міграція

- [x] **T1.1 — Alembic `0005`:** `user_profiles.consent_analytics boolean not null default false`; оновити [schema.dbml](../schema.dbml) і модель `UserProfile`.
- [x] **T1.2 —** перевірити `upgrade head` → `downgrade -1` → `upgrade head`.

## 2. Згода — бекенд

- [x] **T2.1 —** `PATCH /auth/me/consents {analytics: bool}` → оновлює `consent_analytics` + `consent_updated_at`; `UserResponse` повертає поточне значення.
- [x] **T2.2 —** `services/telemetry_service.tracking_allowed(user, consent_header) -> bool` — одне місце з правилом «залогінений → профіль, гість → заголовок».
- [x] **T2.3 —** *(RODO)* при відкликанні згоди залогіненим — анонімізувати його вже зібрані події (`user_id = NULL`, `session_token = NULL`).

## 3. Події — бекенд

- [x] **T3.1 —** `schemas/telemetry.py`: `EventIn {event_type, product_id?, variant_id?, category_id?, metadata?, source?}`, `EventBatchIn {events: list[EventIn]}`:
  - максимум 50 подій у батчі;
  - `metadata` — плаский dict, ≤ 1 КБ у JSON (захист від сміття в JSONB);
  - `event_type` лише з `EventType`; `Purchase` з клієнта відхиляти (його пише бекенд).
- [x] **T3.2 —** `repositories/telemetry_repository.py`: `bulk_insert_events`, `filter_existing_ids` (одним запитом відкинути неіснуючі `product_id` / `variant_id` / `category_id`, щоб FK не давав 500).
- [x] **T3.3 —** `POST /events` → 204:
  - власник — `get_cart_owner` (той самий `session_token`, що й кошик);
  - без згоди → 403;
  - `@limiter.limit("30/minute")`.
- [x] **T3.4 —** `Purchase` у `order_service.checkout()`: по одній події на рядок замовлення (`product_id`, `variant_id`), лише якщо `tracking_allowed`; у тій самій транзакції. Фронт шле `X-Tracking-Consent` у `createOrder`.
- [x] **T3.5 —** прив'язка гостьових подій при вході: у `auth_service.login` поруч із `_merge_guest_cart` — `UPDATE user_events SET user_id = :uid WHERE session_token = :token AND user_id IS NULL` (лише якщо в користувача `consent_analytics`).

## 4. RODO — видалення та retention

- [x] **T4.1 —** `DELETE /auth/me` (з підтвердженням паролем): спершу анонімізувати події (`session_token = NULL` — інакше їх можна знову зв'язати), потім видалити користувача (каскади вже є: кошики, профіль, токени; `orders.user_id → NULL`). Відкликати refresh-токени, очистити cookie.
- [x] **T4.2 —** `Settings.event_retention_days` (наприклад 365) + `api/scripts/anonymize_events.py`: для подій і `search_queries`, старших за N днів, `user_id = NULL`, `session_token = NULL`. Запуск вручну / cron.

## 5. Аналітика для адміна

- [x] **T5.1 —** `GET /admin/analytics/events?days=30` — кількість подій за типом і днем (`require_role(Manager, Admin)`).
- [x] **T5.2 —** `GET /admin/analytics/top-products?event_type=ProductView&days=30&limit=20`.
- [x] **T5.3 —** перевірити `EXPLAIN ANALYZE` обох запитів — < 500 мс (індекси `(product_id, event_type)`, `(user_id, created_at)` вже є; за потреби — індекс на `created_at`).

## 6. Фронт

- [x] **T6.1 —** `ConsentBanner.tsx`: «Погоджуюсь» / «Відмовитись», без попередньо поставлених галочок; вибір у localStorage `trackingConsent` (`granted` / `denied`); для залогіненого — ще й `PATCH /auth/me/consents`. Банер показується, поки вибору немає.
- [x] **T6.2 —** перемикач згоди в `/account` (відкликати так само легко, як дати).
- [x] **T6.3 —** `web/src/api/telemetryApi.ts` + `useTracking()`:
  - черга в пам'яті, flush кожні 10 с або при 20 подіях;
  - flush при `visibilitychange → hidden` / `pagehide` через `fetch(..., {keepalive: true})` (`beforeunload` ненадійний на мобільних; `sendBeacon` не вміє заголовки);
  - без згоди `track()` нічого не робить і нічого не буферизує;
  - заголовки: `X-Cart-Session`, `Authorization`, `X-Tracking-Consent`.
- [x] **T6.4 —** підключити події: `ProductView` (сторінка товару), `CategoryView` (категорія), `AddToCart` / `RemoveFromCart` (`cartContext`), `FilterApply` (фільтри каталогу).
- [x] **T6.5 —** згода після логіну: рішення акаунта остаточне, якщо є `consent_updated_at` (віддається в `/auth/me`); акаунт без рішення → банер знову. Локальна згода гостя **не** переноситься автоматично — інакше відкликання на іншому пристрої тихо відновилось би (art. 7 ust. 3).
- [x] **T6.6 —** ключі перекладу uk / pl / en (банер, `/account`); посилання на політику конфіденційності (сама сторінка — M10).

## 7. Тести

- [x] **T7.1 —** `POST /events`: валідний батч зберігається; > 50 подій → 422; `Purchase` з клієнта → 422; великий `metadata` → 422; неіснуючий `product_id` відкинуто без 500.
- [x] **T7.2 —** згода: гість без заголовка → 403; залогінений з `consent_analytics = false` → 403 навіть із заголовком.
- [x] **T7.3 —** throttling → 429.
- [x] **T7.4 —** `Purchase` після checkout пишеться лише за згоди.
- [x] **T7.5 —** вхід прив'язує гостьові події; без згоди — не прив'язує.
- [x] **T7.6 —** `DELETE /auth/me`: подій більше не знайти ні за `user_id`, ні за `session_token`; замовлення лишились.
- [x] **T7.7 —** retention-скрипт анонімізує лише старі події.

## 8. Закриття M5

- [ ] **T8.1 —** DoD:
  - сесія дає послідовність подій;
  - реєстрація (перший вхід) прив'язує попередні події;
  - без згоди трекінгу немає.
- [ ] **T8.2 —** `pytest` зелений, `npm run lint` чистий, Swagger `/docs` показує нові ендпоінти.
- [x] **T8.3 —** документація польською: «Zbieranie danych o zachowaniu użytkownika» — типи подій і ваги для M6, схема згоди, анонімізація/retention, правова основа (RODO art. 6 ust. 1 lit. a, art. 7 ust. 3, art. 17) → [telemetria.pl.md](../telemetria.pl.md). Лишилось вставити результати `EXPLAIN ANALYZE` з T5.3.
- [ ] **T8.4 —** ✅ M5 у `roadmap.uk.md` / `roadmap.pl.md`; `graphify update .`.

## Поза M5 (свідомо)

Події `Search` / `search_queries` (M7), `ClickRecommendation` з `source` (M8), `AddToFavorites` (коли будуть обрані), окрема таблиця історії згод (зараз лише останній стан + `consent_updated_at`), експорт даних користувача (RODO art. 20).
