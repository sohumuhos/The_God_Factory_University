"""Programmatic, deterministic scene visuals (no diffusion, no network).

Renders clean, topic-accurate "slides" with the dark-academic palette using PIL
only. These are precise and legible — better than diffusion for instructional
content (bullets, concept diagrams, simple charts) and work for ANY subject. A
slide is returned as a full WxH RGB image and used by the encoder as a *static*
background (no Ken Burns), with the live narration drawn beneath it as a subtitle.

Scene schema (all optional, backward compatible):
    scene["render_mode"]: "bullets" | "concept" | "diagram" | "chart"
                          | "diffusion" | "gradient" | "auto"
    scene["visual"]: {
        "heading": "Why a base case?",
        "bullets": ["calls itself on a smaller input", "stops at a base case", ...],
        "nodes": ["f(3)", "f(2)", "f(1)", "base"],          # diagram (flow)
        "bars": [{"label": "O(1)", "value": 1}, ...],        # chart
    }

Nothing here is subject-specific: headings/bullets/nodes/labels are arbitrary
strings that are wrapped, shrunk, and truncated to fit, so the same renderer
serves a recursion lecture, a French Revolution lecture, or a cell-biology one.
"""
from __future__ import annotations

import re

from PIL import Image, ImageDraw

from media.video.frame_renderer import PALETTE, _load_font, _wrap

# render_modes this module renders (everything else stays diffusion/gradient)
PROGRAMMATIC_MODES = {"bullets", "concept", "diagram", "chart", "slide"}
# modes that mean "pick a sensible slide automatically"
AUTO_MODES = {"", "auto"}

# Height fraction reserved at the bottom for the live narration subtitle.
CAPTION_BAND = 0.26

# Pillow ≥10 moved resampling constants onto an enum; keep an alias either way.
try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:  # very old Pillow
    _RESAMPLE = Image.LANCZOS


def _text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        return int(draw.textlength(text, font=font))
    except Exception:
        return len(text) * 8


def _fit_font(draw, text: str, max_w: int, max_size: int, min_size: int = 11):
    """Largest font (by our loader) whose rendering of *text* fits *max_w*."""
    size = max_size
    while size > min_size:
        f = _load_font(size)
        if _text_w(draw, text, f) <= max_w:
            return f
        size -= 2
    return _load_font(min_size)


def _wrap_to_width(draw, text: str, font, max_w: int, max_lines: int) -> list[str]:
    """Word-wrap *text* to fit *max_w* using real glyph widths; truncate with … ."""
    words = (text or "").split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if _text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    # If content remains, mark truncation on the last line.
    if lines and (len(" ".join(lines).split()) < len(words)):
        last = lines[-1]
        while last and _text_w(draw, last + " …", font) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = (last + " …").strip()
    return lines


def _gradient_bg(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H), PALETTE["bg_dark"])
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(PALETTE["bg_dark"][0] * (1 - ratio) + PALETTE["bg_mid"][0] * ratio)
        g = int(PALETTE["bg_dark"][1] * (1 - ratio) + PALETTE["bg_mid"][1] * ratio)
        b = int(PALETTE["bg_dark"][2] * (1 - ratio) + PALETTE["bg_mid"][2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def _fit_image(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    """Resize *img* to fit inside (box_w, box_h) preserving aspect ratio."""
    iw, ih = img.size
    if iw <= 0 or ih <= 0:
        return img
    scale = min(box_w / iw, box_h / ih)
    nw = max(1, int(iw * scale))
    nh = max(1, int(ih * scale))
    return img.resize((nw, nh), _RESAMPLE)


def _draw_image_inset(base: Image.Image, draw: ImageDraw.ImageDraw,
                      inset: Image.Image, box: tuple[int, int, int, int]) -> None:
    """Composite *inset* into *box* on *base*: centered, framed, with a shadow.

    This is what turns a plain slide into the hybrid slide+image look — a real
    picture appears when diffusion succeeds, while the slide itself remains the
    reliable base if no image is available."""
    bx0, by0, bx1, by1 = (int(v) for v in box)
    margin = 12
    avail_w = max(8, (bx1 - bx0) - 2 * margin)
    avail_h = max(8, (by1 - by0) - 2 * margin)
    fitted = _fit_image(inset.convert("RGB"), avail_w, avail_h)
    fw, fh = fitted.size
    px = bx0 + ((bx1 - bx0) - fw) // 2
    py = by0 + ((by1 - by0) - fh) // 2
    # drop shadow first, then the image, then a gold frame on top
    draw.rectangle([px + 5, py + 5, px + fw + 5, py + fh + 5], fill=(3, 7, 16))
    base.paste(fitted, (px, py))
    draw.rectangle([px - 3, py - 3, px + fw + 2, py + fh + 2],
                   outline=PALETTE["gold"], width=2)


def _slide_base(W: int, H: int, heading: str):
    """Dark slide with a heading + accent rule. Returns (img, draw, content_box)."""
    img = _gradient_bg(W, H)
    draw = ImageDraw.Draw(img)
    pad = max(10, W // 40)

    draw.rectangle([pad, pad, W - pad - 1, H - pad - 1], outline=PALETTE["border"], width=2)

    inner_w = W - 2 * pad - 36
    title_font = _load_font(max(20, W // 30))
    title_y = pad + max(10, H // 24)
    heading = (heading or "").strip()
    if heading:
        # shrink first, then wrap to at most 2 lines so any-length title fits
        title_font = _fit_font(draw, heading, inner_w, max(20, W // 30), min_size=18)
        lh = int(title_font.size * 1.12) if hasattr(title_font, "size") else 26
        for line in _wrap_to_width(draw, heading, title_font, inner_w, 2):
            draw.text((pad + 18, title_y), line, fill=PALETTE["cyan"], font=title_font)
            title_y += lh
        rule_y = title_y + 6
        draw.line([(pad + 18, rule_y), (pad + 18 + min(W // 3, 340), rule_y)],
                  fill=PALETTE["gold"], width=3)
        title_y = rule_y + 16
    else:
        title_y = pad + 20

    content_box = (pad + 18, title_y, W - pad - 18, int(H * (1 - CAPTION_BAND)))
    return img, draw, content_box


def render_bullets(W: int, H: int, heading: str, bullets: list[str],
                   inset_image: Image.Image | None = None) -> Image.Image:
    img, draw, (x0, y0, x1, y1) = _slide_base(W, H, heading)
    bullets = [str(b).strip() for b in (bullets or []) if str(b).strip()][:6]
    # Figure-only slide: a heading plus one large framed image (no bullets).
    if inset_image is not None and not bullets:
        _draw_image_inset(img, draw, inset_image, (x0, y0, x1, y1))
        return img
    if not bullets:
        return img
    text_x1 = x1
    if inset_image is not None:
        # Two-column hybrid: bullets on the left, framed image on the right.
        col_gap = max(16, W // 48)
        panel_w = int((x1 - x0) * 0.42)
        _draw_image_inset(img, draw, inset_image, (x1 - panel_w, y0, x1, y1))
        text_x1 = x1 - panel_w - col_gap
    body_font = _load_font(max(16, W // 46))
    lh = int(body_font.size * 1.3) if hasattr(body_font, "size") else 24
    max_w = text_x1 - x0 - 30
    # Pre-wrap so we know total height, then top-align with comfortable gaps.
    wrapped = [_wrap_to_width(draw, b, body_font, max_w, 2) for b in bullets]
    gap = lh // 2
    block_h = sum(len(w) * lh + gap for w in wrapped)
    y = y0 + max(0, ((y1 - y0) - block_h) // 4)  # nudge toward the top third
    for lines in wrapped:
        my = y + (lh // 2) - 5
        draw.polygon([(x0, my), (x0, my + 12), (x0 + 11, my + 6)], fill=PALETTE["gold"])
        ty = y
        for ln in lines:
            draw.text((x0 + 26, ty), ln, fill=PALETTE["white"], font=body_font)
            ty += lh
        y += len(lines) * lh + gap
        if y > y1:
            break
    return img


def _arrow(draw, x0, y0, x1, y1, colour, width):
    draw.line([(x0, y0), (x1, y1)], fill=colour, width=width)
    ah = 7
    draw.polygon([(x1, y1), (x1 - ah, y1 - ah), (x1 - ah, y1 + ah)], fill=colour)


def render_diagram(W: int, H: int, heading: str, nodes: list[str],
                   edges: list | None = None) -> Image.Image:
    """Left-to-right flow of labelled rounded boxes joined by arrows."""
    img, draw, (x0, y0, x1, y1) = _slide_base(W, H, heading)
    nodes = [str(n).strip() for n in (nodes or []) if str(n).strip()][:6]
    if not nodes:
        return img
    n = len(nodes)
    gap = max(16, W // 46)
    box_h = max(48, min(86, (y1 - y0) // 3))
    cy = (y0 + y1) // 2
    total_w = x1 - x0
    box_w = max(64, (total_w - gap * (n - 1)) // n)

    right_edges = []
    bx = x0
    for label in nodes:
        rect = [bx, cy - box_h // 2, bx + box_w, cy + box_h // 2]
        draw.rounded_rectangle(rect, radius=10, fill=(12, 26, 52),
                               outline=PALETTE["cyan"], width=2)
        # label: shrink to fit the box, wrap to <=2 lines
        font = _fit_font(draw, label, box_w - 14, max(13, W // 54), min_size=11)
        wl = _wrap_to_width(draw, label, font, box_w - 12, 2)
        lh = int(font.size * 1.08) if hasattr(font, "size") else 16
        ty = cy - (len(wl) * lh) // 2
        for ln in wl:
            tw = _text_w(draw, ln, font)
            draw.text((bx + (box_w - tw) // 2, ty), ln, fill=PALETTE["white"], font=font)
            ty += lh
        right_edges.append(bx + box_w)
        bx += box_w + gap

    for i in range(n - 1):
        _arrow(draw, right_edges[i] + 3, cy, right_edges[i] + gap - 3, cy, PALETTE["gold"], 3)
    return img


def render_chart(W: int, H: int, heading: str, bars: list) -> Image.Image:
    """Simple labelled bar chart."""
    img, draw, (x0, y0, x1, y1) = _slide_base(W, H, heading)
    items = []
    for b in (bars or []):
        if isinstance(b, dict):
            try:
                items.append((str(b.get("label", "")), float(b.get("value", 0) or 0)))
            except (TypeError, ValueError):
                continue
    items = items[:7]
    if not items:
        return img
    font = _load_font(max(13, W // 64))
    base_y = y1 - 30
    top_y = y0 + 18
    max_v = max((v for _, v in items), default=1) or 1
    span = max(40, base_y - top_y)
    n = len(items)
    slot = (x1 - x0) // n
    bar_w = max(14, int(slot * 0.55))
    draw.line([(x0, base_y), (x1, base_y)], fill=PALETTE["dim"], width=2)
    for i, (label, val) in enumerate(items):
        h = int(span * (max(0.0, val) / max_v))
        cx = x0 + i * slot + slot // 2
        left = cx - bar_w // 2
        top = base_y - h
        draw.rectangle([left, top, left + bar_w, base_y], fill=(0, 150, 200),
                       outline=PALETTE["cyan"], width=2)
        vt = f"{val:g}"
        draw.text((cx - _text_w(draw, vt, font) // 2, top - 18), vt,
                  fill=PALETTE["gold"], font=font)
        lt = _wrap_to_width(draw, label, font, slot - 6, 1)
        lt = lt[0] if lt else ""
        draw.text((cx - _text_w(draw, lt, font) // 2, base_y + 6), lt,
                  fill=PALETTE["silver"], font=font)
    return img


# ── Topic-agnostic inference (auto slides for any subject) ────────────────────

def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]


def _shorten(s: str, limit: int = 70) -> str:
    s = s.strip().rstrip(".")
    # prefer the first clause (before a comma/semicolon/colon)
    for sep in (";", ":", ", "):
        if sep in s and len(s) > limit:
            s = s.split(sep)[0]
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + " …"
    return s


def _auto_bullets(scene: dict, lecture: dict, scene_index: int) -> list[str]:
    """Derive 3-4 concise points for ANY topic, preferring distinct content over
    the spoken narration: per-scene slice of core terms, else objectives, else
    key sentences pulled from the narration."""
    terms = [str(t).strip() for t in (lecture.get("core_terms") or []) if str(t).strip()]
    if len(terms) >= 3:
        window = terms[scene_index * 4:(scene_index + 1) * 4] or terms[:4]
        if len(window) >= 2:
            return window[:4]
    objs = [str(o).strip() for o in (lecture.get("learning_objectives") or []) if str(o).strip()]
    if objs:
        return [_shorten(o, 80) for o in objs[:4]]
    sents = _sentences(scene.get("narration_prompt", ""))
    if sents:
        return [_shorten(s) for s in sents[:4]]
    return []


def render_scene_slide(scene: dict, lecture: dict, W: int, H: int,
                       scene_index: int = 0,
                       inset_image: Image.Image | None = None) -> Image.Image | None:
    """Dispatch on scene['render_mode']; return a slide image or None to fall back.

    "auto"/"" build a concept slide inferred from the scene — so any lecture, on
    any subject, gets a clean slide even without an explicit visual spec.

    *inset_image* (an AI-generated picture, optional) is composited into bullet /
    concept / auto slides as a framed figure — the hybrid slide+image look. It is
    ignored for chart/diagram modes, which are already self-contained visuals.
    """
    W = int(W) - (int(W) % 2)
    H = int(H) - (int(H) % 2)
    mode = str(scene.get("render_mode", "")).lower()
    spec = scene.get("visual") or {}
    if not isinstance(spec, dict):
        spec = {}
    heading = (spec.get("heading") or scene.get("heading")
               or lecture.get("title", "")).strip()
    try:
        if mode == "chart":
            bars = spec.get("bars")
            return render_chart(W, H, heading, bars) if bars else None
        if mode == "diagram":
            nodes = spec.get("nodes")
            return render_diagram(W, H, heading, nodes, spec.get("edges")) if nodes else None
        # bullets / concept / slide / auto / unset → bullet concept slide, with an
        # optional framed image. With an image we render even when there are no
        # bullets (a clean "figure" slide); otherwise text is required.
        bullets = spec.get("bullets") or _auto_bullets(scene, lecture, scene_index)
        if bullets or inset_image is not None:
            return render_bullets(W, H, heading, bullets, inset_image=inset_image)
        return None
    except Exception:
        return None
