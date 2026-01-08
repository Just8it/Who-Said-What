import json

notebook_path = "tts_pipeline.ipynb"
target_epub = "Dungeon Crawler Carl -- Dinniman, Matt -- Dungeon Crawler Carl 1, 2020 -- Dandy House -- Anna’s Archive.epub"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "test_book.epub" in source:
            print("Found cell with test_book.epub. Updating...")
            # We replace the specific line
            new_source = []
            for line in cell["source"]:
                if "test_book.epub" in line:
                    new_source.append(f"epub_path = \"{target_epub}\" \n")
                else:
                    new_source.append(line)
            cell["source"] = new_source
            print("Updated source code.")

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=4)
print("Notebook patched.")
