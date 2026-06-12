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

    scan_type = state.get("scan_type", "auto")
    if scan_type == "deep":
        needs_deep = True
        print("    [INFO] Deep scan forced via UI selection.")
    elif scan_type == "light":
        needs_deep = False
        print("    [INFO] Light scan forced via UI selection.")

    return {
        "scan_summary": scan_output,
        "needs_deep_scan": needs_deep,
        "raw_infra_data": scan_output if scan_output else query,
        "messages": messages + [AIMessage(content=scan_output)]
    }


def deep_analyzer_node(llm_deep, state: AgentState) -> AgentState:
    """
    Deep analyzer using powerful model (Gemini) for thorough IriusRisk-level analysis.
    
    Produces a comprehensive, structured infrastructure assessment that enables
    downstream agents to generate significantly more threats and countermeasures.
    """
    print("\n--- Agent: Deep Analyzer (Powerful Model — IriusRisk Maturity) ---")
    scan_summary = state.get("scan_summary", "")
    query = state.get("query", "")
    messages = state.get("messages", [])

    prompt = (
        "You are an elite infrastructure security analyst performing a DEEP SCAN at IriusRisk threat modeling maturity level.\n"
        "Given the preliminary scan summary and original application description below, perform an exhaustive analysis.\n\n"
        "YOU MUST produce a comprehensive structured report covering ALL of the following sections:\n\n"
        "## 1. Component Inventory\n"
        "List EVERY component in the system (minimum 8-15 components). For each component provide:\n"
        "- Component name and type (web server, API gateway, database, cache, queue, CDN, load balancer, identity provider, storage, etc.)\n"
        "- Technology stack (e.g., Django 4.2, PostgreSQL 15, Redis 7, Nginx 1.25, Kubernetes 1.28)\n"
        "- Exposure level: Internet-facing, Internal, or Restricted\n"
        "- Port(s) and protocol(s)\n\n"
        "## 2. Data Flow Mapping\n"
        "Map ALL data flows between components. For each flow specify:\n"
        "- Source → Destination\n"
        "- Protocol and port (HTTP/HTTPS/gRPC/AMQP/SQL/etc.)\n"
        "- Encryption status (TLS 1.2, TLS 1.3, mTLS, plaintext)\n"
        "- Data sensitivity (Public, Internal, Confidential, Restricted)\n"
        "- Authentication method on this flow (API key, JWT, mTLS, session cookie, none)\n\n"
        "## 3. Trust Boundaries\n"
        "Identify ALL trust boundaries (minimum 4-6). For each boundary:\n"
        "- Name and description (e.g., 'Internet ↔ DMZ', 'DMZ ↔ Internal Network', 'App ↔ Database Tier')\n"
        "- Components on each side\n"
        "- Security controls at this boundary (WAF, firewall, network segmentation, VPN, etc.)\n"
        "- Gaps: any missing controls that should be present\n\n"
        "## 4. Authentication & Authorization Mechanisms\n"
        "For each component/interface:\n"
        "- Auth mechanism (OAuth2, SAML, Basic Auth, API Key, mTLS, none)\n"
        "- Authorization model (RBAC, ABAC, ACL, none)\n"
        "- Session management details (token type, expiry, storage)\n"
        "- MFA status\n\n"
        "## 5. Data Classification\n"
        "Classify ALL data handled by the system:\n"
        "- Data type (PII, PHI, financial, credentials, logs, config, etc.)\n"
        "- Classification level (Public, Internal, Confidential, Restricted)\n"
        "- Storage location and encryption at rest status\n"
        "- Retention policy if inferable\n\n"
        "## 6. Deployment & Infrastructure\n"
        "- Cloud provider and region (if inferable)\n"
        "- Container orchestration (K8s, ECS, etc.)\n"
        "- CI/CD pipeline components\n"
        "- Secrets management approach\n"
        "- Logging and monitoring stack\n\n"
        "## 7. Compliance Scope\n"
        "Based on the data types and architecture, identify applicable compliance frameworks:\n"
        "- OWASP Top 10, OWASP ASVS\n"
        "- PCI-DSS (if payment data)\n"
        "- GDPR (if EU PII)\n"
        "- SOC 2, ISO 27001\n"
        "- NIST CSF\n\n"
        "## 8. Attack Surface Summary\n"
        "- External attack surface (internet-facing endpoints, APIs, login pages)\n"
        "- Internal attack surface (service-to-service, admin panels)\n"
        "- Supply chain risks (third-party dependencies, libraries)\n\n"
        f"=== PRELIMINARY SCAN SUMMARY ===\n{scan_summary}\n\n"
        f"=== ORIGINAL APPLICATION DESCRIPTION ===\n{query}\n\n"
        "Be thorough. Infer reasonable details when not explicitly stated. "
        "This deep analysis will drive the threat identification phase, so completeness is critical."
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

