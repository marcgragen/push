"""
Agent State Definition

Represents the shared state among agents in the graph.
"""
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Represents the shared state among agents in the graph.
    Tracks architecture analysis, threats, mitigations, and user interactions.
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
