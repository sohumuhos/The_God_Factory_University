"""Reusable 'Professor suggests' proactive panel.

Renders the controller's ranked next-action proposals (core.proactive) as
one-click launchers. Clicking dispatches a background, review-gated agent job
via the Professor->Agent bridge, so any ledger writes queue for approval on the
Agent page. Used on the Dashboard and the Agent page.
"""
from __future__ import annotations

import streamlit as st


def render_proactive_panel(*, key_prefix: str = "dash", max_items: int = 3,
                           heading: str = "Professor suggests") -> None:
    try:
        from core.proactive import propose_next_action
        proposals = propose_next_action(max_items=max_items)
    except Exception:
        return
    if not proposals:
        return

    try:
        from ui.theme import section_divider
        section_divider(heading)
    except Exception:
        st.markdown(f"**{heading}**")
    for i, p in enumerate(proposals):
        col_text, col_btn = st.columns([5, 1])
        with col_text:
            st.markdown(f"**{p['label']}** — {p.get('reason', '')}")
        with col_btn:
            if st.button("Run", key=f"{key_prefix}_prop_{i}", use_container_width=True):
                try:
                    from llm.professor import Professor
                    job_id = Professor(session_id="proactive").dispatch_agent_job(
                        p["task_text"], categories=p.get("categories"),
                        mode="bounded", max_steps=10, review="review",
                    )
                    st.success(
                        f"Professor is on it (job {job_id[:8]}). "
                        "Watch it and approve any changes on the Agent page."
                    )
                except Exception as exc:
                    st.error(f"Could not dispatch: {exc}")
