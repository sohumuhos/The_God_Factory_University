# The God Factory University

An AI-powered university built with Python and Streamlit. Generates animated lecture videos with neural narration, binaural beats, and a dark-academic theme. Features a Professor AI advisor, grading system with GPA/degrees, achievements, 24/7 continuous enrichment, and support for 10 LLM providers and 10 image providers.

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

## All 18 Pages

| # | Page | Purpose |
|---|------|---------|
| — | **Dashboard** (`app.py`) | System health, XP/level, recent activity, quick links |
| 1 | **Library** | Browse/import courses (JSON, CSV), media source setup, course tree |
| 2 | **Lecture Studio** | Watch lectures, render video, submit assignments, scribe notes |
| 3 | **Professor AI** | Chat, generate curricula, grade work, create quizzes, research |
| 4 | **Timeline Editor** | Reorder scenes, adjust durations, export scene data |
| 5 | **Batch Render** | Queue lectures for rendering, VFX settings, 24/7 continuous enrichment |
| 6 | **Grades** | GPA calculation, degree progress (Certificate→Doctorate), transcript PDF |
| 7 | **Achievements** | XP system, 10 ranks (Seeker→Archon), 17 milestone badges |
| 8 | **Settings** | Voice, binaural, video quality, deadlines, learning preferences |
| 9 | **Diagnostics** | System health checks, dependency versions, LLM connectivity test |
| 10 | **Help** | 87 contextual topics, end-to-end tutorial, grouped by section |
| 11 | **LLM Setup Wizard** | Step-by-step provider configuration with auto-detection |
| 12 | **Placement** | Adaptive placement tests to determine starting level |
| 13 | **Test Prep** | Practice for GED, SAT, ACT, GRE with timed sessions and scoring |
| 14 | **Programs** | Structured degree programs and academic pathways |
| 15 | **Profile** | Student identity, grade level, learning style, study pace |
| 16 | **Statistics** | Charts: daily activity, grade distribution, study hours, XP trends |
| 17 | **Agent** | Autonomous task execution: bulk course creation, multi-step workflows |
| 18 | **Qualifications** | Track progress toward real-world benchmark equivalencies |

---

## Key Features

### AI Course Generation
Generate complete courses from any topic. The Professor AI creates curricula with modules, lectures, learning objectives, video recipes, and assignments. Courses can be decomposed into sub-courses for deeper learning.

### Video Lecture Rendering
Lectures are rendered as MP4 videos with:
- Neural TTS narration (13 voice options via edge-tts)
- AI-generated or gradient backgrounds (10 image providers)
- Scene transitions, Ken Burns effect, text overlays, ambient particles
- Binaural beats (gamma, beta, alpha, theta presets)

### 24/7 Continuous Enrichment
Automated loop that enriches course content over time:
1. **Enrichment**: Rewrites narration to be richer and more educational
2. **Decomposition**: Splits courses into granular sub-courses
3. **Jargon courses**: Generates terminology mastery courses
4. **Level advancement**: Progresses to more sophisticated content

All enrichments are versioned — prior narration is never lost.

### Grading & Degrees
Full academic tracking: GPA calculation, letter grades, degree progress from Certificate through Doctorate, transcript PDF export, and credit hour tracking.

### Gamification
XP system with 10 progression ranks, 17 achievement badges, streak tracking, weekly quests, and level-up notifications.

---

## LLM Provider Support

| Provider | Type | Cost | Setup |
|----------|------|------|-------|
| Ollama | Local | Free | Install from ollama.com |
| LM Studio | Local | Free | Install from lmstudio.ai |
| Groq | Cloud | Free tier | console.groq.com |
| GitHub Models | Cloud | Free | GitHub PAT |
| OpenAI | Cloud | Paid | platform.openai.com |
| Anthropic | Cloud | Paid | console.anthropic.com |
| Mistral | Cloud | Free tier | console.mistral.ai |
| Together AI | Cloud | Free $5 | api.together.xyz |
| HuggingFace | Cloud | Free tier | huggingface.co |
| Cohere | Cloud | Free trial | dashboard.cohere.com |

All providers support timeout (60s), retry with exponential backoff, and streaming where available.

## Image Provider Support

| Provider | Cost | Notes |
|----------|------|-------|
| Pollinations | Free | Priority 1 (default) |
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

## Project Structure

```
app.py                      Main dashboard / entry point
core/
  database.py               SQLite persistence (WAL mode, facade pattern)
  settings_registry.py      Centralized settings registry (30+ keys)
  continuous_engine.py      24/7 enrichment loop with versioning
  help_registry.py          87 contextual help entries
  content_log.py            Content generation tracking
  decomposition.py          Course decomposition and pacing
  asset_library.py          Generated asset caching and reuse
  app_docs.py               Professor-readable app documentation
llm/
  providers.py              Universal LLM client (10 providers, retry, timeout)
  professor.py              Professor AI (combines base + content + workflow mixins)
  professor_base.py         Chat, history, truncation
  professor_content.py      Curriculum, quiz, homework, grading with validation
  professor_workflows.py    Decomposition, jargon, plan-and-generate
  agent.py                  Autonomous agent with tool execution
  generation_queue.py       Background generation with backoff
media/
  audio_engine.py           TTS, binaural beats, ambient pads
  video/
    encoder.py              Video encoding with VFX pipeline
    frame_renderer.py       Scene frame generation
    scene_builder.py        Scene block orchestration
  diffusion/
    free_tier_cycler.py     10-provider image generation with fallback
ui/
  theme.py                  Dark-academic CSS theme, help buttons, SFX
pages/
  01-18                     All application pages (see table above)
schemas/
  course_schema.json        Example course JSON
  SCHEMA_GUIDE.md           Prompt guide for LLM course generation
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

**Video render fails**: FFmpeg is bundled via `imageio-ffmpeg` -- no system install needed. If issues persist, check `pip show imageio-ffmpeg`.

**LLM not responding**: Use the LLM Setup Wizard (page 11) or Diagnostics (page 9) to test connectivity. For local models, make sure Ollama or LM Studio is running.

## Requirements

- Python 3.9+
- Internet connection (for TTS and cloud LLM providers)
- 8GB+ RAM recommended for local LLM models
- All other dependencies installed automatically via `requirements.txt`

## License

This project is provided as-is for educational purposes.
