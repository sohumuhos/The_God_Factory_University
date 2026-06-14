# Video Rendering — Phase 1 Fixes & Phase 2 Plan

**Date:** 2026-06-13
**Scope:** Output quality of the video renderer (`media/video/*`, render pages).
**Method:** Diagnosed against source, then **rendered real frames/MP4s and visually
inspected them** (standalone PIL harness + full moviepy/ffmpeg pipeline) — iterating
until the output looked and sounded correct.

This was approved as **phased: fix the current renderer first, then the overhaul.**
Phase 1 (below) is implemented and verified. Phase 2 is planned.

---

## 1. What the output actually looked like (baseline)

Rendering a frame with an **AI background** revealed the core problem: the HUD was
tuned for a near-black gradient, so over a real image it self-destructed —

- **Opaque scan-lines.** `draw.line(..., fill=(0,0,0,30))` on an RGB image: PIL
  *ignores the alpha*, so every 4th row was painted **solid black**, shredding and
  darkening the whole image (invisible on the dark gradient, brutal on a photo).
- **HUD chrome covered the subject.** A full-width animated **waveform strip** sat
  across the middle of the image, plus drifting **particles**, **keyword chips**, a
  header bar, timers and a border — all composited on top of the picture.
- **Unreadable captions.** White narration text was drawn directly over a bright
  image with no scrim.
- **Ken Burns zoomed the entire HUD**, not just the image, so text/border drifted.

The **gradient** (no-image) path, by contrast, looked clean and intentional — proving
the HUD was simply never adapted for image backgrounds.

(Frames captured during this work; the gradient frame was coherent, the AI-background
frame was a striped, cluttered mess.)

---

## 2. Phase 1 fixes (implemented + verified)

### `media/video/frame_renderer.py` — visuals
- New `_ken_burns_bg()`: pan/zoom is applied to the **background image only** (kept
  in-bounds), leaving the composited HUD crisp and stable.
- New `_scrim()`: blends a translucent dark band behind the header and caption so
  light text stays legible over any image (PIL can't alpha-fill RGB directly).
- `make_frame` now branches **cinematic (image present)** vs **dashboard (gradient)**:
  - Scan-lines: the broken opaque draw is gone. Dashboard mode gets a *real* subtle
    darkening of alternate rows (numpy); cinematic mode gets **none**.
  - Particles and the waveform strip: **dashboard mode only** (they cluttered images).
  - Header: scrim in cinematic, solid bar in dashboard.
  - Caption: dark scrim behind the text in cinematic; width constrained to a readable
    column; chars-per-line estimated from real glyph width instead of font height.
  - Ken Burns moved off the whole-frame composite (see above).

### `media/video/scene_builder.py` — audio, timing, narration
- **Duration tracks the narration**: `dur = max(tts_dur + 0.6, 3.0)` instead of
  `max(tts_dur, target_dur)` → no trailing dead air, no cut-off words.
- **Removed the magic 30s fallback.** A broken/empty TTS now logs `TTS_EMPTY` and
  falls back to the target length with a *silent* track, instead of silently padding
  every failed scene to 30s.
- **Audio mix degrades gracefully**: each layer is added in its own try/except, so a
  bad ambient/binaural layer no longer silently drops *all* music, and the old
  double-open-on-failure crash path is gone. Audio is cleanly omitted if no usable
  layer exists. Music beds nudged up slightly (ambient .35→.40, binaural .20→.22).
- `build_scene_clip()` gained `width/height/fps` params and enforces **even
  dimensions** (H.264/yuv420p requirement).
- `_build_narration_script()`: enriched-narration threshold 50→30 words (so good
  narration passes through instead of being smothered in template filler), and a
  **length cap** (~`target_words*1.6`, trimmed to a sentence boundary) stops short
  scenes ballooning into minutes of repetitive filler.

### `media/video/encoder.py` — resolution, encode, abort
- Resolution + fps resolved **once**, honoring explicit `width/height` args (this is
  what makes the Batch Render resolution picker actually work — see below), with
  even-dimension enforcement; the values flow into both AI-image sizing and
  `build_scene_clip`.
- Encode params now include **`-pix_fmt yuv420p`** (broad player compatibility) and
  **`-crf 20`** (controlled quality/size); preset `fast`→`medium`.
- New optional `should_continue` callback, checked between scenes, so a render can be
  aborted mid-lecture.

### `pages/05_Batch_Render.py`
- The **Resolution dropdown was a no-op** (`render_lecture` ignored `width/height`).
  Now wired through (fixed in the encoder) and the **Abort** button passes a
  `should_continue` callback so it halts at the next scene boundary, not just between
  lectures.

### `pages/04_Timeline_Editor.py`
- **Duration overrides were silently ignored**: the editor wrote `duration_override_s`
  but the renderer only reads `duration_s`. New `_apply_overrides()` translates them
  (0 = keep original) for both Render and Export.
- Fixed the scene preview reading non-existent keys (`ambiance_prompt`/
  `narration_script` → `visual_prompt`/`narration_prompt`).

---

## 3. Verification (real renders, looked at directly)

Set up a Python 3.14 venv; the pinned deps predate 3.14 wheels, so installed working
versions (numpy 2.4, Pillow 12, **moviepy 1.0.3** + bundled ffmpeg v7.1).

- **Visual harness** (numpy+PIL, no moviepy): rendered `frame_renderer` frames to PNG
  for both modes at t=start/mid/end. Confirmed the baseline problems, then confirmed
  the cinematic frame is now clean (image fills frame, readable scrimmed caption, no
  scanline/waveform/particle clutter) and the dashboard frame is unchanged-good.
- **Full pipeline**: rendered real MP4s through `render_lecture`. Confirmed:
  - Video `h264 / yuv420p / 960x540`, Audio `aac / 44100 Hz / stereo` **present and
    synced**; container duration == narration length (no dead air).
  - Cinematic path composites a real background cleanly end-to-end.
  - The narration cap cut a 2-scene test from **108s → 62s** (the residual is the
    deliberate 50-word/scene minimum, not filler).
- `pytest tests/test_audio.py tests/test_output_paths.py` → **16 passed**.

---

## 4. Accuracy notes (claims that did NOT hold up)

During diagnosis several plausible-sounding bugs were checked against source and
**disproved** — recorded so they aren't "re-fixed":

- *Ken Burns negative-offset frame corruption* — false: `0.5 + 0.5*sin(...)` ∈ [0,1],
  offsets stay in bounds.
- *`measure_rms_lufs` dtype bug* — false: it checks the original dtype correctly.
- *Metadata written on 0 outputs* — false: `render_lecture` returns before metadata.
- *`synth_tts` always overwrites edge-TTS with pyttsx3* — false: pyttsx3 only on
  fallback.
- *VFX-config key mismatch / image-provider key mismatch / visual-prompt text overlay*
  (old `FULL_AUDIT_2026_04_02.md` items 2a/2d/2e) — already fixed in current code.

---

## 5. Known remaining limitations (candidates for Phase 2)

- Music/binaural beds are intentionally quiet; `normalize_loudness`/`auto_gain` exist
  but aren't wired into the final mix.
- The pyttsx3 path hardcodes 165 wpm (ignores rate/pitch); edge-TTS (primary) honors
  them.
- A ~50-word/scene narration floor keeps even very short scenes ≥ ~18s.
- Abort stops between scenes, but can't yet kill an in-flight ffmpeg encode of a
  single scene (needs subprocess management).
- Diffusion providers report `is_available()` optimistically and do only minimal
  validation of returned bytes.

---

## 8. Phase 2c — humanlike voice + hybrid slide-and-image (2026-06-13)

Two follow-ups requested after reviewing the slides ("can the voice be humanlike?
where are the images/figures?"). Both implemented and verified.

### Humanlike voice (TTS) — `media/tts_providers.py`, `media/audio_engine.py`
- **Root-cause bug fixed.** `tts_providers.py` did `import importlib` but called
  `importlib.util.find_spec(...)` — `importlib.util` is **not** auto-loaded as an
  attribute, so in a clean process `get_available_engines()`/`synth_with_cycling()`
  raised `AttributeError` immediately. `synth_tts` swallowed it and limped along on a
  legacy direct-edge-tts path, meaning the **multi-engine cycler (Kokoro / ElevenLabs /
  preferred-engine setting) was effectively unreachable.** Now `import importlib.util`.
  Verified: the cycler lists `[edge_tts(10), pyttsx3(99)]` and selects **edge_tts**.
- **Diagnostics.** `synth_tts` now logs the engine actually used (`tts_engine_used=…`);
  a fall-through to `pyttsx3` logs a WARNING explaining how to get a natural voice. This
  makes "why is it robotic?" answerable from `logs/university.log`.
- The robotic voice was only ever the **offline last-resort** (`pyttsx3`, priority 99).
  With `edge-tts` installed + internet, Microsoft neural voices (Aria/Guy/Ryan/…) are
  used automatically. Verified end-to-end: a 6.0s neural MP3 (en-GB-RyanNeural, +8%).
- For the **most** humanlike: set `elevenlabs_api_key`. Fully **offline-natural**: Kokoro
  (local neural, priority 1, auto-installs). No code change needed — the cycler now picks
  them correctly once available.

### Hybrid slide + AI image — `diagram_renderer.py`, `encoder.py`
The "figures" are the programmatic slides; AI diffusion images are separate and only
appeared when `ai_backgrounds=True` **and** a provider returned bytes. Previously a scene
was *either* a slide *or* a full-bleed diffusion image. Now they combine:

- `render_scene_slide(..., inset_image=…)` composites an AI picture into a slide as a
  **framed inset** (gold border + shadow): two-column when the slide has bullets, a single
  large centered figure when it has only a heading. Charts/flow-diagrams ignore the inset.
- `encoder.render_lecture` reordered into three steps: (1) generate AI images for any scene
  with a `visual_prompt`; (2) render the default slide for every non-`diffusion`/`gradient`
  scene, passing the generated image as the inset (the **hybrid** look); (3) only an
  explicit `render_mode:"diffusion"` scene gets the old full-bleed cinematic background.
- **Degrades cleanly:** if diffusion is off / unconfigured / rate-limited, the inset is
  simply absent and the slide alone renders — a figure is never required. So figures now
  show up *whenever* a provider works, without ever risking a blank/broken scene.
- Verified: rendered hybrid slides (bullets+inset, figure-only, auto-derived bullets,
  no-image fallback) and a real MP4 through the encoder with diffusion mocked — the framed
  image appears beside the bullets in the actual video frame. `schemas/SCHEMA_GUIDE.md`
  updated (hybrid behavior + `"diffusion"` = full-bleed opt-in).

**Reference scan.** Surveyed GitHub `topics/video-generator` (short-video-maker,
ContentMachine, the Reddit/Shorts TTS auto-uploaders, MoCoGAN/ConsisID/Helios). Takeaways:
the popular tools are *short-form social* pipelines (TTS + stock/AI clips + **burned-in
word-by-word captions** via Whisper timestamps), and the research repos are GPU
text-to-video models — neither fits a local, deterministic, offline-first lecture renderer.
The one genuinely portable idea is **forced-alignment captions** (Whisper/aeneas word
timings → on-beat subtitle highlighting) to replace our heuristic typewriter reveal; logged
as a future option, not adopted now (adds a heavy optional dep).

---

## 7. Phase 2 — status (kicked off + MVP implemented, 2026-06-13)

The programmatic-visuals MVP is **implemented and verified** (rendered slide MP4s and
inspected the frames). New module `media/video/diagram_renderer.py` (PIL only, no
network) renders clean, topic-accurate slides:

- `render_mode: "bullets"|"concept"` — heading + gold-marker bullet list.
- `render_mode: "diagram"` — left→right flow of labelled rounded boxes + arrows.
- `render_mode: "chart"` — simple labelled bar chart.

Pipeline wiring:
- `encoder.render_lecture` runs a **slide pre-pass** (programmatic modes take priority
  over diffusion); `gradient` forces the dashboard; everything else is unchanged.
- `frame_renderer` gained a `static_bg` path: a slide is used as-is (no Ken Burns,
  no duplicate header/border/chips/waveform/particles), with the live narration drawn
  as a **bottom subtitle** over a scrim.
- Backward compatible: a missing `render_mode` keeps the existing diffusion/gradient
  behavior — no migration needed (graceful `.get()` defaults), so the formal
  `schema_version`/migration framework is deferred until a breaking field change.
- Schema documented in `schemas/SCHEMA_GUIDE.md`.

Audio caveats addressed: the pyttsx3 fallback now honors the configured rate, and the
final per-scene mix is loudness-normalized for consistent levels.

**Slides are now the DEFAULT for any subject (no regeneration needed).** A scene with
no `render_mode` automatically gets a clean, topic-accurate slide — *unless* the user
has AI backgrounds on with a `visual_prompt` (then diffusion wins) or sets
`render_mode: "gradient"`/`"diffusion"`. Auto content is derived per-scene from the
lecture's core terms → objectives → narration sentences, so it works for recursion,
the French Revolution, the scientific method, or GDP-by-sector alike. Verified by
rendering slides across CS / history / science / chemistry / economics, including
long headings, long bullet lines, and long diagram labels (all wrap/shrink/truncate
to fit). Generation (`enhance_video_prompts`) now also asks the LLM to assign a
`render_mode` + `visual` per scene for richer diagrams/charts.

**Still to do** (next Phase 2 steps):
- More modes (number line, code card, multi-row diagrams); optional Matplotlib/Manim.
- Have the main `generate_curriculum` schema emit `render_mode`/`visual` directly (not
  just the enhancement pass), so first-generation lectures ship with tailored visuals.
- Harden diffusion provider availability + image-bytes validation; audio crossfades.

The original plan below remains the north star.

## 6. Phase 2 — Hybrid programmatic visuals (planned)

Extends the direction approved in `FULL_AUDIT_2026_04_02.md` §6. The remaining quality
ceiling is the *content* of the picture: diffusion backgrounds are generic and
disconnected from the lecture, and the HUD, however clean now, is still a HUD.

1. **Per-scene render modes.** Add a `render_mode` to scene blocks:
   `diagram | chart | equation | timeline | code | diffusion | gradient`.
2. **Deterministic renderers** (no external services, on-theme): Matplotlib/PIL/SVG
   for charts, labeled diagrams, number lines, code walkthroughs, equations
   (and optionally Manim for animated builds). These are precise and topic-accurate —
   better than diffusion for instructional visuals — and compose into the existing
   `scene_builder`/`encoder` integration points.
3. **Diffusion stays optional**, for illustrative/painterly scenes only, behind the
   same fallback cycler. Harden provider availability + image-bytes validation.
4. **Schema versioning + migrations** (`schema_version`, `v1_to_v2`, …) so new scene
   fields roll out without breaking existing lectures; extend `schemas/SCHEMA_GUIDE.md`.
5. **Audio polish**: wire loudness normalization into the final mixed track; proper
   audio crossfades at scene joins.

MVP: schema version + migration framework → one programmatic diagram renderer →
route `render_mode` through `encoder`/`scene_builder`.
