"""Pydantic models shared by the Campus Customs backend.

Catalogue (Problem 3): SizeStock (one inventory row), ProductSummary (a product
card on the Products page) and ProductDetail (a single product page with stock
by size).
Accounts (Problem 4): SignupRequest, LoginRequest, UserPublic.
Chat (Problem 5): ChatMessage / ChatRequest (what the widget sends),
AgentReply (the agent's structured output), ProductCard and ChatResponse
(what the endpoint returns to the widget).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class SizeStock(BaseModel):
    size: str = Field(description="Size label from inventory.size (XS–XXL)")
    quantity: int = Field(description="Units in stock for this size; 0 means out of stock")


class ProductSummary(BaseModel):
    product_id: str
    name: str
    garment_type: str
    price: float
    short_description: str = Field(description="First sentence of the description, for cards")
    colors: list[str]
    image_url: str = Field(description="URL the frontend can load, e.g. /images/<file>.jpg")
    total_stock: int = Field(description="Units in stock across all sizes")


class ProductDetail(ProductSummary):
    description: str
    search_tags: list[str]
    inventory: list[SizeStock] = Field(description="Stock per size, ordered XS → XXL")


# ---- Accounts (Problem 4) --------------------------------------------------


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8, description="Plain password; hashed before storage, never stored as text")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """User info safe to return to the frontend (never the password hash)."""

    id: int
    first_name: str | None
    last_name: str | None
    email: EmailStr


# ---- Chat (Problem 5) ------------------------------------------------------


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    """What the chat widget sends: the conversation so far, newest message last,
    plus who is chatting and what page they're on."""

    messages: list[ChatMessage] = Field(min_length=1, max_length=40)
    user_id: int | None = Field(default=None, description="Logged-in customer's id; None for guests")
    current_product_id: str | None = Field(
        default=None, description="product_id of the product page the customer is viewing, if any (page context)"
    )


class AgentReply(BaseModel):
    """Structured output the agent must return."""

    message: str = Field(description="Reply to the customer, in the Campus Customs voice. Plain text, short.")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=6,
        description="product_id values (from tool results) of products to show as cards; empty if none",
    )


class ChatResponse(BaseModel):
    """What the chat endpoint returns to the widget: the reply text plus the
    products to show on the page. `products` is the same ProductSummary shape as
    GET /api/products, so the frontend renders them with the Problem 3 ProductCard
    component and clicking one opens the same product detail page (Problem 7)."""

    reply: str
    products: list[ProductSummary]


# ---- Chat history (Problem 8) ----------------------------------------------


class ChatHistoryMessage(BaseModel):
    """One saved message replayed to the widget when a logged-in customer returns.
    Assistant messages carry the products that were shown, so the page can restore
    them too."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductSummary] = Field(default_factory=list)


class ChatHistory(BaseModel):
    messages: list[ChatHistoryMessage]


# ---- Audit trail (Problem 12) ----------------------------------------------


class AuditToolCall(BaseModel):
    """One tool the agent called during a run (summarized for the audit log)."""

    tool: str = Field(description="Tool name, e.g. search_products")
    args: str = Field(description="Short summary of the call arguments")
    result_summary: str = Field(description="Short summary of what the tool returned")


class AuditRecord(BaseModel):
    """One agent run, appended to output/audit_trail.json (append-only)."""

    time: str = Field(description="UTC ISO timestamp when the run was recorded")
    user: str = Field(description="Who was chatting: the customer's email, or 'guest'")
    question: str = Field(description="The customer's message for this run (truncated)")
    tool_calls: list[AuditToolCall] = Field(description="Tools called, in order")
    stop_reason: str = Field(description="Why the run stopped: completed, usage_limit_exceeded, or error:<type>")


# ---- Product lookup tool results (Problem 6) -------------------------------
# Typed results the agent's database tools return. Everything here comes straight
# from campus_customs.db so the agent can quote real descriptions, prices, and
# stock and never has to make them up.


class ProductSearchHit(BaseModel):
    """One match from the search_products tool (a shortlist row, not full detail)."""

    product_id: str = Field(description="Use this id with the other tools and in AgentReply.product_ids")
    name: str
    price: float = Field(description="Price in USD, from catalogue.price")
    garment_type: str = Field(description="Raw garment type, lets the agent describe the kind of item")
    colors: list[str] = Field(description="Available colors, so the agent can match color requests")
    total_stock: int = Field(description="Units across all sizes; 0 means the whole product is sold out")


class ProductLookup(BaseModel):
    """Full detail for one product (get_product_details): description, price, and
    inventory by size — what the agent needs to answer detail/price questions."""

    product_id: str
    name: str
    garment_type: str
    price: float = Field(description="Price in USD, from catalogue.price; quote exactly")
    description: str = Field(description="Catalogue description, for 'what is it / what does it look like'")
    colors: list[str]
    total_stock: int = Field(description="Units across all sizes; 0 means sold out in every size")
    sizes: list[SizeStock] = Field(description="Stock per size XS→XXL; quantity 0 means that size is out of stock")


class SizeAvailability(BaseModel):
    """Result of check_size_stock: stock for one product in one size."""

    product_id: str
    name: str
    size: str = Field(description="The size checked, normalized to upper case (XS–XXL)")
    quantity: int = Field(description="Units in stock for this size, from inventory.quantity")
    in_stock: bool = Field(description="True if quantity > 0; if False the agent must say that size is out of stock")


class PriceRange(BaseModel):
    """Result of get_price_range: cheapest/most-expensive price for a category (or the
    whole store) in one call, so the agent can answer 'how much are X' without looking
    up every product."""

    category: str | None = Field(description="Category asked about, or None for the whole store")
    count: int = Field(description="How many products this covers")
    min_price: float = Field(description="Lowest price in USD")
    max_price: float = Field(description="Highest price in USD")
