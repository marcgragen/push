"""
Final Report Generation Agent

Responsible for generating comprehensive threat modeling reports.
"""
from langchain_core.messages import AIMessage
from src.state import AgentState


def final_report_node(state: AgentState) -> AgentState:
    """
    Generates comprehensive final threat modeling report.
    """
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
