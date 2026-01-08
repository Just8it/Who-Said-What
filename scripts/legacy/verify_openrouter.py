import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"Key loaded: {api_key[:10]}..." if api_key else "Key NOT loaded")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

print("\n--- Test 1: JSON Object Mode ---")
try:
    completion = client.chat.completions.create(
      model="google/gemini-2.5-flash",
      messages=[
        {
          "role": "user",
          "content": "Output a JSON object with key 'message' and value 'hello'"
        }
      ],
      response_format={"type": "json_object"}
    )
    print("Success with JSON mode!")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Failed with JSON mode: {e}")
