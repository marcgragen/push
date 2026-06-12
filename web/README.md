# Web UI for Threat Modeling Agent

A modern web interface for the threat modeling security agent with a dashboard, application management, and detailed threat analysis views.

## Features

- **Dashboard**: Overview of all applications with statistics and status charts
- **Application Management**: Create, list, and manage threat modeling applications
- **Detailed Analysis**: View architecture diagrams, STRIDE threats, mitigations, and risk assessments
- **Real-time Updates**: Live polling for background analysis tasks
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
web/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py  # Pydantic models
│   │   ├── routes/
│   │   │   └── applications.py  # API endpoints
│   │   ├── db/
│   │   │   └── storage.py  # Data persistence layer
│   │   └── services/
│   │       └── agent_service.py # Integration with threat modeling agent
│   ├── run.py              # Development server startup
│   └── requirements.txt     # Python dependencies
└── frontend/
    └── index.html          # Single-page application (Vue.js)
```

## Installation

### 1. Install Backend Dependencies

```bash
cd web/backend
pip install -r requirements.txt
```

### 2. Run the Development Server

```bash
cd web/backend
python run.py
```

The application will start at `http://localhost:8000`

## Usage

### Dashboard
- View statistics about all applications
- See status breakdown with charts
- Access recent applications
- Create new applications

### Add Application
1. Click "Add Application" button
2. Enter application name and detailed description (infrastructure, components, data flows)
3. Click "Create & Analyze"
4. The agent will automatically run threat analysis in the background

### Applications List
- View all applications with their current status
- Click any application to view detailed analysis
- Statuses: pending, processing, completed, error

### Application Detail
- View full analysis results including:
  - **Overview**: Architecture description
  - **Threats**: STRIDE-based threats identified
  - **Mitigations**: Recommended security controls
  - **Diagrams**: Mermaid architecture diagrams
- Re-run analysis or delete the application

## API Endpoints

### Health Check
- `GET /api/health` - Server health status

### Dashboard
- `GET /api/dashboard/stats` - Get application statistics

### Applications
- `POST /api/applications` - Create a new application
- `GET /api/applications` - List all applications
- `GET /api/applications/{app_id}` - Get application details
- `POST /api/applications/{app_id}/analyze` - Run threat analysis
- `PUT /api/applications/{app_id}` - Update application with analysis results
- `DELETE /api/applications/{app_id}` - Delete an application

## Data Storage

Applications and analysis results are stored in JSON files in:
```
web/backend/data/applications/
```

Each application gets its own JSON file with the complete analysis data.

## Architecture

The web UI integrates seamlessly with your existing threat modeling agent:

1. **Frontend** (Vue.js SPA) collects application details
2. **FastAPI Backend** stores data and manages API
3. **Background Task** runs the threat modeling agent for each application
4. **Frontend** polls for results and updates in real-time

## Customization

### Styling
Modify the CSS in `frontend/index.html` to match your brand colors and style

### API Response Format
Update `app/services/agent_service.py` to map agent output to your desired format

### Storage
To use a different storage backend (database, cloud storage), modify `app/db/storage.py`

## Development

### Add New Features

1. **New API Routes**: Add endpoints in `app/routes/`
2. **New Models**: Define schemas in `app/models/schemas.py`
3. **Frontend Changes**: Edit `frontend/index.html`

### Debugging

Enable debug logging:
```python
# In run.py
uvicorn.run(..., log_level="debug")
```

## Next Steps

- [ ] Add WebSocket support for real-time updates instead of polling
- [ ] Implement user authentication
- [ ] Add application versioning and history
- [ ] Export analysis reports (PDF, JSON)
- [ ] Integration with JIRA/GitHub for issue tracking
- [ ] Advanced filtering and search
