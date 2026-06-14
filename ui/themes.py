"""Theme CSS for The God Factory University — *no Streamlit import*.

This module holds the raw stylesheet strings and a single ``build_theme_css``
entry point. It deliberately imports nothing from Streamlit so the CSS can be
reused by tooling (e.g. the headless screenshot harness) and unit-tested without
a running app. ``ui/theme.py`` imports from here and injects via ``st.markdown``.

Themes:
  - "classic" — the original dark-academic terminal look (sharp, neon, solid panels).
  - "glass"   — "Frosted Obsidian": dark glassmorphism (translucent, blurred,
                rounded) inspired by Apple's Liquid Glass, over an animated mesh.
"""
from __future__ import annotations

from pathlib import Path as _Path

_UI_DIR = _Path(__file__).resolve().parent


def _read_css(name: str) -> str:
    """Load a sidecar .css file from ui/ (empty string if missing)."""
    try:
        return (_UI_DIR / name).read_text(encoding="utf-8")
    except Exception:
        return ""


# ─── CLASSIC (original) ───────────────────────────────────────────────────────
CLASSIC_CSS = """
/* ── Reset & typography ───────────────────────────────────────────────── */
* { box-sizing: border-box; }
html, body, [class*="css"] {
    background-color: #060812 !important;
    color: #b8b8d0 !important;
    font-family: 'Share Tech Mono', 'Courier New', monospace !important;
}
h1, h2, h3 { color: #00d4ff !important; letter-spacing: 2px; }
h4, h5, h6 { color: #ffd700 !important; }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #090e20 !important;
    border-right: 1px solid #001830 !important;
}
[data-testid="stSidebar"] h1 { font-size: 1.1rem !important; }

/* ── Main content ─────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background-color: #060812 !important;
}

/* ── Metric boxes ─────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #0e1230;
    border: 1px solid #00d4ff44;
    border-radius: 4px;
    padding: 12px;
}
[data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { color: #606080 !important; font-size: 0.75rem !important; }
[data-testid="stMetricDelta"] { color: #ffd700 !important; }

/* ── Buttons ──────────────────────────────────────────────────────────── */
div.stButton > button {
    background: #0e1230 !important;
    color: #00d4ff !important;
    border: 1px solid #00d4ff88 !important;
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1px !important;
    transition: all 0.15s ease !important;
}
div.stButton > button:hover {
    background: #001830 !important;
    border-color: #ffd700 !important;
    color: #ffd700 !important;
    box-shadow: 0 0 8px #ffd70044 !important;
}
div.stButton > button:active {
    background: #00d4ff22 !important;
}

/* ── Progress bars ────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #00d4ff, #ffd700) !important;
}
[data-testid="stProgress"] {
    background: #0e1230 !important;
    border: 1px solid #00d4ff22 !important;
}

/* ── Inputs ───────────────────────────────────────────────────────────── */
input, textarea, [data-testid="stTextInput"] input {
    background: #0e1230 !important;
    color: #b8b8d0 !important;
    border: 1px solid #00d4ff44 !important;
    border-radius: 2px !important;
    font-family: monospace !important;
}
input:focus, textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 4px #00d4ff44 !important;
    outline: none !important;
}

/* ── Selectbox ────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #0e1230 !important;
    border: 1px solid #00d4ff44 !important;
    color: #b8b8d0 !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-testid="stTab"] {
    background: #090e20 !important;
    color: #606080 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
    background: #0e1230 !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #090e20 !important;
    border: 1px solid #00d4ff22 !important;
    border-radius: 2px !important;
}
[data-testid="stExpander"] summary { color: #00d4ff !important; }

/* ── Code / monospace ─────────────────────────────────────────────────── */
code, pre {
    background: #060812 !important;
    color: #00d4ff !important;
    border: 1px solid #00d4ff22 !important;
    border-radius: 2px !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #060812; }
::-webkit-scrollbar-thumb { background: #00d4ff44; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff88; }

/* ── Alert / info boxes ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #0e1230 !important;
    border-left: 3px solid #00d4ff !important;
    color: #b8b8d0 !important;
}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border-color: #00d4ff22 !important; }

/* ── Chat messages ────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: #090e20 !important;
    border: 1px solid #00d4ff22 !important;
    border-radius: 4px !important;
}
[data-testid="stChatMessage"][data-role="assistant"] {
    border-left: 3px solid #00d4ff !important;
}
[data-testid="stChatMessage"][data-role="user"] {
    border-left: 3px solid #ffd700 !important;
}
"""

# ─── GLASS ("Frosted Obsidian") ───────────────────────────────────────────────
# Designed via a multi-agent workflow (variants → judge panel → synthesis) and
# refined against headless-Chromium screenshots. The big stylesheets live in
# sidecar .css files (ui/glass_bg.css, ui/glass_global.css) so they keep CSS
# tooling/highlighting and can be screenshot-tested without running Streamlit.
GLASS_BG_CSS = _read_css("glass_bg.css")
GLASS_GLOBAL_CSS = _read_css("glass_global.css")

# Inline-style tokens for the app's custom st.markdown panels, per theme. Each is
# a base style; helpers substitute the accent colour for the `{c}` placeholder
# (and `{c}NN` hex-alpha suffixes), so call sites pass colour=... unchanged.
HELPER_TOKENS = {
    "classic": {
        "panel": "background:#0e1230;border:1px solid {c}44;border-radius:4px;",
        "card": "background:#0e1230;border:1px solid {c}44;border-radius:4px;",
        "badge": "background:#0e1230;border:1px solid {c};border-radius:2px;",
        "celebration": "background:#060812;border:2px solid #ffd700;border-radius:4px;",
    },
    "glass": {
        "panel": "background:rgba(14,18,48,0.62);-webkit-backdrop-filter:blur(10px) saturate(1.08);backdrop-filter:blur(10px) saturate(1.08);border:1px solid rgba(255,255,255,0.10);border-top:1px solid {c}3a;border-radius:14px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.12),0 8px 32px rgba(0,0,0,0.45);padding:18px 22px;margin:8px 0;color:#b8b8d0;font-family:'Share Tech Mono',monospace;",
        "card": "background:rgba(14,18,48,0.70);-webkit-backdrop-filter:blur(11px) saturate(1.10);backdrop-filter:blur(11px) saturate(1.10);border:1px solid {c}44;border-top:1px solid rgba(255,255,255,0.12);border-radius:14px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.12),0 8px 28px rgba(0,0,0,0.42);padding:16px 18px;margin:6px 0;color:{c};font-family:'Share Tech Mono',monospace;text-shadow:0 0 12px {c}30;",
        "badge": "display:inline-block;background:{c}24;-webkit-backdrop-filter:blur(8px) saturate(1.10);backdrop-filter:blur(8px) saturate(1.10);border:1px solid {c}73;border-radius:999px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.14),0 2px 10px {c}2e;padding:5px 16px;color:{c};font-family:'Share Tech Mono',monospace;font-size:0.8rem;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 8px {c}40;",
        "celebration": "text-align:center;background:rgba(14,18,48,0.72);-webkit-backdrop-filter:blur(14px) saturate(1.15);backdrop-filter:blur(14px) saturate(1.15);border:1px solid rgba(255,215,0,0.50);border-top:1px solid rgba(255,255,255,0.18);border-radius:16px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.16),0 0 28px rgba(255,215,0,0.24),0 12px 40px rgba(0,0,0,0.55);padding:24px 22px;margin:14px 0;color:#ffd700;font-family:'Share Tech Mono',monospace;letter-spacing:3px;text-shadow:0 0 16px rgba(255,215,0,0.40);",
    },
}

VALID_THEMES = ("classic", "glass")


_FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Share+Tech+Mono&display=swap');"
)


def glass_available() -> bool:
    """True only when BOTH glass stylesheets are present. Single source of truth so
    the injected CSS and the panel helpers can never disagree (a half-loaded glass
    theme — e.g. missing mesh — is treated as unavailable)."""
    return bool(GLASS_GLOBAL_CSS.strip() and GLASS_BG_CSS.strip())


def build_theme_css(theme: str = "classic") -> str:
    """Return the full ``<style>…</style>`` block for *theme*.

    Falls back to classic for unknown themes or if the glass stylesheets are
    missing. The font ``@import`` is emitted FIRST (a CSS @import after any style
    rule is invalid and silently dropped, and glass_bg.css emits rules)."""
    theme = theme if theme in VALID_THEMES else "classic"
    if theme == "glass" and glass_available():
        return f"<style>\n{_FONT_IMPORT}\n{GLASS_BG_CSS}\n{GLASS_GLOBAL_CSS}\n</style>"
    return f"<style>\n{CLASSIC_CSS}\n</style>"


def helper_tokens(theme: str = "classic") -> dict:
    """Return the inline-style token dict for *theme*.

    Coheres with build_theme_css: if glass is requested but unavailable, returns
    classic tokens so custom panels never render as glass while the page injects
    the classic stylesheet."""
    theme = theme if theme in VALID_THEMES else "classic"
    if theme == "glass" and not glass_available():
        theme = "classic"
    toks = HELPER_TOKENS.get(theme) or {}
    return toks or HELPER_TOKENS["classic"]
