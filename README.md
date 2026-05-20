# The God Factory University

The God Factory University is a Streamlit-based local-first learning platform that combines course import/generation, AI tutoring, assignment grading, adaptive study systems, and lecture video rendering into a single app.

It is not just a course viewer. The repository includes:
- a multi-page academic dashboard
- a SQLite-backed university model
- a Professor AI workflow layer
- a lecture rendering pipeline with audio/video generation
- placement, test-prep, audit, quest, profile, and qualification systems
- an internal automation agent and auto-pipeline tools

---

## What this project does

At a high level, the app lets you:
- import or generate structured courses
- break courses into modules and lectures
- enrich lecture narration with LLMs
- render lectures into narrated MP4 videos
- track progress, grades, credits, achievements, and study activity
- run audits on course quality
- use an in-app AI professor for chat, grading, quiz generation, and curriculum planning
- automate repetitive content workflows

The current repository is heavily Python-based and organized around Streamlit pages, backend facades, and media / LLM subsystems.

---

## Current app surface

The dashboard entry point is `app.py`, and the repository currently includes these page files:

- `pages/01_Library.py`
- `pages/02_Lecture_Studio.py`
- `pages/03_Professor_AI.py`
- `pages/04_Timeline_Editor.py`
- `pages/05_Batch_Render.py`
- `pages/06_Grades.py`
- `pages/07_Achievements.py`
- `pages/08_Settings.py`
- `pages/09_Diagnostics.py`
- `pages/10_Help.py`
- `pages/11_LLM_Setup.py`
- `pages/12_Placement.py`
- `pages/13_Test_Prep.py`
- `pages/14_Programs.py`
- `pages/15_Profile.py`
- `pages/16_Statistics.py`
- `pages/17_Agent.py`
- `pages/18_Qualifications.py`
- `pages/19_Auto_Pipeline.py`
- `pages/21_Quests.py`

There is also a navigation reference to `pages/20_Wizards.py` in `app.py`, but that file is not present in the repository at the moment.

---

## Core workflows

### 1. Course import and structure
Courses are stored in SQLite and organized into:
- courses
- modules
- lectures
- progress records
- assignments
- XP / achievements / settings / terms / chat history

The main database entry point is `core/database.py`, which now acts as a facade layer over multiple focused modules such as:
- `core/db_facade_student.py`
- `core/db_facade_curriculum.py`
- `core/db_facade_ai.py`
- `core/db_assignments.py`
- `core/db_grades.py`
- `core/db_import.py`
- `core/db_quests.py`
- `core/db_programs.py`
- `core/db_subjects.py`
- `core/db_activity.py`
- `core/db_audit.py`

### 2. Professor AI
The AI layer is split across:
- `llm/providers.py`
- `llm/professor.py`
- `llm/professor_base.py`
- `llm/professor_content.py`
- `llm/professor_workflows.py`
- `llm/model_profiles.py`
- `llm/generation_queue.py`
- `llm/token_planner.py`

This system supports conversational tutoring, grading, quiz generation, curriculum generation, decomposition, jargon extraction, and audit workflows.

### 3. Rendering pipeline
Lecture rendering is handled through the media subsystem:
- `media/audio_engine.py`
- `media/tts_providers.py`
- `media/output_paths.py`
- `media/video_engine.py` (compatibility shim)
- `media/video/`
- `media/diffusion/`

Important note: `media/video_engine.py` is now only a backward-compatible shim. The actual rendering logic lives in `media.video.encoder` and related modules under `media/video/`.

### 4. Academic systems
The repo also includes higher-level academic logic for:
- course decomposition and pacing
- qualification and benchmark tracking
- prerequisites and course trees
- achievements and XP
- degree programs
- placement testing
- standardized test prep
- weekly quests
- activity logging and statistics
- scribe-based lecture transcription credit

Relevant modules include:
- `core/decomposition.py`
- `core/university.py`
- `core/course_tree.py`
- `core/course_tree_*.py`
- `core/placement.py`
- `core/test_prep.py`
- `core/db_scribe.py`
- `core/continuous_engine.py`
- `core/auto_pipeline.py`

---

## Installation

### Requirements
- Python 3.9+
- pip
- internet access for cloud LLMs, Edge TTS, and hosted image providers
- more RAM if you intend to run local models

### Install dependencies

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Initialize and run

```bash
python -c "from core.database import init_db; init_db()"
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

### Convenience launchers
The repository also includes:
- `DOUBLE_CLICK_SETUP_AND_START.bat`
- `setup.bat`
- `start.bat`
- `setup.sh`
- `start.sh`

These are the easiest way to bootstrap the app for local use.

---

## Dependencies currently pinned in `requirements.txt`

- `streamlit==1.44.1`
- `moviepy==1.0.3`
- `imageio==2.34.1`
- `imageio-ffmpeg==0.5.1`
- `Pillow==10.4.0`
- `numpy==1.26.4`
- `scipy==1.13.0`
- `edge-tts==6.1.12`
- `pyttsx3==2.98`
- `openai==1.30.1`
- `anthropic==0.25.0`
- `httpx==0.27.0`
- `requests==2.32.3`
- `psutil==5.9.8`
- `jsonschema==4.22.0`

---

## Project structure

```text
app.py
README.md
DEVELOPMENT.md
USAGE_GUIDE.md
requirements.txt
notes.txt

core/
  database.py
  university.py
  decomposition.py
  continuous_engine.py
  auto_pipeline.py
  app_docs.py
  help_registry.py
  settings_registry.py
  ui_mode.py
  llm_setup.py
  placement.py
  test_prep.py
  db_*.py
  db_facade_*.py
  course_tree.py
  course_tree_*.py
  wizards/

llm/
  agent.py
  benchmark.py
  context_manager.py
  generation_queue.py
  model_profiles.py
  professor.py
  professor_base.py
  professor_content.py
  professor_workflows.py
  providers.py
  token_planner.py
  tool_registry.py
  tools.py
  tools_course.py
  tools_enrichment.py
  tools_utility.py
  tools_video.py

media/
  audio_engine.py
  output_paths.py
  tts_providers.py
  video_engine.py
  diffusion/
  video/

pages/
  01_Library.py
  02_Lecture_Studio.py
  03_Professor_AI.py
  04_Timeline_Editor.py
  05_Batch_Render.py
  06_Grades.py
  07_Achievements.py
  08_Settings.py
  09_Diagnostics.py
  10_Help.py
  11_LLM_Setup.py
  12_Placement.py
  13_Test_Prep.py
  14_Programs.py
  15_Profile.py
  16_Statistics.py
  17_Agent.py
  18_Qualifications.py
  19_Auto_Pipeline.py
  21_Quests.py
  library/

tests/
  test_audio.py
  test_contracts.py
  test_course_tree.py
  test_database.py
  test_e2e.py
  test_import.py
  test_logger.py
  test_output_paths.py
  test_providers.py
  test_regression.py
  test_sanitize.py
```

---

## Running tests

The repository includes a real `tests/` suite. To run it:

```bash
python -m pytest tests/
```

Notable coverage areas currently visible from the tree:
- contract/import integrity checks
- database tests
- audio tests
- course tree tests
- provider tests
- output path tests
- regression and end-to-end tests

---

## Documentation in the repo

- `README.md` — high-level project overview
- `USAGE_GUIDE.md` — feature and workflow reference
- `DEVELOPMENT.md` — development rules and architecture constraints
- `schemas/SCHEMA_GUIDE.md` — course JSON generation format

`DEVELOPMENT.md` is especially important. It defines project rules such as:
- hard 1000 LOC max per Python file
- backend-first modular design
- no raw SQL in page files
- checklist-driven development
- pinned dependencies
- no emojis in docs/UI

---

## Pressing issues to address

This section is intentionally direct. These are the most obvious repo-level issues surfaced by reading the current structure and key files.

### 1. Broken navigation reference in `app.py`
`app.py` links to `pages/20_Wizards.py`, but that file is missing from the repository.

**Impact:** Sidebar navigation can point users to a non-existent page.

**Recommended fix:**
- either add `pages/20_Wizards.py`
- or remove the navigation entry until the page exists
- then add a contract test to validate all `st.page_link()` targets actually exist

### 2. README drifted away from the actual repository
The previous README was very detailed, but parts of it no longer matched the codebase exactly.
Examples of drift include:
- page count / page numbering inconsistencies
- references to modules that have since been refactored
- omission of newer files like `pages/21_Quests.py`, `llm/tool_registry.py`, `llm/token_planner.py`, `media/tts_providers.py`, and course tree split modules
- describing `media/video_engine.py` like a full engine when it is now a shim

**Recommended fix:** Keep the README higher-level and move volatile implementation detail to `USAGE_GUIDE.md` or docs pages.

### 3. Contract tests do not validate page-link targets
`tests/test_contracts.py` verifies imports and help-button anchors, which is good, but it does not appear to validate that every linked page file in `app.py` actually exists.

**Impact:** Navigation regressions like the missing Wizards page can slip through tests.

**Recommended fix:** Add a test that parses `st.page_link(...)` usage and asserts each referenced file exists.

### 4. Documentation duplication risk
There is significant overlap between:
- `README.md`
- `USAGE_GUIDE.md`
- in-app help content
- `DEVELOPMENT.md`

**Impact:** high maintenance burden and documentation drift.

**Recommended fix:**
- keep README concise and repository-focused
- keep `USAGE_GUIDE.md` user-focused
- keep `DEVELOPMENT.md` contributor-focused
- let in-app help own page-by-page usage detail

### 5. `core/database.py` remains a high-risk file
The project has clearly been refactored, but `core/database.py` is still a large orchestration / facade module and remains a central risk area for future drift.

**Impact:** future edits can easily reintroduce coupling or make testing harder.

**Recommended fix:** Continue pushing logic outward into focused modules and preserve `database.py` as a thin public API facade.

### 6. Setup and runtime expectations are still implicit
The repo has multiple local and optional subsystems:
- Streamlit
- SQLite
- Edge TTS / fallback TTS
- cloud or local LLM providers
- image generation providers
- rendering dependencies

**Impact:** new users may not know what is strictly required versus optional.

**Recommended fix:** maintain a small “minimum viable run” section and a separate “optional AI/rendering features” section in docs.

---

## Suggested next cleanup passes

If you want to keep improving the repo after this README refresh, the next highest-value tasks are:

1. Add the missing `pages/20_Wizards.py` page or remove the link.
2. Add contract coverage for page navigation targets.
3. Decide one source of truth for feature-level documentation.
4. Add a short architecture diagram or data-flow section.
5. Add a contributor setup section with recommended dev workflow from `DEVELOPMENT.md`.
6. Add a lightweight smoke-test command to the README once the intended command is standardized.

---

## License

This repository currently states that the project is provided as-is for educational purposes.
If you want outside contributions or reuse clarity, add an explicit license file.
