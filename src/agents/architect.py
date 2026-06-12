"""
Architecture Agent

Responsible for analyzing infrastructure and generating architecture descriptions.
"""
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.prompts import SYSTEM_ARCHITECT_PROMPT


MERMAID_REPAIR_PROMPT = """You are a Mermaid.js syntax expert for Mermaid version 11.
The following Mermaid diagram code has syntax errors and fails to render.

BROKEN DIAGRAM:
```
{diagram}
```

Fix ONLY the syntax errors while preserving the original diagram's intent and structure.

COMMON ISSUES TO FIX:
- Unbalanced 'subgraph' / 'end' pairs
- Invalid arrow syntax (use -->, --o, -.->, ---|label|, -->|label|)
- Node IDs with spaces (must be quoted or use underscores)
- Missing semicolons or line breaks between statements
- Invalid characters in labels (escape parentheses inside node labels with quotes)
- 'flowchart TD' is preferred over 'graph TD'
- In sequenceDiagram: use ->> not --> for async, and -> for sync
- Avoid HTML tags inside labels

Return ONLY the fixed Mermaid code, no markdown fences, no explanation."""


def _validate_and_fix_mermaid(diagram: str, llm) -> str:
    """
    Validate a Mermaid diagram for common syntax issues.
    If issues are detected, use the LLM to repair the syntax.
    """
    lines = diagram.strip().splitlines()
    if not lines:
        return diagram

    # Quick syntax checks
    has_issues = False

    # Check 1: Balanced subgraph/end pairs
    subgraph_count = sum(1 for l in lines if l.strip().startswith("subgraph"))
    end_count = sum(1 for l in lines if l.strip() == "end")
    if subgraph_count != end_count:
        has_issues = True

    # Check 2: Common broken arrow patterns
    for line in lines:
        stripped = line.strip()
        # Detect malformed arrows like "-- >" or "- ->"
        if "-- >" in stripped or "- ->" in stripped:
            has_issues = True
            break
        # Detect unquoted labels with special chars in node definitions
        if "[" in stripped and "]" in stripped:
            # Check for unescaped parentheses inside brackets
            bracket_content = stripped[stripped.index("[") + 1:stripped.rindex("]")]
            if "(" in bracket_content and '"' not in bracket_content:
                has_issues = True
                break

    # Check 3: Diagram type declaration
    first_line = lines[0].strip().lower()
    valid_starts = ["flowchart", "graph", "sequencediagram", "statediagram", "classDiagram",
                    "erdiagram", "gantt", "pie", "gitgraph", "mindmap", "timeline",
                    "statediagram-v2"]
    if not any(first_line.startswith(s.lower()) for s in valid_starts):
        has_issues = True

    if not has_issues:
        return diagram

    # Use LLM to repair
    print("    [MERMAID] Syntax issues detected, attempting AI repair...")
    try:
        repair_prompt = MERMAID_REPAIR_PROMPT.replace("{diagram}", diagram)
        response = llm.invoke([HumanMessage(content=repair_prompt)])
        fixed = response.content.strip()
        # Strip markdown fences if the LLM included them anyway
        if fixed.startswith("```"):
            fixed = "\n".join(fixed.split("\n")[1:])
        if fixed.endswith("```"):
            fixed = "\n".join(fixed.split("\n")[:-1])
        if fixed.startswith("mermaid"):
            fixed = "\n".join(fixed.split("\n")[1:])
        print("    [MERMAID] Repair successful.")
        return fixed.strip()
    except Exception as e:
        print(f"    [MERMAID] Repair failed: {e}. Using original diagram.")
        return diagram


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
            raw_diagram = "\n".join(current_mermaid)
            # Validate and fix each diagram before storing
            fixed_diagram = _validate_and_fix_mermaid(raw_diagram, llm)
            mermaid_blocks.append(fixed_diagram)
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

