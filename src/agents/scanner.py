"""
Scanner Agents

Responsible for initial lightweight scanning and deep analysis.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState


def initial_scanner_node(llm_light, state: AgentState) -> AgentState:
    """
    Initial lightweight scanner to assess if deep analysis is needed.
    
    Detects:
    - Model-determined need for deep scan (insufficient information)
    - Manual deep scan triggers from user query
    """
    print("\n--- Agent: Initial Lightweight Scanner ---")
    query = state.get("query", "")
    messages = state.get("messages", [])

    # Check for manual deep scan triggers in user query
    deep_scan_triggers = [
        "deep scan", "thorough", "detailed analysis", "comprehensive", 
        "in-depth", "full scan", "complete analysis"
    ]
    manual_deep_scan = any(trigger.lower() in query.lower() for trigger in deep_scan_triggers)

    prompt = (
        "You are a fast local scanner. Provide a concise summary of the provided input "
        "with discovered components, endpoints, exposed ports, and any obvious misconfigurations. "
        "Consider complexity: insufficient information, vague descriptions, or incomplete data should indicate need for deeper analysis. "
        "Return a short human-readable summary and END with a line 'NEEDS_DEEP_SCAN: yes' or 'NEEDS_DEEP_SCAN: no'.\n\n"
        f"Input to scan:\n{query}\n"
    )

    try:
        response = llm_light.invoke([HumanMessage(content=prompt)])
        scan_output = response.content
    except Exception as e:
        scan_output = f"[LIGHT SCAN ERROR] {e}"

    needs_deep = False
    for line in scan_output.splitlines()[::-1]:
        if line.upper().startswith("NEEDS_DEEP_SCAN:"):
            needs_deep = "yes" in line.lower()
            break
    
    # Override with manual deep scan request
    if manual_deep_scan:
        needs_deep = True
        print("    [INFO] User requested deep scan via query keywords.")

    return {
        "scan_summary": scan_output,
        "needs_deep_scan": needs_deep,
        "raw_infra_data": scan_output if scan_output else query,
        "messages": messages + [AIMessage(content=scan_output)]
    }


def deep_analyzer_node(llm_deep, state: AgentState) -> AgentState:
    """
    Deep analyzer using powerful model for thorough analysis.
    
    Produces enriched infrastructure data suitable for automated architecture parsing.
    """
    print("\n--- Agent: Deep Analyzer (Powerful Model) ---")
    scan_summary = state.get("scan_summary", "")
    messages = state.get("messages", [])

    prompt = (
        "You are a deep analysis engine. Given the preliminary scan summary below, perform a thorough "
        "analysis extracting infrastructure, RBAC, network boundaries, OpenAPI/Swagger details, and produce "
        "an enriched raw_infra_data string suitable for automated architecture parsing.\n\n"
        f"Preliminary scan:\n{scan_summary}\n"
    )

    try:
        response = llm_deep.invoke([HumanMessage(content=prompt)])
        deep_output = response.content
    except Exception as e:
        deep_output = f"[DEEP SCAN ERROR] {e}"

    return {
        "deep_scan_results": deep_output,
        "raw_infra_data": deep_output or scan_summary,
        "messages": messages + [AIMessage(content=deep_output)]
    }
