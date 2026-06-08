import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Buscando modelos compatibles con generación de contenido...")
for model in client.models.list():
    # Usamos supported_actions como sugirió el error
    if "generateContent" in model.supported_actions:
        print(f"- {model.name}")