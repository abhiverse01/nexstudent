# home.py — Nexus Home Dashboard
import streamlit as st
from datetime import datetime

from config import inject_css
from state import init_state
from components import page_header, badge, progress_bar


def render():
    """Render the Home dashboard page."""
    inject_css()
    init_state()

    # ── Dynamic greeting ──────────────────────────────────────────────────────
    hour = datetime.now().hour
    if hour < 6:
        greet, icon = "Good Night", "🌙"
    elif hour < 12:
        greet, icon = "Good Morning", "☀️"
    elif hour < 17:
        greet, icon = "Good Afternoon", "🌤️"
    elif hour < 21:
        greet, icon = "Good Evening", "🌅"
    else:
        greet, icon = "Good Night", "🌙"

    page_header("Home", f"{icon} {greet}, Student!")

    # ── Gather stats ──────────────────────────────────────────────────────────
    tasks = st.session_state.tasks
    notes = st.session_state.notes
    flashcards = st.session_state.flashcards
    habits = st.session_state.habits

    tasks_done = sum(1 for t in tasks if t.get("done"))
    tasks_total = len(tasks)
    notes_count = len(notes)
    flashcards_count = len(flashcards)
    today_str = datetime.now().strftime("%Y-%m-%d")
    habits_today = sum(
        1 for h in habits.values()
        if today_str in h.get("dates", [])
    )
    habits_total = len(habits)

    # ── Hero card ─────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:linear-gradient(135deg, rgba(91,94,244,.15), '
        f'rgba(129,140,248,.08));border:1px solid var(--border);border-radius:var(--r);'
        f'padding:1.6rem 1.8rem;margin-bottom:1.4rem;">'
        f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.8rem;">'
        f'<span style="font-size:1.6rem;">⚡</span>'
        f'<span style="font-size:1.1rem;font-weight:700;color:var(--ink);'
        f'letter-spacing:-.02em;">Nexus Student Toolkit</span></div>'
        f'<p style="color:var(--ink2);font-size:.85rem;line-height:1.6;margin:0 0 1rem;">'
        f'Your all-in-one productivity hub. Track tasks, take notes, study with flashcards, '
        f'manage habits, and more — all in one place.</p>'
        f'<div style="display:flex;gap:1.2rem;flex-wrap:wrap;">'
        f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);'
        f'padding:.55rem 1rem;">'
        f'<span style="color:var(--green);font-weight:700;font-size:.9rem;font-family:DM Mono,monospace;">'
        f'{tasks_done}</span>'
        f'<span style="color:var(--ink3);font-size:.75rem;margin-left:.3rem;">Tasks Done</span></div>'
        f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);'
        f'padding:.55rem 1rem;">'
        f'<span style="color:var(--sol2);font-weight:700;font-size:.9rem;font-family:DM Mono,monospace;">'
        f'{notes_count}</span>'
        f'<span style="color:var(--ink3);font-size:.75rem;margin-left:.3rem;">Notes</span></div>'
        f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);'
        f'padding:.55rem 1rem;">'
        f'<span style="color:var(--amber);font-weight:700;font-size:.9rem;font-family:DM Mono,monospace;">'
        f'{flashcards_count}</span>'
        f'<span style="color:var(--ink3);font-size:.75rem;margin-left:.3rem;">Flashcards</span></div>'
        f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);'
        f'padding:.55rem 1rem;">'
        f'<span style="color:var(--teal);font-weight:700;font-size:.9rem;font-family:DM Mono,monospace;">'
        f'{habits_today}/{habits_total}</span>'
        f'<span style="color:var(--ink3);font-size:.75rem;margin-left:.3rem;">Habits Today</span></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tasks", f"{tasks_done}/{tasks_total}",
                  f"{tasks_done} completed" if tasks_total else None)
    with col2:
        st.metric("Notes", notes_count)
    with col3:
        st.metric("Flashcards", flashcards_count)
    with col4:
        st.metric("Habits Today", f"{habits_today}/{habits_total}")

    st.markdown('<div style="margin-top:1.2rem;"></div>', unsafe_allow_html=True)

    # ── Feature grid ──────────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="font-size:1.15rem;font-weight:700;color:var(--ink);'
        'letter-spacing:-.02em;margin-bottom:1rem;">🚀 All Features</h2>',
        unsafe_allow_html=True,
    )

    features = [
        ("🤖", "AI Assistant", "Chat with Claude for homework help, explanations, and brainstorming.", "var(--sol)", "AI Assistant"),
        ("📝", "Smart Notes", "Create, edit, and preview Markdown notes with live word count.", "var(--sol2)", "Smart Notes"),
        ("✅", "Task Manager", "Organize tasks by priority, category, and due date.", "var(--green)", "Task Manager"),
        ("🍅", "Pomodoro", "Stay focused with customizable work/break timer sessions.", "var(--rose)", "Pomodoro"),
        ("🃏", "Flashcards", "Study smarter with flip cards and self-scoring quizzes.", "var(--amber)", "Flashcards"),
        ("📊", "Data Explorer", "Upload CSV/Excel files and explore data visually.", "var(--teal)", "Data Explorer"),
        ("🧮", "Math Solver", "Solve equations, plot functions, and visualize data.", "var(--sol)", "Math Solver"),
        ("🔄", "Converter", "Convert units, currencies, temperatures, and more.", "var(--green)", "Converter"),
        ("🔐", "Password Gen", "Generate strong, random passwords with custom rules.", "var(--rose)", "Password Gen"),
        ("🎨", "Color Tools", "Pick, convert, and explore color palettes.", "var(--amber)", "Color Tools"),
        ("💰", "Budget Tracker", "Track income and expenses with category breakdowns.", "var(--green)", "Budget Tracker"),
        ("📱", "QR Generator", "Generate and download QR codes for any text or URL.", "var(--sol2)", "QR Generator"),
        ("✂️", "Text Tools", "Transform text — case, encode, decode, word count, and more.", "var(--teal)", "Text Tools"),
        ("📈", "Habit Tracker", "Build daily habits with streaks and visual calendar.", "var(--amber)", "Habit Tracker"),
        ("📸", "OCR Scanner", "Extract text from images using optical character recognition.", "var(--rose)", "OCR Scanner"),
        ("📋", "Markdown Preview", "Write and preview Markdown with a live editor.", "var(--teal)", "Markdown Preview"),
    ]

    # Render 3-column grid
    for i in range(0, len(features), 3):
        row = features[i:i + 3]
        cols = st.columns(len(row))
        for idx, (feat_icon, feat_name, feat_desc, feat_color, page_name) in enumerate(row):
            with cols[idx]:
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    f'border-radius:var(--r);padding:1.2rem 1.1rem;height:100%;'
                    f'display:flex;flex-direction:column;">'
                    f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem;">'
                    f'<span style="font-size:1.3rem;">{feat_icon}</span>'
                    f'<span style="font-weight:700;font-size:.88rem;color:var(--ink);'
                    f'letter-spacing:-.01em;">{feat_name}</span></div>'
                    f'<p style="color:var(--ink2);font-size:.78rem;line-height:1.55;'
                    f'margin:0 0 .8rem;flex:1;">{feat_desc}</p>'
                    f'<div style="margin-top:auto;">'
                    f'<a href="#" onclick="return false;" style="color:{feat_color};'
                    f'font-size:.78rem;font-weight:600;text-decoration:none;">'
                    f'Open →</a></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Open {feat_name}", key=f"feat_{feat_name}", use_container_width=True):
                    st.session_state.page = page_name
                    st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    year = datetime.now().year
    st.markdown(
        f'<div style="text-align:center;padding:2rem 0 .5rem;color:var(--ink3);'
        f'font-size:.78rem;letter-spacing:.02em;">'
        f'⚡ NEXUS · {year}</div>',
        unsafe_allow_html=True,
    )
