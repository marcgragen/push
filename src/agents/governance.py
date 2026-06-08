"""
Governance and Certification Agent

Responsible for risk calculation and OTM report generation.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import GOVERNANCE_PROMPT


def governance_node(llm, state: AgentState) -> AgentState:
    """
    Governance engine calculates residual risk and generates OTM reports.
    """
    print("\n--- Agent: Governance and Scaling ---")
    messages = state["messages"]
    
    gov_prompt = GOVERNANCE_PROMPT + f"\n\nContext: {state['threats_stride']} \n {state['mitigations']}"
    response = llm.invoke([HumanMessage(content=gov_prompt)])
    
    # Simulate status assignment based on LLM logic
    status = "Approved" if "riesgo bajo" in response.content.lower() else "In Review"
    
    return {
        "otm_report": response.content,
        "status": status,
        "messages": messages + [AIMessage(content=f"Estado de Certificación: {status}")]
    }
