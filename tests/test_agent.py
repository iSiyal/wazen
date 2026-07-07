import unittest
import sys
import os
from unittest.mock import patch

# Add src/ to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agent.db import DB_PATH, get_connection, init_db

# ── Offline mock for the LLM parser ───────────────────────────────────────────
# parse_with_llm is mocked before any agent code runs, so tests never make a
# real network call.  The mock mirrors the logic of the regex fallback, but
# returns exact deterministic values for each test message so assertions stay
# stable regardless of model behaviour.
_MOCK_PARSE_TABLE = {
    "سجلت فاتورة كهرباء بـ 250 ريال": ("log_transaction", {"amount": 250.0, "category": "Bills & Rent", "type": "expense"}),
    "صرفت 45 ريال في كافيه اليوم":    ("log_transaction", {"amount": 45.0,  "category": "Dining & Cafes",  "type": "expense"}),
    "كم باقي من ميزانيتي؟":           ("get_budget",      {"month": 7, "year": 2026}),
    "اعرض لي تحليل مصاريفي":          ("get_spending_analysis", {"days_back": 30}),
    "نصائح للادخار":                   ("saving_advice",   {}),
}

def _mock_parse(message: str):
    """Returns a deterministic (intent, extracted) for known test messages."""
    return _MOCK_PARSE_TABLE.get(message, ("general", {}))

# Patch at the nodes module level so router_node picks up the mock
_patcher = patch("agent.nodes.parse_with_llm", side_effect=_mock_parse)
_patcher.start()

# Import agent AFTER patching so the mock is in place during module load
from agent.main import run_wazen_agent  # noqa: E402


class TestWazenAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure database is clean
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except Exception as e:
                print(f"Could not remove database: {e}")
        init_db()

        # Setup initial budget for test month: July 2026
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO monthly_budget (month, year, \"limit\", currency) VALUES (?, ?, ?, ?)",
            (7, 2026, 4000.0, "SAR")
        )
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        _patcher.stop()
        # Clean up database after tests
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except Exception as e:
                print(f"Could not remove database: {e}")

    def test_01_log_transaction_needs(self):
        # 1. Log a utility bill (electricity) - Needs (الاحتياجات)
        history = []
        result = run_wazen_agent("سجلت فاتورة كهرباء بـ 250 ريال", history)
        history = result["messages"]

        self.assertIn("Success", result["response"])
        self.assertIn("250", result["response"])
        self.assertEqual(result["chart_data"]["budget_summary"]["total_spent"], 250.0)
        self.assertEqual(result["chart_data"]["budget_summary"]["total_budget"], 4000.0)
        self.assertEqual(result["chart_data"]["budget_summary"]["remaining_budget"], 3750.0)
        self.assertEqual(result["chart_data"]["datasets"][0]["data"][0], 250.0)  # Index 0 is Needs

    def test_02_log_transaction_wants(self):
        # 2. Log dining out / cafe - Wants (الرغبات)
        result = run_wazen_agent("صرفت 45 ريال في كافيه اليوم")

        self.assertIn("Success", result["response"])
        self.assertEqual(result["chart_data"]["budget_summary"]["total_spent"], 295.0)   # 250 + 45
        self.assertEqual(result["chart_data"]["datasets"][0]["data"][1], 45.0)           # Index 1 is Wants

    def test_03_get_budget(self):
        # 3. Ask for budget summary
        result = run_wazen_agent("كم باقي من ميزانيتي؟")

        self.assertIn("ميزانيتك", result["response"])
        self.assertEqual(result["chart_data"]["budget_summary"]["remaining_budget"], 3705.0)  # 4000 - 295

    def test_04_get_spending_analysis(self):
        # 4. Ask for spending categories analysis
        result = run_wazen_agent("اعرض لي تحليل مصاريفي")

        self.assertIn("تصنيفها", result["response"])
        self.assertEqual(result["chart_data"]["datasets"][0]["data"][0], 250.0)  # Needs
        self.assertEqual(result["chart_data"]["datasets"][0]["data"][1], 45.0)   # Wants

    def test_05_saving_advice(self):
        # 5. Ask for saving tips
        result = run_wazen_agent("نصائح للادخار")

        self.assertIn("رؤية السعودية 2030", result["response"])
        self.assertIn("10%", result["response"])


if __name__ == "__main__":
    unittest.main()
