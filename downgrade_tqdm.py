import json

notebook_path = "tts_pipeline.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changes = 0
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            if "from tqdm.notebook import tqdm" in line:
                print("Swapping to standard tqdm...")
                line = line.replace("from tqdm.notebook import tqdm", "from tqdm import tqdm")
                changes += 1
            new_source.append(line)
        cell["source"] = new_source

if changes > 0:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print(f"Patched {changes} import(s).")
else:
    print("No tqdm.notebook imports found.")
