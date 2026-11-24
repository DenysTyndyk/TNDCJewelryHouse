# M7 — Семантичний пошук e5 + pgvector: план задач

Джерело: `docs/plans/roadmap.uk.md`, розділ M7.

## Що вже є (не робити)
- `product_embeddings` (PK `product_id, locale, model_name`, `content_hash`, `embedding_version`) і HNSW-індекс `vector_cosine_ops (m=16, ef_construction=64)`, див. `api/alembic/versions/0002_core_schema.py`.
- `products.search_vector` (TSVECTOR) з GIN-індексом. Її поки ніхто не заповнює.
- `search_queries.query_embedding` для кешу запитів і enum `SearchType` (Lexical / Semantic / Hybrid).
- `list_products(db, filters, currency, ids=...)` вже фільтрує за списком id. Її беремо для SQL-фільтрів пошуку.

## Чого бракує
- розширення `unaccent` і text search config;
- сервісу embedder і залежності для моделі;
- скрипта build, `/search`, прапорців, «схожих» через вектори, оцінки якості, документа.

---

## T1. Міграція 0008: unaccent і text search config
1. `CREATE EXTENSION IF NOT EXISTS unaccent`.
2. Створити конфігурацію `tndc_search` як `COPY = simple`. У Postgres немає словника для української, а `simple` однаковий для всіх трьох мов.
3. `ALTER TEXT SEARCH CONFIGURATION tndc_search ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple`.
4. `downgrade()` видаляє конфігурацію, розширення залишається (як `vector` у 0001).
5. Додати нотатку про конфігурацію в `docs/schema.dbml`.

**Перевірка:** `SELECT to_tsvector('tndc_search', 'Złoty pierścionek')` повертає токени без діакритики.

## T2. Embedder як окремий сервіс у Compose
1. Тека `embedder/`: `Dockerfile`, `requirements.txt` (`fastapi`, `uvicorn`, `sentence-transformers`), `main.py`.
2. Модель `intfloat/multilingual-e5-small` завантажується один раз під час старту.
3. `POST /embed` приймає `{"texts": [...], "kind": "query" | "passage"}` і повертає `{"vectors": [[384 floats], ...]}`.
   - Префікс `query: ` або `passage: ` додає сам сервіс, щоб API не міг про нього забути.
   - `model.encode(..., normalize_embeddings=True)` дає L2-нормалізацію, тож `<=>` рахує чисту косинусну відстань.
4. `GET /health`.
5. У `docker-compose.yml`: сервіс `embedder`, volume для кешу HuggingFace, `mem_limit: 1g` (ризик RAM 400–600 МБ), `EMBEDDER_URL: http://embedder:8001` в api.

**Перевірка:** `curl -X POST localhost:8001/embed ...` повертає вектор довжиною 384 з нормою ≈ 1.0.

## T3. Налаштування і клієнт embedder в API
1. Нові поля в `Settings` (`api/app/core/config.py`):
   - `embedder_url: str`;
   - `embedding_model: str = "intfloat/multilingual-e5-small"`;
   - `embedding_version: int = 1`;
   - `semantic_search_enabled: bool = True` (прапорець вимкнення семантики);
   - `similar_source: Literal["cbf", "vector"] = "cbf"` (перемикач «схожих»);
   - `search_rrf_k: int = 60`.
2. Додати в `.env.example` і в `environment` сервісів api та jobs.
3. `api/app/services/search/embedder_client.py`: `embed(texts, kind) -> list[list[float]]` через `httpx` (вже в залежностях), таймаут ~2 с. Коли сервіс упав або повернув помилку, кидає `EmbedderUnavailable`.

## T4. Passage-текст і вербалізація чисел
Файл `api/app/services/search/passage.py`, функція `build_passage(product, translation, category_name, variants, gemstones, locale) -> str`.
1. Структура: `назва. категорія. опис. метал, колір, проба. вага. камені.`
2. Числа вербалізувати з одиницями і словами окремо для кожної локалі. Наприклад, `585` дає «проба 585, золото 14 карат», вага дає «вага 3,2 г, легкий» (пороги на зразок «легкий» < 2 г, «масивний» > 8 г). E5 погано розуміє голі числа (ризик «числа в embedding»).
3. Ціну в passage не додавати. Вона змінюється і фільтрується в SQL.
4. `content_hash = sha256(f"{model}|{version}|{passage}")`, тож зміна моделі або версії сама запускає перерахунок.
5. Тест: однаковий вхід дає однаковий hash, змінений опис змінює hash, для `pl` у тексті польські слова.

## T5. Скрипт `api/scripts/build_embeddings.py`
1. Завантажити опубліковані товари з перекладами `uk`, `pl`, `en`. Можна взяти `load_product_features`, якщо полів вистачає.
2. Для кожної пари «товар × локаль» зібрати passage і hash, порівняти з наявними `(product_id, locale, model_name) -> content_hash`.
3. В embedder надсилати лише змінене, батчами по 32. Запис через `INSERT ... ON CONFLICT (product_id, locale, model_name) DO UPDATE`.
4. У тому ж скрипті оновлювати `products.search_vector`: `setweight(to_tsvector('tndc_search', name), 'A') || setweight(to_tsvector('tndc_search', description), 'B')` по всіх локалях. Для зміненого товару це один UPDATE.
5. Наприкінці вивести `checked=N, embedded=M, skipped=K`.
6. Додати `python -m scripts.build_embeddings` у цикл сервісу `jobs`. Завдяки hash прохід без змін майже нічого не коштує.

**DoD-перевірка:** перший запуск дає `embedded=3×N`, другий одразу після нього `embedded=0`. Після зміни опису одного товару в одній локалі виходить `embedded=1`.

## T6. Репозиторій пошуку
`api/app/repositories/search_repository.py`:
1. `lexical(db, q, limit=100) -> list[int]`: `WHERE search_vector @@ websearch_to_tsquery('tndc_search', :q) ORDER BY ts_rank_cd(...) DESC`.
2. `semantic(db, qvec, limit=100) -> list[int]`: `ORDER BY embedding <=> :qvec` по **всіх локалях**, групування за `product_id` з `min(distance)`. Це і дає кросмовність (PL-запит знаходить UK-опис). Порядок: `SET LOCAL hnsw.ef_search = 100`, внутрішній запит з `LIMIT 300` по HNSW, і лише потім групування, інакше індекс не використовується.
3. `cached_query_embedding(db, normalized_q)` повертає останній `query_embedding` із `search_queries` для того самого тексту.
4. `EXPLAIN ANALYZE` має показувати `Index Scan using ix_product_embeddings_embedding_hnsw`. Ліміт < 500 мс.

## T7. Сервіс пошуку і RRF
`api/app/services/search/service.py`:
1. `rrf(rankings: list[list[int]], k=60) -> list[int]` рахує `score(id) = Σ 1/(k + rank)`. Юніт-тест на маленьких списках обов'язковий.
2. `search(db, q, mode, filters, locale, owner)`:
   - нормалізувати `q` (strip, lower, обрізати до 500 символів);
   - для semantic або hybrid взяти кеш або викликати `embed([q], "query")`;
   - якщо `semantic_search_enabled=False` або сталося `EmbedderUnavailable`, переключитися на lexical і повернути реальний режим у `mode_used`;
   - hybrid дорівнює `rrf([lexical, semantic])`;
   - SQL-фільтри: `list_products(db, filters, currency, ids=ranked)`, потім відновити порядок за рангом і зробити пагінацію.
3. Логувати в `search_queries` поля `query_text`, `locale`, `results_count`, `search_type`, `query_embedding`. `user_id` і `session_token` записувати **тільки якщо `tracking_allowed`** (RODO). Кеш embedding зберігати і без згоди, бо персональних даних у ньому немає.

## T8. Ендпоінт `GET /search`
1. `api/app/routers/search.py`, параметри: `q` (1–200 символів), `mode=lexical|semantic|hybrid` (за замовчуванням hybrid), `limit`, `offset`, фільтри з `ProductFilter` (метал, колір, проба, ціна, наявність).
2. Відповідь `{mode_used, total, items: [ProductCard]}`. Картки збирає `catalog_service.product_cards`, як у recommendations.
3. Підключити роутер у `main.py`, додати опис і приклади в OpenAPI (`/docs`).
4. Тести `api/tests/test_search_api.py`, `embed` мокати через monkeypatch:
   - lexical знаходить товар за словом;
   - при вимкненому прапорці `mode_used == "lexical"`;
   - фільтр ціни відсікає зайве;
   - коли embedder падає, відповідь 200 з fallback.

## T9. «Схожі» з двох джерел
1. `search_repository.similar_by_vector(db, product_id, limit)`: середнє або `uk`-embedding товару, далі `<=>` проти інших товарів із групуванням за `product_id`.
2. У `engine.similar` (`api/app/services/recommendation/engine.py`) при `settings.similar_source == "vector"` брати `ranked` з вектора замість `content_based`. `rules.apply_rules` спільний.
3. У роутері `algorithm` має бути `"content"` або `"vector"`, щоб фронт і звіт бачили, яке джерело спрацювало.
4. Тест: при `similar_source="vector"` на замоканих embedding'ах найближчий товар іде першим.

## T10. Фронтенд (мінімум)
1. Поле пошуку в хедері, сторінка `/search?q=` з картками й тими самими фільтрами, що в каталозі.
2. Показувати `mode_used`. Перемикач режиму лише в dev, для демо на захисті.
3. Клік по результату надсилає подію `Search` або оновлює `clicked_product_id` (через `/events`, лише зі згодою).

## T11. Оцінка трьох варіантів
1. `api/scripts/eval_search.py` бере набір із 20–30 запитів `docs/eval/search_queries.json`: `{q, locale, relevant_ids}`. Туди входять описові запити без збігу слів («подарунок мамі на ювілей», «щось легке на кожен день») і крос-мовні (PL-запит до UK-товарів).
2. Для lexical, semantic і hybrid рахувати Precision@5, MRR@10, nDCG@10, латентність p50/p95.
3. Вивести markdown-таблицю для документації.

**DoD:** semantic і hybrid помітно кращі на описових запитах, де lexical дає ≈ 0.

## T12. Документація (польською)
1. `docs/wyszukiwanie-semantyczne.md` як deliverable «Wyszukiwanie semantyczne i podobieństwo wektorowe»:
   - архітектура (API, embedder, pgvector);
   - формат passage і префікси e5;
   - чому HNSW і cosine;
   - алгоритм `content_hash`;
   - RRF;
   - таблиця з T11;
   - CBF проти vector для «схожих»;
   - ризики (RAM, латентність 20–80 мс, числа) і як їх закрито.
2. Оновити `docs/architecture.md` (новий сервіс) і `api/README.md` (команди build та eval).

---

## Порядок
**T1 → T2 → T3 → T4 → T5** (база), потім **T6 → T7 → T8** (пошук), далі **T9, T10, T11** (паралельно), і **T12** наостанок.

## Команди (запускати вручну)
```bash
# from api/
alembic revision -m "unaccent and search config"   # T1, then fill in upgrade/downgrade
alembic upgrade head
# repo root
docker compose up -d --build embedder
docker compose exec api python -m scripts.build_embeddings
docker compose exec api python -m scripts.eval_search
docker compose exec api pytest tests/test_search_api.py
```

Після додавання нових файлів запустити `graphify update .`.

## Ризик
Перед T6 перевірити, що `EXPLAIN` справді показує HNSW-індекс. При `GROUP BY` планувальник може його оминути, тому внутрішній `LIMIT` тримати в підзапиті.
