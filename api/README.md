# API — baza danych i migracje (Milestone 1)

Modele SQLAlchemy są w `app/models/`, migracje Alembic w `alembic/versions/`.
Wszystkie polecenia uruchamiasz ręcznie (patrz `Cloude.md`).

## Kolejność migracji

| Rewizja | Kto tworzy | Zawartość |
|---|---|---|
| `0001` | ręczna (gotowa) | rozszerzenie `vector`, typy enum, funkcja `set_updated_at()` |
| `0002` | **autogenerowana** | wszystkie tabele, indeksy, ograniczenia CHECK |
| `0003` | ręczna (gotowa) | triggery `updated_at` |

## Uruchomienie

```bash
# 1. Konfiguracja (z katalogu głównego repozytorium)
cp .env.example .env        # uzupełnij POSTGRES_PASSWORD i DATABASE_URL

# 2. Baza z pgvector
docker compose up -d postgres

# 3. Środowisko Pythona (z katalogu api/)
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
set -a && source ../.env && set +a   # eksportuje DATABASE_URL

# 4. Migracje
alembic upgrade 0001
alembic revision --autogenerate -m "core schema" --rev-id 0002
# przejrzyj api/alembic/versions/0002_*.py (patrz lista kontrolna poniżej)
alembic upgrade head

# 5. Test cofania o jeden krok
alembic downgrade -1 && alembic upgrade head
```

## Lista kontrolna dla wygenerowanej migracji `0002`

- Plik ma `down_revision = "0001"`.
- Brak `CREATE TYPE` dla enumów (typy tworzy `0001`, w modelach jest `create_type=False`).
- Obecny jest indeks `ix_users_email_active` (`lower(email)`, `WHERE deleted_at IS NULL`). Autogenerate potrafi pominąć indeksy funkcyjne — jeśli go brakuje, dodaj ręcznie `op.create_index(..., [sa.text("lower(email)")], unique=True, postgresql_where=sa.text("deleted_at IS NULL"))`.
- Obecny jest indeks HNSW na `product_embeddings.embedding` (`vector_cosine_ops`, `m=16`, `ef_construction=64`) oraz GIN na `products.search_vector`.
- Kolumny `*_at` mają typ `TIMESTAMP(timezone=True)`.

## Decyzje odzwierciedlone w schemacie

- D6: `variant_prices.is_manual_override` — ręczna cena nie jest nadpisywana przez przeliczanie walutowe.
- D8: tłumaczenia `uk`/`pl`/`en` w `*_translations`; klucz `product_embeddings (product_id, locale, model_name)`.
- ON DELETE: `CASCADE` dla danych podrzędnych katalogu/koszyka, `RESTRICT` dla `orders`/`order_items`/`payments`, `SET NULL` dla `user_events` (anonimizacja RODO) i `orders.user_id`.
