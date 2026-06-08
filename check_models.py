import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Searching for models compatible with content generation...")
for model in client.models.list():
    # We use supported_actions as suggested by the error
    if "generateContent" in model.supported_actions:
        print(f"- {model.name}")