import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    # Intentamos la importación oficial del nuevo paquete
    from langchain_tavily import TavilySearchResults
except ImportError:
    # Fallback de seguridad si el paquete de integración falla en Python 3.14
    print("[SISTEMA] Aviso: Usando fallback de búsqueda debido a incompatibilidad de entorno.")
    from langchain_community.tools.tavily_search import TavilySearchResults

# 1. Cargar variables de entorno ocultas
load_dotenv()

# 2. Definir el modelo principal y el de respaldo
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

# 3. Definir herramientas: Búsqueda para investigar arquitecturas online
if os.getenv("TAVILY_API_KEY"):
    herramientas = [TavilySearchResults(max_results=3)]
else:
    # Evita que el agente falle al iniciar si falta la clave, simplemente deshabilita la búsqueda
    print("[ADVERTENCIA] TAVILY_API_KEY no configurada. El agente no tendrá acceso a internet.")
    herramientas = []

# 4. Inicializar memoria
memoria = MemorySaver()

# 5. Crear el System Prompt
instrucciones_sistema = """Rol: Actúa como un Arquitecto de Seguridad DevSecOps experto en metodologías de Threat Modeling.

TAREA: Generar un Reporte de Modelado de Amenazas formal y profesional utilizando Mermaid.js para la visualización técnica de la arquitectura.

ACCIONES OBLIGATORIAS:
1. INVESTIGACIÓN: Si el usuario da un nombre de aplicación, utiliza la herramienta de búsqueda para obtener información técnica sobre su arquitectura típica, stack y dependencias.
2. CLARIFICACIÓN: Si la información no se encuentra o es insuficiente, solicita al usuario los detalles necesarios (componentes, flujos de datos, usuarios, entorno de despliegue).
3. MODELADO (Reporte Final):
   - Generar diagramas Mermaid.js siguiendo los estándares técnicos detallados abajo.
   - Matriz STRIDE Tabular: Genera una tabla Markdown con ID de Amenaza, Componente Afectado, Categoría STRIDE, Descripción Técnica y Nivel de Riesgo (Alto/Medio/Bajo).
   - Controles de Mitigación Accionables: Proporciona contramedidas técnicas específicas (ej. "Implementar TLS 1.3" en lugar de "Cifrar").

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
"""

# 6. Crear el agente
try:
    agente = create_react_agent(
        llm, 
        herramientas, 
        checkpointer=memoria,
        messages_modifier=instrucciones_sistema 
    )
except TypeError:
    agente = create_react_agent(
        llm, 
        herramientas, 
        checkpointer=memoria,
        prompt=instrucciones_sistema 
    )

# 7. Configuración
config = {"configurable": {"thread_id": "threat_modeling_session_01"}}

print("\n--- Agente Arquitecto de Seguridad (Threat Modeling) Iniciado ---")
print("Introduce el nombre de una aplicación o describe una arquitectura para comenzar.")

# 8. El Bucle del Chatbot
while True:
    pregunta = input("\nTú: ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("Guardando bicicleta y apagando agente...")
        break

    resultado = agente.invoke(
        {"messages": [HumanMessage(content=pregunta)]},
        config=config
    )

    print(f"\nAgente: {resultado['messages'][-1].content}")