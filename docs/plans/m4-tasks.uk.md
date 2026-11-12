# M4 — задачі (кошик, замовлення, платежі)

> Детальний опис milestone: [roadmap.uk.md](roadmap.uk.md#m4--кошик-замовлення-платежі-34-тижні). Виконувати по порядку; кожна задача — окремий коміт.

## 0. Підготовка

- [ ] **T0.1 — `price_history` у seed.** Адмінський `set_price` ([admin_catalog_service.py:175](../../api/app/services/admin_catalog_service.py#L175)) та імпорт ([import_products.py:104](../../api/scripts/import_products.py#L104)) вже пишуть історію цін. А [seed.py:503](../../api/scripts/seed.py#L503) створює `VariantPrice` напряму, тому після seed таблиця `price_history` порожня. Виправлення: у seed замість прямого `VariantPrice(...)` викликати `svc.set_price(...)` або поруч додати `PriceHistory(...)`.
- [ ] **T0.2 — backfill для вже засіяної БД** (одноразовий SQL, виконати вручну):
  ```sql
  INSERT INTO price_history (variant_id, currency, price)
  SELECT vp.variant_id, vp.currency, vp.price
  FROM variant_prices vp
  WHERE NOT EXISTS (
    SELECT 1 FROM price_history ph
    WHERE ph.variant_id = vp.variant_id AND ph.currency = vp.currency
  );
  ```
- [ ] **T0.3 — тест:** після seed у кожного `variant_prices` є хоча б один рядок у `price_history`.
- [x] **T0.4 — оновити `CLAUDE.md`:** прибрати ринок PL, `markets`, Przelewy24/InPost і bcrypt; узгодити з D1/D3/D6/D8.
- [ ] **T0.5 — pepper для паролів.** Сіль уже є: `argon2-cffi` генерує випадкову сіль для кожного хеша. Перцю в [security.py](../../api/app/core/security.py) немає.
  - `Settings.password_pepper` (обов'язковий секрет з env, ≥32 байти); у `.env.example` — лише плейсхолдер. У БД перець не зберігати.
  - `hash_password` / `verify_password`: `argon2(HMAC-SHA256(pepper, password))`; `DUMMY_PASSWORD_HASH` теж рахувати з перцем.
  - Старі хеші без перцю: у `login` спершу перевірити з перцем; якщо не підійшов — перевірити без перцю і при успіху одразу перехешувати з перцем. Альтернатива для dev: перезасіяти БД і нічого не мігрувати.
  - Тести: hash/verify з перцем; хибний перець → відмова; старий хеш після логіну стає хешем з перцем.

## 1. Міграція

- [ ] **T1.1 — Alembic `0004`:**
  - частковий unique `carts(user_id) WHERE status='Active'`;
  - unique `payments(provider, external_id)`;
  - sequence `order_number_seq`.
- [ ] **T1.2 —** перевірити `upgrade head` → `downgrade -1` → `upgrade head`.

## 2. Кошик — бекенд

- [ ] **T2.1 —** `schemas/cart.py`: `CartItemIn {variant_id, quantity}`, `CartOut` (рядки, `subtotal`, `currency`).
- [ ] **T2.2 —** `repositories/cart_repository.py`: знайти/створити активний кошик за `user_id` або `session_token`; операції з рядками.
- [ ] **T2.3 —** `services/cart_service.py`: add / update / remove з перевіркою `quantity <= stock - reserved` і ціною з `variant_prices` (`unit_price_at_add`).
- [ ] **T2.4 —** `routers/cart.py`: `GET /cart`, `POST /cart/items`, `PATCH /cart/items/{id}`, `DELETE /cart/items/{id}`. Гостя визначаємо за заголовком `X-Cart-Session`; якщо його немає, генеруємо `secrets.token_urlsafe` і повертаємо.
- [ ] **T2.5 —** `cart_service.merge(guest_token, user_id)`: кількості сумуються з обмеженням до stock, гостьовий кошик стає `Converted`. Викликати з `auth_service.login`.
- [ ] **T2.6 —** тести: CRUD кошика, ліміт stock, merge.

## 3. Кошик — фронт

- [ ] **T3.1 —** `web/src/api/cartApi.ts` (+ заголовок `X-Cart-Session`).
- [ ] **T3.2 —** переписати `cartContext.tsx` на API. У localStorage лишається тільки `cartSession`.
- [ ] **T3.3 —** «Додати в кошик» на сторінці товару передає `variant_id`; узгодити тип `Item` / `CartLine`.
- [ ] **T3.4 —** перечитувати кошик після login/logout; `/auth/login` надсилає `X-Cart-Session`.
- [ ] **T3.5 —** ручна перевірка: гість додає товар → вхід → кошик злито.

## 4. Замовлення — бекенд

- [ ] **T4.1 —** `GET /shipping-methods`.
- [ ] **T4.2 —** `schemas/order.py`: `CheckoutIn` (отримувач, телефон, email, `shipping_method_id`, місто, відділення НП, коментар), `OrderOut`.
- [ ] **T4.3 —** `services/order_service.checkout()` в одній транзакції:
  1. `FOR UPDATE` на варіанти, відсортовані за id;
  2. перевірка наявності, при нестачі → 409;
  3. snapshot `order_items`;
  4. `reserved_quantity += qty`;
  5. доставка з урахуванням `free_from_amount`;
  6. кошик → `Converted`.
- [ ] **T4.4 —** `core/email.py: send_email()` — поки що лише лог, як в auth; лист «замовлення створено».
- [ ] **T4.5 —** `POST /orders`, `GET /orders`, `GET /orders/{order_number}` (гість — за `session_token`).
- [ ] **T4.6 —** `ALLOWED_TRANSITIONS` (dict статусів) + `POST /orders/{n}/cancel`, який знімає резерв і заповнює `cancelled_at`.
- [ ] **T4.7 —** тести:
  - checkout: snapshot і зростання reserved;
  - 409 при нестачі товару;
  - конкурентна покупка останньої одиниці;
  - cancel.

## 5. Checkout — фронт (без оплати)

- [ ] **T5.1 —** `web/src/api/orderApi.ts`.
- [ ] **T5.2 —** сторінка `/checkout`: форма, вибір доставки, підсумок; кнопка Checkout у [Cart.tsx](../../web/src/pages/Cart.tsx) веде на неї.
- [ ] **T5.3 —** сторінка `/orders/:number` (статус) + список замовлень в `/account`.
- [ ] **T5.4 —** ключі перекладу uk / pl / en.

## 6. Платежі (sandbox)

- [ ] **T6.1 —** `services/payments/base.py`: Protocol `PaymentProvider` (`create_checkout`, `verify_webhook`).
- [ ] **T6.2 —** `services/payments/liqpay.py` (sandbox) + `LIQPAY_PUBLIC_KEY` / `LIQPAY_PRIVATE_KEY` у `.env.example`.
- [ ] **T6.3 —** `POST /orders/{n}/pay` із заголовком `Idempotency-Key`: повторний запит повертає той самий `payments`; у відповіді redirect URL.
- [ ] **T6.4 —** `POST /payments/webhook/liqpay`:
  - невалідний підпис → 400;
  - платіж уже `Succeeded` → 200 без змін;
  - успіх → `Paid` → `Processing`, `stock -= qty`, `reserved -= qty`, лист «оплачено»;
  - помилка → платіж `Failed`.
- [ ] **T6.5 —** фронт: «Оплатити» → redirect; після повернення — `/orders/:number`.
- [ ] **T6.6 —** тести webhook: валідний, невалідний, дубль; повторний `Idempotency-Key`.
- [ ] **T6.7 —** наскрізна перевірка через LiqPay sandbox + `ngrok http 8000`.
- [ ] *(опційно)* `monobank.py` — лише якщо лишиться час.

## 7. Закриття M4

- [ ] **T7.1 —** DoD:
  - гість → реєстрація → кошик злито;
  - замовлення зменшує stock і шле email;
  - sandbox-оплата → `Processing`.
- [ ] **T7.2 —** `pytest` зелений, `npm run lint` чистий, Swagger `/docs` показує нові ендпоінти.
- [ ] **T7.3 —** документація польською: діаграма станів Order/Payment, sequence checkout → LiqPay → webhook, ідемпотентність, `FOR UPDATE` проти overselling.
- [ ] **T7.4 —** ✅ M4 у `roadmap.uk.md` / `roadmap.pl.md`; `graphify update .`.

## Поза M4 (свідомо)

Справжній SMTP, довідник відділень Нової Пошти, `stock_reservations` з TTL і автоскасування неоплачених замовлень. Без автоскасування резерв неоплаченого замовлення знімається лише ручним cancel.
