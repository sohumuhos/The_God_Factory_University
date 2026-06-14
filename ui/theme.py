"""
Dark-academic procedural theme for The God Factory University.
No emojis. No external assets. All graphics and sounds generated in code.

Colour palette:
  - Obsidian background:   #060812
  - Deep panel:            #0e1230
  - God Factory cyan:           #00d4ff
  - Accent gold:           #ffd700
  - Crimson alert:         #e04040
  - Shadow silver:         #b8b8d0
  - Dim mist:              #606080
  - Success green:         #40dc80
"""

from __future__ import annotations

import base64
import html
import io
import math
import random
import time

import numpy as np
import streamlit as st
import re


# ─── LLM output sanitizer ────────────────────────────────────────────────────

def sanitize_llm_output(text: str) -> str:
    """Sanitize LLM-generated text before rendering via st.markdown.

    Strips potentially dangerous HTML tags while preserving safe Markdown.
    Prevents XSS injection through st.markdown(unsafe_allow_html=True) contexts.
    Also strips layout HTML tags (div, span, p, br, etc.) so they don't render
    as raw text in the UI.
    """
    if not isinstance(text, str):
        return str(text)
    # Remove script tags and their contents
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove iframe, object, embed, form tags
    text = re.sub(r'<(iframe|object|embed|form|link|meta)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(iframe|object|embed|form|link|meta)[^>]*/?\s*>', '', text, flags=re.IGNORECASE)
    # Remove event handler attributes (onclick, onerror, onload, etc.)
    text = re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bon\w+\s*=\s*\S+', '', text, flags=re.IGNORECASE)
    # Remove javascript: URLs
    text = re.sub(r'javascript\s*:', '', text, flags=re.IGNORECASE)
    # Remove data: URLs (can contain scripts)
    text = re.sub(r'data\s*:\s*text/html', 'data:blocked', text, flags=re.IGNORECASE)
    # Strip layout HTML tags that LLMs sometimes emit (div, span, p, br, section, etc.)
    text = re.sub(r'</?(?:div|span|p|br|section|article|header|footer|main|nav|aside|table|tr|td|th|thead|tbody|ul|ol|li|dl|dt|dd|figure|figcaption|details|summary|blockquote|pre|hr|h[1-6])\b[^>]*/?>', '', text, flags=re.IGNORECASE)
    return text

# ─── CSS constants ────────────────────────────────────────────────────────────
FONT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
"""

# The actual theme stylesheets now live in ui/themes.py — a Streamlit-free module
# so the CSS can be screenshot-tested headless and reused outside the app. This
# file keeps the injection entry point and the procedural UI component helpers.


# ─── Theme injection ──────────────────────────────────────────────────────────

def active_theme() -> str:
    """Return the user-selected UI theme: 'classic' (default) or 'glass'."""
    try:
        from core.database import get_setting
        t = get_setting("ui_theme", "classic")
    except Exception:
        t = "classic"
    return t if t in ("classic", "glass") else "classic"


def inject_theme() -> None:
    from ui.themes import build_theme_css
    st.markdown(build_theme_css(active_theme()), unsafe_allow_html=True)


def _panel_attrs(token_name: str, colour: str, classic_style: str) -> str:
    """Return the HTML container attributes (class + style) for a custom panel,
    honoring the active theme.

    Under "glass" (and only when the glass stylesheets are actually loaded) it
    emits the frosted token — accent ``{c}`` → *colour* — plus a ``gf-glass`` class
    so the CSS ``prefers-reduced-transparency`` fallback can override the inline
    blur (a media query can't otherwise reach an inline style). Under "classic" it
    returns the original inline style verbatim, so the classic look is
    rendering-identical (zero regression)."""
    if active_theme() == "glass":
        try:
            from ui.themes import helper_tokens, glass_available
            if glass_available():
                tok = helper_tokens("glass").get(token_name)
                if tok:
                    style = tok.replace("{c}", colour)
                    return f'class="gf-glass" style="{style}"'
        except Exception:
            pass
    return f'style="{classic_style}"'


# ─── ASCII art components ─────────────────────────────────────────────────────

def gf_header(title: str, subtitle: str = "") -> None:
    width = max(len(title) + 8, 60)
    border = "╔" + "═" * (width - 2) + "╗"
    inner = f"║  {title.upper():<{width - 4}}║"
    bottom = "╚" + "═" * (width - 2) + "╝"
    text = f"```\n{border}\n{inner}\n{bottom}\n```"
    st.markdown(text)
    if subtitle:
        st.caption(subtitle)


def section_divider(label: str = "") -> None:
    if label:
        line = f"◆─── {label.upper()} ───◆"
    else:
        line = "◆" + "─" * 58 + "◆"
    st.markdown(f"<p style='color:#00d4ff44;font-family:monospace;letter-spacing:2px;'>{line}</p>",
                unsafe_allow_html=True)


def stat_card(label: str, value: str, delta: str = "", colour: str = "#00d4ff") -> None:
    classic = (f"background:#0e1230;border:1px solid {colour}44;border-radius:4px;"
               f"padding:14px 18px;margin:4px 0;")
    attrs = _panel_attrs("card", colour, classic)
    lbl, val, dlt = html.escape(str(label).upper()), html.escape(str(value)), html.escape(str(delta))
    inner = (
        f'<div style="color:{colour};font-size:0.7rem;letter-spacing:2px;">{lbl}</div>'
        f'<div style="color:{colour};font-size:1.8rem;font-weight:bold;font-family:monospace;">{val}</div>'
        + (f"<div style='color:#ffd700;font-size:0.75rem;'>{dlt}</div>" if delta else "")
    )
    st.markdown(f'<div {attrs}>{inner}</div>', unsafe_allow_html=True)


def xp_bar(current: int, maximum: int, label: str = "XP") -> None:
    pct = min(current / max(maximum, 1), 1.0)
    fill = int(pct * 40)
    empty = 40 - fill
    bar = "█" * fill + "░" * empty
    filled_text = f"```\n[{label}] [{bar}] {current}/{maximum}\n```"
    st.markdown(filled_text)


def level_badge(level_idx: int, title: str) -> None:
    symbols = ["◇", "◆", "★", "✦", "▲", "▶", "◉", "⊕", "⊗", "✸"]
    sym = symbols[min(level_idx, len(symbols) - 1)]
    colour_map = [
        "#808080", "#8888ff", "#44aaff", "#00d4ff",
        "#44ffaa", "#ffd700", "#ff8844", "#ff4444",
        "#ff44ff", "#ffffff",
    ]
    col = colour_map[min(level_idx, len(colour_map) - 1)]
    classic = (f"display:inline-block;background:#0e1230;border:1px solid {col};"
               f"border-radius:2px;padding:8px 16px;font-family:monospace;")
    attrs = _panel_attrs("badge", col, classic)
    ttl = html.escape(str(title).upper())
    inner = (
        f'<span style="color:{col};font-size:1.2rem;">{sym} LVL {level_idx}</span>'
        f'<span style="color:{col}aa;font-size:0.9rem;margin-left:12px;">{ttl}</span>'
    )
    st.markdown(f'<div {attrs}>{inner}</div>', unsafe_allow_html=True)


def achievement_card(title_or_dict, description: str = "", category: str = "", unlocked: bool = False) -> None:
    """Accepts either a dict or (title, description, category, unlocked) positional args."""
    if isinstance(title_or_dict, dict):
        ach = title_or_dict
        title = ach.get("title", "")
        description = ach.get("description", "")
        category = ach.get("category", "")
        unlocked = bool(ach.get("unlocked_at"))
        xp_reward = ach.get("xp_reward", 0)
    else:
        title = str(title_or_dict)
        xp_reward = 0
    border = "#ffd700" if unlocked else "#303050"
    icon = "◆" if unlocked else "◇"
    # Locked tone lifted #404060 → #8a8aae for WCAG AA (the ◇ icon + gray-vs-gold
    # title still distinguish locked from unlocked without relying on contrast).
    colour = "#ffd700" if unlocked else "#8a8aae"
    text_col = "#b8b8d0" if unlocked else "#8a8aae"
    ttl = html.escape(str(title).upper())
    desc = html.escape(str(description))
    cat_str = (f"<div style='color:#8a8aae;font-size:0.62rem;'>{html.escape(str(category).upper())}</div>"
               if category else "")
    xp_str = f"<div style='color:#8a8aae;font-size:0.62rem;'>+{int(xp_reward)} XP</div>" if xp_reward else ""
    classic = (f"background:#090e20;border:1px solid {border};border-radius:4px;"
               f"padding:10px 14px;margin:4px 0;")
    attrs = _panel_attrs("panel", border, classic)
    markup = (
        f"<div {attrs}>"
        f"<div style='color:{colour};font-size:0.8rem;'>{icon} {ttl}</div>"
        f"<div style='color:{text_col};font-size:0.7rem;margin-top:4px;'>{desc}</div>"
        f"{cat_str}{xp_str}</div>"
    )
    st.markdown(markup, unsafe_allow_html=True)


def progress_badge(status: str) -> str:
    mapping = {
        "completed":   ("<span style='color:#40dc80;'>▶ COMPLETE</span>", "#40dc80"),
        "in_progress": ("<span style='color:#ffd700;'>► IN PROGRESS</span>", "#ffd700"),
        "not_started": ("<span style='color:#404060;'>◇ NOT STARTED</span>", "#404060"),
    }
    badge, _ = mapping.get(status, mapping["not_started"])
    return badge


def deadline_pill(seconds_remaining: float) -> str:
    if seconds_remaining < 0:
        return "<span style='color:#e04040;'>OVERDUE</span>"
    if seconds_remaining < 3600:
        return f"<span style='color:#e04040;'>{int(seconds_remaining//60)}m remaining</span>"
    if seconds_remaining < 86400:
        return f"<span style='color:#ffd700;'>{int(seconds_remaining//3600)}h remaining</span>"
    return f"<span style='color:#40dc80;'>{int(seconds_remaining//86400)}d remaining</span>"


def render_gpa_display(gpa: float) -> None:
    colour = "#40dc80" if gpa >= 3.5 else "#ffd700" if gpa >= 2.5 else "#e04040"
    label = "Summa Cum Laude" if gpa >= 3.9 else "Magna Cum Laude" if gpa >= 3.7 else \
            "Cum Laude" if gpa >= 3.5 else "Dean's List" if gpa >= 3.0 else \
            "Good Standing" if gpa >= 2.0 else "Academic Probation"
    attrs = _panel_attrs("card", colour, "font-family:monospace;")
    st.markdown(
        f"<div {attrs}>"
        f"<span style='color:{colour};font-size:2.5rem;'>{gpa:.2f}</span>"
        f"<span style='color:#8a8aae;font-size:0.9rem;margin-left:12px;'>{html.escape(label)}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─── Procedural SFX (autoplay via HTML) ──────────────────────────────────────

def play_sfx(sfx_name: str) -> None:
    from media.audio_engine import generate_sfx_bytes
    wav_bytes = generate_sfx_bytes(sfx_name)
    b64 = base64.b64encode(wav_bytes).decode()
    st.components.v1.html(
        f'<audio autoplay style="display:none">'
        f'<source src="data:audio/wav;base64,{b64}" type="audio/wav">'
        f'</audio>',
        height=0,
    )


# ─── Animated ASCII loading strip ─────────────────────────────────────────────

def loading_strip(text: str = "PROCESSING") -> None:
    frames = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰", "▱▱▱▱▰", "▱▱▱▰▰"]
    frame = frames[int(time.time() * 4) % len(frames)]
    st.markdown(
        f"<p style='color:#00d4ff;font-family:monospace;font-size:0.85rem;'>"
        f"{frame} {text}...</p>",
        unsafe_allow_html=True,
    )


# ─── Completion celebration ──────────────────────────────────────────

def completion_burst(message: str = "QUEST COMPLETE") -> None:
    burst = random.choice([
        "╔══ ★ ══╗",
        "◆══════◆",
        "▶══════◀",
    ])
    classic = ("text-align:center;font-family:monospace;padding:20px;"
               "background:#060812;border:2px solid #ffd700;border-radius:4px;")
    attrs = _panel_attrs("celebration", "#ffd700", classic)
    msg = html.escape(str(message))
    st.markdown(
        f"<div {attrs}>"
        f"<div style='color:#ffd700;font-size:1.4rem;letter-spacing:4px;'>{burst}</div>"
        f"<div style='color:#00d4ff;font-size:1.8rem;letter-spacing:3px;margin:10px 0;'>"
        f"{msg}</div>"
        f"<div style='color:#ffd700;font-size:1.4rem;letter-spacing:4px;'>{burst}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─── Degree tier display ─────────────────────────────────────────────────────

DEGREE_SIGILS = {
    "Certificate": "◇",
    "Associate":   "◆",
    "Bachelor":    "★",
    "Master":      "✦",
    "Doctorate":   "⊕",
}

def degree_display(eligible: list[str]) -> None:
    if not eligible:
        st.markdown(
            "<p style='color:#404060;font-family:monospace;'>No degree eligibility yet. Keep studying.</p>",
            unsafe_allow_html=True,
        )
        return
    top = eligible[-1]
    sigil = DEGREE_SIGILS.get(top, "◇")
    classic = ("font-family:monospace;text-align:center;padding:16px;"
               "background:#090e20;border:1px solid #ffd700;border-radius:4px;")
    attrs = _panel_attrs("panel", "#ffd700", classic)
    markup = (
        f"<div {attrs}>"
        f"<div style='color:#ffd700;font-size:2rem;'>{sigil}</div>"
        f"<div style='color:#ffd700;font-size:1.2rem;letter-spacing:3px;'>{html.escape(str(top).upper())}</div>"
        f"</div>"
    )
    st.markdown(markup, unsafe_allow_html=True)


# ─── Help button ──────────────────────────────────────────────────────────────

def help_button(topic_key: str, label: str = "[?]") -> None:
    """Render a small inline help link that navigates to the Help page at the given anchor."""
    url = f"/Help?topic={topic_key}"
    html = (
        f"<a href='{url}' target='_self' "
        f"style='color:#00d4ff;font-size:0.75rem;text-decoration:none;"
        f"font-family:monospace;padding:0 4px;border:1px solid #00d4ff44;"
        f"border-radius:3px;margin-left:4px;' "
        f"title='Help: {topic_key}'>{label}</a>"
    )
    st.markdown(html, unsafe_allow_html=True)
