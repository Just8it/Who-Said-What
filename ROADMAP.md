# 🗺️ Project Roadmap

This document outlines the planned improvements to evolve the **BTAB Speaker Separation** tool from a prototype to a production-grade pipeline.

## Phase 1: 🧠 Quality & Reliability (Immediate)

*Goal: drastically reduce "hallucinations" and ensure 100% chapter completion rates.*

- [x] **Few-Shot Prompting**
  - **Problem**: Models sometimes misunderstand "sandwiched" dialogue (Narrator -> Character -> Narrator) or fail to strictly follow JSON format.
  - **Solution**: Embed 3 "Perfect Examples" into the system prompt. Show the model *exactly* how to handle edge cases.
  - **Impact**: Higher accuracy in identifying speakers; fewer malformed JSON errors.

- [x] **Automated Retry Logic**
  - **Problem**: A single API timeout or random JSON error crashes or skips the entire chapter.
  - **Solution**: Wrap the API call in a `retry` loop (max 3 attempts) with exponential backoff.
  - **Impact**: "Set it and forget it" reliability.

## Phase 2: ⚡ Speed & Scale (Short Term)

*Goal: Reduce processing time for a full book from 1 hour+ to <15 minutes.*

- [ ] **Parallel Processing (AsyncIO)**
  - **Problem**: Chapters are processed concurrently (1 at a time).
  - **Solution**: Implement `asyncio` to process batches of chapters (e.g., 5 chapters at once).
  - **Impact**: **5x - 10x Speedup**.

- [ ] **Smart Caching**
  - **Problem**: Re-running a chapter (e.g., to fix one typo) costs money again.
  - **Solution**: Hash the input text + prompt. If it matches a previous run, load the result from disk instantly.

## Phase 3: 🛠️ User Experience (Future)

*Goal: Make the tool easier to configure and monitor.*

- [ ] **Centralized Configuration**
  - Move all "hardcoded" toggles (model name, batch size, cost limits) to a single `config.yaml` or the top of the Notebook.
- [ ] **Progress Dashboard**
  - Replace text logs with a simple `tqdm` progress bar for the entire book batch.

## Phase 4: 🤖 Advanced Features (Exploratory)

- [ ] **Voice Casting Assistant**: Use the descriptions to automatically suggest voice actors or TTS presets.
- [ ] **Scene Segmentation**: Identify scene breaks (time jumps, location changes) automatically.
