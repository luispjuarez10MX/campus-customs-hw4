# Homework 4 – AI Prompt Log

## Problem 1 – Create the AI Prompt Log

### Prompt 1

I believe we can star now. For Problem 1, create AI_prompts.md and keep updating it as we go through the homework.
For each problem, add a section with the problem number and title, the prompt I actually gave you in my own words, and if I need a follow-up, include that too with one short sentence on what was missing after the first try.
Don’t invent prompts or extra explanations I didn’t give you. We’ll keep filling this file as we work problem by problem. The running site, database changes, and screenshots will be the evidence, so we don’t need an extra proof essay. This as we've done it before (which model is better? Lunea or sol? to define which to use)

### Follow-up Prompt

What was lacking after Prompt 1: the model to use for the homework had not been chosen yet.

lets use sol, it will get tougher

## Problem 2 – Inspect the Database Structure

### Prompt 1

Now, for Problem 2, let’s inspect data/campus_customs.db and understand how the database is structured. Look at the actual tables and fields in the database, especially catalogue, inventory, and users. Don’t assume or invent any fields.
Then start output/harness.md. Add each table, its fields, and one short explanation of why each field matters for either the shop or the chatbot.
Keep this file simple for now since we’ll continue adding to the same harness in later problems.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 3 – Build the First Version of the Website

### Prompt 1

let’s build the first working version of the Campus Customs website using React + Vite + TypeScript.
Add a top navigation bar with Home, Products, About Us, Log in, and Create account.
For the Home and About Us pages, use yalebulldogblue.com only as inspiration for the Campus Customs tone and messaging, but write the text in our own words.
On the Products page, show the catalogue products using the image paths from the database, with the product name, price, and a short description.
Each product card should open its own product page with a larger image, the full product description, price, and sizes/stock when available.
Also add a chat box in the bottom-right corner of the site. It does not need to work with the AI agent yet, just make the interface ready so we can connect it later.
If needed, create a simple backend/main.py FastAPI endpoint just to read products and images from the database for now. We’ll expand that backend later.
Don’t worry about making the design perfect yet. For this problem I mainly want the site structure and navigation working correctly.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 4 – Create-Account and Login Flow

### Prompt 1

add a normal create-account and login flow to the site.
For account creation, ask for first name, last name, email, and password. Confirm password is optional but fine to add. New users should be saved in the existing users table.
For login, use email and password. Make sure passwords are stored securely as hashes, never as plain text.
Please test both cases: first, confirm the existing test user can log in with test@campuscustoms.yale.edu / password, and second, create a brand-new account and make sure that new user can also log in successfully.
Also update output/harness.md with a short explanation of how authentication works, what user information we store, and how the passwords are protected.

### Follow-up Prompt 1

What was lacking after Prompt 1: I began checking the seeded hash in a way that looked like brute-forcing the iteration count, so this prompt set the rules.

Don’t try to scan or brute-force PBKDF2 iteration counts. We already know the test password and only need to implement the normal authentication flow for this course project.
Please inspect the existing users table and the stored password hash format, plus any existing project files/dependencies that can tell us which hashing method was used. If the hash itself contains the algorithm, salt, iteration count, or other parameters, use those directly.
Then implement the normal password verification function using the correct hashing scheme and test the provided account:
test@campuscustoms.yale.edu
password: password
If the existing hash format does not contain enough information to determine how it was generated, stop and tell me exactly what information is missing rather than trying different parameters or cracking the hash.

### Follow-up Prompt 2

What was lacking after Follow-up 1: inspection confirmed the iteration count is missing, so this prompt said how to proceed without it.

This looks like a missing parameter in the seeded course data, so don’t brute-force or guess the PBKDF2 iteration count and don’t modify the seeded user to fake the test.
Please finish the authentication flow for new accounts using a secure self-describing password hash so new users can register and log in normally.
For the existing 3-part pbkdf2_sha256$salt$digest hashes, keep a separate legacy verification function that can use the correct iteration count once I get it from the professor/TA. Make that value easy to configure rather than hardcoding a guessed number.
Also make sure we can later migrate a legacy hash to the new format after a successful login.
For now, test that creating a brand-new account and logging into it works, and clearly note that verification of the seeded test user is pending the missing iteration count.

## Problem 5 – Connect the Chat to a PydanticAI Agent

### Prompt 1

let’s connect the website chat to a real PydanticAI agent through FastAPI.
Put the backend in `backend/`. Use `backend/main.py` as the FastAPI app, and create the agent files next to it:

* `backend/prompts/prompt.md`
* `backend/agent.py`
* `backend/tools.py`
* `backend/models.py`

`prompt.md` should start defining the Campus Customs voice and basic safety rules. `agent.py` should wire the agent together, `tools.py` should hold the tools it can call, and `models.py` should contain the structured types we need for chat replies and product cards.
In `main.py`, create a chat endpoint so messages from the website chat widget go to the agent and return the agent’s response. Keep the existing product/auth routes working too.
Use my Portkey API key and one of the course OpenAI models for the agent.
Also update `output/harness.md` with a short explanation of how the frontend sends messages to FastAPI and how the backend loads the agent, including the prompt file and model.
Make sure I can run the backend from inside the `backend/` folder with:
`uvicorn main:app --reload --port 8000`

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 6 – Give the Chatbot Database Lookup Tools

### Prompt 1

Now , for Problem 6, let’s give the chatbot tools to look up real product information from campus_customs.db.
In backend/tools.py, add tools so the agent can get a product’s description, price, and inventory. For stock, it should be able to check the quantity by size when the customer asks.
Make sure these answers always come from the database. The agent should never make up prices or stock, and if a size is out of stock it should say that clearly.
Also update backend/prompts/prompt.md so the agent knows to use these tools whenever the user asks about price, product details, or availability. Add or update the structured return types in backend/models.py as needed.
Finally, update output/harness.md with the tools we added and a short explanation of the fields in the lookup result models and why we chose them.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 7 – Chat Search Updates the Page with Product Cards

### Prompt 1

For Problem 7, let’s make the chat actually update the website when someone asks for a type of product.
For example, if the user asks “what hoodies do you have?”, the agent should search the catalogue and return structured product matches, and the frontend should dynamically show those results as product cards with the image, name, price, and short info.
Keep this as a clear API handoff: the agent/backend returns the product data, and the React frontend is what renders the cards.
Make sure the product cards added by the chat behave exactly like the regular product cards from Problem 3. If I click one, it should still open the same single-product detail page with the large image and full product information.
Also update backend/prompts/prompt.md and output/harness.md so it’s clear how a chat search gets turned into product results on the page.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 8 – Customer Memory, Identity, and Page Context

### Prompt 1

Now, for Problem 8, let’s add customer memory to the chat.
If the user is logged in, save their chat history in the database and reload it when they come back. The agent should also know who is chatting, at least their name and email, using agent deps or another clear pattern.
Also pass the current page/product context to the agent, so if someone is on a product page and asks something like “do you have this in pink?”, the agent knows which product “this” refers to.
Guests should still be able to chat, but we only need persistent chat history for logged-in users.
Finally, update output/harness.md explaining how the chat history is stored, which customer fields the agent sees, and how the current page context is passed to the agent.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 9 – Four Usability Improvements

### Prompt 1

Great, now for Problem 9, let’s add 4 usability improvements to the app: 2 on the front end and 2 for the agent/backend.
For the front end, add:

1. Better product search/filtering so shoppers can find products more easily.
2. Better loading, empty, and error states so the site feels clearer when something is loading or nothing is found.

For the agent/backend, add:

1. Better product search that can handle partial names or small typos instead of only exact matches.
2. If the user’s request is ambiguous, have the agent ask a short clarification instead of guessing.

Create `output/usability.md` before or while building these. For each improvement, write what we added and why it helps either the shopper or Campus Customs.
Most importantly, actually implement all 4 improvements in the running app so they are visible/testable, not just listed in the markdown file.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 10 – Visual Design Polish

### Prompt 1

now polish the site so it feels like a real Campus Customs storefront, not a default Vite project.
Improve the visual design across the site: typography, colors, spacing, hierarchy, product cards, product detail pages, buttons, navigation, and the chat experience. Add some subtle motion/interaction where it helps, but keep it clean and usable. I want it to feel more creative and distinctive, while still fitting the Yale/Campus Customs brand.
Please also create output/design.md with a short explanation of the main design changes we made and why each one should help customers stay on the site longer, understand the products better, or be more likely to buy.
Keep design.md concrete and short. I don’t want a generic design essay, just the actual changes we made and why they help.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.

## Problem 11 – App Check with Screenshots

### Prompt 1

let’s test the actual site and create `output/app_check.html` documenting that the main features work.
I need 3 real checks with screenshots:

1. The chat answering an inventory question with the correct stock/price from the database.
2. The dynamic product cards appearing after asking something like “what hoodies do you have?”
3. One of the usability improvements we added in Problem 9.

Save the screenshots in `output/app_check_images/`. In `app_check.html`, make a section for each test with a heading, the screenshot, and 1–2 short sentences explaining what it proves.
Use relative image paths like `app_check_images/inventory.png` so I can double-click `app_check.html` and everything loads correctly. Please use screenshots of the real running app, not placeholders.

### Follow-up Prompt 1

What was lacking after Prompt 1: the user tested it themselves and supplied their own screenshots to use instead, and asked to fix two issues they found.

also we had an issue in the chat, fix it. dont know what failed tho.
And fix also the app_check.html is not showing the images actually

(Fix 1 — chat: broad "range of prices" questions made the agent call a per-product tool too many times and hit the tool-call limit, which surfaced as a 502. Added a one-call get_price_range tool, prompt guidance to use it and be economical, a higher tool-call limit, and graceful handling so it never errors out. Fix 2 — images: embedded the three screenshots into app_check.html as base64 so they always display.)

## Problem 12 – Audit Trail, Safety Rules, and Finished Harness

### Prompt 1

For Problem 12, let’s finish the audit, safety rules, and output/harness.md.
Keep output/audit_trail.json append-only. Every agent run should add entries with the time, tool name, short arguments, short result summary, and the reason the agent stopped. Don’t erase the previous history between runs.
Also add a short safety section to prompts/prompt.md with the main rules the agent should follow, especially not inventing product info, not exposing private user data, and not taking actions it shouldn’t.
Then finish output/harness.md so it clearly explains the full system: the models in models.py and why we chose those fields, the tools and what the agent can do, the safety rules, and the main specs like loop limits, result caps, which models we use, and how to run both the frontend and backend.
Keep the harness concise but complete enough that someone can understand how the system works without reading all the code.

### Follow-up Prompt

No additional prompt was needed after Prompt 1.
