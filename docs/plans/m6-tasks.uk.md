# M6 — задачі (класичні алгоритми рекомендацій)

> Детальний опис milestone: [roadmap.uk.md](roadmap.uk.md#m6--класичні-алгоритми-23-тижні). Виконувати по порядку; кожна задача — окремий коміт.
>
> Шлях модуля: `api/app/services/recommendation/` (у roadmap скорочено до `api/services/…`). Без нових залежностей: каталог малий, вектори рахуємо в чистому Python (`dict` / `math`), numpy не додаємо.

## 0. Підготовка

- [ ] **T0.1 — коефіцієнти в `Settings`** ([config.py](../../api/app/core/config.py)): `reco_weight_behavior` / `content` / `popularity` / `novelty` (a, b, c, d), `reco_decay_lambda` (λ), `reco_popularity_window_days` (7/30), `reco_limit` (дефолт 12). Плейсхолдери з дефолтами — у `.env.example`.
- [ ] **T0.2 — ваги подій** як константа `EVENT_WEIGHTS` (`ProductView=1, Search=1, ClickRecommendation=2, AddToFavorites=3, AddToCart=4, Purchase=6`) — у коді, не в env: це частина алгоритму, а не тюнінг.
- [ ] **T0.3 — перевірити дані:** у `user_events` для `Search` немає `product_id` → вирішити, як його зараховувати (напр., лише якщо подія має `product_id` у payload, інакше пропускати). Зафіксувати рішення коментарем у `behavior.py`.

## 1. Репозиторій

- [ ] **T1.1 —** `repositories/recommendation_repository.py`:
  - `load_product_features()` — одним запитом: id, `category_id`, `published_at`, мульти-набори `metal_type` / `metal_color` / `fineness` / `gemstone_id` по варіантах, мін. ціна з `variant_prices`, `available = sum(stock - reserved) > 0`. Лише опубліковані товари;
  - `user_events_for(user_id | session_token, since)` — `(product_id, event_type, created_at)`;
  - `event_counts_since(days)` — `product_id → кількість` (агрегація в SQL);
  - `purchased_product_ids(user_id)` — з `order_items` неcкасованих замовлень.
- [ ] **T1.2 — індекси:** перевірити `EXPLAIN ANALYZE` для запитів T1.1 (ліміт 500 мс). Якщо бракує індексу `user_events(product_id, created_at)` — Alembic `0006` (+ `downgrade`).

## 2. Content-based

- [ ] **T2.1 —** `content_based.py: build_vectors(features)` — one-hot / multi-hot для категорії, металу, кольору, проби, каменів; ціна → min-max у [0, 1]; L2-нормалізація вектора.
- [ ] **T2.2 —** `cosine(a, b)` (на нормалізованих — скалярний добуток по спільних ключах) + `similar(product_id, k)`.
- [ ] **T2.3 —** `profile_vector(weighted_products)` — зважена сума векторів товарів користувача (для гібрида).
- [ ] **T2.4 —** тести: однакові атрибути → 1.0; без спільних → 0; товар не повертає сам себе.

## 3. Behavior

- [ ] **T3.1 —** `behavior.py: score(events, now)` — `Σ w(type)·exp(−λ·days)` по товару.
- [ ] **T3.2 —** тести: свіжа подія важить більше за стару; `Purchase` > `ProductView`; λ=0 → без згасання.

## 4. Popularity

- [ ] **T4.1 —** `popularity.py: score(counts_7, counts_30, published_at, now)` — зважена сума вікон 7/30 днів, поділена на вік товару (`max(age_days, 1)`, обмежений вікном, щоб нові товари не вибухали). Нормалізація в [0, 1].
- [ ] **T4.2 —** тести: більше подій → вище; молодший товар з тією ж кількістю → вище.

## 5. Hybrid + бізнес-правила

- [ ] **T5.1 —** `hybrid.py: combine()` — кожну компоненту нормалізувати в [0, 1], потім `a·behavior + b·content + c·popularity + d·novelty`; `novelty` — від `published_at` (новіше → ближче до 1).
- [ ] **T5.2 —** `rules.py` (або в `engine.py`): прибрати `available = false`, уже куплене, поточний товар; різноманітність — не більше N товарів однієї категорії в топ-K (жадібний прохід по відсортованому списку).
- [ ] **T5.3 —** тести: відсутні та куплені не потрапляють; ліміт на категорію дотримано; при `a=b=d=0` результат = popularity.

## 6. Engine + ендпоінти

- [ ] **T6.1 —** `engine.py`:
  - `similar(product_id)` → content-based + правила;
  - `for_you(user_id | session_token)` → без історії (гість без подій) — popularity; з історією — hybrid.
  - Згода (RODO): якщо `tracking_allowed` = false — історію не використовувати, лише popularity.
- [ ] **T6.2 —** `schemas/recommendation.py`: `RecommendationOut {algorithm, items: [ProductCard]}` — перевикористати картку товару з каталогу (ціна, primary image, назва за `resolve_locale`).
- [ ] **T6.3 —** `routers/recommendations.py`: `GET /recommendations/similar/{product_id}`, `GET /recommendations/for-you` (гість — за `X-Cart-Session`, як у кошику; користувач — опційний JWT). 404 на неіснуючий товар. Підключити в `main.py`, перевірити `/docs`.
- [ ] **T6.4 —** інтеграційні тести:
  - гість без історії → `algorithm = "popularity"`;
  - користувач з історією → інший порядок, ніж у гостя (**DoD**);
  - `similar` не містить сам товар і відсутні;
  - без згоди → popularity.
- [ ] **T6.5 —** latency: заміряти обидва ендпоінти на засіяній БД (< 500 мс). Кеш не робимо — `recommendation_cache` з TTL у M8.

## 7. Закриття M6

- [ ] **T7.1 —** DoD: гість → popularity; користувач з історією → інший результат; коефіцієнти задокументовані.
- [ ] **T7.2 —** `pytest` зелений, Swagger `/docs` показує нові ендпоінти.
- [ ] **T7.3 —** документація польською «Algorytmy klasyczne»: псевдокод кожного алгоритму, складність (O(P·F) для побудови векторів, O(P) на запит similar, O(E) для behavior), таблиця ваг і коефіцієнтів з обґрунтуванням дефолтів.
- [ ] **T7.4 —** ✅ M6 у `roadmap.uk.md` / `roadmap.pl.md`; `graphify update .`.

## Поза M6 (свідомо)

Фронт-секції рекомендацій, `recommendation_cache`, прапорець `algorithm=cbf|vector|hybrid`, `click_recommendation` з algorithm id — усе M8. Векторна схожість (e5 + pgvector) — M7. Метрики якості (Precision/nDCG) і підбір коефіцієнтів — M9.
