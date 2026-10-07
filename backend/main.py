"""Campus Customs backend – FastAPI entry point.

Run from inside the backend/ folder:
    uvicorn main:app --reload --port 8000

Routes:
  * /api/products, /api/products/{id}  – catalogue + stock (Problem 3)
  * /api/auth/signup, /api/auth/login  – accounts (Problem 4)
  * /api/chat                          – chat with the PydanticAI agent (Problem 5)
Product photos from data/products/ are served under /images/<file>.
"""

from __future__ import annotations

import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import auth
import db
from agent import answer_customer
from config import FRONTEND_ORIGIN, PRODUCTS_DIR
from models import (
    ChatHistory,
    ChatRequest,
    ChatResponse,
    LoginRequest,
    ProductDetail,
    ProductSummary,
    SignupRequest,
    UserPublic,
)

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=PRODUCTS_DIR), name="images")


@app.get("/api/health")
def health() -> dict:
    with db.connect() as conn:
        products = conn.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    return {"status": "ok", "products": products}


# ---- Catalogue (Problem 3) -------------------------------------------------


@app.get("/api/products", response_model=list[ProductSummary])
def list_products() -> list[ProductSummary]:
    return db.list_products()


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    product = db.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---- Accounts (Problem 4) --------------------------------------------------


def user_public(row: sqlite3.Row) -> UserPublic:
    return UserPublic(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
    )


@app.post("/api/auth/signup", response_model=UserPublic, status_code=201)
def signup(body: SignupRequest) -> UserPublic:
    email = body.email.lower()
    password_hash = auth.hash_password(body.password)
    full_name = f"{body.first_name} {body.last_name}".strip()
    with db.connect() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, body.first_name, body.last_name),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return user_public(row)


@app.post("/api/auth/login", response_model=UserPublic)
def login(body: LoginRequest) -> UserPublic:
    email = body.email.lower()
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
        try:
            ok = auth.verify_password(body.password, row["password_hash"])
        except auth.LegacyIterationsUnknown:
            # Seeded course users: the iteration count for their legacy hash is
            # not available yet, so we cannot verify them (not a wrong password).
            raise HTTPException(
                status_code=503,
                detail=(
                    "This account uses a legacy password hash that can't be verified yet "
                    "(pending the course iteration count). New accounts work normally."
                ),
            )
        if not ok:
            raise HTTPException(status_code=401, detail="Incorrect email or password.")

        # Upgrade a legacy hash to the new self-describing format now that we have
        # the correct password in hand. Only reachable once legacy verification works.
        if auth.needs_migration(row["password_hash"]):
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (auth.hash_password(body.password), row["id"]),
            )
            conn.commit()
    return user_public(row)


# ---- Chat (Problem 5) ------------------------------------------------------


@app.get("/api/chat/history", response_model=ChatHistory)
def chat_history(user_id: int) -> ChatHistory:
    """Saved chat for a logged-in customer, so the widget can reload it on return.
    Returns an empty list for an unknown user."""
    if db.get_user(user_id) is None:
        return ChatHistory(messages=[])
    return ChatHistory(messages=db.load_chat_history(user_id))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Send the widget's conversation to the PydanticAI agent and return its
    reply plus any product cards it chose to show."""
    try:
        return await answer_customer(body)
    except Exception:  # noqa: BLE001 - surface a friendly message, log the detail
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail="The shopping assistant is having trouble right now. Please try again.",
        )
