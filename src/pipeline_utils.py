import requests
import json
import re
from typing import List, Dict

class CostMonitor:
    @staticmethod
    def get_usage(api_key: str) -> float:
        if not api_key or "YOUR_API_KEY" in api_key: return 0.0
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return float(data.get("data", {}).get("usage", 0.0))
        except:
            return 0.0
        return 0.0

class PromptFactory:
    @staticmethod
    def create_prompt(context_header: str, chunk_text: str) -> str:
        return f"""
You are an expert novel text analyzer. Convert the text into a JSON list of segments.

{context_header}

### INSTRUCTIONS:
1. Split the text strictly by Speaker.
2. **The Sandwich Rule:** If a paragraph has dialogue in the middle, split it! (Narrator -> Character -> Narrator).
3. **The Quote Rule:** Text inside "quotation marks" is dialogue. Text outside is Narration.
4. **The Thought Rule:** Thoughts (often in italics) are NOT dialogue. Set 'is_dialogue': false.
5. **Emotion/Tone:** Infer the emotion from the text context.

### JSON FORMAT:
[
  {{"text": "...", "speaker": "Name", "is_dialogue": true, "emotion": "...", "tone": "..."}}
]

TEXT TO PROCESS:
{chunk_text}

Respond ONLY with the valid JSON list.
"""

class OutputJanitor:
    @staticmethod
    def clean_json(raw_text: str) -> List[Dict]:
        """Fixes malformed JSON and trims overlaps."""
        clean = re.sub(r'```json\s*', '', raw_text)
        clean = re.sub(r'\s*```', '', clean).strip()
        
        # Smart Closure
        if clean.startswith('{') and not clean.endswith('}'): clean += '}'
        elif clean.startswith('[') and not clean.endswith(']'): clean += ']'
        
        try:
            data = json.loads(clean)
            # Unwrap dicts
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list): 
                        data = v 
                        break
        except json.JSONDecodeError:
            print("[Janitor] JSON Decode Error - returning empty list.")
            return []
            
        if not isinstance(data, list):
            return []

        # Fix Overlap
        for i in range(len(data) - 1):
            curr = data[i]
            nxt = data[i+1]
            c_txt = curr.get("text", "")
            n_txt = nxt.get("text", "")
            
            # If next segment is fully contained at the END of current segment
            if c_txt.endswith(n_txt) and len(n_txt) > 0 and len(n_txt) < len(c_txt):
                # Trim it
                new_text = c_txt[:-len(n_txt)].strip()
                # print(f"[Janitor] Trimming echo: '{c_txt}' -> '{new_text}'")
                curr["text"] = new_text

        return data
