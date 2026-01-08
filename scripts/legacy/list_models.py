import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

print("Listing models matching 'gemini' and 'flash'...")
try:
    models = client.models.list()
    for model in models.data:
        if "gemini" in model.id and "flash" in model.id:
            print(f"- {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
