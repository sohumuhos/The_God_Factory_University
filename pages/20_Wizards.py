"""
Wizards Hub — central launch page for guided workflows.

This page was reconstructed from available project references.
It links to existing guided tools (LLM setup, auto pipeline, batch render)
and reports the status of legacy wizard engine modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ui.theme import inject_theme, gf_header, section_divider, stat_card, help_button

inject_theme()
gf_header("Wizards Hub", "Guided workflows and setup assistants.")
help_button("llm-setup-wizard")

section_divider("Available Wizards")

c1, c2, c3 = st.columns(3)
with c1:
    stat_card("LLM Setup", "Ready", colour="#40dc80")
    st.page_link("pages/11_LLM_Setup.py", label="Open LLM Setup Wizard")

with c2:
    stat_card("Auto Pipeline", "Ready", colour="#40dc80")
    st.page_link("pages/19_Auto_Pipeline.py", label="Open Auto Pipeline")

with c3:
    stat_card("Batch Render", "Ready", colour="#40dc80")
    st.page_link("pages/05_Batch_Render.py", label="Open Batch Render")

section_divider("Legacy Wizard Engine")

wizard_engine_path = ROOT / "core" / "wizard_engine.py"
video_wizard_path = ROOT / "core" / "wizards" / "video_wizard.py"

if video_wizard_path.exists() and not wizard_engine_path.exists():
    st.warning(
        "Found core/wizards/video_wizard.py but missing core/wizard_engine.py. "
        "The legacy generic wizard runtime is incomplete in this copy."
    )
elif video_wizard_path.exists() and wizard_engine_path.exists():
    st.success("Legacy wizard engine modules are present.")
else:
    st.info("No legacy wizard engine modules detected.")

with st.expander("What happened to the old 20_Wizards page?"):
    st.markdown(
        "- This file appears to have been missing in the current workspace copy.\n"
        "- No git history is available here to recover the original content exactly.\n"
        "- This page is a safe rebuild using the wizard-like features that still exist."
    )

section_divider("Quick Actions")
qa1, qa2 = st.columns(2)
with qa1:
    st.page_link("app.py", label="Back to Dashboard")
with qa2:
    st.page_link("pages/10_Help.py", label="Open Help")
