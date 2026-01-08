from llm_handler import LLMHandler
import os

print("--- Testing Auth Logic ---")

# Test 1: Instantiating without arguments (Expected to work if .env is correct)
print("\nTest 1: LLMHandler()")
try:
    handler = LLMHandler(model="google/gemini-2.0-flash-exp:free")
    key = handler.client.api_key
    print(f"Loaded Key: {key[:8]}..." if key else "No key loaded!")
    
    if key and "your-key" not in key.lower() and key != "YOUR_API_KEY_HERE":
        print("Success: Key seems to be loaded from .env")
    else:
        print("Failure: Key looks like a placeholder or is missing.")
except Exception as e:
    print(f"Error in Test 1: {e}")

# Test 2: Instantiating with placeholder (Simulating the bug)
print("\nTest 2: LLMHandler(api_key='YOUR_API_KEY_HERE')")
try:
    handler_buggy = LLMHandler(api_key="YOUR_API_KEY_HERE")
    key_buggy = handler_buggy.client.api_key
    print(f"Loaded Key: {key_buggy}")
    if key_buggy == "YOUR_API_KEY_HERE":
        print("Confirmed: Passing placeholder overrides .env logic.")
except Exception as e:
    print(f"Error in Test 2: {e}")
