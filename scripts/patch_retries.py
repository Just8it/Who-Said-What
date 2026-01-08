import json
import os

notebook_path = "tts_pipeline.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changes_made = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source_str = "".join(cell["source"])
        
        # 1. Inject Config
        if "os.environ" in source_str and "MAX_RETRIES" not in source_str:
            print("Patching Config Cell...")
            # Append to the end of the cell
            cell["source"].append("\n# --- RETRY CONFIGURATION ---\n")
            cell["source"].append("MAX_RETRIES = 3  # Set to 0 to disable retries")
            changes_made = True
            
        # 2. Update Function Call
        if "handler.process_chapter(" in source_str and "max_retries=" not in source_str:
            print("Patching Execution Cell...")
            new_lines = []
            for line in cell["source"]:
                if "handler.process_chapter(" in line:
                    new_lines.append(line)
                elif "chapter_id=i" in line:
                    new_lines.append(line.rstrip() + ",\n") # Add comma
                    new_lines.append("                max_retries=MAX_RETRIES\n")
                else:
                    new_lines.append(line)
            cell["source"] = new_lines
            changes_made = True

if changes_made:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print("Notebook patched successfully!")
else:
    print("No changes needed (already patched?).")
