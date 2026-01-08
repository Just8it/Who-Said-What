from pipeline_utils import CostMonitor
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("Error: No API Key found in .env")
else:
    print(f"Checking usage for key ending in ...{api_key[-5:]}")
    usage = CostMonitor.get_usage(api_key)
    print(f"Current Usage Reported: ${usage:.4f}")
