"""Tools the Campus Customs agent can call (Problems 5–6).

Every tool reads the live catalogue/inventory in campus_customs.db through db.py,
so the descriptions, prices, and stock the agent quotes always match the product
pages and are never made up. Each returns a typed model from models.py:

    search_products       -> list[ProductSearchHit]   (find products)
    get_product_details   -> ProductLookup            (description, price, inventory)
    check_size_stock      -> SizeAvailability          (stock for one size)

On bad input (unknown product_id or size) a tool raises ModelRetry so the agent
is told what went wrong and can correct itself (e.g. search again) instead of
guessing.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher

from pydantic_ai import ModelRetry

from db import category_of, connect, get_product
from models import PriceRange, ProductLookup, ProductSearchHit, SizeAvailability

# Shop categories the agent can filter by (see db.category_of / frontend categories.ts)
CATEGORIES = ["tees", "crewnecks", "hoodies", "quarter-zips", "outerwear"]

# How close a word must be to count as a typo match (0..1). 0.8 catches "hodie"->
# "hoodie", "harvad"->"harvard" without matching unrelated words.
FUZZY_THRESHOLD = 0.8


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _match_score(query_tokens: list[str], haystack: str) -> float | None:
    """Return a relevance penalty (lower = better) if every query token matches the
    haystack by substring (exact/partial) or close fuzzy match (small typos), else
    None if any token can't be matched at all."""
    haystack_tokens = set(_tokens(haystack))
    penalty = 0.0
    for token in query_tokens:
        if token in haystack:  # exact or partial (substring), e.g. "hood" in "hoodie"
            continue
        best = max((SequenceMatcher(None, token, ht).ratio() for ht in haystack_tokens), default=0.0)
        if len(token) >= 4 and best >= FUZZY_THRESHOLD:  # small typo, e.g. "hodie"
            penalty += 1.0 - best
        else:
            return None
    return penalty


def search_products(query: str = "", category: str | None = None, limit: int = 8) -> list[ProductSearchHit]:
    """Find products in the Campus Customs catalogue.

    Matching is forgiving: each word in `query` matches a product by exact text,
    partial text (e.g. "hood" finds hoodies), or a close fuzzy match for small
    typos (e.g. "hodie", "harvad"). Words are checked against the product name,
    colors, garment type, and search tags.

    query: what the customer typed (e.g. "navy hoodie", "harvad", "fleece"). Empty = browse.
    category: optional filter, one of tees, crewnecks, hoodies, quarter-zips, outerwear.
    Returns up to `limit` matches, best/closest and in-stock first. Use a hit's
    product_id with get_product_details / check_size_stock and in product_ids.
    """
    query_tokens = _tokens(query)
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        stock = dict(
            conn.execute("SELECT product_id, COALESCE(SUM(quantity),0) FROM inventory GROUP BY product_id").fetchall()
        )

    scored: list[tuple[float, ProductSearchHit]] = []
    for row in rows:
        if category and category_of(row["garment_type"]) != category:
            continue
        haystack = f"{row['name']} {row['garment_type']} {row['colors']} {row['search_tags']}".lower()
        penalty = _match_score(query_tokens, haystack) if query_tokens else 0.0
        if penalty is None:
            continue
        scored.append(
            (
                penalty,
                ProductSearchHit(
                    product_id=row["product_id"],
                    name=row["name"],
                    price=row["price"],
                    garment_type=row["garment_type"],
                    colors=json.loads(row["colors"]),
                    total_stock=stock.get(row["product_id"], 0),
                ),
            )
        )
    # Closest match first, then in-stock, then cheaper.
    scored.sort(key=lambda item: (item[0], item[1].total_stock == 0, item[1].price))
    return [hit for _, hit in scored[: max(1, min(limit, 12))]]


def get_product_details(product_id: str) -> ProductLookup:
    """Full details for one product: description, price, colors, and stock for
    every size (XS–XXL). Use this whenever a customer asks what a product is,
    what it looks like, how much it costs, or which sizes are available."""
    product = get_product(product_id)
    if product is None:
        raise ModelRetry(
            f"No product has id '{product_id}'. Use search_products to find the correct product_id first."
        )
    return ProductLookup(
        product_id=product.product_id,
        name=product.name,
        garment_type=product.garment_type,
        price=product.price,
        description=product.description,
        colors=product.colors,
        total_stock=product.total_stock,
        sizes=product.inventory,
    )


def check_size_stock(product_id: str, size: str) -> SizeAvailability:
    """Check how many units of a product are in stock in one size (e.g. "M", "XL").
    `in_stock` is False when that size is sold out — tell the customer clearly and
    suggest an in-stock size or a similar product."""
    product = get_product(product_id)
    if product is None:
        raise ModelRetry(
            f"No product has id '{product_id}'. Use search_products to find the correct product_id first."
        )
    wanted = size.strip().upper()
    for item in product.inventory:
        if item.size.upper() == wanted:
            return SizeAvailability(
                product_id=product_id,
                name=product.name,
                size=item.size,
                quantity=item.quantity,
                in_stock=item.quantity > 0,
            )
    available = ", ".join(s.size for s in product.inventory)
    raise ModelRetry(f"'{size}' is not a valid size for {product.name}. Valid sizes: {available}.")


def get_price_range(category: str | None = None) -> PriceRange:
    """Cheapest and most-expensive price (and product count) for a category
    (tees, crewnecks, hoodies, quarter-zips, outerwear) or the whole store if no
    category is given. Use this in ONE call for "how much are X", price-range, or
    cheapest/most-expensive questions instead of looking products up one by one."""
    with connect() as conn:
        rows = conn.execute("SELECT garment_type, price FROM catalogue").fetchall()
    prices = [r["price"] for r in rows if not category or category_of(r["garment_type"]) == category]
    if not prices:
        raise ModelRetry(f"'{category}' is not a valid category. Valid categories: {', '.join(CATEGORIES)}.")
    return PriceRange(category=category, count=len(prices), min_price=min(prices), max_price=max(prices))
