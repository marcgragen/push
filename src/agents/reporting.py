"""
User Input Collection Agent

Responsible for collecting additional information when model requests it.
"""
from langchain_core.messages import HumanMessage
from src.state import AgentState


def user_input_collection_node(state: AgentState) -> AgentState:
    """
    Node that prompts user for additional information when requested by the architect.
    """
    print("\n--- Agent: Waiting for User Input ---")
    user_request_text = state.get("user_request_text", "")
    
    print(f"\nAgent needs additional information:\n{user_request_text}")
    user_add = input("\nYou (provide requested info): ")
    
    messages = state.get("messages", [])
    raw_infra = state.get("raw_infra_data", "")
    
    return {
        "requires_user_input": False,
        "user_request_text": "",
        "messages": messages + [HumanMessage(content=user_add)],
        "raw_infra_data": (raw_infra or "") + "\n[USER PROVIDED ADDITIONAL INFO]\n" + user_add
    }
