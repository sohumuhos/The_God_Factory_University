# The God Factory University — Full Audit Report

**Date:** 2026-04-02  
**Auditor:** GitHub Copilot  
**Scope:** All features, pipeline integration, error logs, video rendering

> **Follow-up 2026-06-13:** The video-rendering output issues (Section 2) were
> re-diagnosed against real rendered frames and a Phase 1 fix pass was implemented
> and verified. See `docs/problems/RENDER_FIXES_2026_06_13.md`. Note: items 2a, 2d,
> 2e were already fixed in current code by the time of that pass.

---

## 1. Error Log Analysis

### error_2.txt (1713 lines)
- **torch.classes RuntimeError** — `torch.classes.__path__._path` conflict with Streamlit's `local_sources_watcher.py`. 1600+ repetitions. Cosmetic but noisy.
- **Thread-28 (do_batch_render)** — `missing ScriptRunContext` warnings. Background thread writes to `st.session_state` which is not thread-safe.

### Wizard Error Files (30+ files)
All `wizard_*.txt` files contain **user-input validation messages**, not real errors:
- "Please enter a topic"
- "No courses selected"  
- "ComfyUI not detected"
These are expected validation flows, not bugs.

---

## 2. Critical Video Pipeline Issues

### 2a. Visual Prompt Text Rendered On Screen
**File:** `media/video/frame_renderer.py` lines 159-170  
**Severity:** CRITICAL  
The `visual_prompt` (meant only for diffusion model image generation) is drawn as visible gold text on every video frame with a `[ Visual ]` header. This is the "prompt text showing on screen" bug.

### 2b. Hardcoded Style Prefix Drowns Subject in Diffusion Prompts
**Files:** All 10 providers under `media/diffusion/`  
**Severity:** HIGH  
Every provider prepends a hardcoded style string before the actual subject prompt:
- 6 providers: `"educational motion design, crisp typography, technical diagrams, soft volumetric lighting, "`
- 4 providers: `"educational, clean, academic: "`

Diffusion models weight early tokens most heavily, so the subject matter gets pushed to the back and ignored. Images come out generic.

### 2c. No Course/Lecture Context in Diffusion Prompts
**File:** `media/video/encoder.py` lines 67-75  
**Severity:** HIGH  
The raw `visual_prompt` is passed to diffusion with no course title, lecture topic, or learning context. Combined with the style prefix, images are completely disconnected from content.

### 2d. VFX Config Key Mismatch (Wizard → Renderer)
**File:** `core/wizards/video_wizard.py` lines 98-105  
**Severity:** MEDIUM  
Wizard saves: `text_overlays`, `particles`, `color_grading`  
Renderer reads: `text_overlay`, `ambient_particles`, `color_grade`  
VFX toggles from the wizard have zero effect on rendering.

### 2e. Image Provider Key Mismatch
**File:** `media/video/encoder.py` line 67  
**Severity:** MEDIUM  
Encoder reads `preferred_image_provider` from VFX config. Wizard saves `image_provider` to settings DB. These never connect.

### 2f. Enhanced Video Prompts Never Saved
**File:** `llm/professor_content.py` lines 230-240  
**Severity:** HIGH  
`enhance_video_prompts()` generates enhanced prompts via LLM but only logs them to `llm_generated` table — never writes them back to the lecture's `scene_blocks` in the database.

### 2g. Scene Builder Buries Enriched Content in Filler
**File:** `media/video/scene_builder.py` lines 66-165  
**Severity:** MEDIUM  
`_build_narration_script()` always wraps the narration prompt in template filler ("Welcome to today's lecture on...", generic term definitions, closing). Even high-quality LLM-enriched narration gets diluted.

### 2h. Enrichment Silently Skips Lectures Without scene_blocks
**File:** `llm/tools_enrichment.py` lines 82-83  
**Severity:** MEDIUM  
`if not scenes: continue` — lectures missing `scene_blocks` are silently skipped during enrichment, with no feedback to the user about what was skipped or why.

---

## 3. Feature Integration Issues

### 3a. Achievement ID Mismatch
- `core/db_achievements.py` seeds 17 achievements with IDs like: `first_lecture`, `ten_lectures`, `xp_5000`, `degree_cert`, `degree_assoc`, etc.
- `pages/07_Achievements.py` displays 20 badges with DIFFERENT IDs like: `first_curriculum`, `scholar`, `sage`, `certificate`, `associate`, `streak_7`, `xp_10000`, etc.
- Only ~4 IDs overlap. ~10 page badges are unreachable; ~7 DB achievements are invisible.

### 3b. Placeholder Questions in Test Prep & Placement
- `pages/13_Test_Prep.py` lines 61-67: Hardcoded placeholder questions, answer always "A"
- `pages/12_Placement.py` lines 73-82: Hardcoded placeholder questions, answer always "Option A"
- `core/placement.py` line 118: `get_adaptive_difficulty()` exists but is never called
- These pages function as UI shells but have no real educational value.

### 3c. Batch Render Thread Safety
- `pages/05_Batch_Render.py` lines 237-239: Background thread writes to `st.session_state` (not thread-safe in Streamlit)
- Line 260: "Abort" button only changes state, doesn't actually stop the render thread

### 3d. Quest System Has No UI
- `core/db_quests.py` has a fully wired backend with 3 weekly quests and progress tracking
- No page exists to display or interact with quests — completely invisible to users

---

## 4. Feature Status Matrix

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| 1 | Library browser | WORKING | |
| 2 | Lecture Studio | WORKING | |
| 3 | Professor AI chat | WORKING | |
| 4 | Timeline Editor | WORKING | |
| 5 | Batch Render | WORKING | Thread safety + abort flow fixed |
| 6 | Grades | WORKING | |
| 7 | Achievements | WORKING | DB/page IDs aligned |
| 8 | Settings | WORKING | |
| 9 | Diagnostics | WORKING | |
| 10 | Help | WORKING | |
| 11 | LLM Setup | WORKING | |
| 12 | Placement | PARTIAL | LLM-first questions + adaptive difficulty; placeholder fallback remains |
| 13 | Test Prep | PARTIAL | LLM-first questions; placeholder fallback remains |
| 14 | Programs | WORKING | |
| 15 | Profile | WORKING | |
| 16 | Statistics | WORKING | |
| 17 | Agent | WORKING | |
| 18 | Qualifications | WORKING | |
| 19 | Auto Pipeline | WORKING | |
| 20 | Quest System | WORKING | UI page added and linked in nav |
| 21 | Video Rendering | PARTIAL | All issues in Section 2 |
| 22 | Diffusion/Images | PARTIAL | Prompts generic, no context |
| 23 | Enrichment | PARTIAL | Skips lectures, prompts not saved back |

---

## 5. Fix Plan (Implemented)

### Phase 1 — Critical Video Fixes
1. Remove visual prompt overlay from frame_renderer.py
2. Fix VFX key mismatch in video_wizard.py
3. Fix diffusion style prefix in all 10 providers (subject-first)
4. Fix image_provider key mismatch in encoder.py

### Phase 2 — Pipeline Quality
5. Inject course context into diffusion prompts (encoder.py)
6. Save enhanced prompts back to DB (professor_content.py)
7. Fix scene_builder narration to prioritize enriched content
8. Fix enrichment to not silently skip lectures

### Phase 3 — Feature Fixes
9. Fix achievement ID alignment between DB and display page
10. Fix batch render thread safety
11. Connect Test Prep/Placement to LLM-generated questions

### Phase 4 — Completion (Implemented 2026-04-19)
12. ✅ Created Quest UI page (pages/21_Quests.py) + added to sidebar nav
13. ✅ Wired adaptive difficulty into Placement answer flow
14. ✅ Suppressed torch.classes watcher noise via early patch in app.py

---

## 6. Phase 5 — Approved Plan (Queued, Not Yet Implemented)

This section records the exact next implementation plan approved on 2026-04-21,
to ensure repo state is updated before coding begins.

### 6.1 Expected Quality (Hybrid Visuals)
- For diagrams, charts, timelines, geometry, code walkthroughs, system architecture, and labeled animations: quality can be excellent (often better than diffusion because it is precise and deterministic).
- For photoreal scenes or painterly art: diffusion still wins.
- Recommended setup: hybrid model — programmatic diagrams first, diffusion for illustrative scenes.

### 6.2 Robust Fallback Architecture
- Add a render mode per scene: `diagram`, `chart`, `equation`, `timeline`, `code`, `diffusion`.
- Use Python renderers (Manim + Matplotlib + PIL/SVG + FFmpeg) to generate animation clips from structured scene specs.
- Compose clips in existing pipeline integration points (`scene_builder.py` and `encoder.py`).
- Keep current diffusion providers optional, not required.

### 6.3 Schema Evolution / Backward Compatibility
- Add `schema_version` to lecture/course payloads.
- Add migration functions (`v1_to_v2`, `v2_to_v3`, etc.).
- Auto-run migrations in DB read/write paths.
- Extend schema docs in `schemas/SCHEMA_GUIDE.md` accordingly.

### 6.4 Built-in App Mastery Curriculum (K–Doctorate)
- Add one bundled meta-curriculum covering app usage from Foundations (K-5) through Doctoral/Builder.
- Include guided in-app tasks, practical projects, rubrics, and capstones for each level.

### 6.5 MVP Start Scope (next coding phase)
1. Schema version + migration framework.
2. One programmatic diagram renderer fallback.
3. One bundled App Mastery starter curriculum seed.
