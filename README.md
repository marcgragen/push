# 🔐 Security Architect Agent

An intelligent AI-powered threat modeling agent that performs **zero-friction infrastructure ingestion** and generates comprehensive security threat models using STRIDE methodology and MITRE ATT&CK mapping.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)]()

---

## 🎯 Overview

The Security Architect Agent is an AI-driven threat modeling system that:

- **Analyzes** infrastructure descriptions, Kubernetes manifests, Terraform configs, and OpenAPI specifications
- **Generates** architecture diagrams with trust boundaries and data flows (Mermaid.js)
- **Identifies** security threats using STRIDE methodology
- **Maps** threats to MITRE ATT&CK tactics and techniques
- **Assesses** impact and risk levels (High, Medium, Low)
- **Recommends** technical mitigations with code snippets
- **Produces** Open Threat Model (OTM) reports for compliance

**Perfect for:** DevSecOps teams, Security architects, Infrastructure teams, and compliance professionals.

---

## ✨ Key Features

### 🔍 Intelligent Scanning
- **Lightweight Scanner**: Quick initial assessment of infrastructure
- **Deep Analyzer**: Comprehensive analysis when additional complexity is detected
- **Manual Deep Scan**: User can explicitly request thorough analysis

### 🏗️ Architecture Analysis
- Parses IaC (K8s manifests, Terraform, Dockerfiles)
- Extracts API endpoints from Swagger/OpenAPI
- Integrates scanner results (Trivy, Kubiscan)
- Generates trust boundary diagrams with Mermaid.js

### 🛡️ Threat Modeling
- **STRIDE Classification**: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege
- **CWE Mapping**: Common Weakness Enumeration references
- **MITRE ATT&CK Integration**: Tactic and technique mapping

### 📊 Risk Assessment
- Impact evaluation per threat
- Risk level calculation (High/Medium/Low)
- Residual risk assessment
- Governance and compliance checking

### 🎓 Smart User Interaction
- Detects when additional information is needed
- Interactive prompts for clarification
- Context-aware re-analysis with user-provided data

### 🔄 Multi-LLM Fallback Strategy
- Primary: Google Gemini 1.5 Flash (most capable)
- Secondary: Google Gemini 1.5 Flash-8b (lightweight)
- Tertiary: Llama 3.2 (local, always available)

---

## 📋 Requirements

### System Requirements
- **Python**: 3.9 or higher
- **Memory**: 8GB RAM minimum (for local LLM)
- **Storage**: 2GB for models

### Dependencies
- `langchain` - LLM orchestration
- `langgraph` - Workflow graph
- `langchain-google-genai` - Google Gemini integration
- `langchain-ollama` - Local model support
- `langchain-tavily` - Web search integration
- `python-dotenv` - Environment configuration

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/security-architect-agent.git
cd security-architect-agent
```

### 2. Create Virtual Environment
```bash
python3 -m venv entorno_agente
source entorno_agente/bin/activate  # On Windows: entorno_agente\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# Tavily Search (optional)
TAVILY_API_KEY=your_tavily_api_key_here
```

**Getting API Keys:**
- [Google Gemini API](https://ai.google.dev/)
- [Tavily Search API](https://tavily.com/) (optional, for web search)

---

## 📖 Usage

### Quick Start

```bash
# Run the agent
python main.py

# You'll see:
# --- Security Architect Agent (Threat Modeling) Initiated ---
# Introduce the name of an application or describe an architecture to begin.
# Tip: Add 'deep scan' to your query to request a thorough analysis.

# Enter your query:
# Tú: Analyze my Kubernetes microservices architecture...
```

### Example Queries

#### 1. **Basic Application Analysis**
```
Analyze a Node.js REST API backend with MongoDB database and Redis cache
```

#### 2. **Infrastructure Analysis**
```
Deep scan: Kubernetes cluster with:
- Nginx ingress controller
- PostgreSQL database in isolated subnet
- Microservices in different namespaces
- Service accounts with RBAC
```

#### 3. **With Infrastructure File**
```
Analyze this Kubernetes manifest:
apiVersion: v1
kind: Pod
...
```

#### 4. **API Specification Analysis**
```
Analyze this OpenAPI spec:
openapi: 3.0.0
...
```

### Command Line Options

| Command | Effect |
|---------|--------|
| `exit` | Exit the agent |
| `quit` | Exit the agent |
| `salir` | Exit the agent (Spanish) |

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│                   (Interactive CLI)                      │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────────┐      ┌──────▼──────┐
    │   Config    │      │   Tools     │
    │ - Models    │      │ - Tavily    │
    │ - Settings  │      │ - LLM       │
    └─────┬───────┘      └──────┬──────┘
          │                     │
    ┌─────▼─────────────────────▼─────┐
    │      Graph Workflow Engine      │
    │  (LangGraph with conditional    │
    │   routing and memory)           │
    └─────┬──────────────────────────┬┘
          │      ┌──────────────────┤
          │      │                  │
    ┌─────▼──────▼─┐           ┌────▼─────────┐
    │    Agents    │           │   Prompts    │
    │ - Scanner    │           │ - Architect  │
    │ - Architect  │           │ - STRIDE     │
    │ - Threat ID  │           │ - Impact     │
    │ - Impact     │           │ - Mitigation │
    │ - Mitigation │           │ - Governance │
    │ - Governance │           └──────────────┘
    │ - Reporting  │
    └──────────────┘
```

### Data Flow

```
User Input
    ↓
Initial Scanner (Quick Assessment)
    ↓
  ┌─ Need Deep Scan? ──┐
  │ YES        │ NO    │
  ↓           ↓       │
Deep       System     │
Analyzer → Architect  │
  │         ↓         │
  └────┬────┘         │
       │              │
   Need User Input? ──┤
   YES        │ NO    │
   ↓          ↓       │
User Input → collect data
   │
   ↓
STRIDE Threat Identifier
   ↓
Impact Assessor (MITRE ATT&CK)
   ↓
Mitigation Advisor
   ↓
Governance & Certification
   ↓
Final Report Generation
   ↓
Output to User
```

### Project Structure

```
my_agent/
├── src/
│   ├── config/              # Configuration & Settings
│   ├── state/               # Application State
│   ├── prompts/             # Agent Prompts
│   ├── agents/              # Agent Implementations
│   ├── routing/             # Conditional Logic
│   ├── graph/               # Workflow Graph
│   └── tools/               # External Tools
├── main.py                  # Entry Point
├── agente.py                # Legacy Implementation
├── README.md                # This file
├── ORGANIZATION_GUIDE.md    # Code Organization
└── README_STRUCTURE.md      # Structure Reference
```

See [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) for detailed structure explanation.

---

## 🔧 Configuration

### Environment Variables

```env
# Required
GOOGLE_API_KEY=xxx                  # Google Gemini API key

# Optional
TAVILY_API_KEY=xxx                  # Web search capability
```

### Model Selection

Edit `src/config/models.py` to change:
- Primary LLM model
- Fallback strategy
- Temperature and parameters
- Local model selection

### Custom Policies

Modify `src/agents/architect.py` to update:
- Corporate security policies
- Compliance requirements
- Risk thresholds

---

## 📊 Output Report

The agent generates a comprehensive threat model report including:

1. **Architecture Description**
   - System components and networks
   - Data flows and protocols
   - Trust boundaries

2. **Mermaid Diagrams**
   - Data flow diagrams (DFD)
   - Trust boundary visualization
   - Authentication sequences
   - RBAC relationships

3. **STRIDE Threats**
   - Threat ID and category
   - Affected component
   - CWE reference
   - Policy compliance notes

4. **Impact Assessment**
   - Risk level (High/Medium/Low)
   - Potential business impact
   - MITRE ATT&CK mappings
   - Tactic and technique references

5. **Mitigations**
   - Technical controls
   - Code snippets/configurations
   - Justification

6. **Governance Report**
   - Residual risk calculation
   - Compliance status
   - OTM (Open Threat Model) format

---

## 💡 Use Cases

### DevSecOps Teams
- Automated threat modeling in CI/CD pipelines
- Pre-deployment security assessment
- Infrastructure security validation

### Security Architects
- Design review threat analysis
- Risk quantification
- Control recommendations

### Compliance Professionals
- Generate compliance documentation
- Evidence for audits
- Policy adherence verification

### Infrastructure Teams
- Cloud architecture security review
- Kubernetes security assessment
- Network segmentation validation

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/security-architect-agent.git
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/amazing-feature
```

### 3. Make Changes
- Follow the code structure in [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md)
- Add docstrings to new functions
- Update relevant prompts in `src/prompts/`

### 4. Test Your Changes
```bash
python main.py
# Test your feature interactively
```

### 5. Commit and Push
```bash
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
```

### 6. Submit Pull Request
- Describe changes clearly
- Reference any related issues

---

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not configured"
```
Solution: Create .env file with your Google API key
```

### "Module not found: langchain"
```bash
Solution: Install dependencies
pip install -r requirements.txt
```

### "Connection timeout with Tavily"
```
Solution: Tavily is optional. Leave TAVILY_API_KEY empty to continue without web search
```

### Agent requests but doesn't receive user input
```
Solution: Make sure terminal is properly focused and ready for input
```

### Deep scan not triggering
```
Solution: Use keywords like "deep scan", "thorough", "detailed analysis", "comprehensive"
Example: "Deep scan of my Kubernetes architecture"
```

---

## 📚 Documentation

- [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) - Code organization and best practices
- [README_STRUCTURE.md](README_STRUCTURE.md) - Project structure reference
- [STRIDE Methodology](https://www.microsoft.com/en-us/securityengineering/sdl/threatmodeling) - Official Microsoft STRIDE docs
- [MITRE ATT&CK Framework](https://attack.mitre.org/) - Attack techniques & tactics
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Graph workflow framework

---

## 📋 Requirements File

See `requirements.txt` for complete dependencies:

```
langchain>=0.1.0
langgraph>=0.1.0
langchain-google-genai>=0.1.0
langchain-ollama>=0.1.0
langchain-tavily>=0.1.0
langchain-community>=0.1.0
python-dotenv>=1.0.0
```

---

## 🔐 Security

### Best Practices
- Never commit `.env` file with real API keys
- Use environment variables for sensitive data
- Regularly rotate API keys
- Review generated threat models with security team

### Responsible Disclosure
If you find a security vulnerability:
1. Do **NOT** create a public GitHub issue
2. Email security concerns to: [your-email@example.com]
3. Include detailed description and reproduction steps

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

MIT License Summary:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

---

## 🙋 Support

### Getting Help

- **Documentation**: Check [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md)
- **Issues**: Create a GitHub issue with:
  - Clear description
  - Steps to reproduce
  - Environment details (OS, Python version)
  - Error messages/logs

### Report Issues
```bash
# Example issue title:
# [BUG] Agent fails to parse Kubernetes manifest with CRDs

# Include:
1. What you tried
2. What happened
3. What you expected
4. Error messages
5. Your environment
```

---

## 🌟 Roadmap

### Current Version (1.0.0)
- ✅ STRIDE threat modeling
- ✅ MITRE ATT&CK mapping
- ✅ Architecture diagram generation
- ✅ Multi-LLM fallback
- ✅ User input collection

### Planned Features
- 🔜 Export to OTM JSON format
- 🔜 CI/CD pipeline integration
- 🔜 Web UI interface
- 🔜 Custom policy templates
- 🔜 Batch analysis mode
- 🔜 Report caching
- 🔜 Threat library management

---

## 👨‍💻 Author

**Marc Grau** - Security Architect & AI Developer

- GitHub: [@marcgrau](https://github.com/marcgrau)
- LinkedIn: [Marc Grau](https://linkedin.com/in/marcgrau)

---

## 🙏 Acknowledgments

- [Microsoft STRIDE Threat Modeling](https://www.microsoft.com/en-us/securityengineering/sdl/threatmodeling)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [LangChain](https://www.langchain.com/) - LLM framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph orchestration
- [Google Gemini](https://ai.google.dev/) - AI models

---

## 📞 Contact & Questions

For questions or suggestions:
- 📧 Email: marc@example.com
- 💬 Discussions: Use GitHub Discussions
- 🐦 Twitter: [@marcgrau](https://twitter.com/marcgrau)

---

**Made with ❤️ for the security community**

Last Updated: 2026-06-08  
Version: 1.0.0
