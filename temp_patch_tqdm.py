import json

notebook_path = "tts_pipeline.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        source_str = "".join(source)
        
        # Identify the main execution cell
        if "from llm_handler import LLMHandler" in source_str and "handler.process_chapter" in source_str:
            print("Found Main Execution Cell.")
            new_source = []
            
            # 1. Inject Import if missing
            if "from tqdm.notebook import tqdm" not in source_str:
                print("Adding tqdm import...")
                import_added = False
                for line in source:
                    new_source.append(line)
                    if "import json" in line and not import_added:
                        new_source.append("from tqdm.notebook import tqdm\n")
                        import_added = True
                source = new_source # Update for next step
            
            # 2. Wrap Loop
            final_source = []
            for line in source:
                if "for i in range(START_IDX, effective_end):" in line:
                    print("Wrapping loop with tqdm...")
                    final_source.append(line.replace("range(START_IDX, effective_end)", "tqdm(range(START_IDX, effective_end), desc=\"Processing Chapters\", unit=\"chapter\")"))
                else:
                    final_source.append(line)
            
            cell["source"] = final_source
            print("Cell updated.")
            break

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4)

print("Notebook patched with tqdm.")
