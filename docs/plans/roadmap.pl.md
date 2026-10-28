# Diploma roadmap — TNDC Jewelry House

> Języki: [Українська](roadmap.uk.md) · **Polski** (ten plik)

## Kontekst

Praca dyplomowa (inż., Informatyka, promotor K. Łapa, R-WIiSI-D.460): *Projekt i implementacja sklepu internetowego z algorytmami personalizacji UX na przykładzie sklepu z biżuterią* (EN: *Design and implementation of an online store with UX personalization algorithms on the example of a jewelry store*). Aspekt badawczy: nie dotyczy → kryterium oceny to działająca implementacja oraz dobry opis algorytmów; ewaluacja (M9) ma charakter inżynierski, a nie naukowy.

Stan obecny: frontend (Vite/React/TS) się nie uruchamia, backendu brak. Cel planu — kolejność M0–M10 ze stałymi decyzjami D1–D8, na której można się opierać.

Ten plik to wersja polska; wersja ukraińska (kanoniczna): [roadmap.uk.md](roadmap.uk.md). Obie wersje należy aktualizować równolegle.

## Przyjęte decyzje

| # | Decyzja |
|---|---|
| D1 | Uwierzytelnianie własne w FastAPI (argon2id, JWT 15 min + refresh z rotacją, blokada konta). Nie Supabase Auth. RLS nie jest granicą bezpieczeństwa |
| D2 | Postgres 16 + pgvector w Docker Compose; Supabase/Neon opcjonalnie na produkcję |
| D3 | Dwa rynki: UA (główny: UAH, uk, Nowa Poczta, Monobank/LiqPay) i PL (PLN, pl, InPost, Przelewy24/PayU/BLIK, Stripe jako fallback). Encja `markets` od pierwszego dnia, bez `if country ==` |
| D4 | i18n przez `product_translations` / `category_translations` |
| D5 | Embeddingi: `multilingual-e5-small`, 384 wymiary, wersjonowanie (`model_name`, `locale`, `embedding_version`) |
| **D6** | **Ceny**: cena w PLN jest generowana z kursu (`exchange_rates`) + marży (per rynek), z możliwością ręcznego nadpisania w `variant_prices` (`is_manual_override`). Ręczna wartość nie jest nadpisywana przez przeliczanie |
| **D7** | **Zmiana rynku w trakcie sesji**: tworzony jest nowy koszyk na nowym rynku, stary pozostaje jako `abandoned`; bez przeliczania |
| **D8** | **Języki: UK + PL + EN** (EN obowiązkowy). Skutek: 3 lokalizacje w `product_translations` i do 3 embeddingów na produkt (M7); seed i tłumaczenia ×3 |

Frontend nigdy nie komunikuje się z bazą bezpośrednio; cały dostęp przez FastAPI.

## Architektura (skrót)

React/TS (authContext z JWT w pamięci + httpOnly refresh cookie, `useTracking`) → FastAPI (Auth, Catalog, Cart/Order, Payment, EventIngestion, Recommendation, SemanticSearch) → Postgres 16 + pgvector (core, events, vectors/HNSW); osobny worker `embedder` (e5-small); Object Storage na obrazy.

## Kolejność i zależności

M0 → M1 → M2 → M3 → {M4, M5, M7 równolegle}; M5 → M6; M6 + M7 → M8 → M9 (+M4) → M10.
M7 zależy tylko od katalogu (M3) i może iść równolegle z M4/M6.

## Kamienie milowe

### M0 — Stabilizacja (1–2 dni)
- Naprawa uruchamiania `web/`: brak `index.css` w `web/src/main.tsx`; import `cartContext.jsx`→`.tsx` w `web/src/components/ItemCard/ItemCard.jsx`; `useContext(CartContext)` w `web/src/context/cartContext.tsx`.
- `web/src/context/authContext.jsx` — zaślepka bez Supabase (zostanie przepisany w M2).
- Zapisać D1–D8 w `docs/architecture.md`; zastąpić wzmianki o Node.js przez FastAPI; zaktualizować `README.md`.
- Eksport DBML → PNG/SVG.
- **DoD**: `cd web && npm run dev` bez błędów w konsoli na wszystkich trasach; architecture.md aktualny.

### M1 — Schemat bazy i migracje (1–2 tygodnie)
- Compose: `postgres` (pgvector), `CREATE EXTENSION vector`; Alembic od pierwszego dnia.
- Modele SQLAlchemy + migracje z DBML, z poprawkami: `markets`, `shipping_methods`, `exchange_rates` (obowiązkowa), `variant_prices` (+ `is_manual_override`, `markup_percent` na rynku — D6), `product_translations` (uk/pl/en), `refresh_tokens`, `email_verification_tokens`, `password_reset_tokens`, `user_events`, `search_queries`; `product_embeddings` z kluczem głównym `(product_id, locale, model_name)`; `products.search_vector` + GIN.
- Uogólnienie `user_addresses` (`delivery_provider` enum, `provider_point_id`, `market_id`), `carts.market_id`, `orders` (`market_id`, `shipping_method_id`, `exchange_rate_used`, `session_token`, `locale`, znaczniki czasu, `recommendation_influenced`), `order_items.product_id`, `cart_items.unit_price_at_add`, `product_variants.length_mm/reserved_quantity`, `product_gemstones.is_center_stone`, `product_images.alt_text/width/height/storage_key`, enum `Status`→`CartStatus`.
- Wszystkie kolumny `*_at` — `DateTime(timezone=True)`. `users.email` — częściowy indeks unikalny `WHERE deleted_at IS NULL` (bez rozróżniania wielkości liter); ta sama zasada dla innych pól unikalnych z soft delete.
- ON DELETE: CASCADE dla zależnych tabel katalogu i koszyka; RESTRICT dla orders/order_items/payments; SET NULL dla nullable `orders.user_id`.
- Trigger `set_updated_at()`; CHECK: stock>=0, price>0, quantity>0, fineness IN (375,500,585,750,875,925,958,999).
- Seed: 2 rynki, kategorie, 20–40 produktów, warianty, ceny UAH + PLN (PLN wg D6), kamienie, tłumaczenia uk/pl/en, admin + użytkownicy testowi (Faker + kilka prawdziwych produktów).
- **DoD**: `alembic upgrade head` od zera; `downgrade -1` działa; seed wystarcza do dema obu rynków.
- **Deliverable**: rozdział „Projekt bazy danych".

### M2 — FastAPI i własne uwierzytelnianie (2–3 tygodnie)
- Struktura `api/`: routers, services, repositories, models, schemas, core; Pydantic Settings, `.env.example`; health/readiness, whitelist CORS, structured logging z request-id, globalny exception handler.
- Auth: argon2id; access JWT 15 min; refresh z rotacją w `refresh_tokens`; weryfikacja e-mail; reset hasła w osobnej tabeli; blokada (5 prób + `locked_until`) + rate limit na `/auth/*`; role User/Manager/Admin.
- Frontend: `authContext` pod własne API (login/register/logout/refresh), access w pamięci, refresh w httpOnly cookie, chroniona trasa `/account`.
- **DoD**: rejestracja z weryfikacją, logowanie/wylogowanie, automatyczny refresh po przeładowaniu, blokada konta, brak sekretów w bundlu.
- **Ryzyko (wysokie)**: podatności → sprawdzone biblioteki, OWASP ASVS L1, testy negatywne.
- **Deliverable**: „Bezpieczeństwo i uwierzytelnianie" (diagram sekwencji, argon2, brute force).

### M3 — Katalog + i18n + rynki (2–3 tygodnie)
- API: `GET /products` (paginacja kursorowa, filtry: kategoria/metal/kolor/próba/cena/kamień/dostępność, sortowanie), `GET /products/{slug}`, `GET /categories` (drzewo), admin CRUD + upload obrazów (WebP, kilka rozmiarów).
- i18n: `Accept-Language` + fallback na język rynku; **PL + UK + EN**; rynek: przełącznik w nagłówku, domyślnie z Accept-Language/geolokalizacji, zapis w cookie i `user_profiles.preferred_market_id`.
- Ceny w walucie rynku z `variant_prices`; serwis przeliczania PLN = baza UAH × kurs × (1 + marża), pomija wiersze z `is_manual_override` (D6). Kursy: NBU/NBP.
- Frontend: Categories z API (usunąć `web/src/mockProducts/data.json`), `/products/:slug` z wyborem wariantu, Home — nowości.
- **DoD**: mocki usunięte; filtr „białe złoto 585, pierścionek, do 3000" zwraca poprawny zestaw; obrazy zoptymalizowane.
- **Deliverable**: moduł katalogu + uzasadnienie wariantów.

### M4 — Koszyk, zamówienia, płatności (3–4 tygodnie)
- Koszyk: `session_token` dla gościa, `user_id` dla zalogowanego; merge przy logowaniu (ilości sumowane, koszyk gościa → converted); cartContext na API, w localStorage tylko session_token. **Zmiana rynku → nowy koszyk (D7)**.
- Zamówienia: wzorzec snapshot; transakcyjne zmniejszanie stanu z `SELECT … FOR UPDATE` (lub `stock_reservations` z TTL); `exchange_rate_used`, statusy ze znacznikami czasu.
- Płatności: wyłącznie sandbox, żadnych kart w bazie; abstrakcja `PaymentProvider` + rejestr dostępności per rynek; w pełni zaimplementować **po jednym dostawcy na rynek** (UA: LiqPay/Monobank + Nowa Poczta; PL: Przelewy24/PayU + InPost), reszta jako interfejsy; webhook z weryfikacją podpisu; `idempotency_key`.
- **DoD**: gość→rejestracja→koszyk scalony; zamówienie zmniejsza stan i wysyła e-mail; płatność sandbox → Processing; UA = UAH + Nowa Poczta, PL = PLN + InPost, mieszanie niemożliwe.
- **Deliverable**: diagram stanów, płatności, idempotentność.

### M5 — Telemetria UX + RODO (1–2 tygodnie)
- Tabele `user_events`, `search_queries`; `POST /events` (batch, walidacja, throttling); `GET /admin/analytics/*`.
- Frontend: `useTracking()` z batchowaniem (interwał + beforeunload); gość = ten sam `session_token` co koszyk; baner zgody **przed** śledzeniem.
- RODO: realne użycie `consent_*` w `user_profiles`; retencja z anonimizacją (user_id→NULL); usunięcie konta anonimizuje zdarzenia.
- **DoD**: sesja daje sekwencję zdarzeń; rejestracja przypisuje wcześniejsze zdarzenia; bez zgody brak śledzenia.
- **Deliverable**: „Zbieranie danych o zachowaniu użytkownika".

### M6 — Algorytmy klasyczne (2–3 tygodnie)
`api/services/recommendation/`: `content_based.py` (one-hot + normalizacja + cosinus), `behavior.py` (wagi view=1, search=1, click_reco=2, fav=3, cart=4, purchase=6; zanik `w·exp(−λ·dni)`), `popularity.py` (7/30 dni, normalizacja względem wieku), `hybrid.py` (`a·behavior + b·content + c·popularity + d·novelty`, współczynniki z env), `engine.py`. Reguły biznesowe: nie pokazywać niedostępnych, już kupionych, zachować różnorodność.
- Endpointy: `/recommendations/similar/{product_id}`, `/recommendations/for-you`.
- **DoD**: gość → popularność, użytkownik z historią → inny wynik; współczynniki udokumentowane.
- **Deliverable**: „Algorytmy klasyczne" (pseudokod, złożoność, wagi).

### M7 — Wyszukiwanie semantyczne e5 + pgvector (2–3 tygodnie, równolegle z M4/M6)
- Tekst passage dla produktu × **3 lokalizacje (uk/pl/en)** z prefiksami `query: ` / `passage: `, werbalizacja cech liczbowych + filtry SQL; normalizacja L2; HNSW `vector_cosine_ops (m=16, ef_construction=64)`, operator `<=>`; `content_hash` dla przeliczania przyrostowego.
- `GET /search?q=` — lexical (tsvector+unaccent), semantic, hybrid (RRF, k≈60); wielojęzyczność (zapytanie PL → opis UK).
- „Podobne produkty" z dwóch źródeł (CBF vs wektor) — przełączane flagą.
- `api/scripts/build_embeddings.py`; embedder jako osobna usługa w Compose; cache embeddingów zapytań w `search_queries`; flaga wyłączenia semantyki.
- **DoD**: opisowe zapytanie zwraca trafne produkty bez zbieżności słów; build przelicza tylko zmienione; porównanie 3 wariantów udokumentowane.
- **Ryzyka**: RAM 400–600 MB, opóźnienie 20–80 ms, liczby w embeddingach.
- **Deliverable**: „Wyszukiwanie semantyczne i podobieństwo wektorowe".

### M8 — Personalizacja w UI (2 tygodnie)
Sekcje „Polecane dla Ciebie", „Podobne produkty", „Ostatnio przeglądane", „Inni oglądali też"; spersonalizowana kolejność w kategoriach; wyszukiwarka w nagłówku z autocomplete; `recommendation_cache` z TTL; flaga `algorithm=cbf|vector|hybrid`; `click_recommendation` z identyfikatorem algorytmu; stany skeleton.
- **DoD**: gość i użytkownik z historią widzą różną stronę główną; każde kliknięcie ma id algorytmu; brak przeskoków layoutu.
- **Deliverable**: integracja w UX + zrzuty „przed/po".

### M9 — Testy, ewaluacja, audyt (2–3 tygodnie)
- pytest: jednostkowe (deterministyczne rankingi), integracyjne (TestClient + testowa baza), negatywne auth (wygasły/odwołany token, blokada, SQLi), smoke na froncie.
- Ewaluacja: generator sesji syntetycznych (persony), Precision/Recall/nDCG@K, Coverage, Diversity; popularność vs CBF vs wektor vs hybryda + warianty współczynników; latencja p50/p95.
- Audyt: OWASP Top 10, pip-audit/npm audit, brak PII/sekretów w logach.
- CI (GitHub Actions): lint + mypy + pytest przy każdym pushu.
- **DoD**: `docs/evaluation.md`; pokrycie krytycznych ścieżek; zielone CI.
- **Deliverable**: „Testy", „Ewaluacja algorytmów".

### M10 — Wdrożenie i dokumentacja (3–4 tygodnie, równolegle)
- Deploy: frontend Netlify/Vercel; API + embedder w Dockerze (Railway/Render/Fly/VPS); zarządzany Postgres z pgvector; storage + CDN; HTTPS, domena, backupy ze sprawdzonym odtworzeniem; health + monitoring błędów.
- Strony prawne per rynek: PL szczegółowo (regulamin, polityka prywatności, cookies, 14 dni na odstąpienie, ceny brutto, formularz RODO), UA poglądowo (oferta, polityka, zwroty).
- Dokumentacja ~60–80 stron: Wstęp; Analiza; Wymagania; Architektura; Implementacja; Algorytmy; Wyszukiwanie semantyczne; Testy; Bezpieczeństwo i RODO; Podsumowanie.
- **DoD**: publiczne demo + tag `v1.0-diploma`; README; instrukcje użytkownika/administratora; 10-minutowy scenariusz dema.
- Zasada: 1–2 strony szkicu pracy po każdym kamieniu milowym, zrzuty ekranu i diagramy zapisywać od razu.

## Tabele opcjonalne (tylko jeśli zostanie czas)
`recommendation_cache` (potrzebna w M8), `stock_reservations` (do wyboru w M4), `audit_log`, `product_reviews`, `coupons` + `coupon_redemptions`, `product_collections`, `ab_experiments`.

## Rejestr ryzyk (najważniejsze)
- Nadmierny zakres (wysokie/wysoki) → twardy MVP na kamień milowy, tylko sandbox, coupons/reviews/ab — jeśli starczy czasu.
- Podwójna złożoność dwóch rynków i 3 języków (wysokie/wysoki) → `markets` od początku; PL „minimalnie kompletny".
- Odkładanie tekstu pracy (wysokie/wysoki) → szkice po każdym kamieniu milowym.
- Rozjazd kodu i schematu → Alembic, bez ręcznych zmian.
- Własne uwierzytelnianie (średnie/wysoki) → biblioteki, ASVS, testy negatywne.
- RODO dla telemetrii → zgoda, anonimizacja, retencja.
- Overselling → FOR UPDATE / rezerwacje.
- Zimny start → popularność + fallback semantyczny + sesje syntetyczne.

## Pierwsze kroki
1. M0: `index.css`, import/`useContext` cartContext, zaślepka authContext.
2. Zapisać D1–D8 w `docs/architecture.md`, zaktualizować `README.md`.
3. Zaktualizować DBML (markets, variant_prices + override, shipping_methods, exchange_rates, delivery_provider, tłumaczenia uk/pl/en).
4. Start M1: compose z pgvector, Alembic, pierwsza migracja (markets/users/user_profiles/categories/products/product_variants/variant_prices).

## Weryfikacja
- M0: `npm run dev`, przejść wszystkie trasy, konsola czysta.
- Dla każdego kamienia milowego — DoD powyżej; ogólnie: `alembic upgrade head && alembic downgrade -1`, `pytest`, zielone CI, scenariusz dema M10.
