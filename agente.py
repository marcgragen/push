import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated, Union
import operator

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

try:
    # Attempting official import of the new package
    from langchain_tavily import TavilySearchResults
    from langchain_core.runnables import RunnableConfig # Required for Tavily
except ImportError:
    # Safety fallback if the integration package fails in Python 3.14
    print("[SYSTEM] Notice: Using search fallback due to environment incompatibility.")
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_core.runnables import RunnableConfig # Required for Tavily

# 1. Load hidden environment variables
load_dotenv()

print("[SYSTEM] Configuring models with quota failover support...")

llm_primary = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

llm_fallback = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-8b", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

llm_local = ChatOllama(
    model="llama3.2",  # Recommended model for performance/speed on M4
    temperature=0
)

# We couple the fallback: First try Gemini Flash, then Gemini Flash-8b, 
# and finally resort to the local model on your Mac Mini M4.
llm = llm_primary.with_fallbacks([llm_fallback, llm_local])

# Lightweight vs Deep LLMs for Two-Phase Scanning
# `llm_light` is used for quick, local scans; `llm_deep` uses cloud models for heavier analysis.
llm_light = llm_local
llm_deep = llm

# --- AgentState Definition ---
class AgentState(TypedDict):
    """
    Represents the shared state among agents in the graph.
    """
    query: str
    raw_infra_data: str  # Ingestion of IaC (K8s, Terraform), OpenAPI or Scans
    corporate_policies: str  # Internal policies and compliance rules
    architecture_description: str
    threats_stride: str
    impact_assessment: str
    mitigations: str
    otm_report: str  # Report in Open Threat Model (JSON) format
    status: str  # Draft -> In Review -> Approved
    mermaid_diagrams: Annotated[List[str], operator.add]
    mitre_attack_references: Annotated[List[str], operator.add]
    messages: Annotated[List[BaseMessage], operator.add]
    scan_summary: str
    needs_deep_scan: bool
    deep_scan_results: str
    requires_user_input: bool
    user_request_text: str

# --- Tools Setup ---
tavily_tool = None
if os.getenv("TAVILY_API_KEY"):
    tavily_tool = TavilySearchResults(max_results=3)
else: # Prevents the agent from failing at startup if the key is missing, simply disables search
    print("[WARNING] TAVILY_API_KEY not configured. The agent will not have internet access.") 


# --- Agent Prompts ---
SYSTEM_ARCHITECT_PROMPT = """
You are a System Architect expert in "Zero-Friction" Ingestion. Your task is to parse infrastructure and code.
Ingestion Capabilities:
1. IaC: Analyze K8s manifests, RBAC, Dockerfiles, and Terraform. Identify components and networks. 
2. APIs: Read Swagger/OpenAPI files to extract endpoints and authentication methods.
3. Scanners: Integrate results from Trivy/Kubiscan if provided.

If the information is insufficient, request more details.
Your goal is to generate a detailed description of the architecture and, most importantly, a Mermaid.js diagram of type 'flowchart TD' representing trust boundaries (using 'subgraph') and data flows (labeling protocols).

DIAGRAMMING CAPABILITIES (MERMAID.JS):
1. Trust Boundaries: Use 'subgraph' to visually isolate components by network level (Internet, DMZ, Internal Network, DB). 
2. Dynamic DFDs (flowchart TD/LR): Label arrows with protocols (|HTTPS/REST|, |SQL via TLS 1.2|). Identify insecure flows. 
3. Authentication Sequences (sequenceDiagram): For Login, OAuth, or OIDC flows, showing JWT/Token exchange between User, App, and IdP. 
4. RBAC and K8s Policies: Visualize relationships between ServiceAccount, RoleBinding, and Pods from infrastructure descriptions. 
5. Data Life Cycles (stateDiagram-v2): Map data sensitivity states (Public -> Confidential -> Encrypted). 

SYNTAX RULES:
- Use `flowchart TD` for general architectures. 
- Components: `[ ]` for processes/apps, `[( )]` for DBs, `(( ))` for external entities or users. 
- All diagrams must be delivered in markdown code blocks for automatic rendering. 

Mermaid output example:
```mermaid
flowchart TD
    Client((External User))

    subgraph Corporate DMZ
        WAF[Web Application Firewall]
        App[Internal Application]
    end

    subgraph Secure Internal Network
        DB[(PostgreSQL)]
    end

    Client --o|HTTPS| WAF
    WAF --o|Proxy| App
    App --o|TCP 5432| DB
```
Asegúrate de que el diagrama sea completo y represente fielmente la arquitectura.
"""

STRIDE_THREAT_IDENTIFIER_PROMPT = """
You are a security expert specialized in the STRIDE methodology for threat modeling.
Your task is to analyze the architecture description and Mermaid diagrams provided by the System Architect.
Identify specific threats using STRIDE categories and contrasting them with corporate policies.
Label each threat with its corresponding CWE (Common Weakness Enumeration).

STRIDE table format:
| Threat ID | Component | Category | CWE | Description (Policy Compliance) |
|---|---|---|---|---|
| T-001 | Authentication | Spoofing | CWE-287 | An attacker could impersonate identity. |
| T-002 | DB | Info Disclosure | CWE-311 | Data exposed without encryption. |
"""

IMPACT_ASSESSOR_PROMPT = """
You are a Security Risk Analyst with experience in MITRE ATT&CK.
Your task is to assess the potential impact of each identified STRIDE threat, assigning a risk level (High, Medium, Low).
Additionally, for each threat, identify and reference relevant MITRE ATT&CK tactics and techniques.
Generate a Markdown table that combines the STRIDE information with the impact assessment and MITRE ATT&CK references.

Impact and MITRE ATT&CK table format:
| Threat ID | Risk Level | Potential Impact | MITRE ATT&CK Tactics | MITRE ATT&CK Techniques |
|---|---|---|---|---|
| T-001 | High | Unauthorized access, data loss. | Credential Access, Persistence | T1078 (Valid Accounts), T1098 (Account Manipulation) |
| T-002 | Medium | Sensitive information leakage, regulatory fines. | Exfiltration, Collection | T1041 (Exfiltration Over C2 Channel), T1005 (Data from Local System) |
"""

MITIGATION_ADVISOR_PROMPT = """
You are a DevSecOps Security Mitigation Advisor.
For each threat, you must provide a technical mitigation and a CODE SNIPPET or configuration (YAML/HCL).

Mitigation table format:
| Threat ID | Mitigation | Snippet / Config | Justification |
|---|---|---|---|
| T-001 | Enable TLS | `ssl-redirect: "true"` | Prevents T1041 |
"""

GOVERNANCE_PROMPT = """
You are the Cybersecurity Governance and Certification Engine.
Your task is:
1. Analyze the presented threats and mitigations.
2. Calculate the residual risk.
3. If the risk is acceptable according to corporate policies, mark the status as 'Approved'. Otherwise, mark as 'Draft'.
4. Generate a summary in Open Threat Model (OTM) JSON format.

Ensure you are rigorous with the company's security thresholds.
"""

def initial_scanner_node(state: AgentState) -> AgentState:
    print("\n--- Agent: Initial Lightweight Scanner ---")
    query = state.get("query", "")
    messages = state.get("messages", [])

    prompt = (
        "You are a fast local scanner. Provide a concise summary of the provided input "
        "with discovered components, endpoints, exposed ports, and any obvious misconfigurations. "
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

    return {
        "scan_summary": scan_output,
        "needs_deep_scan": needs_deep,
        "raw_infra_data": scan_output if scan_output else query,
        "messages": messages + [AIMessage(content=scan_output)]
    }


def deep_analyzer_node(state: AgentState) -> AgentState:
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

# --- Agent Functions (Nodes) ---

def system_architect_node(state: AgentState) -> AgentState:
    print("\n--- Agent: Systems Architect ---")
    query = state.get("query", "")
    messages = state.get("messages", [])
    messages.append(HumanMessage(content=f"Usuario: {query}"))

    # If the initial scanner indicated a need for deep analysis, ensure we run it and merge results
    if state.get("needs_deep_scan") and not state.get("deep_scan_results"):
        print("    [INFO] Deep scan requested by initial scanner. Running deep analyzer...")
        deep_state_updates = deep_analyzer_node(state)
        # Merge deep analyzer outputs into our state variables for downstream use
        state.update({
            "deep_scan_results": deep_state_updates.get("deep_scan_results", ""),
            "raw_infra_data": deep_state_updates.get("raw_infra_data", state.get("raw_infra_data", "")),
            "messages": messages + deep_state_updates.get("messages", [])
        })
        # Refresh local references
        messages = state.get("messages", messages)
    
    # Simulación de carga de políticas corporativas
    policies = "Every DB must be in an isolated subnet. 2. Mandatory use of WAF for external traffic."

    architect_prompt_content = SYSTEM_ARCHITECT_PROMPT + f"\n\nThe application/system to be analyzed is: {query}"
    
    search_results_str = ""
    if tavily_tool and any(x in query.lower() for x in ["buscar", "arquitectura", "swagger", "manifest"]):
        print("    [INFO] Using Tavily to search for architecture information.")
        try:
            # TavilySearchResults.invoke espera un dict con 'query'
            search_results = tavily_tool.invoke({"query": f"technical architecture of {query}"})
            search_results_str = f"\n\nRelevant search results:\n{search_results}"
        except Exception as e:
            print(f"    [WARNING] Error using Tavily: {e}. Continuing with no search results.")
            search_results_str = "\n\n[WARNING] The external search failed."

    final_architect_prompt = architect_prompt_content + search_results_str
    
    # Llamar al LLM con el prompt combinado
    response_message = llm.invoke([HumanMessage(content=final_architect_prompt)])
    architecture_output = response_message.content

    # Initialize mermaid_blocks early so we can safely return if clarification is requested
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
        "Please supply"
    ]

    requires_input = False
    user_request_text = ""
    lower_out = architecture_output.lower()
    for phrase in clarification_triggers:
        if phrase.lower() in lower_out:
            requires_input = True
            # Extract the sentence or the remainder as the user prompt (simple heuristic)
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

    # Extraer diagramas Mermaid (heurística simple por ahora)
    mermaid_blocks = []
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

    # Eliminar bloques mermaid del output para una descripción más limpia
    architecture_description_clean = architecture_output
    for block in mermaid_blocks:
        architecture_description_clean = architecture_description_clean.replace(f"```mermaid\n{block}\n```", "").strip()

    return {
        "architecture_description": architecture_description_clean,
        "raw_infra_data": query, # Guardamos el input crudo para trazabilidad
        "corporate_policies": policies,
        "mermaid_diagrams": mermaid_blocks,
        "messages": messages + [AIMessage(content=architecture_output)] # Almacenar el output completo incluyendo mermaid para contexto
    }

def stride_threat_identifier_node(state: AgentState) -> AgentState:
    print("\n--- Agent: STRIDE Threat Identifier ---")
    architecture_desc = state["architecture_description"]
    mermaid_diagrams = "\n".join(state["mermaid_diagrams"])
    policies = state["corporate_policies"]
    messages = state["messages"]

    stride_prompt = STRIDE_THREAT_IDENTIFIER_PROMPT + \
                    f"\n\nArchitecture Description:\n{architecture_desc}" + \
                    f"\n\n Mermaid Diagrams:\n{mermaid_diagrams}" + \
                    f"\n\nCorporate Policies:\n{policies}"

    response_message = llm.invoke([HumanMessage(content=stride_prompt)])
    stride_output = response_message.content

    return {
        "threats_stride": stride_output,
        "messages": messages + [AIMessage(content=stride_output)]
    }

def impact_assessor_node(state: AgentState) -> AgentState:
    print("\n--- Agent: Impact Assessor ---")
    threats_stride = state["threats_stride"]
    architecture_desc = state["architecture_description"] # Contexto para el impacto
    messages = state["messages"]

    impact_prompt = IMPACT_ASSESSOR_PROMPT + \
                    f"\n\nArchitecture:\n{architecture_desc}" + \
                    f"\n\nIdentified STRIDE Threats:\n{threats_stride}"

    response_message = llm.invoke([HumanMessage(content=impact_prompt)])
    impact_output = response_message.content

    # Extracción simple de referencias MITRE ATT&CK (puede mejorarse)
    mitre_refs = []
    for line in impact_output.splitlines():
        if "T" in line and "(" in line and ")" in line: # Heurística para códigos T
            mitre_refs.append(line)

    return {
        "impact_assessment": impact_output,
        "mitre_attack_references": mitre_refs,
        "messages": messages + [AIMessage(content=impact_output)]
    }

def mitigation_advisor_node(state: AgentState) -> AgentState:
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

def governance_node(state: AgentState) -> AgentState:
    print("\n--- Agent: Governance and Scaling ---")
    messages = state["messages"]
    
    gov_prompt = GOVERNANCE_PROMPT + f"\n\nContext: {state['threats_stride']} \n {state['mitigations']}"
    response = llm.invoke([HumanMessage(content=gov_prompt)])
    
    # Simulamos la asignación de estado basada en la lógica del LLM
    status = "Approved" if "riesgo bajo" in response.content.lower() else "In Review"
    
    return {
        "otm_report": response.content,
        "status": status,
        "messages": messages + [AIMessage(content=f"Estado de Certificación: {status}")]
    }

def final_report_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Generador de Reporte Final ---")
    final_report_content = (
        f"# Reporte de Modelado de Amenazas (Estado: {state['status']})\n\n"
        "## 1. Arquitectura del Sistema (Ingesta Zero-Friction)\n"
        f"{state['architecture_description']}\n\n"
        "### Diagramas Mermaid (DFD / Trust Boundaries)\n"
        + "\n\n".join([f"```mermaid\n{d}\n```" for d in state['mermaid_diagrams']]) + "\n\n"
        "## 2. Amenazas Identificadas (STRIDE + CWE)\n"
        f"{state['threats_stride']}\n\n"
        "## 3. Evaluación de Impacto y MITRE ATT&CK\n"
        f"{state['impact_assessment']}\n\n"
        "## 4. Controles y Mitigaciones (Snippets Dev-Friendly)\n"
        f"{state['mitigations']}\n\n"
        "## 5. Gobernanza y Formato Abierto (OTM)\n"
        "El modelo ha sido catalogado y exportado para integración en CI/CD.\n"
        f"Status: {state['status']}\n"
        "---"
    )
    return {"messages": state["messages"] + [AIMessage(content=final_report_content)]}

# --- Build the Graph ---
workflow = StateGraph(AgentState)
# Añadir nodos para cada agente
workflow.add_node("initial_scanner", initial_scanner_node)
workflow.add_node("system_architect", system_architect_node)
workflow.add_node("stride_threat_identifier", stride_threat_identifier_node)
workflow.add_node("impact_assessor", impact_assessor_node)
workflow.add_node("mitigation_advisor", mitigation_advisor_node)
workflow.add_node("governance_node", governance_node)
workflow.add_node("final_report", final_report_node)

# Definir la secuencia de ejecución
workflow.set_entry_point("initial_scanner")
workflow.add_edge("initial_scanner", "system_architect")
workflow.add_edge("system_architect", "stride_threat_identifier")
workflow.add_edge("stride_threat_identifier", "impact_assessor")
workflow.add_edge("impact_assessor", "mitigation_advisor")
workflow.add_edge("mitigation_advisor", "governance_node")
workflow.add_edge("governance_node", "final_report")
workflow.add_edge("final_report", END)

# Inicializar memoria
memoria = MemorySaver()

# Compilar el grafo
app = workflow.compile(checkpointer=memoria)

# --- Configuración y Bucle Principal ---
config = {"configurable": {"thread_id": "threat_modeling_session_01"}}

print("\n--- Security Architect Agent (Threat Modeling) Initiated ---")
print("Introduce the name of an application or describe an architecture to begin.")

while True:
    pregunta = input("\nTú: ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("Turning off the agent...")
        break

    # Invocar el grafo con el estado inicial
    resultado = app.invoke(
        {
            "query": pregunta,
            "messages": [HumanMessage(content=pregunta)],
            "mermaid_diagrams": [],
            "mitre_attack_references": [],
            "raw_infra_data": "",
            "corporate_policies": "",
            "scan_summary": "",
            "needs_deep_scan": False,
            "deep_scan_results": "",
            "requires_user_input": False,
            "user_request_text": ""
        },
        config=config
    )

    # If any node requested more user input, pause and collect it, then re-invoke
    if resultado.get("requires_user_input"):
        prompt_text = resultado.get("user_request_text") or resultado["messages"][-1].content
        print("\nAgent requests additional information to continue:\n")
        print(prompt_text)
        user_add = input("You (provide requested info): ")

        # Build an updated state incorporating the user's reply
        updated_state = {
            "query": pregunta,
            "messages": resultado.get("messages", []) + [HumanMessage(content=user_add)],
            "mermaid_diagrams": resultado.get("mermaid_diagrams", []),
            "mitre_attack_references": resultado.get("mitre_attack_references", []),
            "raw_infra_data": (resultado.get("raw_infra_data") or "") + "\n" + user_add,
            "corporate_policies": resultado.get("corporate_policies", ""),
            "scan_summary": resultado.get("scan_summary", ""),
            "needs_deep_scan": resultado.get("needs_deep_scan", False),
            "deep_scan_results": resultado.get("deep_scan_results", ""),
            "requires_user_input": False,
            "user_request_text": ""
        }

        resultado = app.invoke(updated_state, config=config)

    # El nodo final_report_node añade el reporte completo a los mensajes.
    # Imprimimos el contenido del último mensaje, que es el reporte final.
    final_report_message = resultado['messages'][-1].content
    print(f"\nAgent: {final_report_message}")