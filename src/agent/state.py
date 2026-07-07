from typing import TypedDict, List, Dict, Any, Optional

class WazenState(TypedDict):
    """
    State definition for the Wazen Conversational Financial Agent.
    """
    messages: List[Dict[str, str]]
    """
    Conversation history. Each message is a dict with 'role' ('user' or 'assistant') 
    and 'content' (str).
    """
    
    current_intent: Optional[str]
    """
    Detected intent: e.g., 'log_transaction', 'get_budget', 'get_spending_analysis', 'saving_advice', 'general'
    """
    
    extracted_data: Dict[str, Any]
    """
    Data extracted from user message (e.g. amount, category, type, month, year, days_back).
    """
    
    budget_summary: Optional[Dict[str, Any]]
    """
    Summary of the budget (total_budget, total_spent, remaining_budget, currency).
    """
    
    category_spending: Optional[Dict[str, Any]]
    """
    Spending grouped by category (category -> sum).
    """
    
    savings_advice: Optional[str]
    """
    Educational advice tailored to the user's spending habits.
    """
    
    frontend_chart_data: Optional[Dict[str, Any]]
    """
    Structured data variables mapped for React and Chart.js frontend visualization.
    """
    
    response_text: Optional[str]
    """
    The main friendly text response from Wazen.
    """
