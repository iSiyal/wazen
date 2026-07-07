"""
llm_parser.py — LLM-powered intent parser for Wazen (وازن).

Replaces the regex/keyword approach in nodes.py with a structured LLM call
that natively understands Modern Standard Arabic, English, and colloquial
Saudi dialect (e.g. صرفت، مقاضي، كافيه، قسط).

Provider is configured entirely via .env:
  LLM_API_KEY   — your API key (OpenAI or Gemini)
  LLM_BASE_URL  — OpenAI-compatible endpoint base URL
  LLM_MODEL     — model name (e.g. gemini-2.0-flash or gpt-4o-mini)

The public interface exposed to nodes.py is a single function:
  parse_with_llm(message: str) -> tuple[str, dict]
which returns the same (intent, extracted_data) shape that the old
parse_user_message() returned, so nothing else in the codebase changes.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

_API_KEY  = os.getenv("LLM_API_KEY", "")
_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
_MODEL    = os.getenv("LLM_MODEL",    "gpt-4o-mini")

# ── Pydantic schema for structured LLM output ────────────────────────────────

class ParsedIntent(BaseModel):
    """
    Structured output schema returned by the LLM.
    Every field except `intent` is optional because not every user message
    contains all pieces of information.
    """

    intent: Literal[
        "log_transaction",
        "get_budget",
        "get_spending_analysis",
        "saving_advice",
        "general",
    ] = Field(
        description=(
            "The primary intent of the user message. "
            "Use 'log_transaction' when the user mentions spending or earning money. "
            "Use 'get_budget' when the user asks about their remaining budget or limits. "
            "Use 'get_spending_analysis' when the user wants a breakdown or chart of spending. "
            "Use 'saving_advice' when the user asks for saving tips or financial guidance. "
            "Use 'general' for greetings or anything else."
        )
    )

    amount: Optional[float] = Field(
        default=None,
        description=(
            "The monetary amount mentioned by the user (as a positive float). "
            "Extract it even if written in Arabic (e.g. '٢٥٠ ريال' → 250.0). "
            "Null if no amount is mentioned."
        ),
    )

    category: Optional[str] = Field(
        default=None,
        description=(
            "The standardised English spending category. "
            "Must be one of: 'Groceries', 'Bills & Rent', 'Transport', "
            "'Dining & Cafes', 'Entertainment & Shopping', 'Savings', 'Salary', 'Other'. "
            "Infer from context (e.g. 'كافيه' → 'Dining & Cafes', 'كهرباء' → 'Bills & Rent'). "
            "Null if intent is not 'log_transaction'."
        ),
    )

    bucket: Optional[Literal["Needs", "Wants", "Savings", "Income"]] = Field(
        default=None,
        description=(
            "The 50/30/20 budget bucket this transaction belongs to: "
            "'Needs' (rent, bills, transport, groceries), "
            "'Wants' (dining, cafes, entertainment, shopping), "
            "'Savings' (investments, savings accounts, emergency fund), "
            "'Income' (salary or any earnings). "
            "Null if intent is not 'log_transaction'."
        ),
    )

    transaction_type: Optional[Literal["expense", "income"]] = Field(
        default=None,
        description=(
            "'income' if the user is recording money received (e.g. salary, freelance). "
            "'expense' for all spending. "
            "Null if intent is not 'log_transaction'."
        ),
    )

    month: Optional[int] = Field(
        default=None,
        description=(
            "The Gregorian month number (1–12) the user is asking about. "
            "Infer from Arabic month names if present (e.g. 'يوليو' → 7). "
            "Null if not explicitly mentioned — the caller will default to the current month."
        ),
    )

    year: Optional[int] = Field(
        default=None,
        description=(
            "The 4-digit Gregorian year the user is asking about. "
            "Null if not explicitly mentioned — caller defaults to the current year."
        ),
    )

    days_back: Optional[int] = Field(
        default=None,
        description=(
            "For 'get_spending_analysis', how many trailing days to include. "
            "Infer from phrases like 'آخر أسبوع' (7) or 'الشهر الماضي' (30). "
            "Null if not specified — caller defaults to 30."
        ),
    )


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """
You are the intent-parsing engine for Wazen (وازن), a personal finance assistant
for Saudi individuals. Your ONLY job is to analyse the user's message and return a
structured JSON object — nothing else, no explanations, no markdown fences.

The user may write in:
  • Modern Standard Arabic (فصحى)
  • Colloquial Saudi Arabic (e.g. صرفت، مقاضي، كافيه، قسط، بنزين، شريت، جاني)
  • English
  • A mix of all three

Category reference (use these exact English strings in "category"):
  Needs:   "Groceries" | "Bills & Rent" | "Transport"
  Wants:   "Dining & Cafes" | "Entertainment & Shopping"
  Savings: "Savings"
  Income:  "Salary"
  Default: "Other"

Current date context: {today}

Return ONLY the JSON object matching the schema. No extra keys, no markdown.
""".strip()


# ── LLM client initialisation ─────────────────────────────────────────────────

def _build_llm() -> ChatOpenAI:
    """Builds the ChatOpenAI client from environment variables."""
    return ChatOpenAI(
        model=_MODEL,
        api_key=_API_KEY,          # type: ignore[arg-type]
        base_url=_BASE_URL,
        temperature=0,             # deterministic parsing
        max_tokens=256,            # schema is small — no need for more
    )


# ── Regex fallback (original logic, kept as safety net) ───────────────────────

def _fallback_parse(message: str) -> tuple[str, dict]:
    """
    Fast regex fallback used when the LLM call fails (network error, quota, etc.).
    Mirrors the original parse_user_message() logic so the agent degrades
    gracefully rather than crashing.
    """
    message_lc = message.lower()
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", message_lc)

    log_kw     = ["صرفت","سجلت","دفعت","شريت","اشتريت","قسط","فاتورة","فواتير",
                  "spent","paid","bought","transaction","expense","income","دخل","راتب"]
    budget_kw  = ["ميزانية","كم باقي","رصيد","كم وفرت","كم صرفت",
                  "budget","remaining","limit","summary"]
    analysis_kw= ["تحليل","تقرير","توزيع","تصنيف","رسم بياني",
                  "analysis","report","spending","categories","chart"]
    advice_kw  = ["نصيحة","ادخار","نصائح","وفر","توفير",
                  "advice","saving","save","tips"]
    income_kw  = ["راتب","دخل","salary","income","جاني"]

    is_log      = any(kw in message_lc for kw in log_kw) or "ريال" in message_lc or "sar" in message_lc
    is_budget   = any(kw in message_lc for kw in budget_kw)
    is_analysis = any(kw in message_lc for kw in analysis_kw)
    is_advice   = any(kw in message_lc for kw in advice_kw)

    now = datetime.now()

    if is_log and numbers:
        is_income = any(kw in message_lc for kw in income_kw)
        return "log_transaction", {
            "amount": float(numbers[0]),
            "category": "Salary" if is_income else "Other",
            "type": "income" if is_income else "expense",
        }
    if is_analysis:
        return "get_spending_analysis", {"days_back": int(numbers[0]) if numbers else 30}
    if is_budget:
        return "get_budget", {
            "month": int(numbers[0]) if numbers and 1 <= int(numbers[0]) <= 12 else now.month,
            "year":  int(numbers[1]) if len(numbers) > 1 and int(numbers[1]) > 2000 else now.year,
        }
    if is_advice:
        return "saving_advice", {}

    return "general", {}


# ── Public interface ──────────────────────────────────────────────────────────

def parse_with_llm(message: str) -> tuple[str, dict]:
    """
    Parses a user message using an LLM with structured output.

    Returns the same (intent, extracted_data) tuple that the old
    parse_user_message() returned, so router_node in nodes.py needs
    only a one-line import change.

    Falls back to _fallback_parse() if the LLM is unavailable.
    """
    # Guard: if no API key configured, go straight to fallback
    if not _API_KEY or _API_KEY == "your_api_key_here":
        return _fallback_parse(message)

    try:
        llm = _build_llm()
        structured_llm = llm.with_structured_output(ParsedIntent)

        system_prompt = _SYSTEM_PROMPT.format(today=datetime.now().strftime("%Y-%m-%d"))
        result: ParsedIntent = structured_llm.invoke([
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": message},
        ])

        # ── Map ParsedIntent → extracted_data dict ────────────────────────────
        now = datetime.now()
        extracted: dict = {}

        if result.intent == "log_transaction":
            extracted["amount"]   = result.amount   or 0.0
            extracted["category"] = result.category or "Other"
            extracted["type"]     = result.transaction_type or "expense"

        elif result.intent == "get_budget":
            extracted["month"] = result.month or now.month
            extracted["year"]  = result.year  or now.year

        elif result.intent == "get_spending_analysis":
            extracted["days_back"] = result.days_back or 30

        return result.intent, extracted

    except Exception as exc:   # noqa: BLE001
        # Log the error but never crash the agent
        print(f"[Wazen LLM Parser] LLM call failed — using fallback. Reason: {exc}")
        return _fallback_parse(message)
