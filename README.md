# BTAB: Advanced Speaker Separation & Enrichment Pipeline (V2)

## Overview

This project processes raw EPUB files into structured, speaker-attributed JSON data suitable for high-quality Text-to-Speech (TTS) generation. By leveraging advanced Large Language Models (LLMs) and a hybrid "Logic + AI" architecture, we achieve high-accuracy diarization, emotion tagging, and consistent character voice tracking across entire novels.

## 🚀 Key Features (V2)

We utilize a **Hybrid Pipeline** combining strict logic with state-of-the-art AI models.

### 🧠 Intelligence & Accuracy

* **Few-Shot Prompting**: System prompts include "Perfect Examples" to handle edge cases like "Sandwiched Dialogue" and "Internal Thoughts" with high precision.
* **Integrity Monitor (Safety Net)**: A passive guardrail that compares input text vs. output JSON. If the AI hallucinates or drops a paragraph, it triggers a `[WARNING]` so you never lose data.
* **Automated Retry Logic**: Networks fail. Our system automatically retries API calls with exponential backoff before skipping a chapter.

### ⚡ Speed & Efficiency

* **Sequential Optimization (Async Enrichment)**:
  * **Old Way**: Generate Ch 1 -> Wait for DB Update -> Generate Ch 2.
  * **New Way**: Generate Ch 1 -> **Immediately** Generate Ch 2 (while Ch 1 DB updates in background).
  * *Result: ~30-50% faster batch processing.*
* **Cost Monitoring**: Real-time tracking of API usage with a configurable "Circuit Breaker" limit (e.g., stopping if cost > $2.00).

### 🛠️ User Experience

* **Progress Dashboard**: sleek `tqdm` progress bar showing ETA per chapter and total batch completion.
* **Centralized Configuration**: All settings (Model Name, Batch Range, API Keys) are managed in a single cell at the top of the Notebook.

## 📂 Project Structure

* `src/`
  * `llm_handler.py`: Interface for OpenRouter/Gemini with Retry Logic.
  * `character_manager.py`: Tracks personas. Handles **Async Enrichment** in background threads.
  * `pipeline_utils.py`: Contains `PromptFactory`, `CostMonitor`, and the new **`IntegrityMonitor`**.
  * `book_processor.py`: EPUB parsing logic.
* `data/`: Input books and persistent `book_config.json`.
* `Runs/`: JSON outputs and logs.
* `scripts/`: Maintenance tools (e.g., `push_release.py` for mirroring).

## 🏃 Usage

1. **Setup**:
    * Install requirements: `pip install -r requirements.txt`
    * Set `OPENROUTER_API_KEY` in `.env`.
2. **Run**:
    * Open `tts_pipeline.ipynb`.
    * Adjust the **USER CONFIGURATION** cell (Model, Batch Start/End).
    * Run All.

## 🤖 Models

* **Primary**: `google/gemini-2.5-flash` (via OpenRouter) - Chosen for high context, low cost, and reliable JSON adherence.

---
*Maintained by Just8it*
