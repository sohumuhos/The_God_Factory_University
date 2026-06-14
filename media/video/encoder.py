"""Encoder — final rendering, batch export, timeline support."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Callable

from core.database import get_setting, unlock_achievement, add_xp
from core.logger import log_render, log_error
from core.tts_config import get_tts_settings
from media.output_paths import (
    get_full_video_path,
    get_scene_video_path,
    get_video_cache_dir,
    write_render_metadata,
)
from media.video.scene_builder import build_scene_clip, load_vfx_config, assemble_clips

CACHE_DIR = get_video_cache_dir()


def _slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def render_lecture(lecture_data: dict, output_dir: Path, chunk_by_scene: bool = False,
                   fps: int | None = None, width: int | None = None, height: int | None = None,
                   suffix: str = "", output_mode: str = "full",
                   should_continue: Callable[[], bool] | None = None) -> list[Path]:
    """Render a lecture to one (or more) MP4 files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _render_t0 = time.time()
    lid = lecture_data.get("lecture_id", lecture_data.get("id", "lec"))
    temp_dir = CACHE_DIR / f"{lid}_{_slug(lecture_data.get('title', 'lecture'))}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    tts_settings = get_tts_settings()
    scenes = lecture_data.get("video_recipe", {}).get("scene_blocks", [])

    # Resolve output resolution + fps ONCE. Explicit args (e.g. the Batch Render
    # resolution picker) win over settings; even dimensions are required by H.264.
    actual_fps = fps or int(get_setting("video_fps", "15"))
    res_w = int(width) if width else int(get_setting("video_width", "960"))
    res_h = int(height) if height else int(get_setting("video_height", "540"))
    res_w -= res_w % 2
    res_h -= res_h % 2

    if not scenes:
        scenes = [{
            "block_id": "A",
            "duration_s": lecture_data.get("duration_min", 5) * 60,
            "narration_prompt": f"This lecture covers {lecture_data.get('title', 'the topic')}. "
                                f"We will explore: {', '.join(lecture_data.get('learning_objectives', [])[:3])}.",
            "visual_prompt": f"Educational explainer for {lecture_data.get('title', 'lecture')}.",
            "ambiance": {"music": "ambient", "sfx": "gentle", "color_palette": "cyan and dark"},
        }]

    # ── Resolve AI-background availability ───────────────────────────────────
    bg_images: dict[str, "Image.Image | None"] = {}
    static_bids: set[str] = set()
    # AI images keyed by block_id. Each becomes either a framed inset inside a
    # programmatic slide (the hybrid default) or — for explicit render_mode
    # "diffusion" scenes — a full-bleed cinematic background.
    ai_images: dict[str, "Image.Image"] = {}
    try:
        from media.video.scene_builder import load_vfx_config as _load_vfx
        _vfx_cfg = _load_vfx()
        _ai_bg_enabled = _vfx_cfg.get("ai_backgrounds", True)
    except Exception:
        _vfx_cfg = {}
        _ai_bg_enabled = True

    # ── Step 1: generate AI images for any scene with a visual_prompt ─────────
    # These are produced up front so the slide pass below can composite them as
    # insets. If a provider is missing / rate-limited the dict simply stays empty
    # and the slides render clean and figure-less — diffusion is never required.
    if _ai_bg_enabled:
        try:
            from media.diffusion.free_tier_cycler import generate_image_with_fallback
            from PIL import Image
            _preferred_prov = (
                _vfx_cfg.get("preferred_image_provider", "")
                or get_setting("image_provider", "Auto (priority order)")
            )
            # Context prefix so diffusion images match the lecture subject.
            _ctx_title = lecture_data.get("title", "")
            _ctx_course = lecture_data.get("course_title", "")
            if _ctx_course and _ctx_title:
                _ctx_prefix = f"{_ctx_course}: {_ctx_title} — "
            elif _ctx_title:
                _ctx_prefix = f"{_ctx_title} — "
            else:
                _ctx_prefix = ""
            gen_count = 0
            for scene in scenes:
                bid = scene.get("block_id", "?")
                _mode = str(scene.get("render_mode", "")).lower()
                visual = scene.get("visual_prompt", "")
                if _mode == "gradient":
                    continue  # gradient scenes never want an image
                if not visual or "title card" in visual.lower():
                    continue
                try:
                    img_path, prov_name = generate_image_with_fallback(
                        _ctx_prefix + visual, res_w, res_h,
                        course_id=lecture_data.get("course_id", ""),
                        lecture_id=lid,
                        preferred_provider=_preferred_prov if _preferred_prov != "Auto (priority order)" else "",
                    )
                    if img_path and img_path.exists():
                        ai_images[bid] = Image.open(img_path).convert("RGB")
                        gen_count += 1
                        log_render(lid, "img_gen_ok", scene=bid, provider=prov_name)
                    else:
                        log_render(lid, "img_gen_miss", scene=bid,
                                   reason="all_providers_returned_none")
                except Exception as img_err:
                    log_error(f"Image gen failed for scene {bid}: {img_err}",
                              category="diffusion", error_id="IMG_GEN_FAIL")
            log_render(lid, "img_gen_done", generated=gen_count, total=len(scenes))
        except ImportError:
            log_render(lid, "img_gen_skip", reason="diffusion_not_installed")
    else:
        log_render(lid, "img_gen_skip", reason="ai_backgrounds_disabled")

    # ── Step 2: programmatic slides — the default visual for any subject ──────
    # Every scene that isn't an explicit "diffusion"/"gradient" gets a clean,
    # topic-accurate slide. When an AI image exists for that scene it is
    # composited into the slide as a framed inset (the hybrid slide+image look),
    # so a real figure shows up when diffusion works and the slide alone is the
    # reliable fallback when it doesn't. No regeneration needed for any topic.
    try:
        from media.video.diagram_renderer import render_scene_slide
        for idx, scene in enumerate(scenes):
            bid = scene.get("block_id", "?")
            mode = str(scene.get("render_mode", "")).lower()
            if mode in ("diffusion", "gradient"):
                continue
            inset = ai_images.get(bid)
            slide = render_scene_slide(scene, lecture_data, res_w, res_h,
                                       scene_index=idx, inset_image=inset)
            if slide is not None:
                bg_images[bid] = slide
                static_bids.add(bid)
                log_render(lid, "slide_ok", scene=bid, mode=mode or "auto",
                           hybrid=bool(inset))
            elif inset is not None:
                # No slide content but we do have an image → full-bleed cinematic.
                bg_images[bid] = inset
                log_render(lid, "img_fullbleed", scene=bid)
            else:
                log_render(lid, "slide_empty", scene=bid, mode=mode or "auto")
    except Exception as e:
        log_error(f"Slide render failed: {e}", category="render", error_id="SLIDE_FAIL")

    # ── Step 3: explicit full-bleed diffusion scenes (Ken Burns + HUD) ───────
    for scene in scenes:
        bid = scene.get("block_id", "?")
        mode = str(scene.get("render_mode", "")).lower()
        if mode == "diffusion" and bid not in bg_images and bid in ai_images:
            bg_images[bid] = ai_images[bid]  # not in static_bids → cinematic path

    clips: list[tuple[dict, "VideoClip"]] = []
    failed_scenes: list[str] = []
    total_scenes = len(scenes)
    for scene_idx, scene in enumerate(scenes):
        if should_continue is not None and not should_continue():
            log_error(f"Render of {lid} aborted before scene {scene.get('block_id', '?')}",
                      category="render", error_id="RENDER_ABORTED")
            break
        bid = scene.get("block_id", "?")
        clip = None
        bg_img = bg_images.get(bid)
        for attempt in range(2):
            try:
                clip = build_scene_clip(lecture_data, scene, temp_dir, tts_settings,
                                        output_mode=output_mode, bg_image=bg_img,
                                        scene_index=scene_idx, total_scenes=total_scenes,
                                        width=res_w, height=res_h, fps=actual_fps,
                                        static_bg=bid in static_bids)
                break
            except Exception as e:
                if attempt == 0:
                    log_error(f"Scene {bid} attempt 1 failed: {e}, retrying",
                              category="render", error_id="SCENE_RETRY")
                else:
                    log_error(f"Scene {bid} failed after retry: {e}",
                              category="render", error_id="SCENE_FAIL")
                    failed_scenes.append(bid)
        if clip is not None:
            clips.append((scene, clip))

    outputs: list[Path] = []
    # yuv420p = broad player compatibility; CRF 20 = good quality at sane size.
    ffmpeg_params = ["-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                     "-movflags", "+faststart"]
    vfx = load_vfx_config()

    if not clips:
        log_error(f"No valid clips for {lid} — nothing to render",
                  category="render", error_id="NO_CLIPS")
        return outputs

    if chunk_by_scene:
        for scene, clip in clips:
            out = get_scene_video_path(lecture_data, str(scene.get("block_id", "X")), output_dir, suffix=suffix)
            out.parent.mkdir(parents=True, exist_ok=True)
            clip.write_videofile(str(out), fps=actual_fps, codec="libx264", audio_codec="aac",
                                 ffmpeg_params=ffmpeg_params, verbose=False, logger=None)
            clip.close()
            outputs.append(out)
    else:
        final = assemble_clips(clips, vfx)
        out = get_full_video_path(lecture_data, output_dir, suffix=suffix)
        out.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(str(out), fps=actual_fps, codec="libx264", audio_codec="aac",
                              ffmpeg_params=ffmpeg_params, verbose=False, logger=None)
        final.close()
        outputs.append(out)

    for _, c in clips:
        try:
            c.close()
        except Exception:
            pass

    unlock_achievement("video_render")
    add_xp(100, f"Rendered lecture {lid}", "video")
    log_render(lid, "completed", duration_s=time.time() - _render_t0, scenes=len(scenes))
    write_render_metadata(lecture_data, outputs, output_dir, chunk_by_scene=chunk_by_scene, suffix=suffix, output_mode=output_mode)
    return outputs


def batch_render_all(output_dir: Path, progress_callback: Callable | None = None) -> dict:
    """Render every lecture in the database as full MP4s."""
    from core.database import get_all_courses, get_modules, get_lectures

    all_outputs: list[Path] = []
    jobs: list[dict] = []
    errors: list[str] = []
    t0 = time.time()

    for course in get_all_courses():
        for module in get_modules(course["id"]):
            for lec in get_lectures(module["id"]):
                try:
                    data = json.loads(lec["data"]) if lec.get("data") else {}
                    data.setdefault("lecture_id", lec["id"])
                    data.setdefault("title", lec["title"])
                    jobs.append(data)
                except Exception:
                    pass

    total = len(jobs)
    for i, lec_data in enumerate(jobs):
        try:
            outs = render_lecture(lec_data, output_dir)
            all_outputs.extend(outs)
        except Exception as e:
            err_msg = f"{lec_data.get('lecture_id', '?')}: {e}"
            errors.append(err_msg)
            log_error(f"Batch render failed: {err_msg}",
                      category="render", error_id="BATCH_RENDER_FAIL")
        if progress_callback:
            progress_callback(i + 1, total)

    if len(all_outputs) >= 5:
        unlock_achievement("batch_render")

    elapsed = time.time() - t0
    log_render("batch", "completed", duration_s=elapsed,
               total=total, succeeded=len(all_outputs), failed=len(errors))

    return {
        "outputs": all_outputs,
        "total": total,
        "succeeded": len(all_outputs),
        "failed": len(errors),
        "errors": errors,
        "elapsed_s": round(elapsed, 2),
    }


def reorder_and_render(lecture_data: dict, scene_order: list[str],
                       duration_overrides: dict[str, int],
                       output_dir: Path) -> Path:
    """Re-render a lecture with scenes in a custom order and optional duration overrides."""
    original_scenes = {s["block_id"]: s for s in lecture_data.get("video_recipe", {}).get("scene_blocks", [])}
    reordered = []
    for bid in scene_order:
        if bid in original_scenes:
            scene = original_scenes[bid].copy()
            if bid in duration_overrides:
                scene["duration_s"] = duration_overrides[bid]
            reordered.append(scene)

    modified = {**lecture_data}
    modified.setdefault("video_recipe", {})["scene_blocks"] = reordered
    return render_lecture(modified, output_dir, chunk_by_scene=False)[0]
