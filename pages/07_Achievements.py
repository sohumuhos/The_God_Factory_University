"""
Achievements — badge gallery, XP history, level progression.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.database import get_all_achievements, get_xp_history, get_total_xp, get_level
from ui.theme import (
    inject_theme, gf_header, section_divider,
    achievement_card, xp_bar, level_badge, stat_card, help_button,
)

inject_theme()
gf_header("Achievements", "Your record of conquest at The God Factory.")
help_button("achievement-system")

total_xp = get_total_xp()
level, level_name, xp_in_level, xp_for_next = get_level(total_xp)

lb1, lb2, lb3 = st.columns(3)
with lb1:
    level_badge(level, level_name)
with lb2:
    stat_card("Total XP", str(total_xp), colour="#ffd700")
with lb3:
    stat_card("Next Level in", f"{xp_for_next - xp_in_level} XP", colour="#00d4ff")

xp_bar(xp_in_level, xp_for_next)

# ─── Level progression ────────────────────────────────────────────────────────
section_divider("Level Progression")
help_button("level-system")

LEVELS = [
    (0,     "Seeker",      "#808080"),
    (100,   "Initiate",    "#40dc80"),
    (300,   "Scholar",     "#00d4ff"),
    (700,   "Adept",       "#8080ff"),
    (1500,  "Expert",      "#c060ff"),
    (3000,  "Sage",        "#ffd700"),
    (6000,  "Transcendent",      "#ff8040"),
    (10000, "Grandmaster", "#ff4040"),
    (20000, "Luminary",    "#ff40c0"),
    (50000, "Archon",      "#ffffff"),
]

for i, (xp_req, name, colour) in enumerate(LEVELS):
    unlocked = total_xp >= xp_req
    is_current = level == i
    marker = "[ CURRENT ]" if is_current else ("[ UNLOCKED ]" if unlocked else "[ LOCKED ]")
    text_colour = colour if unlocked else "#303050"
    st.markdown(
        f"<div style='font-family:monospace;margin:2px 0;"
        f"{"background:#0e1230;border-left:3px solid " + colour + ";padding:4px 8px;" if is_current else "padding:4px 8px;"}'>"
        f"<span style='color:{text_colour};font-weight:{"bold" if is_current else "normal"};'>"
        f"Lv {i:2d}  {name:<14}  {xp_req:>6} XP  {marker}</span></div>",
        unsafe_allow_html=True,
    )

# ─── Achievement badges ───────────────────────────────────────────────────────
section_divider("Achievement Badges")
help_button("achievement-system")

ALL_BADGES = [
    # ── Progress ──────────────────────────────────────────────────────────────
    {"id": "first_lecture",    "title": "Awakening",           "desc": "Complete your first lecture.",            "category": "progress"},
    {"id": "ten_lectures",     "title": "Apprentice Path",     "desc": "Complete 10 lectures.",                   "category": "progress"},
    {"id": "speed_reader",     "title": "Swift Scholar",       "desc": "Complete a lecture in one session.",       "category": "progress"},
    # ── Academic ──────────────────────────────────────────────────────────────
    {"id": "first_quiz",       "title": "Trial Taker",         "desc": "Submit your first assignment.",            "category": "academic"},
    {"id": "perfect_score",    "title": "Flawless",            "desc": "Score 100% on any assignment.",            "category": "academic"},
    # ── XP ────────────────────────────────────────────────────────────────────
    {"id": "xp_1000",          "title": "Rising Star",         "desc": "Earn 1,000 XP total.",                    "category": "xp"},
    {"id": "xp_5000",          "title": "Transcendent Adept",  "desc": "Earn 5,000 XP total.",                    "category": "xp"},
    # ── Degree ────────────────────────────────────────────────────────────────
    {"id": "degree_cert",      "title": "Certified",           "desc": "Earn Certificate eligibility.",            "category": "degree"},
    {"id": "degree_assoc",     "title": "Associate",           "desc": "Earn Associate degree eligibility.",       "category": "degree"},
    {"id": "degree_bachelor",  "title": "Bachelor",            "desc": "Earn Bachelor degree eligibility.",        "category": "degree"},
    {"id": "degree_master",    "title": "Grand Scholar",       "desc": "Earn Master degree eligibility.",          "category": "degree"},
    {"id": "degree_doctor",    "title": "Doctorate",           "desc": "Earn Doctorate eligibility.",              "category": "degree"},
    # ── Habits ────────────────────────────────────────────────────────────────
    {"id": "night_owl",        "title": "Night Owl",           "desc": "Study after midnight.",                    "category": "habit"},
    # ── System ────────────────────────────────────────────────────────────────
    {"id": "bulk_import",      "title": "Archivist",           "desc": "Import a bulk JSON curriculum.",           "category": "system"},
    # ── LLM ───────────────────────────────────────────────────────────────────
    {"id": "professor_query",  "title": "The Asking",          "desc": "Query the Professor AI 10 times.",         "category": "llm"},
    # ── Media ─────────────────────────────────────────────────────────────────
    {"id": "video_render",     "title": "Projector",           "desc": "Render your first lecture video.",         "category": "media"},
    {"id": "batch_render",     "title": "Dreamweaver",         "desc": "Batch render 5 or more lectures.",         "category": "media"},
]

unlocked_ids = {a["id"] for a in get_all_achievements()}
categories = sorted(set(b["category"] for b in ALL_BADGES))
selected_cat = st.selectbox("Filter by category", ["all"] + categories)

filtered = ALL_BADGES if selected_cat == "all" else [b for b in ALL_BADGES if b["category"] == selected_cat]
cols = st.columns(3)
for i, badge in enumerate(filtered):
    unlocked = badge["id"] in unlocked_ids
    with cols[i % 3]:
        achievement_card(badge["title"], badge["desc"], badge["category"], unlocked)

# ─── XP event history ─────────────────────────────────────────────────────────
section_divider("XP History")
history = get_xp_history(50)
if history:
    for ev in history:
        import datetime
        ts = datetime.datetime.fromtimestamp(ev["occurred_at"]).strftime("%Y-%m-%d %H:%M")
        st.markdown(
            f"<span style='font-family:monospace;color:#606080;font-size:0.82rem;'>"
            f"{ts}  </span>"
            f"<span style='font-family:monospace;color:#ffd700;'>"
            f"+{ev['xp_gained']:>5} XP  </span>"
            f"<span style='font-family:monospace;color:#a0a0c0;'>{ev['description']}</span>",
            unsafe_allow_html=True,
        )
else:
    st.info("No XP events recorded yet. Complete lectures to start earning XP.")
