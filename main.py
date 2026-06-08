"""
Security Architect Agent - Main Entry Point

Threat modeling AI agent with Zero-Friction ingestion capabilities.
"""
import sys
from langchain_core.messages import HumanMessage

from src.config import initialize_models, Settings
from src.tools import initialize_tools
from src.graph import build_workflow
from src.state import AgentState


def initialize_agent():
    """Initialize and configure the threat modeling agent."""
    print("[SYSTEM] Initializing Security Architect Agent...")
    print(f"[SYSTEM] Threat Modeling Session: {Settings.THREAD_ID}\n")
    
    # Initialize models and tools
    models = initialize_models()
    tools = initialize_tools()
    
    # Build workflow
    app = build_workflow(models, tools)
    
    return app


def create_initial_state(query: str) -> AgentState:
    """Create initial state for a new analysis request."""
    return {
        "query": query,
        "messages": [HumanMessage(content=query)],
        "mermaid_diagrams": [],
        "mitre_attack_references": [],
        "raw_infra_data": "",
        "corporate_policies": "",
        "scan_summary": "",
        "needs_deep_scan": False,
        "deep_scan_results": "",
        "requires_user_input": False,
        "user_request_text": "",
        "architecture_description": "",
        "threats_stride": "",
        "impact_assessment": "",
        "mitigations": "",
        "otm_report": "",
        "status": "Draft"
    }


def main():
    """Main interactive loop for threat modeling analysis."""
    app = initialize_agent()
    
    print("\n--- Security Architect Agent (Threat Modeling) Initiated ---")
    print("Introduce the name of an application or describe an architecture to begin.")
    print("Tip: Add 'deep scan' to your query to request a thorough analysis.\n")
    print("Commands: 'salir', 'exit', 'quit' to exit\n")
    
    config = {"configurable": {"thread_id": Settings.THREAD_ID}}
    
    while True:
        try:
            pregunta = input("\nTú: ").strip()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Turning off the agent...")
            break
        except EOFError:
            print("\n\nEnd of input. Turning off the agent...")
            break
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("Turning off the agent...")
            break
        
        if not pregunta:
            print("Please enter a query or description.")
            continue
        
        # Invoke the workflow
        try:
            resultado = app.invoke(create_initial_state(pregunta), config=config)
            
            # Display final report
            final_report_message = resultado['messages'][-1].content
            print(f"\nAgent: {final_report_message}")
        
        except Exception as e:
            print(f"\n[ERROR] An error occurred during analysis: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
