# Campus Customs — Yale Apparel Store + Chatbot

MGT 409 (AI Foundations for Managers) · Homework 4.

A customer-facing storefront for **Campus Customs**, a Yale apparel shop, with an AI shopping
assistant. Customers can browse the catalogue, create an account and log in, and chat with an
assistant that answers questions about products, prices, sizes, and stock — with matching product
cards appearing on the page.

- **Frontend:** React + Vite + TypeScript (`frontend/`)
- **Backend:** Python + FastAPI (`backend/`)
- **Chatbot:** a PydanticAI agent using an OpenAI model (`gpt-5.6-sol`) through the **Portkey** gateway

## Repository layout

```
hw4/
├── frontend/              # React + Vite + TypeScript app
├── backend/
│   ├── main.py            # FastAPI app (run: uvicorn main:app --reload --port 8000)
│   ├── agent.py           # the PydanticAI chat agent
│   ├── tools.py           # tools the agent can call (search, details, stock, price range)
│   ├── models.py          # Pydantic models (API + agent + audit)
│   ├── prompts/prompt.md  # system prompt (voice + safety rules)
│   ├── config.py          # settings, .env loading, Portkey model
│   ├── db.py              # SQLite helpers (catalogue, inventory, users, chat)
│   ├── auth.py            # password hashing / verification
│   └── audit.py           # append-only audit trail
├── output/                # deliverables: harness.md, design.md, usability.md,
│                          #   app_check.html (+ app_check_images/), audit_trail.json
├── AI_prompts.md          # log of the prompts used to build this
├── requirements.txt       # backend Python dependencies
├── .env.example           # copy to .env and add your Portkey key
└── .gitignore
```

## The local data pack (not in this repo)

The course data folder is **not** committed. Place it so the backend can find it — either
**inside `hw4/`** (recommended) or next to it:

```
hw4/
└── data/
    ├── campus_customs.db     # catalogue, inventory (by size), users, chat history
    └── products/             # product images referenced by the catalogue
```

By default the backend looks for `hw4/data/`, then `../data/`. To point somewhere else, set
`CAMPUS_CUSTOMS_DATA_DIR` in `.env`.

## Setup

### 1. Backend

From `hw4/`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then open .env and add your Portkey API key
```

`.env` needs your Portkey key (never commit it):

```
PORTKEY_API_KEY=your-portkey-api-key-here
```

### 2. Frontend

From `hw4/frontend/`:

```bash
npm install
```

## Running the app

Run the backend and frontend in two terminals.

**Backend** — from `hw4/backend/`:

```bash
uvicorn main:app --reload --port 8000
```

**Frontend** — from `hw4/frontend/`:

```bash
npm run dev
```

Then open **http://localhost:5173**. The Vite dev server proxies `/api` and `/images` to the
backend on port 8000, so both must be running.

## Notes

- All AI calls go through Portkey using `PORTKEY_API_KEY`; the model is `gpt-5.6-sol`
  (override with `CAMPUS_CUSTOMS_MODEL`).
- Passwords for new accounts are stored as salted PBKDF2-HMAC-SHA256 hashes — never plain text.
- The three pre-seeded demo users can't log in until the course staff provide the iteration count
  for their legacy hashes (set `CAMPUS_CUSTOMS_LEGACY_PBKDF2_ITERATIONS`); newly created accounts
  work normally. See `output/harness.md` for details.
- `output/harness.md` is the full system write-up (models, tools, safety rules, specs).
