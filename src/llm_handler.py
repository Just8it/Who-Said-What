import os
import json
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError
from book_processor import Segment, Chapter

load_dotenv()


class LLMHandler:
    def __init__(self, api_key: str = None, base_url: str = "https://openrouter.ai/api/v1", model: str = "google/gemini-2.5-flash"):
        # Robust handling: Ignore placeholder if passed (common usage error in notebooks)
        if api_key is None or "YOUR_API_KEY_HERE" in str(api_key):
            api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
             print("Warning: No API key found. LLM calls will likely fail.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def process_chapter(self, chapter_text: str, context_header: str = "", chapter_id: int = -1) -> List[Segment]:
        """
        Sends the chapter text to the LLM to be split into attribute segments.
        """
        if not context_header:
            # Fallback if no specific context provided
            context_header = "### KNOWN SPEAKERS: Narrator, Unknown."

        # 1. Create Prompt
        from pipeline_utils import PromptFactory, OutputJanitor
        final_prompt = PromptFactory.create_prompt(context_header, chapter_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": final_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # 2. Janitor Cleaning
            data = OutputJanitor.clean_json(content)
            
            segments = []
            for i, item in enumerate(data):
                try:
                    seg = Segment(**item)
                    segments.append(seg)
                except ValidationError as e:
                    print(f"Warning: Skipping invalid segment at index {i}: {e}")
                    # Optional: Print item content to see what failed
                    # print(f"Bad Item: {item}")
                    continue
            
            return segments

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM: {e}")
            print(f"Raw Output: {content[:500]}...")
            return []
        except Exception as e:
            print(f"API Error: {e}")
            return []
