# The God Factory University — Complete Usage Guide

Every feature, every workflow, end-to-end. This guide also serves as the blueprint for the **One-Click Auto Pipeline** (page 19).

---

## Table of Contents

1. [First Launch & Setup](#first-launch--setup)
2. [UI Modes](#ui-modes)
3. [Dashboard](#dashboard)
4. [Creating Courses](#creating-courses)
5. [Enrichment, Decomposition & Jargon](#enrichment-decomposition--jargon)
6. [24/7 Continuous Enrichment Mode](#247-continuous-enrichment-mode)
7. [Rendering Video Lectures](#rendering-video-lectures)
8. [Visual Effects Configuration](#visual-effects-configuration)
9. [Studying with the Professor](#studying-with-the-professor)
10. [Assignments & AI Policy](#assignments--ai-policy)
11. [Scribe Credit System](#scribe-credit-system)
12. [Course Audit Workbench](#course-audit-workbench)
13. [Grades, GPA & Transcript](#grades-gpa--transcript)
14. [Degree Programs & Enrollment](#degree-programs--enrollment)
15. [Achievements & XP System](#achievements--xp-system)
16. [Flashcards (SM-2 Spaced Repetition)](#flashcards-sm-2-spaced-repetition)
17. [Study Timer](#study-timer)
18. [Notes System](#notes-system)
19. [Certificates](#certificates)
20. [Academic Calendar](#academic-calendar)
21. [Course Prerequisites & Lifecycle](#course-prerequisites--lifecycle)
22. [Timeline Editor](#timeline-editor)
23. [Placement Testing](#placement-testing)
24. [Standardized Test Prep](#standardized-test-prep)
25. [Student Profile](#student-profile)
26. [Statistics Dashboard](#statistics-dashboard)
27. [Autonomous Agent](#autonomous-agent)
28. [Qualifications & Benchmarks](#qualifications--benchmarks)
29. [Settings Reference](#settings-reference)
30. [LLM Setup Wizard](#llm-setup-wizard)
31. [Image Provider Setup](#image-provider-setup)
32. [Audio Configuration](#audio-configuration)
33. [Diagnostics & System Health](#diagnostics--system-health)
34. [Help System](#help-system)
35. [Backup & Restore](#backup--restore)
36. [One-Click Auto Pipeline](#one-click-auto-pipeline)
37. [Troubleshooting](#troubleshooting)

---

## First Launch & Setup

### Step 1: Install & Launch
1. Run the setup script for your OS (see README.md) or double-click `DOUBLE_CLICK_SETUP_AND_START.bat` on Windows
2. Browser opens to the **Dashboard** at `http://localhost:8501`
3. On first launch, the app auto-imports a built-in course from `notes.txt` and initializes the database with 30+ tables

### Step 2: Configure AI Provider
Before using AI features (curriculum generation, enrichment, quizzes, grading, chat):
1. Go to **LLM Setup Wizard** (page 11)
2. Choose **Local** (free, runs on your machine) or **Cloud** (API key required)
3. For the fastest free start: install [Ollama](https://ollama.com), run `ollama pull llama3.2`, then Save & Test in the wizard
4. The wizard auto-detects your hardware (RAM, GPU VRAM) and recommends a model size tier

### Step 3: Configure Image Providers (Optional)
For AI-generated video backgrounds instead of gradient backgrounds:
1. Go to **Library** (page 1) → **Media Sources** tab
2. Enter API keys for any of the 9 cloud image providers
3. **Pollinations** works without a key and is the default (priority 1)
4. Multiple providers will auto-cycle with fallback

### Step 4: Set Your Profile
1. Go to **Profile** (page 15)
2. Set your student name and grade level (K through Post-Doctoral)
3. Choose learning style (Visual/Auditory/Reading/Kinesthetic) and study pace (relaxed/moderate/intensive)

---

## UI Modes

The sidebar mode selector controls which pages are visible:

| Mode | Access | Pages Available |
|------|--------|-----------------|
| **Student** | Study-focused | Dashboard, Library (Explore only), Lecture Studio, Professor AI, Grades, Achievements, Settings, Help, Profile, Statistics |
| **Builder** | Content creation | All Student pages + Library (Build tab), Timeline Editor, Batch Render, Agent |
| **Operator** | Full admin | All Builder pages + Diagnostics, Placement, Test Prep, Programs, Qualifications |

Gated pages in Student mode show a guided prompt explaining what the page does and offering to switch mode.

---

## Dashboard

The main landing page (`app.py`) provides:

- **4 status cards**: Courses count, Lectures completed, Total XP, Current rank
- **4 academic cards**: Verified Credits, Study Hours, Idle Days, Active Days
- **XP bar**: Visual progress through current level
- **Level badge**: Current rank name and level number
- **Audit Queue**: If audit jobs exist, shows title, status, processed/total packets, ETA
- **Weekly Quests**: Icon, title, progress/target, XP reward, progress bar (if quests enabled in Settings)
- **Quick Start guide**: Built-in walkthrough for new users
- **System Health**: 6 expandable self-checks (Database, FFmpeg, TTS Engine, LLM Config, Video Engine, Audio Engine) with [OK]/[!!] status
- **Active Courses**: Styled cards for all courses in the database

---

## Creating Courses

### Option A: Import Existing JSON
1. Go to **Library** (page 1) → **Build & Import** tab
2. Paste course JSON into the BULK IMPORT section (see `schemas/SCHEMA_GUIDE.md` for format)
3. Click Import — courses, modules, and lectures appear instantly
4. **Pro tip**: Copy `schemas/SCHEMA_GUIDE.md` into any external LLM (ChatGPT, Claude, etc.) and ask it to generate a course on your topic, then paste the JSON output

### Option B: AI-Generate via Professor (4 Modes)
Go to **Professor AI** (page 3) → **Generate Curriculum** tab:

1. **Generate New**: Enter topic, difficulty level, lectures per module → Professor creates complete course → Review and Import
2. **Decompose Existing**: Select a course → Professor splits it into deeper sub-courses at the next depth level (respects pacing: fast/standard/slow)
3. **Generate Jargon Course**: Select a course → Professor extracts all terminology into a focused vocabulary sub-course with term, definition, etymology, usage example, related terms
4. **Plan & Generate**: Enter topic → Professor uses token planner + GenerationQueue for budget-aware adaptive generation of all course content (+200 XP)

### Option C: Agent-Generated
1. Go to **Agent** (page 17)
2. Describe the task: "Create a full course on quantum computing with 4 modules"
3. The agent autonomously uses `create_course_outline`, `add_module`, `add_lecture`, and `add_assignment` tools
4. In review mode, you approve each tool call before execution

### Option D: Library Explore Tab
1. Go to **Library** → **Explore** tab
2. Browse existing courses
3. Click "Generate Next Level" on any course to auto-generate the next enrichment depth level

### Course Structure
Every course contains:
- **Course**: id, title, description, credits, credit_hours, pacing, depth_level, subject
- **Modules**: Ordered sections within a course
- **Lectures**: Ordered lessons within modules, each containing:
  - Learning objectives and core terms
  - `video_recipe`: Array of scene blocks, each with narration text, visual prompt, duration, ambiance
  - Assignments (optional)

---

## Enrichment, Decomposition & Jargon

### Enrichment
**What it does**: Rewrites lecture narration scripts to be richer, more detailed, and educational. Adds real examples, definitions, step-by-step explanations.

**How to use**:
- **Single lecture**: In Lecture Studio (page 2) → expand "Enrich Narration with LLM" → Click Enrich. Progress updates per scene
- **Batch**: In Batch Render (page 5) → check "Enrich narration with LLM before rendering"
- **Via Agent**: Agent can call `enrich_course_narration` tool
- **24/7 mode**: Continuous enrichment engine (see below)

**Versioning**: Every enrichment saves the prior narration. Versions are tracked in the `enrichment_versions` table. No content is ever lost.

### Decomposition
**What it does**: Splits a course into deeper sub-courses for more granular learning. Respects three pacing modes:
- **Fast**: 2-3 concepts/lecture, 2 lectures/module, assumes prerequisites, minimal repetition
- **Standard**: 1 concept/lecture, 3 lectures/module, balanced theory & practice with examples and review
- **Slow**: 1 concept across 4 lectures (intro → walkthrough → edge cases → guided practice), heavy repetition, confidence building

**How to use**:
- **Professor AI** → Generate Curriculum → "Decompose Existing Course" mode → Select course → Decompose
- **Via Agent**: `decompose_course` tool
- **24/7 mode**: Automatic after N enrichment cycles

### Jargon Courses
**What it does**: Extracts all key terminology from a course and creates a 1-credit focused vocabulary sub-course. Each term includes: term, definition, etymology, usage example, related terms.

**How to use**:
- **Professor AI** → Generate Curriculum → "Generate Jargon Course" mode → Select course
- **Via Agent**: `generate_jargon_course` tool
- **24/7 mode**: Generated automatically each cycle

---

## 24/7 Continuous Enrichment Mode

The continuous enrichment engine (`core/continuous_engine.py`) runs an automated loop that progressively enriches all course content:

### Setup
1. Go to **Batch Render** (page 5) → scroll to **24/7 Continuous Enrichment**
2. Select target: **All Courses** or a specific course
3. Configure cycle parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Enrichments before decompose | 3 | How many enrichment passes before triggering decomposition |
| Decompositions before level advance | 2 | How many decompositions before advancing education level |
| Jargon per cycle | 1 | Jargon courses generated per decomposition cycle |
| Rate limit | 2.0s | Seconds between LLM calls (prevents rate limiting) |
| Auto-render | Off | Render video after each enrichment cycle |

### Cycle Behavior
Each cycle performs:
1. **Enrich**: Rewrite all lecture narrations (versioned)
2. **Check decompose threshold**: If enrichment count ≥ threshold → decompose into sub-courses
3. **Generate jargon**: Extract terminology sub-course
4. **Check level advance threshold**: If decomposition count ≥ threshold → advance education depth level
5. **Auto-render** (if enabled): Render all lectures to MP4
6. **Repeat** until stopped

### Monitoring
- Live progress display shows: current cycle number, current action, cumulative totals
- Click **Stop** to halt after the current action completes

---

## Rendering Video Lectures

### Single Lecture Render
1. Go to **Lecture Studio** (page 2) → select Course → Module → Lecture
2. Click **Render Full Lecture**
3. The system:
   - Generates TTS audio for each scene (edge-tts with selected voice/rate/pitch)
   - Generates or uses background images (AI or gradient)
   - Applies VFX pipeline (transitions, Ken Burns, color grading, text overlays, particles, watermark)
   - Mixes TTS + binaural beats + ambient pads
   - Encodes to H.264 MP4 via imageio-ffmpeg
4. Watch the video directly in the browser player
5. Click **Mark as Completed** to earn +10 XP and unlock achievements

### Scene Chunk Export
In Lecture Studio → Click **Export Scene Chunks** to render each scene as a separate MP4 file.

### Render All Course Lectures
In Lecture Studio → Click **Render ALL Course Lectures** to render every lecture in the course with a progress bar and log.

### Batch Render
1. Go to **Batch Render** (page 5)
2. Filter by course, difficulty, or sort order
3. Select lectures via checkboxes (or "Select all")
4. Choose FPS (10/15/24) and resolution (960×540 / 1280×720 / 1920×1080)
5. Optionally check "Enrich narration" for first-time renders
6. Click **Start Batch Render**
7. Monitor progress bar and render log ([OK]/[ERR] per lecture)
8. Click **Abort** to stop mid-batch

### Quality Profiles
Set in **Settings** (page 8) → Video & Rendering:
- **Draft (Fast)**: Low resolution, minimal VFX — for previewing
- **Balanced**: Medium settings, good for reviewing
- **High Quality**: Full VFX, higher resolution
- **Final**: Maximum quality, all effects
- **Custom**: Set each parameter individually

---

## Visual Effects Configuration

Configure VFX in **Batch Render** or **Lecture Studio** → Visual Effects section:

| Effect | Description |
|--------|-------------|
| **AI-generated backgrounds** | Replace gradient backgrounds with AI images. Toggle on/off, select provider |
| **Scene transitions** | Crossfade between scenes |
| **Ken Burns pan/zoom** | Slow pan and zoom on still images for cinematic feel |
| **Cinematic color grading** | Film-like color correction |
| **Title/term overlays** | Display learning objectives and key terms as text overlays |
| **Ambient particles** | Floating particle effect overlay |
| **Watermark** | Branding watermark on video |

---

## Studying with the Professor

The Professor AI (page 3) has 8 modes of interaction:

### Chat Tab
- Free-form conversation with the Professor AI using Socratic method
- Session-based history (persisted to database)
- +5 XP per consultation
- Shows provider status: [LOCAL/API/FREE] PROVIDER / MODEL

### Generate Curriculum Tab
4 generation modes (see [Creating Courses](#creating-courses)):
- Generate New (+100 XP)
- Decompose Existing (+150 XP)
- Generate Jargon Course (+75 XP)
- Plan & Generate (+200 XP)

### Grade Work Tab
- Paste essay text or code into the submission box
- Professor returns: numerical score, letter grade, detailed feedback, strengths, areas for improvement
- Rubric-based evaluation

### Create Quiz Tab
- Enter any topic or select a lecture
- Professor generates MCQ (multiple choice) + short answer questions
- Self-assessment mode for practice
- +15 XP per quiz taken

### Research Rabbit Hole Tab
- Enter a seed topic to explore deeply
- Professor generates a research chain: historical context, open problems, connections to other fields, recommended resources
- Each exploration awards XP

### Audit Workbench Tab
- Create a course audit job by selecting a course
- Professor generates audit packets that review course quality
- Review each packet: Pass or Flag for remediation
- View remediation backlog for failed packets
- Regenerate flagged content
- Uses model profiles for variable audit rigor

### Chat History Tab
- Browse and review previous conversations
- Sessions listed with timestamps

### App Guide Tab
- In-app tutorial powered by the Professor
- Contextual help for current page

---

## Assignments & AI Policy

### Assignment Types
Assignments are attached to lectures and appear in the Lecture Studio:
- **Quiz**: Multiple choice and short answer
- **Homework**: Essay or code submission
- **Project**: Extended assignments

### AI Policy Levels
Each assignment has an AI policy controlling how AI may be used:

| Policy | Badge | Description |
|--------|-------|-------------|
| Unrestricted | `[OPEN]` | AI use allowed freely |
| Assisted | `[AIDED]` | AI for specific tasks only |
| Supervised | `[WATCH]` | AI under constraints, may trigger prove-it verification |
| Prohibited | `[NONE]` | No AI assistance, verification required |

### Prove-It Verification
When AI-assisted work is flagged under Supervised or Prohibited policy:
1. The system auto-generates a "prove-it" verification assignment
2. Student must demonstrate understanding without AI help
3. Generated via `build_verification_prompt()` in `core/decomposition.py`

### Submitting Assignments
1. In Lecture Studio → expand an assignment
2. Enter submission text (essay/code/answers)
3. Click Submit → Professor AI grades it
4. Score, feedback, and grade appear
5. +25 XP per submission

### Deadlines
When deadlines are enabled (Settings → General → Deadlines toggle):
- Deadline pills show countdown timers on open assignments
- Past-due assignments are flagged

---

## Scribe Credit System

Students earn credit by transcribing lecture content in their own words:

1. In **Lecture Studio** (page 2) → **Scribe Credit** section
2. View current status: Words submitted, Requirement (10,000 minimum), Progress %
3. Expand the scribe submission area
4. Write transcription in the text area
5. Click Submit

### Completion Requirements
- **Minimum 10,000 words** per course for scribe completion
- **Per-depth-level tracking**: Each depth level of a course has its own word count
- **Originality verification**: Heuristic check for vocabulary diversity + sentence variation
- **Scribe quiz**: Auto-generated comprehension quiz based on submitted text

### Functions
- `save_scribe()`: Save transcription text
- `total_scribe_words()`: Current word count
- `scribe_complete()`: Check if 10K threshold met
- `verify_scribe_originality()`: Heuristic originality check
- `generate_scribe_quiz()`: Generate comprehension quiz from text

---

## Course Audit Workbench

The audit system (Professor AI → Audit Workbench tab) reviews course quality:

### Creating an Audit
1. Select a course from the course selector
2. Click Create Audit Job
3. The system generates audit packets by analyzing each lecture

### Reviewing Packets
1. The audit workbench shows the next pending packet
2. Review the content quality assessment
3. Click **Pass** to approve or **Flag** to mark for remediation
4. Each review records your feedback

### Remediation
1. View the remediation backlog for all flagged packets
2. Click **Regenerate** to re-generate the flagged content
3. Or manually fix the content

### Model Profiles
Audits use model profiles (`llm/model_profiles.py`) that adjust rigor based on the LLM model's capabilities.

---

## Grades, GPA & Transcript

### Viewing Grades (Page 6)
- **GPA Summary**: Cumulative GPA, Verified Credits, Eligible Degrees
- **Study Hours**: Total, Assessment, Hour-Based Credits
- **Enrollment Info**: Enrolled date, Days studied

### Grade Scale
| Grade | Score Range | GPA Points |
|-------|------------|------------|
| A+ | 97–100% | 4.0 |
| A | 93–96% | 4.0 |
| A- | 90–92% | 3.7 |
| B+ | 87–89% | 3.3 |
| B | 83–86% | 3.0 |
| B- | 80–82% | 2.7 |
| C+ | 77–79% | 2.3 |
| C | 73–76% | 2.0 |
| C- | 70–72% | 1.7 |
| D+ | 67–69% | 1.3 |
| D | 60–66% | 1.0 |
| F | <60% | 0.0 |

### Assignments by Course
Each course expander shows:
- Verified completion badge
- Official and activity credits
- Passed assignment count
- Assignment table: Title, Type, AI Policy, Score, Grade, Status
- Deadline pills for open assignments

### Term Grouping
If terms exist, assignments are also grouped by academic term.

### Transcript Export
- **Download CSV**: Spreadsheet-compatible transcript
- **Download JSON**: Machine-readable format

### Degree Progress
Progress bars for each degree track:
- **Certificate**: 15 credits, 2.0 GPA minimum
- **Associate**: 60 credits, 2.0 GPA
- **Bachelor**: 120 credits, 2.0 GPA
- **Master**: 150 credits, 3.0 GPA
- **Doctorate**: 180 credits, 3.5 GPA

### Time-to-Degree Estimate
Select a degree → view: Credits Needed, Hours Remaining, Estimated Days Left, GPA warning if needed.

---

## Degree Programs & Enrollment

### Viewing Programs (Page 14)
- Academic status summary: GPA, Verified Credits, Verified Courses
- Browse 7 seeded programs: Certificate in CS, Certificate in Math, Associate General, Bachelor in CS, Bachelor in Engineering, Master in CS, Doctorate in CS

### Enrolling
1. Browse available programs
2. Click **Enroll** on any program
3. Track progress via the progress bar (credits earned / required)
4. View all enrollments in the "Your Enrollments" list

### Program Requirements
Each program has specific course and credit requirements that must be met for completion.

---

## Achievements & XP System

### XP Events
| Action | XP Earned |
|--------|-----------|
| Complete a lecture | +10 |
| Submit an assignment | +25 |
| Take a quiz | +15 |
| Import courses | +10 per course |
| Generate curriculum | +100 |
| Decompose a course | +150 |
| Generate jargon course | +75 |
| Plan & Generate course | +200 |
| Consult Professor | +5 |
| Study session (25+ min) | +15 |
| Complete weekly quest | +50–100 |

### 17 Achievements (Page 7)
Achievements unlock automatically when conditions are met. Each awards bonus XP:
- **Progress**: Awakening (first lecture, +50), Apprentice Path (10 lectures, +200)
- **Academic**: Trial Taker (first assignment, +75), Flawless (100% score, +150)
- **Efficiency**: Swift Scholar (lecture in one session, +100)
- **XP milestones**: Rising Star (1000 XP, +100), Transcendent Adept (5000 XP, +250)
- **Degrees**: Certified (+500), Associate (+1000), Bachelor (+2000), Grand Scholar/Master (+5000), Doctorate (+10000)
- **Habits**: Night Owl (study after midnight, +75)
- **System**: Archivist (bulk import, +100)
- **LLM**: The Asking (10 Professor queries, +100)
- **Media**: Projector (first render, +150), Dreamweaver (batch 5+ renders, +300)

### Level Progression
XP accumulates into levels. Page 7 shows 10 level progression rows with:
- Level number and name
- XP required for each level
- Status: [CURRENT] / [UNLOCKED] / [LOCKED]

### Study Streak
- **Consecutive days** of activity tracked
- **Streak bonus**: +N% XP multiplier based on streak length
- Visible on Profile page (page 15)

### Weekly Quests
When enabled (Settings → General → Weekly Quests toggle):
- Dashboard shows active quests with icon, title, progress/target, XP reward
- Quests refresh weekly

---

## Flashcards (SM-2 Spaced Repetition)

The university includes a full SM-2 flashcard system (`core/university.py`):

### Creating Flashcards
- **Manual**: Create with front (question) and back (answer) text, optionally linked to a lecture or course
- **Auto-generated**: `generate_flashcards_from_lecture()` extracts key terms and creates flashcard sets

### Reviewing
- `get_due_flashcards()` returns cards due for review based on SM-2 scheduling
- Rate each card 0-5 (quality of recall)
- SM-2 algorithm adjusts interval, ease factor, and next review date
- Higher quality → longer interval before next review

### Browsing
- `get_all_flashcards()` lists all cards, optionally filtered by course

---

## Study Timer

Pomodoro-style study timer (`core/university.py`):

1. **Start**: `start_study_session(session_type, lecture_id)` begins tracking
2. **End**: `end_study_session(session_id, notes)` records duration and notes
3. **Stats**: `get_study_stats()` returns total hours, session count, minutes today
4. Sessions of 25+ minutes earn **+15 XP**

---

## Notes System

Save personal notes linked to lectures or courses:

- `save_note(content, lecture_id, course_id)` — Create a note
- `update_note(note_id, content)` — Edit
- `get_notes(lecture_id, course_id)` — Retrieve (filter by lecture or course)
- `delete_note(note_id)` — Remove

---

## Certificates

Generate completion certificates when finishing a course:

1. Complete all lectures in a course
2. `generate_certificate(course_id, grade, gpa)` creates a certificate record
3. `get_certificates()` lists all earned certificates
4. Certificates include: course title, completion date, grade, GPA

---

## Academic Calendar

Track academic events and deadlines:

- `add_calendar_event(event_type, title, start_date, end_date, course_id, data)` — Add exam dates, term starts, deadlines
- `get_calendar_events(course_id)` — List events, optionally filtered by course

---

## Course Prerequisites & Lifecycle

### Prerequisites
- `add_prerequisite(course_id, prereq_id, required)` — Require one course before another
- `check_prerequisites_met(course_id)` — Returns (met: bool, missing: list)
- `get_prerequisite_graph()` — Full dependency graph for visualization

### Course Lifecycle
Courses have three states:
- **Draft**: Being built, not yet available to students
- **Published**: Active and available
- **Archived**: No longer active, kept for records

Manage via `set_course_status()`, `get_course_status()`, `get_courses_by_status()`.

---

## Timeline Editor

Fine-tune lecture video timing (page 4):

1. Select Course → Module → Lecture
2. View all scenes as blocks showing: index, block ID, ambiance prompt, narration preview
3. **Reorder**: Click Up (^) or Down (v) buttons to move scenes
4. **Override duration**: Set per-scene duration (0 = use TTS audio length)
5. **Reset**: Restore original scene order
6. **Render Edited**: Render with modified timeline (output suffix `_edited`)
7. **Export JSON**: Save modified scene data for backup

---

## Placement Testing

Adaptive placement exams (page 12, Operator mode):

1. Select a **subject domain** from the hierarchy
2. Optionally narrow to a specific field
3. Start the exam — 10 questions with adaptive difficulty (1-10 scale)
4. Difficulty adjusts based on answer streak
5. Question format: 4-choice MCQ with difficulty dots indicator (⬥⬦)
6. Results: Score %, Correct/Total, **Recommended Level** (beginner/intermediate/advanced)
7. View test history: last 10 tests
8. +XP awarded on completion

---

## Standardized Test Prep

Timed practice for standardized tests (page 13, Operator mode):

### Available Tests & Sections
| Test | Sections |
|------|----------|
| **SAT** | Reading, Writing & Language, Math No Calc, Math Calculator |
| **ACT** | English, Math, Reading, Science |
| **GRE** | Verbal, Quantitative, Analytical Writing |
| **GED** | Language Arts, Math, Science, Social Studies |

### Practice Flow
1. Select test and section
2. Toggle timed mode (10-minute sessions)
3. Click **Start Practice**
4. Answer questions (MCQ with 4 choices) — auto-submit on timeout
5. **Score Report**: Score %, Correct/Total, Percentile estimate, Time taken
6. View session history: last 10 sessions

---

## Student Profile

Customize your academic identity (page 15):

- **Student name**: Used throughout the app
- **Grade level**: 20 options from Kindergarten through Post-Doctoral
- **Learning style**: Visual, Auditory, Reading, or Kinesthetic
- **Study pace**: Relaxed, moderate, or intensive
- **Academic Summary**: Rank, XP, GPA, Verified Credits
- **Study Streak**: Consecutive active days, last active date, streak XP bonus

---

## Statistics Dashboard

Activity analytics (page 16):

- **8 overview cards**: Study Hours, Lectures Done, Assignments, GPA, Courses, Verified Credits, Total XP, Activities
- **Daily Activity Chart**: Bar chart of activities per day (last 30 days, pandas DataFrame)
- **Activity Breakdown**: Event type counts
- **Grade Distribution**: A/B/C/D/F histogram

---

## Autonomous Agent

The Agent (page 17, Builder/Operator mode) executes multi-step tasks autonomously:

### Configuration
- **Execution Mode**: Bounded (fixed N steps) or Unlimited (until TASK_COMPLETE or TASK_BLOCKED)
- **Max Steps**: 5–200 (in bounded mode)
- **Review Mode**: Auto (execute immediately) or Review (queue tool calls for your approval)
- **Rate Limit**: 0–10 seconds between steps
- **Tool Categories**: Enable/disable course, video, utility, enrichment tool groups

### Creating a Task
1. Enter a detailed task description (e.g., "Create a course on molecular biology with 3 modules, enrich all narrations, then render all lectures")
2. Click **Launch Agent**
3. The agent thinks, selects tools, executes them, processes results, and repeats

### 22 Available Tools
The agent has access to 22 tools across 4 categories:
- **Course** (13 tools): create_course_outline, add_module, add_lecture, add_assignment, get_course_manifest, get_all_courses_summary, validate_and_import, search_courses, generate_quiz_for_lecture, decompose_course, generate_jargon_course, enrich_course_narration, advance_course_level
- **Video** (8 tools): list_scenes, edit_scene, add_scene, remove_scene, reorder_scenes, enhance_narration, render_lecture, batch_render_course
- **Utility** (1 tool): get_lecture_data

### Monitoring
- Progress bar and status text
- Live log of last 20 steps
- Abort button to stop mid-execution
- Full log viewable in expanded view

### Draft Queue (Review Mode)
When review mode is active:
- Each tool call is queued as a draft
- View tool name, description, argument JSON
- Click Approve or Reject for each

### Job History
- View past jobs with status, step count, task preview
- Resume paused jobs
- Delete completed/failed jobs

---

## Qualifications & Benchmarks

Track progress toward real-world academic equivalencies (page 18, Operator mode):

### Overview
- GPA, Verified Credits, Tracked Benchmarks count
- Activity credits and verified courses

### Qualification Progress
Each qualification shows:
- Status mark and progress percentage
- Description, school reference, category
- Progress bar toward completion
- Min GPA, Min Hours, Required Courses metrics

### Benchmark Comparison
Expandable section per qualification with 5 metrics:
- Coverage % (topics covered / total)
- Rigor % (difficulty alignment)
- Mastery % (demonstrated understanding)
- Assessment % (evaluation coverage)
- Gap topics (recommended remaining coursework)

### Roadmap
- Completed courses list
- Remaining course requirements
- Hours and GPA needs to reach qualification

### Refreshing Status
Click **Refresh Qualification Status** to re-evaluate all qualifications against current academic record.

---

## Settings Reference

Settings are organized in 7 collapsible sections (page 8):

### General
| Setting | Type | Description |
|---------|------|-------------|
| Student name | Text | Your display name throughout the app |
| Deadlines enabled | Toggle | Show countdown timers on assignments |
| Weekly Quests enabled | Toggle | Enable quest system on dashboard |

### LLM & AI
Shows current provider, model, and API key status. Links to LLM Setup Wizard for changes.

### Voice & Audio
| Setting | Type | Options |
|---------|------|---------|
| TTS Voice | Dropdown | 13 Microsoft Neural voices (Aria, Jenny, Amber, Emma, Guy, Brian, Davis, Andrew, Sonia, Ryan, Natasha, William, Clara) |
| Speaking Rate | Slider | -50% to +50% |
| Pitch | Slider | -50Hz to +50Hz |
| Preview Voice | Button | Generate and play sample |
| Binaural Preset | Radio | None, Gamma 40Hz, Beta 18Hz, Alpha 10Hz, Theta 6Hz |
| Preview Binaural | Button | Generate and play 10s sample |

### Video & Rendering
| Setting | Type | Options |
|---------|------|---------|
| Quality Profile | Dropdown | Draft, Balanced, High Quality, Final, Custom |
| FPS | Selector | 10, 15, 24, 30 |
| Resolution | Selector | 960×540, 1280×720, 1920×1080 |
| Render Engine | Selector | local, comfyui, free_cloud_mix, custom_api |

### Image Generation
API key inputs for all 10 image providers (password-masked).

### Course & Learning
| Setting | Type | Description |
|---------|------|-------------|
| Daily Token Target | Number | Target generation budget per day |
| Learning Preferences | Text area | Free-form learning style notes |

### Advanced
| Setting | Type | Options |
|---------|------|---------|
| Media Sharing Mode | Radio | private (your eyes only), course_shared (visible to course members), global (visible to all) |

---

## LLM Setup Wizard

Step-by-step provider configuration (page 11):

### Step 1: Choose Type
- **Local** (free, private, runs on your machine): Ollama or LM Studio
- **Cloud** (requires API key, faster for small GPUs): 7 providers

### Hardware Profile
Auto-detected: RAM, GPU VRAM, GPU name, free disk space → recommended model tier with reasoning.

### Local: Ollama
1. Install from ollama.com
2. The wizard auto-detects the Ollama service
3. Select a model from 5 tiers (Tiny 1-3B for 4GB RAM → XL 70B+ for 64GB RAM)
4. Pull models directly from the UI (async POST to `/api/pull`)
5. Save & Test button verifies connectivity

### Local: LM Studio
1. Install from lmstudio.ai
2. Start the local server (port 1234)
3. The wizard auto-detects the server
4. Enter model name → Save & Test

### Cloud Providers
Radio selector for 7 providers, each with:
- Cost information and free tier details
- Signup link
- API key input (password field)
- Model selector dropdown
- Base URL input (advanced)
- Save & Test button

### Provider Comparison
Expandable table comparing: type, cost, speed, quality, context window, best-for use case.

### Quick Switch
Pre-configured provider buttons for one-click switching between providers.

---

## Image Provider Setup

Configure AI image generation for video backgrounds:

1. Go to **Library** (page 1) → **Media Sources** tab
2. For each of the 9 cloud providers:
   - Enter API key
   - The system tests connectivity
3. **Pollinations** (default) works without any API key
4. Providers auto-cycle with fallback — if one fails, the next is tried automatically
5. Each generation attempt has a 30-second timeout

---

## Audio Configuration

### TTS Voices
13 Microsoft Neural voices via edge-tts:
- **Female**: Aria, Jenny, Amber, Emma, Sonia, Natasha, Clara
- **Male**: Guy, Brian, Davis, Andrew, Ryan, William

### Binaural Beats
Stereo presets for focus enhancement:
- **Gamma 40Hz**: Peak focus, learning
- **Beta 18Hz**: Active thinking, alertness
- **Alpha 10Hz**: Relaxed focus, creativity
- **Theta 6Hz**: Deep meditation, memory consolidation

### Audio Processing Pipeline
1. TTS generates speech audio (edge-tts → pyttsx3 fallback)
2. Binaural beats generated (stereo sine wave interference)
3. Ambient pads generated (additive synthesis: chord + tremolo + breathing)
4. All tracks mixed with separate volume controls
5. LUFS normalization + clipping detection + auto-gain
6. Output as stereo WAV → encoded into MP4

### Procedural SFX
8 built-in sound effects: click, success, unlock, error, xp_gain, level_up, page_turn, collect.

---

## Diagnostics & System Health

Comprehensive system check (page 9, Operator mode):

1. **Environment**: Python version, platform, processor, working directory, database size
2. **Dependencies**: 14 packages with version numbers + FFmpeg binary path
3. **Database Stats**: Courses, Modules, Lectures, Completed, Assignments, Graded, GPA, Credits, XP, Level
4. **LLM Provider Config**: Provider/Model/Base URL/API Key status + **Test Connection** button
5. **Audio Engine**: Voice/Rate/Pitch/Binaural preset + **Test TTS** button (generates test MP3)
6. **Video Engine**: Resolution, FPS
7. **Settings Dump**: Full settings with API keys masked (xxxx)
8. **Module Health**: `py_compile` on all Python files → [OK]/[ERROR] table
9. **Recent Errors**: JSONL error log with ID, Category, Message, Timestamp

---

## Help System

60+ contextual help topics (page 10):

- **Deep linking**: Navigate to any topic via URL: `?topic=anchor_name`
- **End-to-End Tutorial**: 6-step guide (AI Provider → Import Course → Study → Render → Track → Advanced)
- **19+ topic groups**: Getting Started, Dashboard, XP & Progression, Library, Lecture Studio, Professor AI, Timeline Editor, Batch Render, Grades, Achievements, Settings, LLM Setup, Diagnostics, Placement, Programs, Profile, Statistics, Agent, Qualifications
- **Sidebar Quick Links**: Jump to any group
- **Quick Reference Footer**: 3-column links for Getting Started, Academic Progress, Configuration & Tools

Every page has a `help_button()` in the UI that links directly to its relevant help topic.

---

## Backup & Restore

Database backup and restore (`core/university.py`):

- **Backup**: `backup_database(output_path)` creates a timestamped copy of `university.db`
- **Restore**: `restore_database(backup_path)` replaces the current database with a backup
- **List**: `list_backups()` shows all available backup files with timestamps and sizes

---

## One-Click Auto Pipeline

> **This section describes the automated pipeline available on page 19 (Auto Pipeline).**

The Auto Pipeline automates the most common multi-step workflows with a single click. Instead of manually navigating between pages and clicking through steps, the pipeline handles everything programmatically.

### Available Pipeline Presets

#### 1. Full Course Build
**Input**: Topic name, difficulty level, pacing (fast/standard/slow)
**Automation**:
1. Generate curriculum via Professor AI (Plan & Generate mode)
2. Enrich all lecture narrations (versioned)
3. Generate jargon sub-course
4. Render all lectures to MP4
**Output**: Complete course with enriched narration and rendered videos

#### 2. Deep Enrichment Cycle
**Input**: Select course(s)
**Automation**:
1. Enrich all narrations
2. Decompose into sub-courses
3. Generate jargon courses
4. Enrich sub-course narrations
5. Render all content
**Output**: Deep course tree with multiple enrichment levels

#### 3. Study Prep Package
**Input**: Select course
**Automation**:
1. Generate flashcards from all lectures
2. Generate quizzes for each lecture
3. Prepare study materials
**Output**: Complete study package ready for review

#### 4. Full Render Pipeline
**Input**: Select courses, quality profile
**Automation**:
1. Enrich narrations if not yet enriched
2. Configure VFX settings
3. Batch render all lectures
**Output**: All lectures rendered as MP4 videos

#### 5. Custom Pipeline
**Input**: Select which steps to include
**Automation**: Any combination of the above steps in user-defined order

### Pipeline Configuration
- **Pacing**: Fast (minimal delay) / Standard / Slow (with confidence building)
- **LLM Rate Limit**: Seconds between API calls
- **Auto-render**: Enable/disable video rendering
- **VFX Profile**: Quality preset for rendering
- **Target Courses**: All or specific selection

---

## Troubleshooting

### LLM Not Responding
1. Open **Diagnostics** (page 9) → run **LLM Connectivity Test**
2. Check **LLM Setup Wizard** (page 11) — is the provider configured and tested?
3. For Ollama: ensure `ollama serve` is running (check port 11434)
4. For LM Studio: ensure server is running (check port 1234)
5. For cloud providers: verify API key is valid and not expired
6. Check **Recent Errors** in Diagnostics for error details

### Video Render Fails
1. Check Diagnostics → Dependencies for missing packages (MoviePy, Pillow, imageio-ffmpeg)
2. Try "Draft (Fast)" quality profile first
3. Check disk space in the `exports/` directory
4. Run `pip install --force-reinstall imageio-ffmpeg` if FFmpeg issues
5. Run `pip install --upgrade Pillow` if black screen

### Import Fails
1. Ensure you're pasting raw JSON (not wrapped in markdown code fences)
2. Use `schemas/SCHEMA_GUIDE.md` as the format reference
3. Check for JSON syntax errors (missing commas, unbalanced brackets)
4. Use `schemas/course_validation_schema.json` for automated validation

### No AI Backgrounds
1. Go to **Library** → **Media Sources** tab
2. Configure at least one image provider API key
3. Or ensure Pollinations is reachable (requires internet, no key needed)
4. Check the "Enable AI-generated backgrounds" toggle in VFX settings
5. Check Diagnostics for image provider errors

### Scribe Credit Issues
1. Minimum 10,000 words per course required
2. Originality check may reject copy-pasted content (needs vocabulary diversity + sentence variation)
3. Check word count in Lecture Studio → Scribe Credit section

### Agent Issues
1. Check that an LLM provider is configured and working
2. Try bounded mode with 20 max steps before unlimited
3. Increase rate limit if hitting API rate limits
4. Check that required tool categories are enabled in sidebar config
5. Review draft queue if using review mode (drafts may be waiting for approval)

### Audit Problems
1. Ensure LLM connectivity is working
2. Check that the course has content to audit
3. Review model profile settings
4. Check remediation backlog for stuck items

### Database Issues
If data seems corrupted or database is locked:
1. Close **all** browser tabs using the app
2. Delete `university.db`, `university.db-wal`, and `university.db-shm`
3. Re-run the app (database will be recreated from scratch)
4. Or use **Backup/Restore** to recover from a previous backup

### Performance Issues
1. Low GPU VRAM: Use smaller LLM models (Tiny or Small tier)
2. Slow rendering: Reduce resolution and FPS, use Draft quality profile
3. High API costs: Use free-tier providers (Groq, GitHub Models, Pollinations)
4. Rate limiting: Increase rate limit delay in continuous enrichment settings
