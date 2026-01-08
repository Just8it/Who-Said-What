import os
from dotenv import load_dotenv
from openai import OpenAI

print("--- Test: Force Placeholder Key ---")
try:
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key="YOUR_API_KEY_HERE",
    )
    
    completion = client.chat.completions.create(
      model="google/gemini-2.0-flash-exp:free",
      messages=[{"role": "user", "content": "hi"}]
    )
    print("Success (Unexpected)")
except Exception as e:
    print(f"Failed as expected: {e}")
