"""
Graph Workflow Construction

Builds the LangGraph state machine for threat modeling.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState
from src.config import initialize_models
from src.tools import initialize_tools
from src.agents import (
    initial_scanner_node,
    deep_analyzer_node,
    system_architect_node,
    stride_threat_identifier_node,
    impact_assessor_node,
    mitigation_advisor_node,
    governance_node,
    user_input_collection_node,
    final_report_node,
)
from src.routing import (
    route_after_scan,
    route_after_architect,
    route_after_user_input,
)


def build_workflow(models: dict, tools: dict):
    """
    Build the complete threat modeling workflow graph.
    
    Args:
        models: Dictionary of initialized LLM models
        tools: Dictionary of initialized tools (Tavily, etc.)
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(AgentState)
    
    # Extract models and tools
    llm = models["llm"]
    llm_light = models["llm_light"]
    llm_deep = models["llm_deep"]
    tavily_tool = tools.get("tavily_tool")
    
    # Create node wrappers with dependencies injected
    def initial_scanner_wrapper(state):
        return initial_scanner_node(llm_light, state)
    
    def deep_analyzer_wrapper(state):
        return deep_analyzer_node(llm_deep, state)
    
    def system_architect_wrapper(state):
        return system_architect_node(llm, tavily_tool, state)
    
    def stride_threat_wrapper(state):
        return stride_threat_identifier_node(llm, state)
    
    def impact_assessor_wrapper(state):
        return impact_assessor_node(llm, state)
    
    def mitigation_advisor_wrapper(state):
        return mitigation_advisor_node(llm, state)
    
    def governance_wrapper(state):
        return governance_node(llm, state)
    
    # Add all nodes to workflow
    workflow.add_node("initial_scanner", initial_scanner_wrapper)
    workflow.add_node("deep_analyzer", deep_analyzer_wrapper)
    workflow.add_node("user_input_collection", user_input_collection_node)
    workflow.add_node("system_architect", system_architect_wrapper)
    workflow.add_node("stride_threat_identifier", stride_threat_wrapper)
    workflow.add_node("impact_assessor", impact_assessor_wrapper)
    workflow.add_node("mitigation_advisor", mitigation_advisor_wrapper)
    workflow.add_node("governance_node", governance_wrapper)
    workflow.add_node("final_report", final_report_node)
    
    # Define execution flow with conditional edges
    workflow.set_entry_point("initial_scanner")
    
    workflow.add_conditional_edges(
        "initial_scanner",
        route_after_scan,
        {
            "deep_analyzer": "deep_analyzer",
            "system_architect": "system_architect"
        }
    )
    
    workflow.add_edge("deep_analyzer", "system_architect")
    
    workflow.add_conditional_edges(
        "system_architect",
        route_after_architect,
        {
            "user_input_collection": "user_input_collection",
            "stride_threat_identifier": "stride_threat_identifier"
        }
    )
    
    workflow.add_conditional_edges(
        "user_input_collection",
        route_after_user_input,
        {
            "system_architect": "system_architect"
        }
    )
    
    workflow.add_edge("stride_threat_identifier", "impact_assessor")
    workflow.add_edge("impact_assessor", "mitigation_advisor")
    workflow.add_edge("mitigation_advisor", "governance_node")
    workflow.add_edge("governance_node", "final_report")
    workflow.add_edge("final_report", END)
    
    # Compile with memory checkpoint
    memoria = MemorySaver()
    app = workflow.compile(checkpointer=memoria)
    
    return app
