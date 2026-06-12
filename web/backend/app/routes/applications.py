"""
API routes for threat modeling operations.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from app.models.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    DashboardStats,
    AnalysisUpdate,
    AnalysisRequest
)
from app.db.storage import get_storage
from app.services.agent_service import run_threat_analysis

router = APIRouter(prefix="/api", tags=["applications"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    storage = get_storage()
    stats = storage.get_statistics()
    return DashboardStats(**stats)


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(req: ApplicationCreate):
    """Create a new application for threat modeling."""
    storage = get_storage()
    app_data = storage.create_application(req.name, req.description, req.scan_type)
    return ApplicationResponse.model_validate(app_data)


@router.get("/applications", response_model=List[ApplicationResponse])
async def list_applications():
    """Get all applications."""
    storage = get_storage()
    applications = storage.list_applications()
    return [ApplicationResponse.model_validate(app) for app in applications]


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str):
    """Get a specific application."""
    storage = get_storage()
    app_data = storage.get_application(app_id)
    
    if app_data is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return ApplicationResponse.model_validate(app_data)


@router.post("/applications/{app_id}/analyze")
async def analyze_application(app_id: str, background_tasks: BackgroundTasks):
    """Run threat analysis on an application."""
    storage = get_storage()
    app_data = storage.get_application(app_id)
    
    if app_data is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update status to "processing"
    updated_app = storage.update_application(app_id, {"status": "processing"})
    
    # Run analysis in background
    background_tasks.add_task(run_threat_analysis, app_id)
    
    return ApplicationResponse.model_validate(updated_app)


@router.put("/applications/{app_id}")
async def update_application(app_id: str, updates: AnalysisUpdate):
    """Update application with analysis results."""
    storage = get_storage()
    app_data = storage.get_application(app_id)
    
    if app_data is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Filter out None values
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    updated_app = storage.update_application(app_id, update_dict)
    return ApplicationResponse.model_validate(updated_app)


@router.delete("/applications/{app_id}")
async def delete_application(app_id: str):
    """Delete an application."""
    storage = get_storage()
    success = storage.delete_application(app_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"status": "deleted", "app_id": app_id}
