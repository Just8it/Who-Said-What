from book_processor import EpubLoader
import os

epub_path = "test_book.epub"

if os.path.exists(epub_path):
    print(f"Loading {epub_path}...")
    loader = EpubLoader(epub_path)
    chapters = loader.extract_chapters()
    print(f"Total chapters: {len(chapters)}")
    
    print("\n--- First 10 Chapters ---")
    for i, chap in enumerate(chapters[:10]):
        # Print index, title, and length of content
        content_snippet = chap.content_raw[:50].replace('\n', ' ')
        print(f"Index {i}: Title='{chap.title}', Length={len(chap.content_raw)} chars. Start='{content_snippet}...'")
else:
    print("test_book.epub not found.")
