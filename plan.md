Phase 1 — UI foundation
Мета: React UI в web/, схожий на design/mocks/, 5 сторінок, мок-каталог, кошик у localStorage.
Не робити зараз: Next.js, API, Supabase, Docker, auth/merge в БД.

T1 Scaffold → T2 Tokens → T3 Router/Layout → T4 Pages → T5 Mock data → T6 Cart → T7 Polish
T1 — Scaffold
Готово, коли: cd web && npm run dev відкриває порожню React-сторінку.

Створити Vite + React + TypeScript у папці web/
Перевірити скрипти dev / build
Короткий web/README.md (як запустити)
У кореневому README.md додати посилання на web/
Docs: https://vitejs.dev/guide/

T2 — Tailwind + бренд
Готово, коли: фон deep-black, текст warm-white, золотий акцент.

Підключити Tailwind до Vite
https://tailwindcss.com/docs/installation/using-vite
Перенести змінні з design/tokens.css у web/src
Шрифти: Cormorant Garamond + Outfit
Theme Tailwind під токени (colors / fonts)
Скопіювати design/brand/ → web/public/brand/
T3 — Layout + роутинг
Готово, коли: кліки по меню змінюють URL і контент.

Додати React Router
AppLayout: logo + nav + badge кошика + footer + Outlet
Маршрути:
Path	Page
/
Home
/categories
Categories
/cart
Cart
/about
About
/contact
Contact
Мобільне меню (бургер)
Active link (aria-current)
Спочатку сторінки-заглушки з заголовком.

T4 — Верстка сторінок (без логіки)
Готово, коли: екрани близькі до HTML-моків.

Роби по одній сторінці:

Home — hero + new arrivals + category tiles ← design/mocks/home.html
Categories — hero + filter chips + сітка ← category.html
Cart — рядки + summary (поки hardcode) ← cart.html
About — текст + факти ← about.html
Contact — форма + map placeholder; submit = preventDefault ← contact.html
Винеси по ходу: Button, SectionHeader, ProductCard.

T5 — Мок-дані
Готово, коли: Home і Categories беруть товари з одного файлу.

Типи Product, Category
web/src/data/mockProducts.ts (6–8 товарів, 4 категорії)
Home: new arrivals (isNew або перші N)
Categories: фільтр реально ховає/показує
Ціни PLN
T6 — Guest cart (localStorage)
Готово, коли: Add → badge оновлюється; /cart показує рядки; F5 зберігає кошик.

Тип { productId, quantity }
Ключ напр. tndc.cart.v1
Context/hook: add / update / remove / clear + sync
Кнопка Add на картці
Cart page = context + join з моками
Subtotal; checkout disabled / «later»
Empty state + лінк на Categories
Не робити: merge після логіну, запис у БД.

T7 — Полірування
Готово, коли: можна показувати Phase 1.

Desktop + mobile (~375px) на всіх 5 сторінках
Легкі hover/transition
Прибрати «TODO» з UI
У web/README.md: що вміє Phase 1 / що ні
Definition of Done
 npm run dev працює
 5 маршрутів як у дизайні
 Мок-каталог + фільтр
 Cart у localStorage + badge
 Без API / Supabase / Docker
Починай з T1. Якщо в web/ уже щось лежить від попередньої спроби — або перепиши поверх, або видали папку сам і створи з нуля. Коли застрягнеш: напиши «підказка по T1» (без прохання написати весь код).