"""SQLite helpers shared by the API routes (main.py) and the agent tools (tools.py).

Both read products through these functions, so the product pages, the chat
product cards, and the prices/stock the agent quotes all come from the same
queries on data/campus_customs.db.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import PurePosixPath

from config import DB_PATH
from models import ChatHistoryMessage, ProductDetail, ProductSummary, SizeStock

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def image_url(image_file_path: str) -> str:
    """catalogue.image_file_path is 'products/<file>.jpg'; photos are served at /images/<file>."""
    return f"/images/{PurePosixPath(image_file_path).name}"


def short_description(description: str) -> str:
    first = description.split(". ")[0].rstrip(".")
    return first + "."


def category_of(garment_type: str) -> str:
    """Group the 22 inconsistent garment_type spellings into 5 shop categories
    (same grouping as frontend/src/categories.ts)."""
    kind = garment_type.lower()
    if "quarter-zip" in kind:
        return "quarter-zips"
    if "jacket" in kind:
        return "outerwear"
    if "hood" in kind:
        return "hoodies"
    if "crewneck" in kind or "mockneck" in kind:
        return "crewnecks"
    return "tees"


def inventory_for(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()
    stock = [SizeStock(size=r["size"], quantity=r["quantity"]) for r in rows]
    return sorted(stock, key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else len(SIZE_ORDER))


def to_summary(conn: sqlite3.Connection, row: sqlite3.Row) -> ProductSummary:
    inventory = inventory_for(conn, row["product_id"])
    return ProductSummary(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        price=row["price"],
        short_description=short_description(row["description"]),
        colors=json.loads(row["colors"]),
        image_url=image_url(row["image_file_path"]),
        total_stock=sum(s.quantity for s in inventory),
    )


def list_products() -> list[ProductSummary]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        return [to_summary(conn, row) for row in rows]


def get_product(product_id: str) -> ProductDetail | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None
        summary = to_summary(conn, row)
        return ProductDetail(
            **summary.model_dump(),
            description=row["description"],
            search_tags=json.loads(row["search_tags"]),
            inventory=inventory_for(conn, product_id),
        )


# ---- Users and chat history (Problem 8) ------------------------------------


def get_user(user_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def save_chat_message(user_id: int, role: str, content: str, products: list[ProductSummary] | None = None) -> None:
    """Persist one chat message for a logged-in customer. Assistant messages store
    the products shown with them (products_json) so they can be restored later."""
    products_json = json.dumps([p.model_dump() for p in products]) if products else None
    with connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()


def load_chat_history(user_id: int, limit: int = 100) -> list[ChatHistoryMessage]:
    """Load a logged-in customer's saved chat, oldest first (most recent `limit`)."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    rows.reverse()  # back to oldest-first
    history: list[ChatHistoryMessage] = []
    for row in rows:
        products = [ProductSummary(**p) for p in json.loads(row["products_json"])] if row["products_json"] else []
        history.append(ChatHistoryMessage(role=row["role"], content=row["content"], products=products))
    return history


def product_summaries(product_ids: list[str]) -> list[ProductSummary]:
    """Product summaries for the ids the agent chose, in order, deduped, built
    from the database (never from model text). Unknown ids are skipped. This is
    the SAME shape as GET /api/products, so the chat results render with the same
    ProductCard component as the Products page (Problem 7 handoff)."""
    summaries: list[ProductSummary] = []
    with connect() as conn:
        for product_id in dict.fromkeys(product_ids):  # dedupe, keep order
            row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
            if row is not None:
                summaries.append(to_summary(conn, row))
    return summaries
