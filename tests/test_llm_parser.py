"""
tests/test_llm_parser.py — LIVE integration tests for the LLM parser.

These tests make REAL API calls and require a valid API key in .env.
Run only manually:
    python -m pytest tests/test_llm_parser.py -v
or:
    python tests/test_llm_parser.py

They are intentionally excluded from the main unittest suite so CI
never blocks on missing credentials or network.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agent.llm_parser import parse_with_llm

# Each entry: (human_readable_label, message, expected_intent, expected_key_values)
TEST_CASES = [
    (
        "Electricity bill in colloquial Saudi",
        "سجلت فاتورة كهرباء بـ 250 ريال",
        "log_transaction",
        {"amount": 250.0, "type": "expense"},
    ),
    (
        "Cafe spend in dialect",
        "صرفت 45 ريال في كافيه اليوم",
        "log_transaction",
        {"amount": 45.0, "type": "expense"},
    ),
    (
        "Grocery shopping colloquial",
        "شريت مقاضي بـ 320 ريال",
        "log_transaction",
        {"amount": 320.0, "type": "expense"},
    ),
    (
        "Salary income",
        "جاني راتبي اليوم 8500 ريال",
        "log_transaction",
        {"amount": 8500.0, "type": "income"},
    ),
    (
        "Budget check",
        "كم باقي من ميزانيتي؟",
        "get_budget",
        {},
    ),
    (
        "Spending analysis",
        "اعرض لي تحليل مصاريفي الشهر هذا",
        "get_spending_analysis",
        {},
    ),
    (
        "Saving advice",
        "أبغى نصائح لأوفر أكثر",
        "saving_advice",
        {},
    ),
    (
        "English transaction",
        "I paid 150 SAR for internet bill",
        "log_transaction",
        {"amount": 150.0, "type": "expense"},
    ),
    (
        "Greeting (general)",
        "مرحبا",
        "general",
        {},
    ),
]


def run_live_tests():
    print("=" * 60)
    print("Wazen LLM Parser — Live Integration Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    for label, message, expected_intent, expected_keys in TEST_CASES:
        try:
            intent, extracted = parse_with_llm(message)
            ok = True

            if intent != expected_intent:
                print(f"\n❌  FAIL  [{label}]")
                print(f"     Message : {message}")
                print(f"     Intent  : got '{intent}', expected '{expected_intent}'")
                ok = False

            for k, v in expected_keys.items():
                if extracted.get(k) != v:
                    if ok:
                        print(f"\n❌  FAIL  [{label}]")
                        print(f"     Message : {message}")
                    print(f"     Field '{k}': got {extracted.get(k)!r}, expected {v!r}")
                    ok = False

            if ok:
                print(f"✅  PASS  [{label}]")
                print(f"          intent={intent}  extracted={extracted}")
                passed += 1
            else:
                failed += 1

        except Exception as exc:
            print(f"\n💥  ERROR [{label}]: {exc}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(TEST_CASES)}")
    print("=" * 60)


if __name__ == "__main__":
    run_live_tests()
