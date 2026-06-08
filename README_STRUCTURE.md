# Security Architect Agent - Scalable Structure

## Project Structure

```
my_agent/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── config/                   # Configuration & Settings
│   │   ├── __init__.py
│   │   ├── models.py            # LLM model initialization & fallback strategy
│   │   └── settings.py          # Environment variables & settings
│   ├── state/                    # Application State
│   │   ├── __init__.py
│   │   └── agent_state.py       # TypedDict definition for shared state
│   ├── prompts/                  # Agent Prompts (Modular & Reusable)
│   │   ├── __init__.py
│   │   ├── architect.py         # System Architect prompt
│   │   ├── threat_identifier.py # STRIDE Threat Identifier prompt
│   │   ├── impact_assessor.py   # Impact Assessment prompt
│   │   ├── mitigation_advisor.py# Mitigation Advisor prompt
│   │   └── governance.py        # Governance & Certification prompt
│   ├── agents/                   # Agent Node Implementations
│   │   ├── __init__.py
│   │   ├── scanner.py           # Initial scanner & deep analyzer
│   │   ├── architect.py         # System Architect node
│   │   ├── threat.py            # Threat Identifier node
│   │   ├── impact.py            # Impact Assessor node
│   │   ├── mitigation.py        # Mitigation Advisor node
│   │   ├── governance.py        # Governance node
│   │   ├── reporting.py         # User input collection node
│   │   └── report.py            # Final report generation node
│   ├── routing/                  # Conditional Edge Logic
│   │   └── __init__.py          # Route functions for intelligent routing
│   ├── graph/                    # Graph Construction
│   │   └── __init__.py          # Workflow graph builder
│   └── tools/                    # External Tools Integration
│       └── __init__.py          # Tool initialization (Tavily, etc.)
├── main.py                      # Entry point / Main loop
├── agente.py                    # Old monolithic file (keep for reference)
├── Activities.csv               # Data file
└── README_STRUCTURE.md          # This file
```

## Key Improvements

### 1. **Separation of Concerns**
- **config/**: All configuration centralized
- **state/**: Single source of truth for data structure
- **prompts/**: Prompts isolated and easily updatable
- **agents/**: Each agent/node in its own module
- **routing/**: Conditional logic separated
- **graph/**: Graph construction logic isolated
- **tools/**: External tools management

### 2. **Scalability**
- **Easy to add new agents**: Create new file in `agents/`, define prompt in `prompts/`, add to graph in `graph/__init__.py`
- **Easy to update prompts**: Change any prompt file without touching agent logic
- **Easy to change models**: Update `config/models.py`
- **Easy to add tools**: Update `tools/__init__.py`

### 3. **Best Practices for AI Development**
- **Dependency Injection**: Models and tools passed to nodes, not hardcoded
- **Modular Prompts**: Each prompt in its own file with clear documentation
- **State Management**: Single TypedDict definition for type safety
- **Error Handling**: Centralized in main loop with better debugging
- **Logging/Monitoring**: Easy to add instrumentation per module

### 4. **Maintainability**
- **Clear imports**: `from src.config import initialize_models`
- **Documentation**: Each module has docstrings
- **Testing**: Easy to test individual agents in isolation
- **Versioning**: Package version defined in `__init__.py`

## Running the Agent

```bash
# Run the new modular version
python main.py

# Old version still works for compatibility
python agente.py
```

## Adding a New Agent

To add a new agent to the workflow:

1. **Create prompt** in `src/prompts/my_new_agent.py`:
```python
MY_NEW_AGENT_PROMPT = """
Your prompt here...
"""
```

2. **Create agent node** in `src/agents/my_new_agent.py`:
```python
def my_new_agent_node(llm, state: AgentState) -> AgentState:
    # Implementation
    return {...}
```

3. **Export** in `src/agents/__init__.py`:
```python
from .my_new_agent import my_new_agent_node
__all__ = [..., "my_new_agent_node"]
```

4. **Add to graph** in `src/graph/__init__.py`:
```python
workflow.add_node("my_new_agent", my_new_agent_wrapper)
workflow.add_edge("previous_node", "my_new_agent")
```

## Updating Models or Tools

To change LLM models or add new tools:

1. **Models**: Edit `src/config/models.py` → `initialize_models()`
2. **Tools**: Edit `src/tools/__init__.py` → `initialize_tools()`
3. Changes automatically propagate through dependency injection

## State Flow Diagram

```
┌─────────────────┐
│  Initial Input  │
└────────┬────────┘
         │
    ┌────v──────────────┐
    │ Initial Scanner   │ (lightweight, fast)
    └────┬──────────────┘
         │
    ┌────v──────────────────────┐
    │ Need Deep Scan?           │
    │ (conditional routing)     │
    └────┬──────────┬──────────┘
         │ Yes      │ No
    ┌────v────┐  ┌──v──────────────┐
    │ Deep    │  │ System Architect │
    │Analyzer │  │                  │
    └────┬────┘  └──┬──────────────┘
         │          │
         └─────┬────┘
              │
         ┌────v────────────────┐
         │ Need User Input?    │
         │ (conditional)      │
         └────┬────────┬──────┘
              │ Yes    │ No
         ┌────v────┐  ┌──v───────────────┐
         │  User   │  │ STRIDE Threat    │
         │  Input  │  │ Identifier       │
         └────┬────┘  └──┬───────────────┘
              └─────┬────┘
                   │
            ┌──────v──────────┐
            │ Impact Assessor │
            └────────┬────────┘
                     │
            ┌────────v─────────┐
            │ Mitigation       │
            │ Advisor          │
            └────────┬─────────┘
                     │
            ┌────────v────────┐
            │ Governance      │
            │ & Certification │
            └────────┬────────┘
                     │
            ┌────────v─────────┐
            │ Final Report     │
            │ Generation       │
            └──────────────────┘
```

## Benefits

✅ **Scalable**: Easy to add agents, prompts, tools
✅ **Maintainable**: Clear separation of concerns
✅ **Testable**: Isolated modules with clear dependencies
✅ **Professional**: Follows industry best practices
✅ **Documented**: Clear module documentation
✅ **Flexible**: Easy to modify any component
✅ **Type-Safe**: Using TypedDict for state validation
✅ **Reusable**: Prompts and agents can be reused in other projects

## Next Steps

1. Run `python main.py` to test the new structure
2. Keep `agente.py` as a reference (old implementation)
3. Gradually migrate code as needed
4. Add tests for individual agents
5. Add more comprehensive logging
6. Implement caching for expensive operations
