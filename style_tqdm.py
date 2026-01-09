import json

notebook_path = "tts_pipeline.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changes = 0
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            if "tqdm(" in line and "Processing Chapters" in line:
                print("Customizing tqdm bar...")
                # We want to change the tqdm call to include ascii=" █" and maybe cols
                # Current line: for i in tqdm(range(START_IDX, effective_end), desc="Processing Chapters", unit="chapter"):
                # Goal: for i in tqdm(range(START_IDX, effective_end), desc="Processing Chapters", unit="chapter", ascii=" █", ncols=80):
                
                # Simple replacement strategy
                if "ascii=" not in line:
                    line = line.replace('unit="chapter")', 'unit="chapter", ascii=" ░▒▓█", ncols=100)')
                    changes += 1
            new_source.append(line)
        cell["source"] = new_source

if changes > 0:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print(f"Patched {changes} tqdm call(s).")
else:
    print("No matching tqdm calls found.")
