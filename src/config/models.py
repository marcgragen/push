"""
Configuration for LLM Models and Fallback Strategy
"""
import os
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


def initialize_models():
    """
    Initialize LLM models with quota failover support.
    
    Strategy:
    1. Primary: Gemini Flash (most capable, cloud-based)
    2. Fallback: Gemini Flash-8b (lightweight cloud model)
    3. Final: Llama 3.2 (local, always available)
    """
    print("[SYSTEM] Configuring models with quota failover support...")

    llm_primary = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    llm_fallback = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-8b", 
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    llm_local = ChatOllama(
        model="llama3.2",  # Recommended model for performance/speed on M4
        temperature=0
    )

    # Couple the fallback: First try Gemini Flash, then Gemini Flash-8b, 
    # and finally resort to the local model on your Mac Mini M4.
    llm = llm_primary.with_fallbacks([llm_fallback, llm_local])

    # Lightweight vs Deep LLMs for Two-Phase Scanning
    # `llm_light` is used for quick, local scans; `llm_deep` uses cloud models for heavier analysis.
    llm_light = llm_local
    llm_deep = llm

    return {
        "llm_primary": llm_primary,
        "llm_fallback": llm_fallback,
        "llm_local": llm_local,
        "llm": llm,
        "llm_light": llm_light,
        "llm_deep": llm_deep,
    }
