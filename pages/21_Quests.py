"""
Quests — weekly challenges with XP rewards.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.database import get_active_quests, seed_weekly_quests, get_total_xp, get_level
from core.ui_mode import require_ui_mode
from ui.theme import (
    inject_theme, gf_header, section_divider,
    stat_card, xp_bar, level_badge, help_button, play_sfx,
)

inject_theme()
gf_header("Weekly Quests", "Complete challenges each week to earn bonus XP.")
help_button("quest-system")

# Ensure this week's quests exist
seed_weekly_quests()

# ─── XP summary strip ─────────────────────────────────────────────────────────
total_xp = get_total_xp()
level, level_name, xp_in_level, xp_for_next = get_level(total_xp)

c1, c2, c3 = st.columns(3)
with c1:
    level_badge(level, level_name)
with c2:
    stat_card("Total XP", str(total_xp), colour="#ffd700")
with c3:
    stat_card("Next Level", f"{xp_for_next - xp_in_level} XP", colour="#00d4ff")

xp_bar(xp_in_level, xp_for_next)

# ─── Active quests ─────────────────────────────────────────────────────────────
section_divider("This Week's Quests")

quests = get_active_quests()

if not quests:
    st.info("No quests available this week. Check back next Monday!")
else:
    for q in quests:
        progress = q.get("progress", 0)
        target = q.get("target", 1)
        completed = bool(q.get("completed", 0))
        pct = min(progress / target, 1.0) if target > 0 else 0

        title = q.get("title", "Quest")
        desc = q.get("description", "")
        xp_reward = q.get("xp_reward", 0)

        # Badge colour based on status
        if completed:
            border_col = "#ffd700"
            status_text = "COMPLETE"
            status_col = "#ffd700"
        elif progress > 0:
            border_col = "#00d4ff"
            status_text = "IN PROGRESS"
            status_col = "#00d4ff"
        else:
            border_col = "#303050"
            status_text = "NOT STARTED"
            status_col = "#606080"

        st.markdown(
            f"<div style='"
            f"border-left: 3px solid {border_col}; "
            f"background: #0a0e20; "
            f"padding: 12px 16px; margin: 8px 0; "
            f"font-family: monospace;'>"
            f"<span style='color:{status_col};font-size:0.75rem;'>{status_text}</span><br>"
            f"<span style='color:#e0e0ff;font-size:1.05rem;font-weight:bold;'>{title}</span><br>"
            f"<span style='color:#a0a0c0;font-size:0.85rem;'>{desc}</span><br>"
            f"<span style='color:#ffd700;font-size:0.82rem;'>Reward: {xp_reward} XP</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.progress(pct, text=f"{progress}/{target}")

# ─── Summary ───────────────────────────────────────────────────────────────────
section_divider("Summary")
total_quests = len(quests)
completed_quests = sum(1 for q in quests if q.get("completed"))
st.markdown(
    f"<span style='font-family:monospace;color:#a0a0c0;'>"
    f"Completed: {completed_quests}/{total_quests} quests this week</span>",
    unsafe_allow_html=True,
)

if completed_quests == total_quests and total_quests > 0:
    play_sfx("level_up")
    st.balloons()
    st.success("All quests complete! You're a true scholar this week.")
