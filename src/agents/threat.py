"""
Threat Identification Agent

Responsible for identifying security threats using STRIDE methodology.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import STRIDE_THREAT_IDENTIFIER_PROMPT


def stride_threat_identifier_node(llm, state: AgentState) -> AgentState:
    """
    STRIDE threat identifier analyzes architecture for security threats.
    """
    print("\n--- Agent: STRIDE Threat Identifier ---")
    architecture_desc = state["architecture_description"]
    mermaid_diagrams = "\n".join(state["mermaid_diagrams"])
    policies = state["corporate_policies"]
    messages = state["messages"]

    stride_prompt = STRIDE_THREAT_IDENTIFIER_PROMPT + \
                    f"\n\nArchitecture Description:\n{architecture_desc}" + \
                    f"\n\nMermaid Diagrams:\n{mermaid_diagrams}" + \
                    f"\n\nCorporate Policies:\n{policies}"

    response_message = llm.invoke([HumanMessage(content=stride_prompt)])
    stride_output = response_message.content

    return {
        "threats_stride": stride_output,
        "messages": messages + [AIMessage(content=stride_output)]
    }
