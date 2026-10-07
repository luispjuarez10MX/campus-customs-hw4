# Campus Customs – Design Polish (Problem 10)

Concrete visual changes we made and why each should help customers stay, understand the products, or buy. All changes are live in the running app (mostly `frontend/src/index.css`, plus `index.html` fonts and `ProductCard.tsx`).

## Typography
- **Added a real font pairing:** Fraunces (a warm display serif) for headings, the brand, and prices; Inter for body text. Replaced the default system/Georgia stack.
- **Why:** The serif gives the store a distinctive, collegiate, "established" feel instead of a default Vite look, and the clear serif/sans contrast makes headings and prices easier to scan — customers grasp the page faster and trust the brand more.

## Color and brand accent
- **Kept Yale navy** but added a **collegiate gold accent** (`--gold`) used on the brand mark, section eyebrows, product tags, primary "Create account" button, active nav underline, and the chat badge.
- **Why:** One consistent accent ties the site together and draws the eye to the actions that matter (sign up, key labels), which lifts engagement and conversions. Gold + navy also reads unmistakably Yale.

## Navigation
- Translucent navy bar with blur, a small gold "Y" brand mark, and an **animated gold underline** on hover/active links.
- **Why:** A sticky, clearly-branded header keeps navigation one click away as people scroll, and the active-link cue helps them know where they are — less friction, longer sessions.

## Hero
- Layered navy gradient with a soft gold glow and a subtle decorative ring, a larger fluid headline, and gold primary / outline secondary buttons.
- **Why:** A confident hero sets the brand tone immediately and gives a clear primary action ("Shop all products"), nudging visitors into the catalogue instead of bouncing.

## Product cards
- Redesigned cards: contained image area with a **zoom-on-hover**, a **gold garment-type tag**, two-line description clamp, a **"Low stock" / "Sold out" badge**, and a **"View details →"** overlay on hover. Cards lift with a shadow and fade in.
- **Why:** The tag and badges help shoppers understand and compare products at a glance (type and urgency), the hover affordance makes it obvious cards are clickable, and scarcity cues ("Low stock") gently encourage purchase.

## Product detail page
- Wider two-column layout with a **sticky, framed product image**, a large gold eyebrow + Fraunces title + big price, and **interactive size boxes** (hover lift; sold-out sizes clearly struck through).
- **Why:** The image stays visible while reading, the clear price and size availability answer the two biggest pre-purchase questions immediately, and the sold-out styling prevents confusion about what's buyable.

## Buttons and forms
- Pill buttons with hover lift + shadow, a distinct gold primary, visible `:focus-visible` rings, and cleaner card-style forms.
- **Why:** Consistent, tactile buttons make actions feel reliable; focus rings keep it keyboard-accessible; tidy forms reduce sign-up friction.

## Chat experience
- Gradient header, softer chat bubbles with "tails", a toggle with a **pulsing gold dot** to invite use, and a gentle pop-in animation for the panel.
- **Why:** A more inviting, lively assistant gets used more, and the chat is the fastest path to the right product — more chat use means more guided discovery and sales.

## Motion and accessibility
- Subtle fade/rise on cards and sections, image zoom, and the chat ping — all disabled under `prefers-reduced-motion`.
- **Why:** Light motion makes the site feel modern and responsive without being distracting, and respecting reduced-motion keeps it comfortable for everyone.

## Tested
- Verified in the browser on Home, Products, and a product detail page: Fraunces loads (confirmed on the detail `h1`), gold accents and product tags/badges render, images load, hover and size-box states work, and there are no console errors. Build and lint pass.
