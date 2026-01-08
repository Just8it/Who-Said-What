import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import List, Optional
import re

# --- Data Models ---

class Segment(BaseModel):
    text: str = Field(..., description="The exact spoken text or narration")
    speaker: str = Field(..., description="Name of the speaker or 'Narrator'")
    is_dialogue: bool = Field(..., description="True if spoken by a character, False if narration")
    emotion: Optional[str] = Field(None, description="Emotional tone of the segment given context")
    tone: Optional[str] = Field(None, description="Speech characteristics (e.g. 'Shouting', 'Whispering')")

class Chapter(BaseModel):
    title: str
    content_raw: str = Field(..., description="Raw text content of the chapter for processing")
    segments: List[Segment] = Field(default_factory=list)

# --- EPUB Loader ---

class EpubLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.book = epub.read_epub(file_path)

    def extract_chapters(self) -> List[Chapter]:
        """Iterates through EPUB items and extracts text from chapters."""
        chapters = []
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Basic filter: ignore nav/toc files usually
                # This might need refinement based on exact epub structure
                if 'nav' in item.get_name() or 'toc' in item.get_name():
                    continue
                
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n\n').strip()
                
                # Heuristic: skip very short "chapters" (likely copyright page, etc)
                if len(text) < 100:
                    continue
                    
                # Try to find a title from h1/h2 tags, else use filename
                title_tag = soup.find(['h1', 'h2'])
                title = title_tag.get_text().strip() if title_tag else item.get_name()
                
                chapters.append(Chapter(title=title, content_raw=text))
        
        return chapters

    @staticmethod
    def clean_text(text: str) -> str:
        """Basic cleanup normalization."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
