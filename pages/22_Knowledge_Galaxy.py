"""Knowledge Galaxy — interactive force-directed map of the whole curriculum."""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ui.theme import inject_theme, gf_header, help_button
from pages.library.map_view import render_knowledge_galaxy

inject_theme()
gf_header("Knowledge Galaxy", "Your whole curriculum as a living, navigable map.")
help_button("browsing-courses")

render_knowledge_galaxy()
