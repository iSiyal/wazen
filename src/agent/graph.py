from langgraph.graph import StateGraph, END
from agent.state import WazenState
from agent.nodes import (
    router_node,
    budgeting_agent_node,
    data_analyst_node,
    advisor_node,
    responder_node
)

def route_after_router(state: WazenState) -> str:
    """
    Determines which node to transition to based on intent.
    """
    intent = state.get("current_intent")
    if intent in ("log_transaction", "get_budget"):
        return "budgeting"
    elif intent == "get_spending_analysis":
        return "data_analyst"
    elif intent == "saving_advice":
        return "advisor"
    else:
        return "responder"

# Initialize StateGraph
builder = StateGraph(WazenState)

# Add all nodes
builder.add_node("router", router_node)
builder.add_node("budgeting", budgeting_agent_node)
builder.add_node("data_analyst", data_analyst_node)
builder.add_node("advisor", advisor_node)
builder.add_node("responder", responder_node)

# Set entry point
builder.set_entry_point("router")

# Define conditional routing from router
builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "budgeting": "budgeting",
        "data_analyst": "data_analyst",
        "advisor": "advisor",
        "responder": "responder"
    }
)

# Connect remaining nodes sequentially
builder.add_edge("budgeting", "data_analyst")
builder.add_edge("data_analyst", "advisor")
builder.add_edge("advisor", "responder")
builder.add_edge("responder", END)

# Compile graph
wazen_graph = builder.compile()
