import json
import os

notebook_path = "../tts_pipeline.ipynb"

# The NEW content for the cell (imports + batch logic)
new_source_lines = [
    "import sys\n",
    "import os\n",
    "# Ensure we can import from src\n",
    "sys.path.append(os.path.abspath('src'))\n",
    "sys.path.append(os.path.abspath('.'))\n",
    "\n",
    "from src.book_processor import EpubLoader, Chapter\n",
    "from src.llm_handler import LLMHandler\n",
    "from src.pipeline_utils import CostMonitor\n",
    "from src.character_manager import CharacterManager\n",
    "from src.logger_utils import run_logger\n",
    "from dotenv import load_dotenv\n",
    "import json\n",
    "\n",
    "# Load Environment\n",
    "load_dotenv()\n",
    "\n",
    "# CONFIG\n",
    "config_path = \"data/book_config_dcc.json\"\n",
    "char_manager = CharacterManager(config_path)\n",
    "\n",
    "# Initialize LLM\n",
    "# Priority: Local Var > OpenRouter Env > OpenAI Env\n",
    "if 'api_key' not in locals():\n",
    "    api_key = os.getenv(\"OPENROUTER_API_KEY\") or os.getenv(\"OPENAI_API_KEY\") or \"YOUR_API_KEY_HERE\"\n",
    "\n",
    "# Ensure Output Dir (Standalone safety)\n",
    "if 'output_dir' not in locals():\n",
    "    # Standard logging start\n",
    "    output_dir = run_logger.start_run()\n",
    "    print(f'Output directory set to: {output_dir}')\n",
    "else:\n",
    "    os.makedirs(output_dir, exist_ok=True)\n",
    "\n",
    "handler = LLMHandler(api_key=api_key, model=\"google/gemini-2.5-flash\")\n",
    "\n",
    "# --- SAFETY CONFIG ---\n",
    "MAX_COST_PER_RUN = 2.00\n",
    "try:\n",
    "    start_usage = CostMonitor.get_usage(api_key)\n",
    "    print(f\"Initial Usage: ${start_usage:.4f}\")\n",
    "except Exception:\n",
    "    start_usage = 0.0\n",
    "    print(\"Initial Usage: Unknown (monitor failed)\")\n",
    "\n",
    "# --- BATCH CONFIGURATION ---\n",
    "START_IDX = 0  # Start index (inclusive)\n",
    "END_IDX = 10   # End index (inclusive)\n",
    "# ---------------------------\n",
    "\n",
    "if 'chapters' in locals() and chapters:\n",
    "    print(f\"Starting Batch Run: Chapters {START_IDX} to {END_IDX}\")\n",
    "    effective_end = min(END_IDX + 1, len(chapters))\n",
    "    \n",
    "    for i in range(START_IDX, effective_end):\n",
    "        # Cost Check\n",
    "        current_usage = CostMonitor.get_usage(api_key)\n",
    "        run_cost = current_usage - start_usage\n",
    "        if run_cost > MAX_COST_PER_RUN:\n",
    "            print(f\"\\n[SAFETY] Limit Reached! Run Cost: ${run_cost:.4f}\")\n",
    "            break\n",
    "            \n",
    "        chapter = chapters[i]\n",
    "        \n",
    "        # Safe Filename\n",
    "        safe_title = \"\".join([c if c.isalnum() else \"_\" for c in chapter.title])[:50]\n",
    "        filename = f\"chapter_{i:03d}_{safe_title}.json\"\n",
    "        filepath = os.path.join(output_dir, filename)\n",
    "        \n",
    "        if os.path.exists(filepath):\n",
    "            print(f\"Skipping Chapter {i}: {filename} exists.\")\n",
    "            continue\n",
    "            \n",
    "        print(f\"\\n=== Processing Chapter {i}: {chapter.title} ===\")\n",
    "        try:\n",
    "            # STEP 1: CONTEXT AWARE PROMPTING (Local)\n",
    "            context_header = char_manager.get_dynamic_prompt_header(chapter.content_raw)\n",
    "            \n",
    "            # STEP 2: GENERATION (API Call 1)\n",
    "            segments = handler.process_chapter(\n",
    "                chapter.content_raw,\n",
    "                context_header=context_header,\n",
    "                chapter_id=i\n",
    "            )\n",
    "            \n",
    "            # STEP 3: AUTOSYNC (Local)\n",
    "            char_manager.update_profiles(segments, chapter_id=i)\n",
    "            \n",
    "            # STEP 4: ACTIVE ENRICHMENT (API Call 2)\n",
    "            # Deduplicates and profiles new characters\n",
    "            char_manager.enrich_db(handler.client, segments, handler.model)\n",
    "            \n",
    "            # Save\n",
    "            with open(filepath, \"w\", encoding=\"utf-8\") as f:\n",
    "                json.dump([s.dict() for s in segments], f, indent=2)\n",
    "            print(f\"Saved: {filename}\")\n",
    "            \n",
    "        except Exception as e:\n",
    "            print(f\"ERROR processing Chapter {i}: {e}\")\n",
    "            continue\n",
    "            \n",
    "    print(\"\\nBatch Run Complete.\")"
]

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

found = False
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        # Identify the main processing cell (originally Step 3)
        if "Initialize LLM" in source and "handler =" in source:
            print("Found Step 3 cell. Updating...")
            cell["source"] = new_source_lines
            found = True
            break
            
if found:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print("Notebook updated successfully.")
else:
    print("Could not find targets to update. Please check notebook structure.")

