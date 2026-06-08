"""
Impact Assessment Agent

Responsible for assessing threat impact and MITRE ATT&CK mapping.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import IMPACT_ASSESSOR_PROMPT


def impact_assessor_node(llm, state: AgentState) -> AgentState:
    """
    Impact assessor evaluates threat severity and maps to MITRE ATT&CK framework.
    """
    print("\n--- Agent: Impact Assessor ---")
    threats_stride = state["threats_stride"]
    architecture_desc = state["architecture_description"]
    messages = state["messages"]

    impact_prompt = IMPACT_ASSESSOR_PROMPT + \
                    f"\n\nArchitecture:\n{architecture_desc}" + \
                    f"\n\nIdentified STRIDE Threats:\n{threats_stride}"

    response_message = llm.invoke([HumanMessage(content=impact_prompt)])
    impact_output = response_message.content

    # Simple extraction of MITRE ATT&CK references
    mitre_refs = []
    for line in impact_output.splitlines():
        if "T" in line and "(" in line and ")" in line:  # Heuristic for T codes
            mitre_refs.append(line)

    return {
        "impact_assessment": impact_output,
        "mitre_attack_references": mitre_refs,
        "messages": messages + [AIMessage(content=impact_output)]
    }
