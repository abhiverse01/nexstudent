# state.py — Session state management
import streamlit as st
import uuid as _uuid

DEFAULTS = {
    "page": "Home",
    "tasks": [],
    "notes": {},
    "flashcards": [],
    "habits": {},
    "budget_items": [],
    "chat_history": [],
    "active_card": 0,
    "show_answer": False,
    "quiz_score": 0,
    "quiz_total": 0,
    "_passwords": [],
    "_qr_img": None,
    "_qr_data": "",
    "_qr_size": 250,
    "_transformed": "",
    "_tx_name": "",
    "_quiz_idx": 0,
    "_active_note": None,
    # Pomodoro enhancements
    "pomodoro_running": False,
    "pomodoro_end": None,
    "pomodoro_sessions": 0,
    "pomodoro_total_mins": 0,
}


def init_state():
    """Ensure all session-state keys exist with sensible defaults."""
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_all():
    """Clear every tracked value back to defaults."""
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


def export_state() -> dict:
    """Return a JSON-safe snapshot of all persistent session data."""
    import json, copy
    snapshot = {}
    for k, v in DEFAULTS.items():
        snapshot[k] = copy.deepcopy(st.session_state.get(k, v))
    return snapshot


def import_state(data: dict):
    """Restore session state from a previously exported snapshot."""
    for k in DEFAULTS:
        if k in data:
            st.session_state[k] = data[k]
