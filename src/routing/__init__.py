"""
Conditional Routing Logic

Defines intelligent routing between graph nodes based on state.
"""
from typing import Literal
from src.state import AgentState


def route_after_scan(state: AgentState) -> Literal["deep_analyzer", "system_architect"]:
    """
    Route to deep analyzer if needed, otherwise go to system architect.
    
    Decision based on:
    - needs_deep_scan flag from initial scanner
    """
    if state.get("needs_deep_scan"):
        print("    [ROUTING] Deep scan needed - routing to deep_analyzer...")
        return "deep_analyzer"
    return "system_architect"


def route_after_architect(state: AgentState) -> Literal["user_input_collection", "stride_threat_identifier"]:
    """
    Route to user input collection if more information is needed.
    
    Decision based on:
    - requires_user_input flag from system architect
    """
    if state.get("requires_user_input"):
        print("    [ROUTING] User input required - routing to user_input_collection...")
        return "user_input_collection"
    return "stride_threat_identifier"


def route_after_user_input(state: AgentState) -> Literal["system_architect"]:
    """
    After collecting user input, go back to system architect for re-analysis.
    """
    print("    [ROUTING] User input collected - returning to system_architect for re-analysis...")
    return "system_architect"
