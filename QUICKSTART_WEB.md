# 🚀 Quick Start Guide - Web UI

## Installation (5 minutes)

### 1. First time setup only:
```bash
bash setup-web.sh
```

This will:
- Create a Python virtual environment
- Install all necessary dependencies
- Prepare the web backend

### 2. Start the server:
```bash
bash run-web.sh
```

You'll see:
```
🔐 Starting Threat Modeling Agent Web UI...
📱 Open your browser and go to: http://localhost:8000
```

### 3. Open your browser
Visit: **http://localhost:8000**

---

## How to Use

### Creating Your First Threat Model

1. **Click "Add Application"** button on the dashboard
2. **Fill in the details:**
   - **Application Name**: e.g., "E-Commerce Platform"
   - **Application Details**: Describe your infrastructure:
     ```
     Frontend: React SPA served from CloudFront
     Backend: Node.js API running on ECS
     Database: PostgreSQL RDS in private subnet
     Authentication: OAuth 2.0 via Auth0
     ```
3. **Click "Create & Analyze"** - the analysis runs automatically!

### Understanding the Results

The AI agent generates:
- 🏗️ **Architecture Diagram** - Visual representation with trust boundaries
- 🎯 **STRIDE Threats** - Security threats organized by category:
  - **S**poofing
  - **T**ampering
  - **R**epudiation
  - **I**nformation Disclosure
  - **D**enial of Service
  - **E**levation of Privilege
- 🛡️ **Mitigations** - Recommended security controls with implementation details
- 📊 **Risk Assessment** - Impact and likelihood evaluation

### Dashboard Overview

- **Total Applications** - Count of all projects
- **Completed** - Finished analyses
- **In Progress** - Currently analyzing
- **Pending** - Awaiting analysis
- **Status Chart** - Visual breakdown of application states

---

## What You Can Do

✅ Create multiple applications  
✅ Run threat analysis on each  
✅ View detailed findings  
✅ Re-analyze anytime  
✅ Delete applications  
✅ View real-time status updates  
✅ Export diagrams (copy from page)  

---

## API Endpoints (for integration)

If you want to integrate with your own tools:

```bash
# Create application
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{"name":"My App","description":"Details..."}'

# List applications
curl http://localhost:8000/api/applications

# Get specific application
curl http://localhost:8000/api/applications/{app_id}

# Run analysis
curl -X POST http://localhost:8000/api/applications/{app_id}/analyze

# Get statistics
curl http://localhost:8000/api/dashboard/stats
```

---

## Troubleshooting

**Port 8000 already in use?**
```bash
# Edit run-web.sh and change port 8000 to something else like 8001
```

**Missing API keys?**
```bash
# Make sure your .env file has:
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

**Analysis not starting?**
```bash
# Check the terminal for error messages
# Make sure all dependencies installed correctly
bash setup-web.sh
```

---

## File Structure

```
my_agent/
├── web/                          # Web UI
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py          # FastAPI server
│   │   │   ├── models/          # API schemas
│   │   │   ├── routes/          # API endpoints
│   │   │   ├── db/              # Data storage
│   │   │   └── services/        # Business logic
│   │   ├── run.py               # Server startup
│   │   └── requirements.txt
│   ├── frontend/
│   │   └── index.html           # Web interface (Vue.js)
│   └── data/                     # Application storage
│       └── applications/
├── setup-web.sh                  # First-time setup
├── run-web.sh                    # Start server
├── src/                          # Your original agent code
├── main.py                       # Original entry point
└── ...
```

---

## Next Steps

- Check the [Web UI README](web/README.md) for advanced configuration
- Review the agent's original [README](README.md) for more details
- Customize the UI styling by editing `web/frontend/index.html`

---

## Features Overview

| Feature | Status |
|---------|--------|
| Dashboard with stats | ✅ |
| Create applications | ✅ |
| Run threat analysis | ✅ |
| View detailed results | ✅ |
| Real-time updates | ✅ |
| Mermaid diagrams | ✅ |
| Responsive design | ✅ |
| User authentication | 🔄 Coming soon |
| Export reports | 🔄 Coming soon |
| API integrations | 🔄 Coming soon |

---

**Happy threat modeling! 🔐**
