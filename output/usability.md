# Campus Customs – Usability Improvements (Problem 9)

Four improvements, all implemented and tested in the running app: two on the front end and two in the agent/backend.

## Front end

### 1. Better product search and filtering

**What we added.** The Products page now has, on top of the existing keyword search and category chips:
- a **Sort** dropdown (Featured, Price: low→high, Price: high→low, Name A–Z),
- an **In stock only** toggle that hides sold-out products,
- a **Clear filters** link that resets everything.

All of these live in the URL (`?q=&category=&sort=&stock=1`), so a filtered view can be shared or reloaded. (Files: `frontend/src/pages/Products.tsx`.)

**Why it helps.** Shoppers can narrow 102 products down to exactly what they want — e.g. in-stock hoodies, cheapest first — in a couple of clicks, instead of scrolling the whole catalogue. Sharable URLs and a one-click reset reduce dead ends. For Campus Customs, "in stock only" steers shoppers toward products they can actually buy now.

### 2. Better loading, empty, and error states

**What we added.**
- **Loading:** skeleton placeholder cards on the Products grid and a skeleton layout on the product detail page, so the page keeps its shape while data loads instead of flashing blank. (`frontend/src/components/ProductCardSkeleton.tsx`.)
- **Empty:** when a search matches nothing, a clear "No products match your search" box with a hint and a Clear-filters button, instead of a silent empty grid.
- **Error:** if the API can't be reached, a friendly error box with a **Try again** button that refetches (and a matching box on the product page). (`frontend/src/pages/Products.tsx`, `ProductPage.tsx`.)

**Why it helps.** The shopper always knows what's happening: content is loading, nothing was found, or something broke — and in each case there's an obvious next step. This builds trust and keeps people from assuming the site is broken and leaving.

## Agent / backend

### 3. Forgiving product search (partial names and small typos)

**What we added.** The agent's `search_products` tool (`backend/tools.py`) no longer needs exact matches. Each word in the query matches by:
- exact or **partial** text (e.g. "hood" finds hoodies),
- or a **close fuzzy match** for small typos, using `difflib.SequenceMatcher` with a 0.8 similarity threshold (e.g. "hodie" → hoodie, "harvad" → harvard, "crewnck" → crewneck).

Results are ranked closest-match first, then in-stock, then cheaper. Genuinely unrelated words (e.g. "xyzzy") still return nothing.

**Why it helps.** Customers type fast and misspell. Forgiving search means a typo still finds the right merch instead of a dead end, so the chatbot stays helpful and Campus Customs doesn't lose a sale to a spelling mistake.

### 4. The agent asks for clarification when a request is ambiguous

**What we added.** The system prompt (`backend/prompts/prompt.md`) now tells the agent: if a request could reasonably mean several different products, or is missing something needed to answer well (e.g. "a sweatshirt" — crewneck or hoodie?, or "something for the game"), ask **one** short clarifying question and stop, returning no products — don't guess. Clear requests are still answered directly without extra questions.

**Why it helps.** A quick clarifying question beats a confident wrong answer: the shopper gets to what they actually want faster, and Campus Customs avoids recommending the wrong category of product.

## Tested

- **Filtering:** hoodies + in-stock-only + price ascending → 27 products, prices ascending, none out of stock; filters persist in the URL.
- **States:** skeletons while loading; a "No products match" box with Clear filters for a no-match search; an error box with a working **Try again** button when the API was down (recovered to all 102 products on retry).
- **Fuzzy search:** "hodie", "harvad", "crewnck", "quater zip" all return the right products; "xyzzy" returns none.
- **Clarification:** "I need a sweatshirt" → "Would you prefer a crewneck or a hoodie?" with no product cards, while "navy hodie under $70" answers directly with cards.
