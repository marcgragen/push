"""
Architecture Agent

Responsible for analyzing infrastructure and generating architecture descriptions.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import SYSTEM_ARCHITECT_PROMPT


def system_architect_node(llm, tavily_tool, state: AgentState) -> AgentState:
    """
    System Architect agent analyzes infrastructure and generates architecture diagrams.
    
    Also detects when user needs to provide more information.
    """
    print("\n--- Agent: Systems Architect ---")
    query = state.get("query", "")
    messages = state.get("messages", [])
    messages.append(HumanMessage(content=f"Usuario: {query}"))
    
    # Load corporate policies
    policies = "Every DB must be in an isolated subnet. 2. Mandatory use of WAF for external traffic."

    architect_prompt_content = SYSTEM_ARCHITECT_PROMPT + f"\n\nThe application/system to be analyzed is: {query}"
    
    search_results_str = ""
    if tavily_tool and any(x in query.lower() for x in ["buscar", "arquitectura", "swagger", "manifest"]):
        print("    [INFO] Using Tavily to search for architecture information.")
        try:
            search_results = tavily_tool.invoke({"query": f"technical architecture of {query}"})
            search_results_str = f"\n\nRelevant search results:\n{search_results}"
        except Exception as e:
            print(f"    [WARNING] Error using Tavily: {e}. Continuing with no search results.")
            search_results_str = "\n\n[WARNING] The external search failed."

    final_architect_prompt = architect_prompt_content + search_results_str
    
    response_message = llm.invoke([HumanMessage(content=final_architect_prompt)])
    architecture_output = response_message.content

    mermaid_blocks = []

    # Detect when the model asks for more information from the user
    clarification_triggers = [
        "To provide an accurate analysis",
        "I'll need access to",
        "please provide",
        "please share",
        "I need",
        "Could you provide",
        "Can you provide",
        "Please supply",
        "need more information",
        "additional information",
        "more details",
        "clarification"
    ]

    requires_input = False
    user_request_text = ""
    lower_out = architecture_output.lower()
    for phrase in clarification_triggers:
        if phrase.lower() in lower_out:
            requires_input = True
            idx = lower_out.find(phrase.lower())
            user_request_text = architecture_output[idx:]
            break

    if requires_input:
        return {
            "requires_user_input": True,
            "user_request_text": user_request_text,
            "architecture_description": architecture_output,
            "raw_infra_data": query,
            "corporate_policies": policies,
            "mermaid_diagrams": mermaid_blocks,
            "messages": messages + [AIMessage(content=architecture_output)]
        }

    # Extract Mermaid diagrams
    current_mermaid = []
    in_mermaid_block = False
    for line in architecture_output.splitlines():
        if line.strip() == "```mermaid":
            in_mermaid_block = True
            current_mermaid = []
        elif line.strip() == "```" and in_mermaid_block:
            in_mermaid_block = False
            mermaid_blocks.append("\n".join(current_mermaid))
            current_mermaid = []
        elif in_mermaid_block:
            current_mermaid.append(line)

    # Remove Mermaid blocks from output for cleaner description
    architecture_description_clean = architecture_output
    for block in mermaid_blocks:
        architecture_description_clean = architecture_description_clean.replace(f"```mermaid\n{block}\n```", "").strip()

    return {
        "architecture_description": architecture_description_clean,
        "raw_infra_data": query,
        "corporate_policies": policies,
        "mermaid_diagrams": mermaid_blocks,
        "messages": messages + [AIMessage(content=architecture_output)]
    }
