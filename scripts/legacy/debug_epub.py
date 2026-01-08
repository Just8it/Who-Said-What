import os
from ebooklib import epub

filename = "Dungeon Crawler Carl -- Dinniman, Matt -- Dungeon Crawler Carl 1, 2020 -- Dandy House -- Anna’s Archive.epub"

print(f"Checking for file: {filename}")
if os.path.exists(filename):
    print("File exists.")
    try:
        book = epub.read_epub(filename)
        print("Successfully read epub with ebooklib.")
    except Exception as e:
        print(f"Error reading epub: {e}")
else:
    print("File does not exist.")
    # List directory to show actual filenames
    print("Files in current directory:")
    for f in os.listdir("."):
        if f.endswith(".epub"):
            print(f" - {f}")
