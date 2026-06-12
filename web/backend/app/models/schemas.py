"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ApplicationCreate(BaseModel):
    """Request model for creating a new application."""
    name: str
    description: str
    scan_type: str = "auto"


class AnalysisUpdate(BaseModel):
    """Request model for updating analysis results."""
    status: Optional[str] = None
    analysis: Optional[str] = None
    scan_type: Optional[str] = None
    deep_scan_used: Optional[bool] = None
    mermaid_diagrams: Optional[List[str]] = None
    threats: Optional[List[Dict[str, Any]]] = None
    mitigations: Optional[List[Dict[str, Any]]] = None
    impact_assessment: Optional[str] = None
    otm_report: Optional[Dict[str, Any]] = None


class ApplicationResponse(BaseModel):
    """Response model for an application."""
    id: str
    name: str
    description: str
    scan_type: str = "auto"
    deep_scan_used: Optional[bool] = None
    status: str
    created_at: str
    updated_at: str
    analysis: Optional[str] = None
    mermaid_diagrams: List[str] = []
    threats: List[Dict[str, Any]] = []
    mitigations: List[Dict[str, Any]] = []
    impact_assessment: Optional[str] = None
    otm_report: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle string conversions."""
        if isinstance(obj, dict):
            # Ensure mermaid_diagrams is a list
            if isinstance(obj.get('mermaid_diagrams'), str):
                obj['mermaid_diagrams'] = []
            elif obj.get('mermaid_diagrams') is None:
                obj['mermaid_diagrams'] = []
            
            # Ensure threats is a list
            if isinstance(obj.get('threats'), str):
                obj['threats'] = []
            elif obj.get('threats') is None:
                obj['threats'] = []
            
            # Ensure mitigations is a list
            if isinstance(obj.get('mitigations'), str):
                obj['mitigations'] = []
            elif obj.get('mitigations') is None:
                obj['mitigations'] = []
            
            # Ensure otm_report is None or dict
            if isinstance(obj.get('otm_report'), str) and obj['otm_report'] == '':
                obj['otm_report'] = None
        
        return super().model_validate(obj)


class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_applications: int
    by_status: Dict[str, int]


class AnalysisRequest(BaseModel):
    """Request to analyze an application."""
    app_id: str
    run_analysis: bool = True
