# The God Factory University — Usage Guide

A complete guide to using every feature of the application.

---

## Getting Started

### First Launch

1. Run the setup script for your OS (see README.md)
2. The browser opens to the **Dashboard** at `http://localhost:8501`
3. The dashboard shows system health, XP/level, and quick links

### Configure Your AI Provider

Before using AI features, set up an LLM provider:

1. Go to **LLM Setup Wizard** (page 11)
2. Choose **Local** (Ollama or LM Studio — free, runs on your machine) or **Cloud** (requires API key)
3. For the fastest free start: install [Ollama](https://ollama.com), run `ollama pull llama3.2`
4. The wizard auto-detects your setup and tests the connection

### Setting Up Image Providers

For AI-generated video backgrounds:

1. Go to **Library** → **Media Sources** tab
2. Enter API keys for any image providers you want to use
3. Pollinations works without a key and is the default

---

## Creating Courses

### Option A: Import Existing JSON

1. Go to **Library** → expand **BULK IMPORT**
2. Paste course JSON (see `schemas/SCHEMA_GUIDE.md` for the format)
3. Click Import — courses, modules, and lectures appear instantly

**Tip**: Copy `schemas/SCHEMA_GUIDE.md` and paste it into any LLM (ChatGPT, Claude, etc.) and ask it to generate a course on your topic. Then paste the JSON output into the import box.

### Option B: AI-Generate a Course

1. Go to **Professor AI** → **Generate Curriculum** tab
2. Enter a topic (e.g., "Introduction to Machine Learning")
3. Choose difficulty level and number of lectures per module
4. Click Generate — the AI creates a complete course structure
5. Review the generated curriculum and click Import

### Option C: Agent-Generated Courses

1. Go to **Agent Dashboard** (page 17)
2. Create a job like "Create a full course on quantum computing with 4 modules"
3. The agent autonomously creates the course using tools

---

## Enrichment vs Decomposition

### Enrichment
**What it does**: Rewrites lecture narrations to be richer, more detailed, and truly educational.

**When to use**: After generating a course, the initial narration is often generic. Enrichment rewrites it with real examples, definitions, and step-by-step explanations.

**How**: 
- One-time: In Batch Render, check "Enrich narration with LLM before rendering"
- Continuous: Use the 24/7 Continuous Enrichment section in Batch Render
- Via Agent: The agent can call `enrich_course_narration` tool

### Decomposition
**What it does**: Splits a course into deeper sub-courses for more granular learning.

**When to use**: When a course covers broad topics and you want to go deeper into each area.

**How**:
- In Professor AI → Generate Curriculum tab → "Decompose Existing Course" mode
- Via Agent: The agent can call `decompose_course` tool

### Jargon Courses
**What it does**: Extracts key terminology from a course and creates a focused vocabulary sub-course.

**When to use**: When studying a field with specialized vocabulary (medicine, law, computer science, etc.).

**How**:
- In Professor AI → Generate Curriculum tab → "Generate Jargon Course" mode
- Via Agent: The agent can call `generate_jargon_course` tool

---

## 24/7 Continuous Enrichment Mode

The continuous enrichment engine runs an automated loop:

1. Go to **Batch Render** → scroll to **24/7 Continuous Enrichment**
2. Select a target course (or "All Courses")
3. Configure cycle parameters:
   - **Enrichments before decompose**: How many enrichment passes before triggering decomposition (default: 3)
   - **Decompositions before level advance**: How many decompositions before advancing the education level (default: 2)
   - **Jargon per cycle**: Jargon courses generated per decomposition cycle (default: 1)
   - **Rate limit**: Seconds between LLM calls (default: 2.0)
   - **Auto-render**: Render video after each enrichment cycle
4. Click **Start Continuous Enrichment**
5. Monitor the live progress display
6. Click **Stop** when ready

**Versioning**: Every enrichment saves a version. Prior narration is never lost.

---

## Rendering Video Lectures

### Single Lecture
1. Go to **Lecture Studio** → select a course, module, and lecture
2. Click **Render Full Lecture**
3. The system generates TTS audio, animates visuals, and encodes to MP4
4. Watch the video directly in the browser

### Batch Render
1. Go to **Batch Render**
2. Filter by course, difficulty, or date
3. Select lectures to render
4. Choose FPS and resolution
5. Optionally check "Enrich narration" for first renders
6. Click **Start Batch Render**

### Visual Effects
Configure in the **Visual Effects** section of Batch Render or Lecture Studio:
- AI-generated backgrounds (toggle on/off, choose provider)
- Scene transitions (crossfade)
- Ken Burns pan/zoom on stills
- Cinematic color grading
- Title/term text overlays
- Ambient particle effects
- Watermark/branding

---

## Studying with the Professor

### Chat
Ask the Professor AI any question. It uses Socratic method to guide understanding.

### Quizzes
1. Go to **Professor AI** → **Create Quiz** tab
2. Select a lecture
3. The AI generates quiz questions testing comprehension
4. Submit answers for instant grading

### Grading Work
1. Go to **Professor AI** → **Grade Work** tab
2. Paste your essay or code
3. The AI provides feedback, scores, and suggestions

### Research Rabbit Hole
1. Go to **Professor AI** → **Research Rabbit Hole** tab
2. Enter a topic to explore deeply
3. The AI generates a research chain, diving deeper at each step

---

## Settings

Settings are organized in collapsible sections (page 8):

| Section | What it controls |
|---------|-----------------|
| **General** | Student name, deadlines, weekly quests |
| **LLM & AI** | Current provider (edit in LLM Setup) |
| **Voice & Audio** | TTS voice (13 options), speaking rate, pitch, binaural beats |
| **Video & Rendering** | Quality profile, FPS, resolution, render engine |
| **Image Generation** | Quick access to image provider API keys |
| **Course & Learning** | Daily token target, learning preferences |
| **Advanced** | Media sharing mode |

---

## Troubleshooting

### LLM Not Responding
1. Open **Diagnostics** (page 9) → run LLM Connectivity Test
2. Check **LLM Setup Wizard** (page 11) — is the provider configured?
3. For Ollama: ensure `ollama serve` is running
4. For cloud providers: verify API key is valid

### Video Render Fails
1. Check Diagnostics for missing dependencies (MoviePy, Pillow, imageio-ffmpeg)
2. Try "Draft (Fast)" quality profile first
3. Check disk space in the `exports/` directory

### Import Fails
1. Ensure you're pasting raw JSON (not wrapped in markdown code fences)
2. Use `schemas/SCHEMA_GUIDE.md` as the format reference
3. Check for JSON syntax errors (missing commas, brackets)

### No AI Backgrounds
1. Go to Library → Media Sources tab
2. Configure at least one image provider API key
3. Or enable Pollinations (works without a key)
4. Check the "Enable AI-generated backgrounds" toggle in VFX settings

### Database Issues
If data seems corrupted:
1. Close all browser tabs using the app
2. Delete `university.db`, `university.db-wal`, and `university.db-shm`
3. Re-run the app (database will be recreated)
