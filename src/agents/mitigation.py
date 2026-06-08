"""
Mitigation Advisory Agent

Responsible for recommending security mitigations and code snippets.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import MITIGATION_ADVISOR_PROMPT


def mitigation_advisor_node(llm, state: AgentState) -> AgentState:
    """
    Mitigation advisor recommends technical controls and provides code snippets.
    """
    print("\n--- Agent: Mitigation Advisor ---")
    threats_stride = state["threats_stride"]
    impact_assessment = state["impact_assessment"]
    messages = state["messages"]

    mitigation_prompt = MITIGATION_ADVISOR_PROMPT + \
                        f"\n\nSTRIDE Threats:\n{threats_stride}" + \
                        f"\n\nImpact Assessment and MITRE ATT&CK:\n{impact_assessment}"

    response_message = llm.invoke([HumanMessage(content=mitigation_prompt)])
    mitigation_output = response_message.content

    return {
        "mitigations": mitigation_output,
        "messages": messages + [AIMessage(content=mitigation_output)]
    }
