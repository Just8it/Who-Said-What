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

- [x] **Sequential Optimization (Pipelining)**
  - **Problem**: Full parallelism breaks character continuity (Chapter N needs Chapter N-1's DB updates).
  - **Solution**: Overlap *non-dependent* steps (e.g., while Ch 1 saves/enriches, Ch 2 starts loading) or optimize the enrichment bottleneck.
  - **Impact**: **1.5x - 2x Speedup (Safe)**.

- [ ] **Smart Caching**
  - **Problem**: Re-running a chapter (e.g., to fix one typo) costs money again.
  - **Solution**: Hash the input text + prompt. If it matches a previous run, load the result from disk instantly.

## Phase 3: 🛠️ User Experience (Future)

*Goal: Make the tool easier to configure and monitor.*

- [x] **Centralized Configuration**
  - Move all "hardcoded" toggles (model name, batch size, cost limits) to a single `config.yaml` or the top of the Notebook.
- [x] **Progress Dashboard**
  - Replace text logs with a simple `tqdm` progress bar for the entire book batch.

## Phase 4: 🤖 Advanced Features (Exploratory)

- [ ] **Voice Casting Assistant**: Use the descriptions to automatically suggest voice actors or TTS presets.
- [ ] **Scene Segmentation**: Identify scene breaks (time jumps, location changes) automatically.
