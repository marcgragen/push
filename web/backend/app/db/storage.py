"""
Storage layer for threat modeling applications and results.
Uses JSON file-based storage for simplicity.
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


class ApplicationStorage:
    """Manages persistence of application threat models."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize storage with data directory."""
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), "../../data")
        self.storage_dir = storage_dir
        self.applications_dir = os.path.join(storage_dir, "applications")
        
        # Create directories if they don't exist
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        Path(self.applications_dir).mkdir(parents=True, exist_ok=True)
    
    def create_application(self, app_name: str, description: str) -> Dict[str, Any]:
        """Create a new application record."""
        app_id = self._generate_id()
        app_data = {
            "id": app_id,
            "name": app_name,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "analysis": None,
            "mermaid_diagrams": [],
            "threats": [],
            "mitigations": [],
            "otm_report": None
        }
        
        self._save_application(app_data)
        return app_data
    
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get a single application by ID."""
        file_path = os.path.join(self.applications_dir, f"{app_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """Get all applications."""
        applications = []
        for filename in os.listdir(self.applications_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.applications_dir, filename)
                with open(file_path, 'r') as f:
                    applications.append(json.load(f))
        
        # Sort by creation date, newest first
        applications.sort(key=lambda x: x['created_at'], reverse=True)
        return applications
    
    def update_application(self, app_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an application with analysis results."""
        app_data = self.get_application(app_id)
        if app_data is None:
            return None
        
        app_data.update(updates)
        app_data['updated_at'] = datetime.now().isoformat()
        self._save_application(app_data)
        return app_data
    
    def delete_application(self, app_id: str) -> bool:
        """Delete an application."""
        file_path = os.path.join(self.applications_dir, f"{app_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def _save_application(self, app_data: Dict[str, Any]) -> None:
        """Save application data to file."""
        file_path = os.path.join(self.applications_dir, f"{app_data['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(app_data, f, indent=2)
    
    def _generate_id(self) -> str:
        """Generate a unique application ID."""
        import uuid
        return str(uuid.uuid4())[:12]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all applications."""
        applications = self.list_applications()
        
        statuses = {"pending": 0, "completed": 0, "error": 0}
        for app in applications:
            status = app.get('status', 'pending')
            if status in statuses:
                statuses[status] += 1
        
        return {
            "total_applications": len(applications),
            "by_status": statuses
        }


# Global storage instance
_storage = None


def get_storage() -> ApplicationStorage:
    """Get or create the global storage instance."""
    global _storage
    if _storage is None:
        _storage = ApplicationStorage()
    return _storage
