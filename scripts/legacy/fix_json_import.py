import json

notebook_path = "tts_pipeline.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

found = False
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "from book_processor import EpubLoader" in source:
             if "import json" not in source:
                print("Found batch cell. Adding missing 'import json'...")
                # Insert import json at the top
                cell["source"].insert(0, "import json\n")
                found = True
                break

if found:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print("Notebook patched: Added 'import json'.")
else:
    print("Batch cell not found or already has import.")
