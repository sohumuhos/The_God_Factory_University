# The God Factory University

A full-stack AI-powered university built with Python and Streamlit. Generates animated lecture videos with neural narration, binaural beats, and a dark-academic theme. Features a Professor AI tutor with 8 modes, GPA/degree tracking from Certificate through Doctorate, 17 achievements across 7 categories, SM-2 spaced-repetition flashcards, 22 autonomous agent tools, 24/7 continuous enrichment with versioned narration, scribe transcription credit, course audit workbench, prove-it AI verification, adaptive placement testing, standardized test prep (SAT/ACT/GRE/GED), real-world qualification benchmarking, 7 seeded degree programs, 20 grade levels (K through Post-Doctoral), and support for 10 LLM providers and 10 image providers.

---

## Quick Start

### Windows (Easiest)

1. Install [Python 3.9+](https://www.python.org/downloads/) — check **"Add Python to PATH"** during install
2. Double-click **`DOUBLE_CLICK_SETUP_AND_START.bat`**
3. Wait for first-time setup to finish (installs dependencies, creates database)
4. Browser opens automatically at `http://localhost:8501`

Or from a terminal:
```powershell
.\setup.bat
.\start.bat
```

### macOS / Linux

```bash
git clone https://github.com/Ileices/The_God_Factory_University.git
cd The_God_Factory_University
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```

---

## UI Modes

The app has three access modes, selectable from the sidebar:

| Mode | Access Level | Description |
|------|-------------|-------------|
| **Student** | Study-focused | Library, Lecture Studio, Professor AI, Grades, Achievements, Profile, Statistics |
| **Builder** | Content creation | Everything in Student + Library Build tab, Timeline Editor, Batch Render, Agent |
| **Operator** | Full admin | Everything in Builder + Diagnostics, Placement, Test Prep, Programs, Qualifications |

Pages gated behind Builder or Operator show a guided access prompt in Student mode.

---

## All 19 Pages

### Dashboard (`app.py`)
- **Mode selector** (student/builder/operator) in sidebar
- **XP bar** showing current XP in level with level badge
- **4 navigation groups**: Student Route, Builder Route, Setup & Support, Admin & Prototype (visibility based on mode)
- **4 status cards**: Courses, Lectures Done, Total XP, Rank
- **4 academic cards**: Verified Credits, Study Hours, Idle Days, Active Days
- **Audit Queue display** with status, processed/total packets, ETA
- **Weekly Quests** with icon, title, progress/target, XP reward, progress bar
- **Quick Start guide** with hardcoded walkthrough
- **System Health** expander: 6 self-checks (Database, FFmpeg, TTS Engine, LLM Config, Video Engine, Audio Engine)
- **Active Courses** section listing all courses with styled cards
- Auto-imports built-in course from `notes.txt` on first run
- Level-up celebration with balloons when `_pending_level_up` is set

### Page 1 — Library
5 tabs for comprehensive course management:
- **Explore**: Browse courses with search, inline Professor Q&A, generate next enrichment level
- **Build & Import**: Bulk JSON import with validation, pacing/depth controls (fast/standard/slow)
- **Course Map**: Full hierarchy view with recursive course tree rendering
- **Curriculum Alignment**: Audit built-in curriculum files, hardware benchmarks, batch enrichment
- **Media Sources**: Configure 9 cloud image generation services (Pollinations, HuggingFace, Leonardo, GitHub Models, LimeWire, Stability, GetImg, DeepAI, Prodia)

### Page 2 — Lecture Studio
- **Course → Module → Lecture** drill-down selectors
- **Detail cards**: Duration, Scenes, Status
- **Learning Objectives & Core Terms** expander
- **Video player** with streaming playback
- **Render controls**: Render This Lecture, Export Scene Chunks, Render ALL Course Lectures
- **LLM Narration Enrichment** expander: enriches every scene with progress updates
- **Visual Effects** expander: AI backgrounds (toggle + provider selector), scene transitions, Ken Burns pan/zoom, cinematic color grading, title/term overlays, ambient particles, watermark
- **Assignments** section: AI Policy badge ([OPEN]/[AIDED]/[WATCH]/[NONE]), description, deadline pill, submission status, "Ask Professor about assignments" input
- **Scribe Credit** section: Words submitted, requirement (10,000 minimum), progress %, scribe submission with word count validation and originality verification

### Page 3 — Professor AI
8 interactive tabs powered by the Professor AI:
- **Chat**: Free-form Socratic tutoring with session-based history
- **Generate Curriculum**: 4 modes — Generate New, Decompose Existing, Generate Jargon Course, Plan & Generate (budget-aware). Inputs: topic, difficulty, lectures/module
- **Grade Work**: Essay or code submission → rubric-based evaluation with score, feedback, strengths/areas for improvement
- **Create Quiz**: Generate MCQ + short answer quizzes from any topic
- **Research Rabbit Hole**: Deep exploration with historical context, open problems, connections, resources (+XP)
- **Audit Workbench**: Create course audit jobs, review packets, remediation backlog, regenerate or pass packets. Uses model profiles for audit rigor
- **Chat History**: Browse previous conversations
- **App Guide**: In-app tutorial powered by Professor

### Page 4 — Timeline Editor
- **Course → Module → Lecture** selectors
- **Scene block list**: Index, Block ID, ambiance prompt, narration preview
- **Duration override** per scene (0 = use TTS length)
- **Up/Down reorder** buttons per scene
- Reset to Original, Render Edited Timeline (suffix `_edited`), Export Modified JSON

### Page 5 — Batch Render
- **Filter & Sort**: Course, Difficulty, Sort By dropdowns
- **Lecture selection**: Select all + individual checkboxes
- **Render settings**: FPS (10/15/24), Resolution (960×540 / 1280×720 / 1920×1080)
- **AI Backgrounds** provider status with per-provider breakdown
- **Enrich narration** checkbox (LLM enrichment before render)
- **Visual Effects** auto-applied: AI backgrounds, transitions, Ken Burns, color grading, text overlay, particles, watermark
- **24/7 Continuous Enrichment** section:
  - Course selector (All or specific)
  - Enrichments before decompose (default: 3)
  - Decompositions before level advance (default: 2)
  - Jargon per cycle (default: 1)
  - Rate limit slider, auto-render toggle
  - Start/Stop with live progress display (cycle #, action, totals)
- **Rendered Files** section listing last 30 MP4 files with sizes

### Page 6 — Grades
- **Student identity** from settings
- **GPA + Credit summary**: GPA, Verified Credits, Eligible Degrees
- **Academic summary**: Activity Credits, Verified Courses, Verified Assessments
- **Study hours**: Total Hours, Assessment Hours, Hour-Based Credits
- **Enrollment date**: Enrolled date, Days Studied
- **Term grouping**: Per-term assignment breakdown
- **Assignments by course**: Per-course expander with verified completion badge, official/activity credits, passed count, assignment table (Title, Type, AI Policy, Score, Grade, Status), deadline pills
- **Download Transcript**: CSV and JSON export
- **Degree Progress**: Per-degree progress bar (Certificate → Associate → Bachelor → Master → Doctorate) with [ELIGIBLE]/[LOCKED] status
- **Time-to-degree estimate**: Credits Needed, Hours Remaining, Est. Days Left, GPA warning
- Grade scale: A+ (97+, 4.0) through F (<60, 0.0) with 12 letter grades

### Page 7 — Achievements
- **Level badge** + XP stats (Total XP, Next Level)
- **Level Progression**: 10 level rows with name, XP required, [CURRENT]/[UNLOCKED]/[LOCKED] status
- **Achievement Badges**: Category filter, 3-column gallery, 17 achievements across 7 categories (progress, academic, efficiency, xp, degree, habit, system, llm, media)
- **XP History**: Last 50 events with timestamp, XP gained, description

### Page 8 — Settings
7 collapsible expander sections:
1. **General**: Student name, deadlines toggle, weekly quests toggle
2. **LLM & AI**: Current provider/model/API key status, link to LLM Setup Wizard
3. **Voice & Audio**: 13 neural voices, rate/pitch sliders, preview button, binaural presets (Gamma 40Hz, Beta 18Hz, Alpha 10Hz, Theta 6Hz)
4. **Video & Rendering**: Quality profiles (Draft/Balanced/High/Final/Custom), FPS (10/15/24/30), resolution, render engine (local/comfyui/free_cloud_mix/custom_api)
5. **Image Generation**: API keys for all image providers
6. **Course & Learning**: Daily token target, learning preferences
7. **Advanced**: Media sharing mode (private/course_shared/global)

### Page 9 — Diagnostics (Operator only)
- **Environment**: Python version, platform, processor, working directory, DB size
- **Dependencies**: 14 packages with versions + FFmpeg binary path
- **Database Stats**: Courses, Modules, Lectures, Completed, Assignments, Graded, GPA, Credits, XP, Level
- **LLM Provider Config**: Provider/Model/Base URL/API Key status + Test Connection button
- **Audio Engine**: Voice/Rate/Pitch/Binaural preset + Test TTS button
- **Video Engine**: Resolution, FPS
- **Settings Dump**: Full dump with masked API keys
- **Module Health**: py_compile check on all Python files with [OK]/[ERROR] table
- **Recent Errors**: JSONL error log with ID, Category, Message, Timestamp

### Page 10 — Help
- **Context navigation**: URL param `?topic=anchor_name` for deep linking
- **End-to-End Tutorial**: 6-step walkthrough (AI Provider → Import Course → Study → Render → Track → Advanced)
- **60+ help topics** organized into 19+ groups (Getting Started, Dashboard, XP, Library, Lecture Studio, Professor AI, Timeline, Batch Render, Grades, Achievements, Settings, LLM Setup, Diagnostics, Placement, Programs, Profile, Statistics, Agent, Qualifications)
- **Sidebar Quick Links** matching group order
- **Quick Reference** 3-column footer

### Page 11 — LLM Setup Wizard
- **Step 1**: Choose Local vs. Cloud with comparison
- **Hardware Profile**: RAM, GPU VRAM, GPU name, Disk free, recommended model + reason, model size guide
- **Local — Ollama**: Installation guide, model pull from UI (async POST to `/api/pull`), auto-detection, 5-tier model catalog (Tiny 1-3B → XL 70B+), Save & Test
- **Local — LM Studio**: Installation guide, server auto-detection, model name input, Save & Test
- **Cloud**: Radio selector for 7 providers (Groq, GitHub, OpenAI, Anthropic, Mistral, Together, HuggingFace) with per-provider cost, setup steps, signup link, API key input, model selector, base URL input, Save & Test
- **Provider Comparison** expander: type, cost, speed, quality, context, best-for table
- **Quick Switch** buttons for pre-configured providers

### Page 12 — Placement (Operator only)
- **Subject selector**: Domain + specific field drill-down
- **Adaptive placement exam**: 10 questions, difficulty scales based on streak (1-10), 4-choice MCQ, Submit Answer
- **Results**: Score %, Correct/Total, Recommended Level (beginner/intermediate/advanced)
- **Test History**: Last 10 tests with ID, Subject, Status, Score %
- XP reward on completion

### Page 13 — Test Prep (Operator only)
- **Test selector**: SAT, ACT, GRE, GED
- **Section selector**: SAT (Reading, Writing & Language, Math No Calc, Math Calculator), ACT (English, Math, Reading, Science), GRE (Verbal, Quantitative, Analytical Writing), GED (Language Arts, Math, Science, Social Studies)
- **Timed practice**: 10-minute sessions with countdown timer
- **Score report**: Score %, Correct/Total, Percentile estimate, Time taken
- **Session History**: Last 10 sessions with Score % and Percentile

### Page 14 — Programs
- **Academic Status**: GPA, Verified Credits, Verified Courses
- **7 seeded programs**: cert_cs, cert_math, assoc_gen, bach_cs, bach_eng, mast_cs, doct_cs
- **Per-program**: Name, level, total credits, school, description, progress bar, [OK] Enrolled or Enroll button
- **Your Enrollments** list: status icon + name + level + status

### Page 15 — Profile
- **Identity**: Student name, grade level (20 levels from K through Post-Doctoral)
- **Learning Preferences**: Learning style (Visual/Auditory/Reading/Kinesthetic), study pace (relaxed/moderate/intensive)
- **Academic Summary**: Rank, XP, GPA, Verified Credits
- **Study Streak**: Consecutive days, last active date, streak bonus (+N% XP)

### Page 16 — Statistics
- **Overview**: 8 cards (Study Hours, Lectures Done, Assignments, GPA, Courses, Verified Credits, Total XP, Activities)
- **Daily Activity Chart**: Bar chart, last 30 days (pandas DataFrame)
- **Activity Breakdown**: Event types with counts
- **Grade Distribution**: A/B/C/D/F histogram

### Page 17 — Agent (Builder/Operator only)
- **Sidebar config**: Execution mode (bounded/unlimited), max steps (5-200), review mode (auto/review), rate limit (0-10s), tool category checkboxes
- **New Task**: Description text area, Launch Agent / Stop Agent buttons
- **Executing**: Progress bar, status text, log (last 20 steps), abort button
- **Draft Queue** (review mode): Per-draft details + Approve/Reject buttons
- **Job History**: Per-job status, task preview, step count, Resume/Delete buttons
- **Available Tools Reference**: 22 tools grouped by category (course, video, utility)
- Agent loop: Think → Parse tool call → Execute (or queue for review) → Process result → TASK_COMPLETE or TASK_BLOCKED

### Page 18 — Qualifications (Operator only)
- **Overview**: GPA, Verified Credits, Tracked Benchmarks count
- **Qualification Progress**: Per-qualification expander with status mark, progress %, description, school ref, category, progress bar
- **Benchmark Comparison**: Coverage %, rigor %, mastery %, assessment %, gap topics
- **Roadmap**: Completed courses, remaining courses, hours/GPA needs
- Refresh Qualification Status button triggers re-evaluation

### Page 19 — Auto Pipeline
- **One-click automated workflows** that bypass manual page navigation
- **5 presets**: Full Course Build, Deep Enrichment Cycle, Study Prep Package, Full Render Pipeline, Custom Pipeline
- **Full Course Build**: Topic → Generate → Enrich → Jargon → Render (all automatic)
- **Deep Enrichment**: Select courses → Enrich → Decompose → Jargon → Enrich sub-courses → Render
- **Study Prep**: Select courses → Generate flashcards + quizzes for all lectures
- **Full Render**: Select courses → Enrich → Batch render
- **Custom**: Toggle individual steps (generate, enrich, decompose, jargon, flashcards, quiz, render)
- **Configuration**: Topic, difficulty, pacing, target courses, FPS, resolution, rate limit
- **Live progress**: Progress bar, step counter, full pipeline log
- **Results**: Steps completed, courses created, created course IDs, full log

---

## Core Systems

### Academic Infrastructure (`core/university.py`)
Beyond courses and lectures, the university provides:
- **Prerequisites**: Add/remove/check prerequisite chains between courses, prerequisite graph
- **Course Lifecycle**: Draft → Published → Archived status management
- **Flashcards**: SM-2 spaced repetition algorithm — create, review (quality 0-5), due date scheduling, generate from lecture
- **Study Timer**: Pomodoro-style sessions with start/end tracking, total hours, sessions today
- **Notes**: Save/update/delete notes per lecture or course
- **Certificates**: Generate completion certificates with grade and GPA
- **Syllabus**: Auto-generate structured syllabus per course
- **Academic Calendar**: Add/view events (exams, deadlines, terms) per course
- **Backup/Restore**: Full database backup/restore with listing
- **Analytics**: Per-course and global analytics (completion rates, hours, scores)

### Course Decomposition & Pacing (`core/decomposition.py`)
Courses decompose into sub-courses at increasing depth levels with three pacing modes:
- **Fast**: 2-3 concepts/lecture, 2 lectures/module, assumes prerequisites, minimal repetition
- **Standard**: 1 concept/lecture, 3 lectures/module, balanced theory & practice, examples + review
- **Slow**: 1 concept across 4 lectures (intro → walkthrough → edge cases → guided practice), heavy repetition, confidence building

Additional features: jargon course extraction, prove-it verification assignment generation, sub-course registration with depth tracking.

### Scribe System (`core/db_scribe.py`)
Students earn credit by transcribing lecture content:
- **Minimum 10,000 words** per course for scribe completion
- **Per-level tracking**: Words per depth level, completion status
- **Originality verification**: Vocabulary diversity + sentence variation heuristics
- **Scribe quiz generation**: Comprehension quiz based on transcribed text

### Course Audit Workbench
The Professor AI can audit entire courses:
- **Create audit jobs** with course selector
- **Packet-by-packet review**: Each audit packet is reviewed, passed, or flagged for remediation
- **Model profiles**: Different audit rigor levels based on LLM model
- **Remediation backlog**: Track failed packets that need regeneration

### AI Policy & Academic Integrity
Four levels of AI policy per assignment:
- **Unrestricted** (`[OPEN]`): AI use allowed freely
- **Assisted** (`[AIDED]`): AI for specific tasks only
- **Supervised** (`[WATCH]`): AI under constraints, may trigger prove-it verification
- **Prohibited** (`[NONE]`): No AI assistance, verification required

Prove-it assignments are auto-generated to verify understanding when AI-assisted work is flagged.

### Grading Scale & Degrees
- **12 letter grades**: A+ (97+, 4.0) through F (<60, 0.0)
- **5 degree tracks**: Certificate (15 credits, 2.0 GPA), Associate (60, 2.0), Bachelor (120, 2.0), Master (150, 3.0), Doctorate (180, 3.5)
- **Bloom's Taxonomy** levels 1-6: Remember, Understand, Apply, Analyze, Evaluate, Create
- **Credit hour ratio**: Converts study hours to verified credits
- **Activity credits**: Tracked separately from verified credits

### 17 Achievements

| ID | Title | Category | XP Reward |
|----|-------|----------|-----------|
| `first_lecture` | Awakening | progress | 50 |
| `ten_lectures` | Apprentice Path | progress | 200 |
| `first_quiz` | Trial Taker | academic | 75 |
| `perfect_score` | Flawless | academic | 150 |
| `speed_reader` | Swift Scholar | efficiency | 100 |
| `xp_1000` | Rising Star | xp | 100 |
| `xp_5000` | Transcendent Adept | xp | 250 |
| `degree_cert` | Certified | degree | 500 |
| `degree_assoc` | Associate | degree | 1,000 |
| `degree_bachelor` | Bachelor | degree | 2,000 |
| `degree_master` | Grand Scholar | degree | 5,000 |
| `degree_doctor` | Doctorate | degree | 10,000 |
| `night_owl` | Night Owl | habit | 75 |
| `bulk_import` | Archivist | system | 100 |
| `professor_query` | The Asking | llm | 100 |
| `video_render` | Projector | media | 150 |
| `batch_render` | Dreamweaver | media | 300 |

### XP Awards

| Action | XP |
|--------|----|
| Lecture completion | +10 |
| Assignment submit | +25 |
| Quiz take | +15 |
| Course import | +10 per course |
| Curriculum generation | +100 |
| Course decomposition | +150 |
| Jargon course generation | +75 |
| Plan & Generate course | +200 |
| Professor consult | +5 |
| Study session (25+ min) | +15 |
| Weekly quest complete | +50–100 |

### 20 Grade Levels

K, 1st–5th Grade (Elementary), 6th–8th Grade (Middle School), 9th–12th Grade (High School), College Freshman, Sophomore, Junior, Senior, Master's Student, Doctoral Candidate, Post-Doctoral.

---

## LLM Provider Support

### Local Providers (Free)

| Provider | Setup | Models |
|----------|-------|--------|
| **Ollama** | Install from ollama.com, run `ollama serve` | 5 tiers: Tiny (1-3B, 4GB RAM) → XL (70B+, 64GB RAM). Includes llama3.2, qwen3, gemma3, deepseek-r1, mistral, phi4, codellama |
| **LM Studio** | Install from lmstudio.ai, start server on port 1234 | Any GGUF model from HuggingFace |

### Cloud Providers

| Provider | Cost | Models | Best For |
|----------|------|--------|----------|
| **Groq** | Free tier | llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768, gemma2-9b-it | Fastest inference |
| **GitHub Models** | Free (GitHub account) | gpt-4.1, gpt-4.1-mini, o4-mini, o3-mini, Meta-Llama-3.1-405B/70B, Mistral-large, Phi-4, DeepSeek-R1 | Best free quality |
| **OpenAI** | Paid | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, o3-mini | Best overall quality |
| **Anthropic** | Paid | claude-sonnet-4-20250514, claude-3-5-haiku, claude-3-5-sonnet | 200K context, best reasoning |
| **Mistral** | Free experiment tier | mistral-large-latest, mistral-small-latest, codestral-latest | European, code-focused |
| **Together AI** | Free $5 credit | Llama-3.3-70B-Turbo, Qwen2.5-72B-Turbo, DeepSeek-R1 | Budget, open models |
| **HuggingFace** | Free tier | Llama-3.3-70B, Qwen2.5-72B, Mistral-7B | Open-source community |

All providers support: timeout (60s), retry with exponential backoff + jitter, streaming (where available), error classification (auth, rate_limit, timeout, network, bad_model, provider_down), cost estimation, token estimation (~4 chars/token), and fallback chains via `chat_with_fallback()`.

### Image Provider Support

| Provider | Cost | Notes |
|----------|------|-------|
| Pollinations | Free | Default priority 1, no API key needed |
| HuggingFace | Free tier | Requires API token |
| GitHub Models | Free | Uses GitHub PAT |
| DeepAI | Free tier | 5 free/month |
| Prodia | Free tier | Fast generation |
| GetImg.ai | Free tier | High quality |
| Stability AI | Paid | Stable Diffusion |
| Leonardo AI | Paid | Fine-tuned models |
| LimeWire | Free tier | Community models |
| ComfyUI | Local/Free | Requires local install |

Image providers auto-cycle with fallback. Each attempt has a 30s timeout.

---

## Agent Tools (22 Total)

### Course Tools
| Tool | Description |
|------|-------------|
| `create_course_outline` | Create a new course with title, description, and module skeleton |
| `add_module` | Add a new module to an existing course |
| `add_lecture` | Add a lecture with full video recipe to a module |
| `add_assignment` | Add a quiz or homework assignment |
| `get_course_manifest` | Get compact manifest of a course |
| `get_all_courses_summary` | Summary list of all courses |
| `validate_and_import` | Validate JSON against schema and import (requires review) |
| `search_courses` | Search courses by keyword |
| `generate_quiz_for_lecture` | Generate quiz using LLM |
| `decompose_course` | Decompose into deeper sub-courses |
| `generate_jargon_course` | Generate terminology sub-course |
| `enrich_course_narration` | Enrich all narrations via LLM (versioned) |
| `advance_course_level` | Advance to next education depth level |

### Video Tools
| Tool | Description |
|------|-------------|
| `list_scenes` | List all scenes for a lecture |
| `edit_scene` | Edit narration, visual prompt, or duration |
| `add_scene` | Add a new scene to a lecture |
| `remove_scene` | Remove a scene |
| `reorder_scenes` | Reorder by block_id list |
| `enhance_narration` | LLM-rewrite scene narration |
| `render_lecture` | Render lecture to MP4 |
| `batch_render_course` | Render all lectures in a course |

### Utility Tools
| Tool | Description |
|------|-------------|
| `get_lecture_data` | Full lecture data including scenes, objectives, terms |

---

## Audio Engine

- **13 Neural Voices**: Microsoft Edge-TTS (Aria, Jenny, Amber, Emma, Guy, Brian, Davis, Andrew, Sonia, Ryan, Natasha, William, Clara)
- **Multi-engine TTS**: Cycling providers → edge-tts fallback → pyttsx3 offline
- **Binaural Beats**: Gamma 40Hz, Beta 18Hz, Alpha 10Hz, Theta 6Hz presets — stereo generation
- **Ambient Pads**: Additive synthesis with chord + tremolo + breathing
- **8 Procedural SFX**: click, success, unlock, error, xp_gain, level_up, page_turn, collect
- **Audio Processing**: RMS/LUFS measurement, loudness normalization, clipping detection, auto-gain, stereo WAV writing
- **Mix Pipeline**: TTS + ambient mixing via MoviePy with separate volume controls

---

## Video Pipeline

- **Frame Renderer**: PIL + numpy for scene frame generation with text overlays
- **Scene Builder**: Block orchestration with timing and animation
- **VFX Pipeline**: Scene transitions (crossfade), Ken Burns pan/zoom, cinematic color grading, title/term text overlays, ambient particle effects, watermark/branding
- **Encoding**: H.264 MP4 via imageio-ffmpeg (no system FFmpeg install required)
- **AI Backgrounds**: 10-provider image generation with auto-cycling fallback, 30s timeout per attempt
- **Quality Profiles**: Draft (fast), Balanced, High Quality, Final, Custom
- **Resolution Options**: 960×540, 1280×720, 1920×1080
- **FPS Options**: 10, 15, 24, 30

---

## Database Architecture

- **Engine**: SQLite with WAL mode, foreign keys enabled
- **Pattern**: 3 facades (student, curriculum, AI) delegating to 12+ sub-modules
- **30+ Tables**: courses, modules, lectures, progress, assignments, achievements, xp_events, chat_history, settings, quests, terms, flashcards, study_sessions, certificates, notes, academic_calendar, prerequisites, course_lifecycle, placement tests, test prep sessions, programs, enrollments, activity log, scribe entries, audit jobs, audit packets, enrichment versions, benchmarks, qualifications, remediation backlog
- **80+ Public Functions** exported via `core/database.py`
- **4 Versioned Migrations**: subject_id, course tree columns, ai_policy, assessment tracking
- **Backup/Restore**: Full database backup with timestamped files, listing, and restore

---

## Project Structure

```
app.py                          Main dashboard (mode selector, XP bar, system health, quests)
notes.txt                       Built-in course auto-imported on first run
USAGE_GUIDE.md                  End-to-end usage documentation
DOUBLE_CLICK_SETUP_AND_START.bat  One-click Windows launcher
setup.bat / setup.sh            Platform setup scripts
start.bat / start.sh            Platform start scripts
requirements.txt                Python dependencies
university.db                   SQLite database (auto-created)

core/
  database.py                   SQLite persistence (WAL, 3 facades, 80+ functions)
  university.py                 Prerequisites, flashcards, study timer, notes, certificates,
                                syllabus, calendar, backup/restore, analytics
  decomposition.py              Course decomposition, pacing (fast/standard/slow), jargon prompts
  continuous_engine.py           24/7 enrichment loop with versioned narration
  auto_pipeline.py              One-click pipeline engine (5 presets, 7 steps)
  settings_registry.py           Centralized settings registry (30+ keys, 7 categories)
  help_registry.py              60+ contextual help entries organized in 19 groups
  ui_mode.py                    Route access control (student/builder/operator)
  tts_config.py                 Voice/pitch/rate config, 13 neural voices, binaural presets
  llm_setup.py                   Hardware detection, provider catalogs, connectivity testing
  placement.py                  Adaptive placement exam engine (10 questions, difficulty 1-10)
  test_prep.py                  Standardized test practice (SAT/ACT/GRE/GED, timed sessions)
  content_log.py                 Content generation tracking
  asset_library.py              Generated asset caching and reuse
  app_docs.py                   Professor-readable app documentation
  db_achievements.py            17 achievements across 7 categories
  db_activity.py                Activity logging, daily counts, profile storage
  db_assignments.py             Assignment CRUD, AI policy, term grouping
  db_audit.py                   Course audit jobs, packets, remediation
  db_facade_ai.py               AI facade (chat, audit, agent)
  db_facade_curriculum.py       Curriculum facade (courses, modules, lectures)
  db_facade_student.py          Student facade (progress, XP, grades)
  db_grades.py                  GPA calculation, grade scale, degree tracks
  db_import.py                  Bulk JSON import with validation
  db_levels.py                  20 grade levels (K through Post-Doctoral)
  db_programs.py                7 seeded degree programs, enrollments
  db_qualifications.py          Benchmark tracking, qualification roadmaps
  db_quests.py                  Weekly quest system
  db_scribe.py                  Scribe transcription (10K word minimum, originality checks)
  db_subjects.py                Subject domains and hierarchies

llm/
  providers.py                  Universal LLM client (10 providers, retry, timeout, streaming, fallback)
  professor.py                  Professor AI (combines base + content + workflow mixins)
  professor_base.py             Chat, history truncation (preserves first message)
  professor_content.py          Curriculum, quiz, homework, grading with JSON validation
  professor_workflows.py        Decomposition, jargon, plan-and-generate, verification
  agent.py                      Autonomous agent (bounded/unlimited, review mode, 22 tools)
  tools.py                      Tool registry and dispatcher
  tools_course.py               9 course tools
  tools_video.py                7 video tools (reject error narrations)
  tools_enrichment.py           5 enrichment tools (decompose, jargon, enrich, advance, batch)
  tools_utility.py              1 utility tool
  generation_queue.py           Background generation with exponential backoff + jitter
  model_profiles.py             Audit model profiles

media/
  audio_engine.py               TTS (13 voices), binaural beats, ambient pads, SFX, mixing
  output_paths.py               Video/audio output path resolution
  video/
    encoder.py                  H.264 encoding with full VFX pipeline
    frame_renderer.py           PIL + numpy scene frame generation
    scene_builder.py            Scene block orchestration
  diffusion/
    free_tier_cycler.py         10-provider image generation with fallback + 30s timeout

ui/
  theme.py                      Dark-academic CSS, help buttons, stat cards, badges, SFX
  professor_tabs.py             8 Professor tab render functions

pages/
  01_Library.py                 5-tab course management
  02_Lecture_Studio.py          Video playback, rendering, assignments, scribe
  03_Professor_AI.py            8-tab Professor interface
  04_Timeline_Editor.py         Scene reordering and override
  05_Batch_Render.py            Queue rendering + 24/7 continuous enrichment
  06_Grades.py                  GPA, transcript, degree eligibility
  07_Achievements.py            XP system, badges, level progression
  08_Settings.py                7-section configuration hub
  09_Diagnostics.py             System health, dependency check, module compile
  10_Help.py                    60+ topics, tutorial, quick reference
  11_LLM_Setup.py               Guided provider configuration
  12_Placement.py               Adaptive placement testing
  13_Test_Prep.py               SAT/ACT/GRE/GED practice
  14_Programs.py                Degree programs and enrollments
  15_Profile.py                 Student identity and preferences
  16_Statistics.py              Activity dashboard with charts
  17_Agent.py                   Autonomous task execution
  18_Qualifications.py          Real-world benchmark tracking
  19_Auto_Pipeline.py           One-click automated workflows
  library/                      Sub-modules (explore, build, map, alignment, media_setup, services)

schemas/
  course_schema.json            Example course JSON structure
  assignment_schema.json        Assignment JSON structure
  course_validation_schema.json Course validation rules
  SCHEMA_GUIDE.md               Prompt guide for LLM course generation
```

---

## Troubleshooting

### Windows

| Problem | Fix |
|---------|-----|
| `python` not recognized | Reinstall Python, check "Add Python to PATH" |
| Long path errors | `reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f` |
| Edge-TTS timeout | Check firewall — requires HTTPS to `*.tts.speech.microsoft.com` |
| MoviePy FFmpeg errors | `pip install --force-reinstall imageio-ffmpeg` |
| Black screen in video | `pip install --upgrade Pillow` |

### macOS / Linux

| Problem | Fix |
|---------|-----|
| `python3` not found | macOS: `brew install python@3.11` · Ubuntu: `sudo apt install python3 python3-venv` |
| PEP 668 error | Use the `.venv` virtual environment (setup script creates one) |
| Permission denied | `chmod +x setup.sh start.sh` |

### General

| Problem | Fix |
|---------|-----|
| Database locked | Close other tabs sharing the database |
| Import fails | Paste raw JSON. Use `schemas/SCHEMA_GUIDE.md` for format |
| Professor not responding | Check Diagnostics (page 9) and LLM Setup (page 11) |
| Stale data | Delete `university.db*`, re-run |
| No AI backgrounds | Configure at least one image provider in Library → Media Sources. Pollinations works without a key |
| Scribe credit not counting | Must reach 10,000 words minimum per course. Check originality verification |
| Agent stuck | Check rate limit settings. Try bounded mode with fewer max steps first |
| Audit packets failing | Check LLM connectivity. Model profile may need adjustment |

---

## Manual Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -c "from core.database import init_db; init_db()"
streamlit run app.py
```

**FFmpeg**: Bundled via `imageio-ffmpeg` — no system install needed. If issues persist, check `pip show imageio-ffmpeg`.

**LLM**: Use the LLM Setup Wizard (page 11) or Diagnostics (page 9) to test connectivity. For local models, ensure Ollama or LM Studio is running.

## Requirements

- Python 3.9+
- Internet connection (for TTS and cloud LLM providers)
- 4GB+ RAM minimum, 8GB+ recommended for local LLM models
- All other dependencies installed automatically via `requirements.txt`

## License

This project is provided as-is for educational purposes.
