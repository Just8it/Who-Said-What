# BTAB: Advanced Speaker Separation & Enrichment Pipeline

## Overview

This project processes raw EPUB files into structured, speaker-attributed JSON data suitable for high-quality Text-to-Speech (TTS) generation. By leveraging advanced Large Language Models (LLMs) and a hybrid "Logic + AI" architecture, we achieve high-accuracy diarization, emotion tagging, and consistent character voice tracking across entire novels.

## 🚀 Current Architecture & Models

We currently utilize a **Hybrid Pipeline** that combines strict robust code logic with state-of-the-art AI models.

### Paid Models

* **Primary Model**: `google/gemini-2.5-flash` (via OpenRouter)
  * **Why?**: Selected for its massive context window (crucial for processing full chapters at once), low latency, and extreme cost-efficiency compared to GPT-4o or Claude 3.5 Sonnet.

### Core Components

1. **Ingestion (`EpubLoader`)**: Extracts and cleans raw text from `.epub` files, handling HTML parsing and formatting.
2. **Context Engine (`CharacterManager`)**:
    * Maintains a persistent database of characters (`book_config.json`).
    * Generates **Dynamic Context Headers** for each chapter, telling the LLM exactly *who* is likely to appear based on recent narrative flow (Recency Bias).
    * **Self-Healing**: Automatically detects new characters, generates profiles for them, and updates the database ("Enrichment Cycle").
3. **Diarization Engine (`LLMHandler`)**: Sends chapter text to Gemini with specific "Sandwich," "Quote," and "Thought" rules to strictly separate dialogue from narration.
4. **Sanpshot Logic (`OutputJanitor`)**: A regex-based post-processor that fixes malformed JSON, trims overlapping text hallucinations, and ensures data integrity before saving.

## 🛠️ Setup & Installation

### Prerequisites

* Python 3.10+
* An [OpenRouter](https://openrouter.ai/) API Key

### Installation

1. **Clone the repository**:

    ```bash
    git clone <repo-url>
    cd speaker-separation
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Environment Setup**:
    Create a `.env` file in the root directory:

    ```env
    OPENROUTER_API_KEY=sk-or-your-api-key-here
    ```

## 🏃 Usage

The primary workflow is managed via the **Jupyter Notebook** for interactive visibility.

1. **Place your EPUB**:
    Put your target `.epub` file in the `data/` directory.

2. **Launch the Pipeline**:
    Open `tts_pipeline.ipynb` in VS Code or Jupyter Lab.

    * **Step 1**: Run the Setup & Config cells to initialize logging (`Runs/` directory).
    * **Step 2**: The `EpubLoader` will parse your book.
    * **Step 3**: Configure the batch range (e.g., Chapters 3 to 10) and Run.

3. **Monitor Output**:
    * **Terminal/Output**: Real-time logs showing cost usage, character updates, and processing speed.
    * **`Runs/` Directory**: Contains the generated JSON files (e.g., `chapter_003_title.json`) and full logs.

## 📂 Project Structure

* `src/`: Core logic modules.
  * `llm_handler.py`: Interface for OpenRouter/Gemini.
  * `character_manager.py`: Logic for tracking and enriching character personas.
  * `book_processor.py`: Pydantic models (`Segment`, `Chapter`) and EPUB handling.
  * `pipeline_utils.py`: Prompts, Cost Monitoring, and Cleaning logic.
* `data/`: Input books and the persistent `book_config.json`.
* `Runs/`: Output directory for every execution session (git-ignored).
