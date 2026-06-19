"""Advanced course hierarchy map tab for the Library page."""
from __future__ import annotations

import streamlit as st

from core.database import get_lectures, get_pacing_for_course, get_progress
from ui.theme import progress_badge, section_divider


def _render_lesson_list(modules: list[dict], max_rows: int = 10) -> None:
    shown = 0
    for module in modules:
        if shown >= max_rows:
            break
        lectures = get_lectures(module["id"])
        st.markdown(f"**{module['title']}**")
        for lecture in lectures:
            progress = get_progress(lecture["id"])
            badge = progress_badge(progress.get("status", "not_started"))
            st.markdown(f"- {lecture['title']} {badge}", unsafe_allow_html=True)
            shown += 1
            if shown >= max_rows:
                break


def render_course_map(root_courses: list[dict], sub_course_map: dict[str, list[dict]], course_summary_fn) -> None:
    section_divider("Course Map")
    st.markdown("Full hierarchy view for advanced planning.")

    def _render(course: dict, indent: int = 0) -> None:
        summary = course_summary_fn(course, sub_course_map)
        children = summary["children"]
        readiness = summary["readiness"]
        label = (
            f"{'  ' * indent}{course['id']}  {course['title']} "
            f"({summary['total_lectures']} lessons, {course['credits']} cr)"
        )
        if children:
            label += f"  [{len(children)} sub-courses]"
        if readiness["ai_ready"]:
            label += "  [AI-ready]"

        # Only top-level courses get expanders; children use indented containers
        if indent == 0:
            with st.expander(label, expanded=False):
                _render_course_body(course, summary, children, indent)
        else:
            # Indented sub-course rendered flat (no nested expander)
            indent_px = indent * 24
            st.markdown(
                f"<div style='border-left:2px solid #00d4ff44;padding:6px 12px;"
                f"margin-left:{indent_px}px;margin-bottom:4px;background:#0a1020;'>"
                f"<span style='color:#00d4ff;font-family:monospace;font-size:0.85rem;'>"
                f"↳ {course['title']}</span>"
                f"<span style='color:#606080;font-size:0.78rem;'>"
                f"  ({summary['total_lectures']} lessons, {course['credits']} cr) "
                f"| {summary['completion_pct']:.0f}% complete"
                f"</span></div>",
                unsafe_allow_html=True,
            )
            # Show child sub-courses recursively (still flat, just more indent)
            for child in children:
                _render(child, indent + 1)

    def _render_course_body(course, summary, children, indent):
        st.caption(course.get("description") or "No description")
        st.caption(
            f"Completion: {summary['completion_pct']:.0f}% | "
            f"Pacing: {get_pacing_for_course(course['id'])} | "
            f"Depth: {course.get('depth_level') or 0}"
        )
        if course.get("parent_course_id"):
            st.caption(f"Parent: {course['parent_course_id']}")
        _render_lesson_list(summary["modules"], max_rows=10)
        for child in children:
            _render(child, indent + 1)

    for course in root_courses:
        _render(course)


# ─── Knowledge Galaxy (interactive force-directed map) ────────────────────────

_GALAXY_PALETTE = [
    "#00d4ff", "#40dc80", "#ffd700", "#ff6f91", "#a78bfa",
    "#22d3ee", "#f59e0b", "#34d399", "#f472b6", "#60a5fa",
]


def render_knowledge_galaxy(max_nodes: int = 160) -> None:
    """Render the whole curriculum as an interactive force-directed graph.

    Nodes are courses (size by credits, colour by subject; jargon courses dimmed);
    edges are parent->child decomposition links. Clicking a node reveals its detail
    and mastery, with a jump into study.
    """
    from core.database import get_all_courses, get_competency_profile
    try:
        from streamlit_agraph import agraph, Node, Edge, Config
    except Exception:
        st.error("Knowledge Galaxy needs the `streamlit-agraph` package "
                 "(`pip install streamlit-agraph`).")
        return

    courses = get_all_courses()
    if not courses:
        st.info("No courses yet — import or generate some first.")
        return

    section_divider("Knowledge Galaxy")
    st.caption(
        "Every star is a course — size by credits, links show how courses decompose. "
        "Drag to explore, scroll to zoom, click a star for detail."
    )

    if len(courses) > max_nodes:
        st.caption(f"Showing the first {max_nodes} of {len(courses)} courses for performance.")
        courses = courses[:max_nodes]

    ids = {str(c["id"]) for c in courses}
    subj_color: dict[str, str] = {}
    nodes, edges = [], []
    for c in courses:
        cid = str(c["id"])
        credits = c.get("credits") or 0
        try:
            size = 12 + min(int(credits), 8) * 3
        except (TypeError, ValueError):
            size = 14
        subj = str(c.get("subject_id") or "general")
        color = subj_color.setdefault(subj, _GALAXY_PALETTE[len(subj_color) % len(_GALAXY_PALETTE)])
        if c.get("is_jargon_course"):
            color = "#8a8aae"
        label = (c.get("title") or cid)[:26]
        nodes.append(Node(id=cid, label=label, size=size, color=color))
        parent = c.get("parent_course_id")
        if parent and str(parent) in ids:
            edges.append(Edge(source=str(parent), target=cid, color="#33415588"))

    config = Config(
        width=1100, height=650, directed=True, physics=True, hierarchical=False,
        nodeHighlightBehavior=True, highlightColor="#00d4ff", collapsible=False,
    )
    selected = agraph(nodes=nodes, edges=edges, config=config)

    if selected:
        course = next((c for c in courses if str(c["id"]) == str(selected)), None)
        if course:
            st.markdown(f"### {course.get('title', selected)}")
            if course.get("description"):
                st.caption(course["description"])
            st.caption(
                f"Credits: {course.get('credits', 0)} | "
                f"Depth: {course.get('depth_level') or 0}"
                + (" | jargon course" if course.get("is_jargon_course") else "")
            )
            try:
                prof = get_competency_profile(str(course["id"]))
                mastery = ", ".join(
                    f"{k}: {v:.0f}%" for k, v in (prof or {}).items()
                    if isinstance(v, (int, float))
                )
                if mastery:
                    st.caption("Mastery — " + mastery)
            except Exception:
                pass
            st.page_link("pages/02_Lecture_Studio.py", label="Study this course")
