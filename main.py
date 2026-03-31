# main.py — Nexus Student Toolkit
# Entry point: injects CSS, initialises session state, renders sidebar,
# then routes to the active page.
#
# Architecture:
#   main.py          ← you are here
#   config.py        ← CSS theme tokens & injection
#   state.py         ← session-state defaults & helpers
#   components.py    ← shared UI helpers
#   sidebar.py       ← navigation sidebar
#   pages/
#       __init__.py  ← page registry (PAGE_MAP)
#       home.py
#       ai_assistant.py
#       notes.py
#       tasks.py
#       pomodoro.py
#       flashcards.py
#       data_explorer.py
#       math_solver.py
#       converter.py
#       password_gen.py
#       color_tools.py
#       budget.py
#       qr_generator.py
#       text_tools.py
#       habit_tracker.py
#       ocr.py        ← 📷 NEW: OCR Scanner

import streamlit as st
from config import inject_css
from state import init_state
from sidebar import render_sidebar
from pages import PAGE_MAP

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Nexus — Student Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap ────────────────────────────────────────────────────────────────
inject_css()
init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar()

# ── Router ───────────────────────────────────────────────────────────────────
page = st.session_state.page
render_fn = PAGE_MAP.get(page)

if render_fn:
    render_fn()
else:
    st.error(f"Unknown page: {page!r}. Redirecting to Home…")
    st.session_state.page = "Home"
    st.rerun()
