"""
Main FastAPI application for threat modeling web service.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import applications

# Create FastAPI app
app = FastAPI(
    title="Threat Modeling Agent API",
    description="Web interface for threat modeling analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router)

# Static files - frontend is in web/frontend relative to the project root
frontend_dir = os.path.join(os.path.dirname(__file__), "../../frontend")
frontend_dir = os.path.abspath(frontend_dir)

print(f"[DEBUG] Frontend directory: {frontend_dir}")
print(f"[DEBUG] Frontend exists: {os.path.exists(frontend_dir)}")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    index_path = os.path.join(frontend_dir, "index.html")
    print(f"[DEBUG] Serving index.html from: {index_path}")
    print(f"[DEBUG] File exists: {os.path.exists(index_path)}")
    
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Threat Modeling Agent Web UI - Frontend not found"}


@app.get("/{path_name}")
async def serve_frontend(path_name: str):
    """Serve frontend pages."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")
