"""The Campus Customs chat agent (Problems 5–8).

One PydanticAI agent running the course OpenAI model (config.MODEL) through the
Portkey gateway. Its system prompt is in prompts/prompt.md, its tools are in
tools.py, and it returns a structured models.AgentReply.

Problem 8 adds customer memory:
  * Who is chatting (name + email) and the page they're on are passed via agent
    deps (ChatDeps) and surfaced to the model with dynamic @instructions.
  * Logged-in customers' chat history is saved in chat_messages and replayed as
    message_history, so the conversation continues when they return. Guests can
    chat too, but nothing is persisted for them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pydantic_ai import Agent, RunContext, capture_run_messages
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.usage import UsageLimits

import audit
import db
from config import MODEL, PROMPTS_DIR, make_model
from models import AgentReply, ChatRequest, ChatResponse
from tools import check_size_stock, get_price_range, get_product_details, search_products

SYSTEM_PROMPT = (PROMPTS_DIR / "prompt.md").read_text(encoding="utf-8")


@dataclass
class ChatDeps:
    """What the agent knows about the current customer and page (Problem 8)."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    current_product_id: str | None = None
    current_product_name: str | None = None


# Keep one agent for the process. The model is created lazily on first use so the
# app can import without a Portkey key present (e.g. for the product/auth routes).
_agent: Agent[ChatDeps, AgentReply] | None = None

# Guard rails per reply: enough for a search plus per-product detail lookups on a
# handful of candidates, without allowing an endless loop.
USAGE_LIMITS = UsageLimits(request_limit=10, tool_calls_limit=18)


def get_agent() -> Agent[ChatDeps, AgentReply]:
    global _agent
    if _agent is None:
        _agent = Agent(
            make_model(),
            deps_type=ChatDeps,
            output_type=AgentReply,
            instructions=SYSTEM_PROMPT,
            tools=[search_products, get_product_details, check_size_stock, get_price_range],
            retries=2,
        )

        @_agent.instructions
        def who_is_chatting(ctx: RunContext[ChatDeps]) -> str:
            deps = ctx.deps
            if deps.first_name or deps.email:
                name = deps.first_name or "a customer"
                email = f" (email: {deps.email})" if deps.email else ""
                return f"You are chatting with {name}{email}, a signed-in customer. You may greet them by first name once."
            return "You are chatting with a guest (not signed in)."

        @_agent.instructions
        def current_page(ctx: RunContext[ChatDeps]) -> str:
            deps = ctx.deps
            if deps.current_product_id:
                name = deps.current_product_name or deps.current_product_id
                return (
                    f"RIGHT NOW the customer is on the product page for '{name}' "
                    f"(product_id: {deps.current_product_id}). If they say 'this', 'this one', 'it', or "
                    f"'this product' without naming something, they mean THIS product — the one on the page "
                    f"above — even if the earlier conversation was about a different item. Resolve such "
                    f"references to product_id '{deps.current_product_id}' and call get_product_details on it "
                    f"before answering about its colors, price, sizes, or stock."
                )
            return ""

    return _agent


def _to_history(turns: list[tuple[str, str]]) -> list[ModelMessage]:
    """Turn (role, content) pairs into PydanticAI message history."""
    history: list[ModelMessage] = []
    for role, content in turns:
        if role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=content)]))
    return history


async def answer_customer(request: ChatRequest) -> ChatResponse:
    latest = request.messages[-1].content

    # Who is chatting + current page -> agent deps.
    deps = ChatDeps(current_product_id=request.current_product_id)
    user_row = db.get_user(request.user_id) if request.user_id else None
    if user_row is not None:
        deps.first_name = user_row["first_name"]
        deps.last_name = user_row["last_name"]
        deps.email = user_row["email"]
    if request.current_product_id:
        product = db.get_product(request.current_product_id)
        deps.current_product_name = product.name if product else None

    # History: logged-in customers resume from the database; guests use the
    # conversation the widget sent (nothing persisted).
    if user_row is not None:
        prior = db.load_chat_history(request.user_id)
        history = _to_history([(m.role, m.content) for m in prior])
    else:
        history = _to_history([(m.role, m.content) for m in request.messages[:-1]])

    # Run the agent, capturing its messages so every run (success, usage-limit, or
    # error) can be written to the append-only audit trail.
    output: AgentReply | None = None
    stop_reason = "completed"
    who = deps.email or "guest"
    with capture_run_messages() as run_messages:
        try:
            result = await get_agent().run(
                latest,
                deps=deps,
                message_history=history or None,
                usage_limits=USAGE_LIMITS,
            )
            output = result.output
        except UsageLimitExceeded:
            stop_reason = "usage_limit_exceeded"
        except Exception as error:  # noqa: BLE001 - record then re-raise for the 502 handler
            stop_reason = f"error:{type(error).__name__}"
            raise
        finally:
            audit.record_run(latest, who, audit.tool_calls_from_messages(run_messages), stop_reason)

    if output is None:
        # The agent tried too many lookups for one question. Answer gracefully
        # instead of erroring, and nudge the customer to narrow it down.
        return ChatResponse(
            reply=(
                "That's a broad question, so I didn't want to guess. Could you narrow it down a little "
                "— a specific product, category (tees, crewnecks, hoodies, quarter-zips, jackets), or price range? "
                "Then I can give you exact prices and stock."
            ),
            products=[],
        )

    # Products are built from the database (never from model text) and match the
    # Problem 3 ProductSummary shape so the frontend reuses ProductCard.
    products = db.product_summaries(output.product_ids)

    # Persist this turn for logged-in customers so it reloads next time.
    if user_row is not None:
        db.save_chat_message(request.user_id, "user", latest)
        db.save_chat_message(request.user_id, "assistant", output.message, products)

    return ChatResponse(reply=output.message, products=products)


if __name__ == "__main__":  # quick manual check: python agent.py "your question"
    import asyncio
    import sys

    from models import ChatMessage

    question = " ".join(sys.argv[1:]) or "Do you have a navy hoodie in XL? How much is it?"
    print(f"model: {MODEL}\nquestion: {question}\n")
    out = asyncio.run(answer_customer(ChatRequest(messages=[ChatMessage(role="user", content=question)])))
    print("reply:", out.reply)
    print("cards:", [(c.product_id, c.price, c.total_stock) for c in out.products])
