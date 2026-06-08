# Code Organization Guide

## Before (Monolithic)
```
agente.py (600+ lines)
├── Imports
├── Configuration (LLMs)
├── State Definition
├── Tools Setup
├── All Prompts (5 large prompts)
├── All Node Functions (9 functions)
├── Graph Building
├── Main Loop
└── Everything in one file!
```

**Problems:**
- Hard to navigate
- Hard to modify (ripple effects)
- Hard to test (everything intertwined)
- Hard to scale (adding agents is messy)
- Hard to debug (mixed concerns)

---

## After (Modular & Scalable)
```
my_agent/
│
├── src/
│   ├── __init__.py                    # Package definition
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py                 # 📊 LLM Initialization
│   │   └── settings.py               # ⚙️  Environment Setup
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   └── agent_state.py            # 📋 Data Structure (TypedDict)
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── architect.py              # 🏗️  System Architect Prompt
│   │   ├── threat_identifier.py      # 🔍 STRIDE Prompt
│   │   ├── impact_assessor.py        # ⚠️  Impact Prompt
│   │   ├── mitigation_advisor.py     # 🛡️  Mitigation Prompt
│   │   └── governance.py             # ✅ Governance Prompt
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scanner.py                # 🔦 Scanner Agents
│   │   ├── architect.py              # 🏗️  Architect Agent
│   │   ├── threat.py                 # 🔍 Threat Agent
│   │   ├── impact.py                 # ⚠️  Impact Agent
│   │   ├── mitigation.py             # 🛡️  Mitigation Agent
│   │   ├── governance.py             # ✅ Governance Agent
│   │   ├── reporting.py              # 💬 User Input Agent
│   │   └── report.py                 # 📄 Report Agent
│   │
│   ├── routing/
│   │   └── __init__.py               # 🚦 Conditional Routing
│   │
│   ├── graph/
│   │   └── __init__.py               # 🔗 Workflow Graph
│   │
│   └── tools/
│       └── __init__.py               # 🔧 External Tools
│
├── main.py                           # 🚀 Entry Point
├── agente.py                         # 📦 Old Version (Backup)
├── README_STRUCTURE.md               # 📚 Documentation
└── Activities.csv                    # 📊 Data
```

**Benefits:**
✅ Easy to navigate
✅ Easy to modify (isolated changes)
✅ Easy to test (individual modules)
✅ Easy to scale (add agents quickly)
✅ Easy to debug (clear separation)

---

## Module Dependencies

```
main.py
  │
  ├─→ config/models.py          (Initialize LLMs)
  ├─→ config/settings.py        (Load settings)
  ├─→ tools/__init__.py         (Initialize tools)
  ├─→ graph/__init__.py         (Build workflow)
  │    │
  │    ├─→ state/agent_state.py (State definition)
  │    ├─→ agents/scanner.py    (Scanner nodes)
  │    ├─→ agents/architect.py  (Architect node)
  │    ├─→ agents/threat.py     (Threat node)
  │    ├─→ agents/impact.py     (Impact node)
  │    ├─→ agents/mitigation.py (Mitigation node)
  │    ├─→ agents/governance.py (Governance node)
  │    ├─→ agents/reporting.py  (User input node)
  │    ├─→ agents/report.py     (Report node)
  │    ├─→ routing/__init__.py  (Routing logic)
  │    └─→ prompts/             (All prompts)
```

---

## Adding New Features

### To Add a New Agent

1. **Create Prompt**: `src/prompts/my_agent.py`
   ```python
   MY_AGENT_PROMPT = "..."
   ```

2. **Create Agent**: `src/agents/my_agent.py`
   ```python
   def my_agent_node(llm, state):
       # Your implementation
       return {...}
   ```

3. **Update Exports**: `src/agents/__init__.py`
   ```python
   from .my_agent import my_agent_node
   __all__ = [..., "my_agent_node"]
   ```

4. **Update Graph**: `src/graph/__init__.py`
   ```python
   workflow.add_node("my_agent", my_agent_wrapper)
   workflow.add_edge("previous_node", "my_agent")
   ```

### To Update a Prompt

- Edit only: `src/prompts/architect.py` (or any specific prompt)
- No need to touch agent code!

### To Change Models

- Edit only: `src/config/models.py`
- Changes automatically used everywhere!

### To Add a Tool

- Edit only: `src/tools/__init__.py`
- Tool automatically available to all agents!

---

## File Size Comparison

| Component | Before (agente.py) | After (New Structure) |
|-----------|-------------------|----------------------|
| **Total Lines** | 600+ | ~550 (distributed) |
| **Imports** | 12 lines | Clean per-module imports |
| **Config** | Mixed in | 50 lines in config/ |
| **State** | 30 lines | 30 lines (isolated) |
| **Prompts** | 100+ lines | 120 lines (organized) |
| **Agents** | 350+ lines | 400 lines (modular) |
| **Graph** | 30 lines | 80 lines (clearer) |
| **Main Loop** | 50+ lines | 40 lines (cleaner) |

**Result:** Same functionality, better organized, easier to maintain!

---

## Best Practices Applied

✅ **Single Responsibility**: Each module has one job
✅ **Dependency Injection**: Pass dependencies explicitly
✅ **Separation of Concerns**: Config ≠ Agents ≠ Prompts
✅ **DRY (Don't Repeat Yourself)**: Prompts centralized
✅ **SOLID Principles**: Scalable and maintainable
✅ **Clear Imports**: Know exactly what comes from where
✅ **Type Safety**: TypedDict for state validation
✅ **Documentation**: Every module documented
✅ **Testability**: Easy to unit test each agent
✅ **Extensibility**: Easy to add new features
