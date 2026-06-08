import os
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated, Union
import operator

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

try:
    # Intentamos la importación oficial del nuevo paquete
    from langchain_tavily import TavilySearchResults
    from langchain_core.runnables import RunnableConfig # Necesario para Tavily
except ImportError:
    # Fallback de seguridad si el paquete de integración falla en Python 3.14
    print("[SISTEMA] Aviso: Usando fallback de búsqueda debido a incompatibilidad de entorno.")
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_core.runnables import RunnableConfig # Necesario para Tavily

# 1. Cargar variables de entorno ocultas
load_dotenv()

print("[SISTEMA] Configurando modelos con tolerancia a fallos de cuota...")

llm_principal = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

llm_respaldo = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-8b", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

llm_ollama = ChatOllama(
    model="llama3.2",  # Modelo recomendado para rendimiento/velocidad en M4
    temperature=0
)

# Acoplamos el fallback: Primero intenta Gemini Flash, luego Gemini Flash-8b, 
# y finalmente recurre al modelo local en tu Mac Mini M4.
llm = llm_principal.with_fallbacks([llm_respaldo, llm_ollama])

# --- AgentState Definition ---
class AgentState(TypedDict):
    """
    Representa el estado compartido entre los agentes en el grafo.
    """
    query: str
    raw_infra_data: str  # Ingesta de IaC (K8s, Terraform), OpenAPI o Scans
    corporate_policies: str  # Políticas internas y reglas de cumplimiento
    architecture_description: str
    threats_stride: str
    impact_assessment: str
    mitigations: str
    otm_report: str  # Reporte en formato Open Threat Model (JSON)
    status: str  # Draft -> In Review -> Approved
    mermaid_diagrams: Annotated[List[str], operator.add]
    mitre_attack_references: Annotated[List[str], operator.add]
    messages: Annotated[List[BaseMessage], operator.add]

# --- Tools Setup ---
tavily_tool = None
if os.getenv("TAVILY_API_KEY"):
    tavily_tool = TavilySearchResults(max_results=3)
else:
    # Evita que el agente falle al iniciar si falta la clave, simplemente deshabilita la búsqueda
    print("[ADVERTENCIA] TAVILY_API_KEY no configurada. El agente no tendrá acceso a internet.")

# --- Agent Prompts ---
SYSTEM_ARCHITECT_PROMPT = """
Eres un Arquitecto de Sistemas experto en Ingesta "Zero-Friction". Tu tarea es parsear infraestructura y código.
Capacidades de Ingesta:
1. IaC: Analiza manifiestos K8s, RBAC, Dockerfiles y Terraform. Identifica componentes y redes.
2. APIs: Lee archivos Swagger/OpenAPI para extraer endpoints y métodos de auth.
3. Scanners: Integra resultados de Trivy/Kubiscan si se proporcionan.

Si la información es insuficiente, solicita más detalles.
Tu objetivo es generar una descripción detallada de la arquitectura y, lo más importante, un diagrama Mermaid.js de tipo 'flowchart TD' que represente las fronteras de confianza (usando 'subgraph') y los flujos de datos (etiquetando los protocolos).

CAPACIDADES DE DIAGRAMACIÓN (MERMAID.JS):
1. Fronteras de Confianza: Usa 'subgraph' para aislar visualmente componentes por nivel de red (Internet, DMZ, Red Interna, DB).
2. DFD Dinámicos (flowchart TD/LR): Etiqueta flechas con protocolos (|HTTPS/REST|, |SQL via TLS 1.2|). Identifica flujos inseguros.
3. Secuencias de Autenticación (sequenceDiagram): Para flujos de Login, OAuth o OIDC, mostrando el intercambio de JWT/Tokens entre Usuario, App e IdP.
4. Políticas RBAC y K8s: Visualiza relaciones entre ServiceAccount, RoleBinding y Pods a partir de descripciones de infraestructura.
5. Ciclos de Vida de Datos (stateDiagram-v2): Mapea el estado de sensibilidad del dato (Público -> Confidencial -> Cifrado).

REGLAS DE SINTAXIS:
- Usa `flowchart TD` para arquitecturas generales.
- Componentes: `[ ]` para procesos/apps, `[( )]` para DBs, `(( ))` para usuarios/entidades externas.
- Todos los diagramas deben entregarse en bloques de código markdown para su renderización automática.

Ejemplo de salida Mermaid:
```mermaid
flowchart TD
    Cliente((Usuario Externo))

    subgraph DMZ Corporativa
        WAF[Web Application Firewall]
        App[Aplicación Interna]
    end

    subgraph Red Interna Segura
        DB[(PostgreSQL)]
    end

    Cliente --o|HTTPS| WAF
    WAF --o|Proxy| App
    App --o|TCP 5432| DB
```
Asegúrate de que el diagrama sea completo y represente fielmente la arquitectura.
"""

STRIDE_THREAT_IDENTIFIER_PROMPT = """
Eres un experto en seguridad especializado en la metodología STRIDE para el modelado de amenazas.
Tu tarea es analizar la descripción de la arquitectura y los diagramas Mermaid proporcionados por el Arquitecto de Sistemas.
Identifica amenazas específicas utilizando las categorías STRIDE y contrastándolas con las políticas corporativas.
Etiqueta cada amenaza con su correspondiente CWE (Common Weakness Enumeration).

Formato de la tabla STRIDE:
| ID Amenaza | Componente | Categoría | CWE | Descripción (Cumplimiento de Política) |
|---|---|---|---|---|
| T-001 | Autenticación | Spoofing | CWE-287 | Un atacante podría suplantar identidad. |
| T-002 | DB | Info Disclosure | CWE-311 | Datos expuestos sin cifrado. |
"""

IMPACT_ASSESSOR_PROMPT = """
Eres un Analista de Riesgos de Seguridad con experiencia en MITRE ATT&CK.
Tu tarea es evaluar el impacto potencial de cada amenaza STRIDE identificada, asignando un nivel de riesgo (Alto, Medio, Bajo).
Además, para cada amenaza, identifica y referencia las tácticas y técnicas relevantes de MITRE ATT&CK.
Genera una tabla Markdown que combine la información de STRIDE con la evaluación de impacto y las referencias a MITRE ATT&CK.

Formato de la tabla de Impacto y MITRE ATT&CK:
| ID Amenaza | Nivel de Riesgo | Impacto Potencial | Tácticas MITRE ATT&CK | Técnicas MITRE ATT&CK |
|---|---|---|---|---|
| T-001 | Alto | Acceso no autorizado, pérdida de datos. | Credential Access, Persistence | T1078 (Valid Accounts), T1098 (Account Manipulation) |
| T-002 | Medio | Fuga de información sensible, multas regulatorias. | Exfiltration, Collection | T1041 (Exfiltration Over C2 Channel), T1005 (Data from Local System) |
"""

MITIGATION_ADVISOR_PROMPT = """
Eres un Asesor de Mitigación de Seguridad DevSecOps.
Por cada amenaza, debes proporcionar una mitigación técnica y un SNIPPET DE CÓDIGO o configuración (YAML/HCL).

Formato de la tabla de Mitigaciones:
| ID Amenaza | Mitigación | Snippet / Config | Justificación |
|---|---|---|---|
| T-001 | Habilitar TLS | `ssl-redirect: "true"` | Previene T1041 |
"""

GOVERNANCE_PROMPT = """
Eres el Motor de Gobernanza y Certificación de Ciberseguridad.
Tu tarea es:
1. Analizar las amenazas y mitigaciones presentadas.
2. Calcular el riesgo residual.
3. Si el riesgo es aceptable según las políticas corporativas, marcar el estado como 'Approved'. De lo contrario, marcar como 'Draft'.
4. Generar un resumen en formato Open Threat Model (OTM) JSON.

Asegúrate de ser riguroso con los umbrales de seguridad de la compañía.
"""

# --- Agent Functions (Nodes) ---

def system_architect_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Arquitecto de Sistemas ---")
    query = state["query"]
    messages = state["messages"]
    messages.append(HumanMessage(content=f"Usuario: {query}"))
    
    # Simulación de carga de políticas corporativas
    policies = "1. Toda DB debe estar en subred aislada. 2. Uso obligatorio de WAF para tráfico externo."

    architect_prompt_content = SYSTEM_ARCHITECT_PROMPT + f"\n\nLa aplicación/sistema a analizar es: {query}"
    
    search_results_str = ""
    if tavily_tool and any(x in query.lower() for x in ["buscar", "arquitectura", "swagger", "manifest"]):
        print("    [INFO] Usando Tavily para buscar información de la arquitectura.")
        try:
            # TavilySearchResults.invoke espera un dict con 'query'
            search_results = tavily_tool.invoke({"query": f"arquitectura técnica de {query}"})
            search_results_str = f"\n\nResultados de búsqueda relevantes:\n{search_results}"
        except Exception as e:
            print(f"    [ADVERTENCIA] Error al usar Tavily: {e}. Continuando sin resultados de búsqueda.")
            search_results_str = "\n\n[ADVERTENCIA] La búsqueda externa falló."

    final_architect_prompt = architect_prompt_content + search_results_str
    
    # Llamar al LLM con el prompt combinado
    response_message = llm.invoke([HumanMessage(content=final_architect_prompt)])
    architecture_output = response_message.content

    # Extraer diagramas Mermaid (heurística simple por ahora)
    mermaid_blocks = []
    current_mermaid = []
    in_mermaid_block = False
    for line in architecture_output.splitlines():
        if line.strip() == "```mermaid":
            in_mermaid_block = True
            current_mermaid = []
        elif line.strip() == "```" and in_mermaid_block:
            in_mermaid_block = False
            mermaid_blocks.append("\n".join(current_mermaid))
            current_mermaid = []
        elif in_mermaid_block:
            current_mermaid.append(line)

    # Eliminar bloques mermaid del output para una descripción más limpia
    architecture_description_clean = architecture_output
    for block in mermaid_blocks:
        architecture_description_clean = architecture_description_clean.replace(f"```mermaid\n{block}\n```", "").strip()

    return {
        "architecture_description": architecture_description_clean,
        "raw_infra_data": query, # Guardamos el input crudo para trazabilidad
        "corporate_policies": policies,
        "mermaid_diagrams": mermaid_blocks,
        "messages": messages + [AIMessage(content=architecture_output)] # Almacenar el output completo incluyendo mermaid para contexto
    }

def stride_threat_identifier_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Identificador de Amenazas STRIDE ---")
    architecture_desc = state["architecture_description"]
    mermaid_diagrams = "\n".join(state["mermaid_diagrams"])
    policies = state["corporate_policies"]
    messages = state["messages"]

    stride_prompt = STRIDE_THREAT_IDENTIFIER_PROMPT + \
                    f"\n\nDescripción de la Arquitectura:\n{architecture_desc}" + \
                    f"\n\nDiagramas Mermaid:\n{mermaid_diagrams}" + \
                    f"\n\nPolíticas Corporativas:\n{policies}"

    response_message = llm.invoke([HumanMessage(content=stride_prompt)])
    stride_output = response_message.content

    return {
        "threats_stride": stride_output,
        "messages": messages + [AIMessage(content=stride_output)]
    }

def impact_assessor_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Evaluador de Impacto ---")
    threats_stride = state["threats_stride"]
    architecture_desc = state["architecture_description"] # Contexto para el impacto
    messages = state["messages"]

    impact_prompt = IMPACT_ASSESSOR_PROMPT + \
                    f"\n\nArquitectura:\n{architecture_desc}" + \
                    f"\n\nAmenazas STRIDE identificadas:\n{threats_stride}"

    response_message = llm.invoke([HumanMessage(content=impact_prompt)])
    impact_output = response_message.content

    # Extracción simple de referencias MITRE ATT&CK (puede mejorarse)
    mitre_refs = []
    for line in impact_output.splitlines():
        if "T" in line and "(" in line and ")" in line: # Heurística para códigos T
            mitre_refs.append(line)

    return {
        "impact_assessment": impact_output,
        "mitre_attack_references": mitre_refs,
        "messages": messages + [AIMessage(content=impact_output)]
    }

def mitigation_advisor_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Asesor de Mitigación ---")
    threats_stride = state["threats_stride"]
    impact_assessment = state["impact_assessment"]
    messages = state["messages"]

    mitigation_prompt = MITIGATION_ADVISOR_PROMPT + \
                        f"\n\nAmenazas STRIDE:\n{threats_stride}" + \
                        f"\n\nEvaluación de Impacto y MITRE ATT&CK:\n{impact_assessment}"

    response_message = llm.invoke([HumanMessage(content=mitigation_prompt)])
    mitigation_output = response_message.content

    return {
        "mitigations": mitigation_output,
        "messages": messages + [AIMessage(content=mitigation_output)]
    }

def governance_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Gobernanza y Escala ---")
    messages = state["messages"]
    
    gov_prompt = GOVERNANCE_PROMPT + f"\n\nContexto: {state['threats_stride']} \n {state['mitigations']}"
    response = llm.invoke([HumanMessage(content=gov_prompt)])
    
    # Simulamos la asignación de estado basada en la lógica del LLM
    status = "Approved" if "riesgo bajo" in response.content.lower() else "In Review"
    
    return {
        "otm_report": response.content,
        "status": status,
        "messages": messages + [AIMessage(content=f"Estado de Certificación: {status}")]
    }

def final_report_node(state: AgentState) -> AgentState:
    print("\n--- Agente: Generador de Reporte Final ---")
    final_report_content = (
        f"# Reporte de Modelado de Amenazas (Estado: {state['status']})\n\n"
        "## 1. Arquitectura del Sistema (Ingesta Zero-Friction)\n"
        f"{state['architecture_description']}\n\n"
        "### Diagramas Mermaid (DFD / Trust Boundaries)\n"
        + "\n\n".join([f"```mermaid\n{d}\n```" for d in state['mermaid_diagrams']]) + "\n\n"
        "## 2. Amenazas Identificadas (STRIDE + CWE)\n"
        f"{state['threats_stride']}\n\n"
        "## 3. Evaluación de Impacto y MITRE ATT&CK\n"
        f"{state['impact_assessment']}\n\n"
        "## 4. Controles y Mitigaciones (Snippets Dev-Friendly)\n"
        f"{state['mitigations']}\n\n"
        "## 5. Gobernanza y Formato Abierto (OTM)\n"
        "El modelo ha sido catalogado y exportado para integración en CI/CD.\n"
        f"Status: {state['status']}\n"
        "---"
    )
    return {"messages": state["messages"] + [AIMessage(content=final_report_content)]}

# --- Build the Graph ---
workflow = StateGraph(AgentState)

# Añadir nodos para cada agente
workflow.add_node("system_architect", system_architect_node)
workflow.add_node("stride_threat_identifier", stride_threat_identifier_node)
workflow.add_node("impact_assessor", impact_assessor_node)
workflow.add_node("mitigation_advisor", mitigation_advisor_node)
workflow.add_node("governance_node", governance_node)
workflow.add_node("final_report", final_report_node)

# Definir la secuencia de ejecución
workflow.set_entry_point("system_architect")
workflow.add_edge("system_architect", "stride_threat_identifier")
workflow.add_edge("stride_threat_identifier", "impact_assessor")
workflow.add_edge("impact_assessor", "mitigation_advisor")
workflow.add_edge("mitigation_advisor", "governance_node")
workflow.add_edge("governance_node", "final_report")
workflow.add_edge("final_report", END)

# Inicializar memoria
memoria = MemorySaver()

# Compilar el grafo
app = workflow.compile(checkpointer=memoria)

# --- Configuración y Bucle Principal ---
config = {"configurable": {"thread_id": "threat_modeling_session_01"}}

print("\n--- Agente Arquitecto de Seguridad (Threat Modeling) Iniciado ---")
print("Introduce el nombre de una aplicación o describe una arquitectura para comenzar.")

while True:
    pregunta = input("\nTú: ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("Guardando bicicleta y apagando agente...")
        break

    # Invocar el grafo con el estado inicial
    resultado = app.invoke(
        {
            "query": pregunta, 
            "messages": [HumanMessage(content=pregunta)], 
            "mermaid_diagrams": [], 
            "mitre_attack_references": [],
            "raw_infra_data": "",
            "corporate_policies": ""
        },
        config=config
    )

    # El nodo final_report_node añade el reporte completo a los mensajes.
    # Imprimimos el contenido del último mensaje, que es el reporte final.
    final_report_message = resultado['messages'][-1].content
    print(f"\nAgente: {final_report_message}")