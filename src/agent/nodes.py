from datetime import datetime
from agent.state import WazenState
from agent.tools import log_transaction_tool, get_budget_summary_tool, get_category_spending_tool
from agent.llm_parser import parse_with_llm

# --- Intent Classification and Parsing Helpers ---

CATEGORY_MAPPING = {
    # Needs
    "groceries": ("Groceries", "Needs"),
    "supermarket": ("Groceries", "Needs"),
    "market": ("Groceries", "Needs"),
    "مقاضي": ("Groceries", "Needs"),
    "سوبرماركت": ("Groceries", "Needs"),
    "أكل البيت": ("Groceries", "Needs"),
    "تموينات": ("Groceries", "Needs"),
    
    "rent": ("Bills & Rent", "Needs"),
    "bill": ("Bills & Rent", "Needs"),
    "bills": ("Bills & Rent", "Needs"),
    "electricity": ("Bills & Rent", "Needs"),
    "water": ("Bills & Rent", "Needs"),
    "internet": ("Bills & Rent", "Needs"),
    "mobile": ("Bills & Rent", "Needs"),
    "إيجار": ("Bills & Rent", "Needs"),
    "سكن": ("Bills & Rent", "Needs"),
    "كهرباء": ("Bills & Rent", "Needs"),
    "مويه": ("Bills & Rent", "Needs"),
    "ماء": ("Bills & Rent", "Needs"),
    "فاتورة": ("Bills & Rent", "Needs"),
    "فواتير": ("Bills & Rent", "Needs"),
    "نت": ("Bills & Rent", "Needs"),
    "جوال": ("Bills & Rent", "Needs"),
    "شحن": ("Bills & Rent", "Needs"),
    "قسط": ("Bills & Rent", "Needs"),
    
    "gas": ("Transport", "Needs"),
    "petrol": ("Transport", "Needs"),
    "car": ("Transport", "Needs"),
    "uber": ("Transport", "Needs"),
    "taxi": ("Transport", "Needs"),
    "transport": ("Transport", "Needs"),
    "بنزين": ("Transport", "Needs"),
    "سيارة": ("Transport", "Needs"),
    "توصيل": ("Transport", "Needs"),
    "مواصلات": ("Transport", "Needs"),
    "أوبر": ("Transport", "Needs"),
    "كريم": ("Transport", "Needs"),
    
    # Wants
    "cafe": ("Dining & Cafes", "Wants"),
    "coffee": ("Dining & Cafes", "Wants"),
    "restaurant": ("Dining & Cafes", "Wants"),
    "dining": ("Dining & Cafes", "Wants"),
    "lunch": ("Dining & Cafes", "Wants"),
    "dinner": ("Dining & Cafes", "Wants"),
    "breakfast": ("Dining & Cafes", "Wants"),
    "كافيه": ("Dining & Cafes", "Wants"),
    "قهوة": ("Dining & Cafes", "Wants"),
    "شاهي": ("Dining & Cafes", "Wants"),
    "حلا": ("Dining & Cafes", "Wants"),
    "مطعم": ("Dining & Cafes", "Wants"),
    "مطاعم": ("Dining & Cafes", "Wants"),
    "عشاء": ("Dining & Cafes", "Wants"),
    "غداء": ("Dining & Cafes", "Wants"),
    "فطور": ("Dining & Cafes", "Wants"),
    
    "cinema": ("Entertainment & Shopping", "Wants"),
    "movies": ("Entertainment & Shopping", "Wants"),
    "shopping": ("Entertainment & Shopping", "Wants"),
    "clothes": ("Entertainment & Shopping", "Wants"),
    "game": ("Entertainment & Shopping", "Wants"),
    "gaming": ("Entertainment & Shopping", "Wants"),
    "travel": ("Entertainment & Shopping", "Wants"),
    "vacation": ("Entertainment & Shopping", "Wants"),
    "سينما": ("Entertainment & Shopping", "Wants"),
    "ألعاب": ("Entertainment & Shopping", "Wants"),
    "ترفيه": ("Entertainment & Shopping", "Wants"),
    "شوبنق": ("Entertainment & Shopping", "Wants"),
    "تسوق": ("Entertainment & Shopping", "Wants"),
    "ملابس": ("Entertainment & Shopping", "Wants"),
    "سفر": ("Entertainment & Shopping", "Wants"),
    "رحلة": ("Entertainment & Shopping", "Wants"),
    
    # Savings
    "savings": ("Savings", "Savings"),
    "save": ("Savings", "Savings"),
    "investment": ("Savings", "Savings"),
    "stock": ("Savings", "Savings"),
    "stocks": ("Savings", "Savings"),
    "crypto": ("Savings", "Savings"),
    "gold": ("Savings", "Savings"),
    "ادخار": ("Savings", "Savings"),
    "توفير": ("Savings", "Savings"),
    "أسهم": ("Savings", "Savings"),
    "استثمار": ("Savings", "Savings"),
    "ذهب": ("Savings", "Savings"),
    "طوارئ": ("Savings", "Savings"),
    "حساب الادخار": ("Savings", "Savings")
}

# parse_user_message() has been replaced by the LLM-powered parse_with_llm()
# imported from agent.llm_parser. The function is kept here as a thin alias
# so any external callers that referenced it by name continue to work.


# --- Node Definitions ---

def router_node(state: WazenState) -> WazenState:
    """
    Analyses the user request via LLM-powered parsing and routes to the
    appropriate downstream agent node.
    """
    last_message = state["messages"][-1]["content"] if state["messages"] else ""

    # LLM-powered parsing (falls back to regex if API key is missing / call fails)
    intent, extracted = parse_with_llm(last_message)

    state["current_intent"] = intent
    state["extracted_data"] = extracted
    return state


def budgeting_agent_node(state: WazenState) -> WazenState:
    """
    Interacts with the SQL database to record transactions and pull budget summaries.
    """
    intent = state["current_intent"]
    data = state["extracted_data"]
    
    if intent == "log_transaction":
        amount = data.get("amount", 0.0)
        category = data.get("category", "Other")
        tx_type = data.get("type", "expense")
        
        # Call db log tool
        result_msg = log_transaction_tool(amount, category, tx_type)
        state["response_text"] = result_msg
        
        # Automatically refresh budget summary for current month
        now = datetime.now()
        state["budget_summary"] = get_budget_summary_tool(now.month, now.year)
        
    elif intent == "get_budget" or state["budget_summary"] is None:
        month = data.get("month", datetime.now().month)
        year = data.get("year", datetime.now().year)
        state["budget_summary"] = get_budget_summary_tool(month, year)
        
    return state


def data_analyst_node(state: WazenState) -> WazenState:
    """
    Queries spending over time and classifies them according to the 50/30/20 budgeting rule.
    """
    # Fetch trailing 30 days spending by default
    days_back = state["extracted_data"].get("days_back", 30)
    spending_by_cat = get_category_spending_tool(days_back)
    state["category_spending"] = spending_by_cat
    
    return state


def advisor_node(state: WazenState) -> WazenState:
    """
    Provides culturally aware savings recommendations mapped to Saudi Vision 2030 (10% target).
    """
    summary = state.get("budget_summary") or {}
    spending = state.get("category_spending") or {}
    
    total_spent = summary.get("total_spent", 0.0)
    total_budget = summary.get("total_budget", 0.0)
    
    # Simple advice algorithm based on 50/30/20 rules
    needs_total = 0.0
    wants_total = 0.0
    savings_total = 0.0
    
    # Classify categories from database
    for category_name, amount in spending.items():
        # Find category mapped bucket
        bucket = "Wants" # Default fallback
        for term, (std_cat, bct) in CATEGORY_MAPPING.items():
            if std_cat.lower() == category_name.lower():
                bucket = bct
                break
        
        if bucket == "Needs":
            needs_total += amount
        elif bucket == "Wants":
            wants_total += amount
        elif bucket == "Savings":
            savings_total += amount

    # Generate personalized cultural recommendation
    advice_parts = []
    
    if total_budget > 0:
        spending_rate = (total_spent / total_budget) * 100
        if spending_rate > 90:
            advice_parts.append(
                "يا صديقي، لقد اقتربت من استهلاك كامل ميزانيتك لهذا الشهر! ننصحك بالتركيز فقط على الاحتياجات الضرورية الآن وتأجيل الكماليات."
            )
        elif wants_total > (total_budget * 0.3):
            advice_parts.append(
                "لاحظنا زيادة في صرفيات الرغبات والترفيه (Wants) وتجاوزها لنسبة 30% المقترحة. خفض زيارات الكافيهات والمطاعم هذا الأسبوع سيساعدك على إعادة التوازن لميزانيتك."
            )
            
    # Include Saudi Vision 2030 context
    advice_parts.append(
        "تذكر دائماً أن الادخار خطوة ذكية لتحقيق الأمان المالي. نحن نسعى سوياً للمساهمة في تحقيق مستهدفات رؤية السعودية 2030 لرفع نسبة ادخار الأسر إلى 10%."
    )
    
    state["savings_advice"] = " ".join(advice_parts)
    return state


def responder_node(state: WazenState) -> WazenState:
    """
    Compiles final outputs into a warm user response and formats clean JSON charts for React/Chart.js.
    """
    intent = state["current_intent"]
    summary = state.get("budget_summary") or {"total_budget": 0.0, "total_spent": 0.0, "remaining_budget": 0.0, "currency": "SAR"}
    spending = state.get("category_spending") or {}
    advice = state.get("savings_advice") or "وازن هنا لمساعدتك دائماً في تنظيم مصاريفك وادخارك."
    
    # Standard values
    total_budget = summary.get("total_budget", 0.0)
    total_spent = summary.get("total_spent", 0.0)
    remaining = summary.get("remaining_budget", 0.0)
    currency = summary.get("currency", "SAR")
    
    # Categorization breakdown for Chart.js variables
    needs_total = 0.0
    wants_total = 0.0
    savings_total = 0.0
    
    for category_name, amount in spending.items():
        bucket = "Wants"
        for term, (std_cat, bct) in CATEGORY_MAPPING.items():
            if std_cat.lower() == category_name.lower():
                bucket = bct
                break
        if bucket == "Needs":
            needs_total += amount
        elif bucket == "Wants":
            wants_total += amount
        elif bucket == "Savings":
            savings_total += amount
            
    # Construct Chart.js compatible variables
    state["frontend_chart_data"] = {
        "chart_type": "doughnut",
        "labels": ["الاحتياجات (Needs)", "الرغبات (Wants)", "الادخار (Savings)"],
        "datasets": [
            {
                "data": [needs_total, wants_total, savings_total],
                "backgroundColor": ["#3182ce", "#dd6b20", "#38a169"]
            }
        ],
        "budget_summary": {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining_budget": remaining,
            "currency": currency
        }
    }
    
    # Synthesize conversational response based on intent
    if intent == "log_transaction":
        logged_msg = state.get("response_text", "")
        # If budget exists, display warm summary
        if total_budget > 0:
            arabic_res = (
                f"أهلاً بك! {logged_msg}\n\n"
                f"📊 مخلص سريع لميزانيتك:\n"
                f"- إجمالي الميزانية: {total_budget} {currency}\n"
                f"- المصروف حتى الآن: {total_spent} {currency}\n"
                f"- المتبقي لك: {remaining} {currency}\n\n"
                f"💡 نصيحة وازن:\n{advice}"
            )
        else:
            arabic_res = (
                f"سجلتها لك بكل سرور! {logged_msg}\n\n"
                f"💡 نصيحة وازن:\n{advice}"
            )
            
    elif intent == "get_budget":
        if total_budget > 0:
            arabic_res = (
                f"مرحباً بك! إليك تفاصيل ميزانيتك:\n"
                f"- الميزانية المحددة: {total_budget} {currency}\n"
                f"- ما تم صرفه: {total_spent} {currency}\n"
                f"- المبلغ المتبقي: {remaining} {currency}\n\n"
                f"💡 نصيحة وازن:\n{advice}"
            )
        else:
            arabic_res = (
                f"لم نجد ميزانية محددة لهذا الشهر بعد. يمكنك إضافة ميزانية لمتابعة صرفياتك بشكل أدق.\n\n"
                f"💡 نصيحة وازن:\n{advice}"
            )
            
    elif intent == "get_spending_analysis":
        category_lines = "\n".join([f"- {cat}: {amt} {currency}" for cat, amt in spending.items()])
        arabic_res = (
            f"أهلاً بك! إليك تفاصيل الصرف وتصنيفها:\n"
            f"{category_lines if category_lines else '- لم يتم تسجيل مصروفات للفترة المحددة.'}\n\n"
            f"💡 نصيحة وازن:\n{advice}"
        )
        
    elif intent == "saving_advice":
        arabic_res = (
            f"مرحباً بك! يسعدني تقديم النصيحة المالية لتنظيم ميزانيتك:\n\n"
            f"💡 {advice}"
        )
        
    else:
        # General welcoming response
        arabic_res = (
            "أهلاً بك! أنا وازن مساعدك المالي الذكي. 💼\n"
            "يمكنني مساعدتك في تسجيل مصروفاتك اليومية (مثل: 'صرفت 45 ريال في كافيه') ومتابعة ميزانيتك الشهرية والادخار.\n"
            "كيف يمكنني مساعدتك اليوم؟"
        )
        
    state["response_text"] = arabic_res
    return state
