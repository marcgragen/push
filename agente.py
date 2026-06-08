import pandas as pd
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

# 1. Conectar con el LLM local
llm = ChatOllama(model="llama3.2", temperature=0)

# 2. Definir la herramienta REAL de Análisis de Telemetría
@tool
def analizar_archivo_entrenamiento(ruta_archivo: str) -> str:
    """Usa esta herramienta EXCLUSIVAMENTE para leer un archivo CSV con datos de entrenamientos de Garmin/Strava."""
    print(f"\n[SISTEMA: Analizando telemetría en {ruta_archivo}...]\n")
    
    if not os.path.exists(ruta_archivo):
        return f"Error: No se pudo encontrar el archivo en la ruta {ruta_archivo}."
    
    try:
        # Leemos el archivo CSV. 
        df = pd.read_csv(ruta_archivo)
        
        # Generamos un resumen estadístico básico de los datos numéricos de la ruta
        resumen_estadistico = df.describe().to_string()
        
        resultado = f"Lectura exitosa. Aquí tienes las estadísticas de la sesión:\n{resumen_estadistico}\n"
        resultado += "Por favor, analiza estos datos e identifica picos de esfuerzo, carga de entrenamiento o sugiere tiempos de recuperación."
        
        return resultado
    except Exception as e:
        return f"Error crítico al procesar el archivo deportivo: {str(e)}"

herramientas = [analizar_archivo_entrenamiento]

# 3. Inicializar la memoria (Checkpointer)
memoria = MemorySaver()

# 4. Crear las instrucciones base del sistema (System Prompt)
instrucciones_sistema = """Eres un analista de rendimiento deportivo y entrenador personal de alto nivel, educado y analítico.
REGLAS ESTRICTAS DE COMPORTAMIENTO:
1. Especialízate en analizar métricas de ciclismo, running y senderismo.
2. Al evaluar el ciclismo, enfócate en la relación entre vatios y el desnivel acumulado.
3. Si el usuario te saluda o hace una pregunta general sobre deporte, responde amablemente.
4. NO utilices tu herramienta de análisis a menos que el usuario te proporcione explícitamente la ruta de un archivo CSV en su ordenador.
5. Tu objetivo es cruzar los datos aportados para detectar fatiga, mejoras de forma y sugerir entrenamientos."""

# 5. Crear el agente pasándole la memoria Y el System Prompt
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

# 6. Configurar el "Hilo" (Thread) de la conversación
config = {"configurable": {"thread_id": "analista_deportivo_01"}}

print("\n--- Agente de Rendimiento Deportivo Iniciado (Escribe 'salir' para terminar) ---")
print("Consejo: Pásale la ruta de un CSV exportado de Strava/Garmin para analizar tu ruta.")

# 7. El Bucle del Chatbot
while True:
    pregunta = input("\nTú: ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("Guardando zapatillas y apagando agente...")
        break

    resultado = agente.invoke(
        {"messages": [HumanMessage(content=pregunta)]},
        config=config
    )

    print(f"\nAgente: {resultado['messages'][-1].content}")