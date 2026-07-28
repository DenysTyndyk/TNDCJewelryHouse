# Architecture Workshop (Student-Owned)

**You** write the architecture. This document only asks questions and lists what a solid thesis chapter usually covers. The AI must not fill in `docs/architecture.md` for you unless you explicitly request a full solution.

Target stack context: **TypeScript · React · Next.js · Tailwind · Node.js · Supabase · Docker · Git**.

Product: family jewelry e-commerce (catalog, cart, about, contact/location, new arrivals, categories). Content languages: **PL / EN / UK**. Docs language: **English**.

---

## How to use this workshop

1. Create [`architecture.md`](./architecture.md) (template sections are ready — fill them yourself).
2. Answer the questions below in writing (short paragraphs + diagrams you draw).
3. Ask the AI for **hints / review** on your draft — not for a finished architecture.
4. Iterate until your diagrams and boundaries are consistent.

Suggested explicit phrases when talking to the AI:

- Hint mode: “Review my architecture draft — hints only.”
- Opt-in: “Give me the full solution for this section.”

---

## A. Context & goals

Answer:

- Who are the actors? guest shopper
- What must ship in v1 vs later? (cart without payment, contact form only)
- What constraints come from the diploma must show layered architecture, Docker, design

Deliverable in your doc: **Problem statement** + **scope (in / out)**.

---

## B. System context

Sketch a **context diagram** (boxes + arrows). Ask yourself:

- What sits outside the system? (browser, email, maps provider, payment later?)
how we can use this outside the system? We must use this technology in the system pyment we will make in the last versions
- Where does Supabase sit — inside your “system” boundary or as an external platform?
what better on you opinion?
- Do you expose a public API, or only a BFF for your Next.js app?
privious I am working only with public API 

Deliverable: one context diagram + 5–10 sentences explaining trust boundaries.

---

## C. Containers (high-level deployable pieces)

You plan Docker for **frontend and backend**. Decide and justify:

| Candidate | Keep? | Responsibility | Talks to |
|-----------|-------|----------------|----------|
| Next.js `web` | ? | UI / SSR / routing (`/cart`, …) | ? |
| Node.js `api` | ? | Business rules / order flow? | ? |
| Supabase (hosted or CLI) | ? | Postgres, Auth, Storage? | ? |
| Other (CDN, mailer…) | ? | | |
 I want your advice about it
Guiding questions (do not skip):

1. If Next.js can call Supabase directly, why do you still want a Node `api` container?
for practise 
2. Which secrets must never ship to the browser? 
maybe all secrects keys from .env file if correct understand your question
3. Where do cart contents live — client only, server session, or database?
offcourse in database 

Deliverable: **container diagram** + short rationale per container.

---

## D. Responsibility split checklist

For each concern, write **one owner** (web / api / supabase / client-only):

- [ web ] Product catalog read
- [ supabase] Product images
- [supabase ] Category listing & filters
- [api ] New arrivals query
- [api ] Cart add/update/remove
- [ api] Checkout / order create (if in scope)
- [api ] Contact form submission
- [ cms] About page content (static vs CMS)
- [ supabase] Auth (if any)
- [ supabase] i18n of product descriptions (PL/EN/UK)
- [ supabase] Admin product upload (if any)

If two layers share a concern, explain the boundary (e.g. “api validates, Supabase stores”).

---

## E. Data

Without pasting a finished ERD from the AI:

1. List entities you think you need (Product, Category, …).
yes
2. For each entity: key fields + which fields are translated.
3. Sketch relationships (1–n, n–n) on paper or Mermaid **you** write.
4. Decide: guest cart vs user cart; how line items reference products.

Deliverable: **ER sketch** + notes on i18n storage strategy (JSON columns? translation tables?).

---

## F. Key flows (sequences)

Pick at least three flows and draw sequence diagrams:

1. Browse category → open product → add to cart
client can open item and check few photos with this item and also can swap photo on cart item (without open item in new/small window)
2. Submit contact form
when clien wrote message and write contact information (email for answer,also can be email from data base which client use for sign on wibsite) and shop owner after read message can give answer on this email for example from gmail   
3. (Optional) Place order / create inquiry
in cart client can write information for make order for example street, delivery information this request sends to mail to owner shop or from CRM system better can confirm/cancle ordenary for this client 

For each flow: which container is called, sync vs async, failure cases (empty stock? mail fail?).
async better on my opinion
---

## G. Next.js routing map (App Router)

Map UI to routes (you own the final tree):

| Page | Proposed path | Server or client heavy? |
|------|---------------|-------------------------|
| Home / new arrivals | `/` | ? |
| Categories | `/categories` … | ? |
| Product | `/products/[slug]` | ? |
| Cart | `/cart` | ? |
| About | `/about` | ? |
| Contact | `/contact` | ? |

Note: prefer App Router over adding `react-router` as a separate library.

---

## H. Docker & local development

Answer before writing Compose files:

- Which services run in Compose for day-to-day work? npm run dev enaf for thid on localhost 
- Do you run full local Supabase or use a hosted project?full local Supabase 
- What belongs in `.env.example` (names only — no secrets)? only name and this file must be in .gitignore
- How do `web` and `api` discover each other on the Docker network? better from DNS-server from docker

Deliverable: bullet list of services + ports + env var **names**.

---

## I. Security & quality (thesis-friendly)

Short answers:

- Authn vs authz (even if v1 is mostly public catalog)
on my opinion better use new table with role and gets evry user role? defoult role fro new users and admin for owner shop and people who working with data base
- Input validation location
validation we will do from beckend and minimal validation from frontend
- Image upload trust model
on my opinion we will not do this option fro client, upload photo can only admin in data base 
- What you will test (unit / integration / e2e) at a high level  - unit tests enaf for project 

---

## J. Diploma documentation map

Suggested chapter outline (adapt to your university template):

1. Introduction & goals  
2. Requirements (functional / non-functional)  
3. Related technologies (why this stack)  
4. Architecture (context → containers → components → data)  
5. Implementation highlights  
6. Deployment (Docker)  
7. Testing & results  
8. Conclusions  
I want skip this in actual time
Your `architecture.md` mainly feeds chapters **4** and **6**.

---

## Review protocol with the AI

When you paste a draft, ask for feedback in this shape:

1. Ambiguities / missing boundaries  
2. Questions you have not answered yet  
3. Analogies to common patterns (BFF, repository, etc.) — without rewriting your doc  

Remember: **hints first; full solutions only on explicit request.**
