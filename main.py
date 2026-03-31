import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, random, string, math, hashlib, base64, io, re, time, datetime
from sympy import symbols, solve, simplify, expand, factor, diff, integrate, sympify, latex
from sympy.parsing.sympy_parser import parse_expr
import qrcode
from PIL import Image, ImageDraw, ImageFilter

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus — Student Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  /* ── Root Variables ── */
  :root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --card:     #16161f;
    --border:   #1e1e2e;
    --accent:   #7c6af7;
    --accent2:  #f06292;
    --accent3:  #4dd0e1;
    --text:     #e2e2f0;
    --muted:    #6b6b8a;
    --success:  #4caf50;
    --warning:  #ffc107;
    --danger:   #f44336;
    --radius:   14px;
    --shadow:   0 8px 32px rgba(0,0,0,0.4);
  }

  /* ── Global Reset ── */
  html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }
  .main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1200px; }

  /* ── Hide Streamlit Chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] .block-container { padding: 1rem 0.8rem; }

  /* ── Cards ── */
  .nx-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    transition: border-color .25s;
  }
  .nx-card:hover { border-color: #2e2e4e; }

  /* ── Section Headings ── */
  .nx-section-title {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .25rem;
    letter-spacing: -.02em;
  }
  .nx-section-sub {
    color: var(--muted);
    font-size: .85rem;
    margin-bottom: 1.4rem;
    font-weight: 400;
  }

  /* ── Badges ── */
  .nx-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
  }
  .nx-badge-purple { background: rgba(124,106,247,.18); color: var(--accent); border: 1px solid rgba(124,106,247,.3); }
  .nx-badge-cyan   { background: rgba(77,208,225,.15);  color: var(--accent3); border: 1px solid rgba(77,208,225,.25); }
  .nx-badge-pink   { background: rgba(240,98,146,.15);  color: var(--accent2); border: 1px solid rgba(240,98,146,.25); }

  /* ── Stat boxes ── */
  .nx-stat {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .nx-stat-num { font-size: 2rem; font-weight: 800; color: var(--accent); }
  .nx-stat-label { font-size: .78rem; color: var(--muted); font-weight: 500; }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div,
  .stNumberInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: .88rem !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,.15) !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, var(--accent), #a78bfa) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    padding: .5rem 1.4rem !important;
    transition: opacity .2s, transform .15s !important;
    letter-spacing: .02em !important;
  }
  .stButton > button:hover { opacity: .88; transform: translateY(-1px); }
  .stButton > button:active { transform: translateY(0); }

  /* Secondary button variant */
  .btn-secondary > button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
  }

  /* ── Metrics ── */
  [data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: .8rem 1rem;
  }
  [data-testid="metric-container"] > div > div:first-child {
    color: var(--muted) !important; font-size: .78rem !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important; font-weight: 700 !important; color: var(--text) !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: .4rem 1rem !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: .82rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    background: transparent !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #fff !important;
  }

  /* ── Expanders ── */
  .streamlit-expanderHeader {
    background: var(--card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    color: var(--text) !important;
  }
  .streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius) var(--radius) !important;
  }

  /* ── Sliders ── */
  .stSlider > div > div > div > div {
    background: var(--accent) !important;
  }

  /* ── Dataframes ── */
  .stDataFrame { border-radius: var(--radius) !important; overflow: hidden !important; }

  /* ── Code blocks ── */
  code, pre {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: .82rem !important;
    color: var(--accent3) !important;
  }

  /* ── Dividers ── */
  hr { border-color: var(--border) !important; margin: 1.2rem 0; }

  /* ── Checkboxes ── */
  .stCheckbox > label { font-size: .88rem !important; }

  /* ── Sidebar nav pill ── */
  .nav-pill {
    display: flex; align-items: center; gap: .7rem;
    padding: .6rem .9rem;
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s;
    font-size: .88rem;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 2px;
  }
  .nav-pill:hover { background: rgba(124,106,247,.12); color: var(--text); }
  .nav-pill.active { background: rgba(124,106,247,.2); color: var(--accent); font-weight: 600; }
  .nav-icon { font-size: 1rem; }

  /* ── Hero banner ── */
  .nx-hero {
    background: linear-gradient(135deg, rgba(124,106,247,.12), rgba(77,208,225,.08));
    border: 1px solid rgba(124,106,247,.2);
    border-radius: 18px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
  }
  .nx-hero::before {
    content:'';
    position:absolute; top:-60px; right:-60px;
    width:200px; height:200px;
    background: radial-gradient(circle, rgba(124,106,247,.25), transparent 70%);
    border-radius: 50%;
  }
  .nx-hero-title {
    font-size: 2.2rem; font-weight: 800; letter-spacing: -.03em;
    background: linear-gradient(135deg, #fff 30%, var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .nx-hero-sub { color: var(--muted); font-size: .92rem; margin-top: .3rem; }

  /* ── Flashcard ── */
  .flashcard {
    background: linear-gradient(135deg, rgba(124,106,247,.15), rgba(240,98,146,.08));
    border: 1px solid rgba(124,106,247,.3);
    border-radius: 18px;
    padding: 2.5rem;
    text-align: center;
    min-height: 180px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    cursor: pointer;
    transition: transform .2s;
  }
  .flashcard:hover { transform: scale(1.01); }
  .flashcard-q { font-size: 1.1rem; font-weight: 600; margin-bottom: .5rem; }
  .flashcard-a { font-size: .95rem; color: var(--accent3); }

  /* ── Task item ── */
  .task-item {
    display: flex; align-items: center; gap: .8rem;
    padding: .7rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: .5rem;
    transition: border-color .2s;
  }
  .task-item:hover { border-color: var(--accent); }
  .task-item.done { opacity: .5; text-decoration: line-through; }

  /* ── Progress bar ── */
  .nx-progress-wrap { background: var(--surface); border-radius: 99px; height: 8px; overflow: hidden; }
  .nx-progress-bar  { background: linear-gradient(90deg, var(--accent), var(--accent3)); border-radius: 99px; height: 100%; transition: width .5s; }

  /* ── Timer display ── */
  .nx-timer {
    font-size: 4.5rem; font-weight: 800; letter-spacing: -.04em;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; line-height: 1;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--muted); }

  /* ── Multiselect ── */
  .stMultiSelect > div > div { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }

  /* ── Radio & selectbox ── */
  .stRadio > div { gap: .5rem; }
  .stRadio label { font-size: .88rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State Defaults ────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "Home",
        "tasks": [],
        "notes": {},
        "flashcards": [],
        "habits": {},
        "budget_items": [],
        "chat_history": [],
        "pomodoro_mins": 25,
        "pomodoro_running": False,
        "pomodoro_end": None,
        "active_card": 0,
        "show_answer": False,
        "quiz_score": 0,
        "quiz_total": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.6rem 0 1.4rem;">
      <div style="font-size:2rem;">⚡</div>
      <div style="font-size:1.2rem;font-weight:800;letter-spacing:-.03em;color:#e2e2f0;">Nexus</div>
      <div style="font-size:.72rem;color:#6b6b8a;font-weight:400;">Student Toolkit</div>
    </div>
    """, unsafe_allow_html=True)

    NAV = [
        ("🏠", "Home"),
        ("🤖", "AI Assistant"),
        ("📝", "Smart Notes"),
        ("✅", "Task Manager"),
        ("⏱️", "Pomodoro"),
        ("🃏", "Flashcards"),
        ("📊", "Data Explorer"),
        ("🧮", "Math Solver"),
        ("🔄", "Converter"),
        ("🔐", "Password Gen"),
        ("🎨", "Color Tools"),
        ("💰", "Budget Tracker"),
        ("📱", "QR Generator"),
        ("✍️", "Text Tools"),
        ("🎯", "Habit Tracker"),
    ]

    for icon, label in NAV:
        active = st.session_state.page == label
        cls = "nav-pill active" if active else "nav-pill"
        if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}",
                             use_container_width=True):
            st.session_state.page = label
            st.rerun()

    st.markdown("<div style='margin-top:2rem;padding:0 .5rem'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(124,106,247,.08);border:1px solid rgba(124,106,247,.2);
    border-radius:12px;padding:.8rem 1rem;font-size:.75rem;color:#6b6b8a;'>
      <div style='color:#7c6af7;font-weight:600;margin-bottom:.3rem;'>💡 Quick tip</div>
      Use Pomodoro + Flashcards for the ultimate study session.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Helper functions ──────────────────────────────────────────────────────────
def card(content):
    return f'<div class="nx-card">{content}</div>'

def badge(text, style="purple"):
    return f'<span class="nx-badge nx-badge-{style}">{text}</span>'

def section_header(title, sub=""):
    st.markdown(f'<div class="nx-section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="nx-section-sub">{sub}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":
    now = datetime.datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    st.markdown(f"""
    <div class="nx-hero">
      <p class="nx-hero-title">{greeting} ✨</p>
      <p class="nx-hero-sub">Welcome to Nexus — your all-in-one student & productivity toolkit.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    tasks_done = sum(1 for t in st.session_state.tasks if t.get("done"))
    tasks_total = len(st.session_state.tasks)
    notes_count = len(st.session_state.notes)
    cards_count = len(st.session_state.flashcards)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📋 Tasks", f"{tasks_done}/{tasks_total}")
    with c2:
        st.metric("📝 Notes", notes_count)
    with c3:
        st.metric("🃏 Flashcards", cards_count)
    with c4:
        habits_today = sum(
            1 for h, days in st.session_state.habits.items()
            if str(datetime.date.today()) in days
        )
        st.metric("🎯 Habits Today", habits_today)

    st.markdown("---")

    # Feature grid
    section_header("✨ Explore Features", "Click any card to jump straight in")

    FEATURES = [
        ("🤖", "AI Assistant",   "Chat with Claude for help, explanations & ideas",   "accent"),
        ("📝", "Smart Notes",    "Rich markdown notes, searchable and organised",      "cyan"),
        ("✅", "Task Manager",   "Prioritised to-do list with categories",             "pink"),
        ("⏱️", "Pomodoro",       "Focus timer with work/break intervals",              "accent"),
        ("🃏", "Flashcards",     "Create, quiz and track your study progress",         "cyan"),
        ("📊", "Data Explorer",  "Upload CSV and generate instant charts",             "pink"),
        ("🧮", "Math Solver",    "Algebra, calculus, symbolic math & statistics",      "accent"),
        ("🔄", "Converter",      "Units, currency, number bases & more",               "cyan"),
        ("🔐", "Password Gen",   "Cryptographically strong password generation",       "pink"),
        ("🎨", "Color Tools",    "Palette generator, gradients & colour theory",       "accent"),
        ("💰", "Budget Tracker", "Track income, expenses and savings goals",           "cyan"),
        ("📱", "QR Generator",   "Instant QR codes for any URL or text",               "pink"),
        ("✍️", "Text Tools",     "Word count, case tools, Lorem ipsum & diff",         "accent"),
        ("🎯", "Habit Tracker",  "Build streaks and visualise consistency",            "cyan"),
    ]

    cols = st.columns(3)
    for i, (icon, name, desc, color) in enumerate(FEATURES):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="nx-card" style="cursor:pointer;padding:1rem 1.2rem;">
              <div style="font-size:1.6rem;margin-bottom:.4rem;">{icon}</div>
              <div style="font-weight:600;font-size:.92rem;margin-bottom:.3rem;">{name}</div>
              <div style="font-size:.78rem;color:#6b6b8a;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open →", key=f"home_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='text-align:center;color:#3a3a5c;font-size:.76rem;'>⚡ Nexus · {now.strftime('%A, %B %d %Y')}</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: AI ASSISTANT
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "AI Assistant":
    section_header("🤖 AI Assistant", "Powered by Claude — ask anything")

    SYSTEM_PRESETS = {
        "General Assistant": "You are a helpful, concise assistant. Keep responses clear and well-structured.",
        "Study Tutor": "You are an expert academic tutor. Explain concepts clearly, use examples, and check understanding.",
        "Code Helper": "You are a senior software engineer. Write clean, well-commented code with explanations.",
        "Essay Writer": "You are an academic writing coach. Help structure arguments, improve clarity and flow.",
        "Math Wizard": "You are a mathematics professor. Solve problems step-by-step with full explanations.",
        "Debate Partner": "You are a debate coach. Present balanced arguments from multiple perspectives.",
    }

    col1, col2 = st.columns([3, 1])
    with col1:
        preset = st.selectbox("Persona", list(SYSTEM_PRESETS.keys()), label_visibility="collapsed")
    with col2:
        if st.button("🗑️ Clear chat"):
            st.session_state.chat_history = []
            st.rerun()

    system_prompt = SYSTEM_PRESETS[preset]

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:.8rem;">
                  <div style="background:rgba(124,106,247,.2);border:1px solid rgba(124,106,247,.3);
                  border-radius:14px 14px 4px 14px;padding:.7rem 1rem;max-width:75%;font-size:.88rem;">
                    {content}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:.8rem;">
                  <div style="background:var(--card);border:1px solid var(--border);
                  border-radius:14px 14px 14px 4px;padding:.7rem 1rem;max-width:80%;font-size:.88rem;">
                    {content}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            user_input = st.text_input("Message", placeholder="Ask anything…", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Send ✈️")

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        try:
            import requests as req
            messages = [{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_history]
            resp = req.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": messages,
                }
            )
            data = resp.json()
            reply = data["content"][0]["text"]
        except Exception as e:
            reply = f"⚠️ Error connecting to AI: {e}"

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#3a3a5c;">
          <div style="font-size:3rem;margin-bottom:.8rem;">🤖</div>
          <div style="font-size:.9rem;">Start a conversation above. Try asking:<br>
          <span style="color:#6b6b8a;">"Explain photosynthesis simply"</span> ·
          <span style="color:#6b6b8a;">"Write a Python sorting function"</span> ·
          <span style="color:#6b6b8a;">"Help me outline an essay"</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: SMART NOTES
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Smart Notes":
    section_header("📝 Smart Notes", "Markdown-powered notes with instant preview")

    col_list, col_editor = st.columns([1, 2])

    with col_list:
        st.markdown("**Your Notes**")
        new_title = st.text_input("New note title", placeholder="My note…")
        if st.button("➕ Create"):
            if new_title.strip() and new_title not in st.session_state.notes:
                st.session_state.notes[new_title] = f"# {new_title}\n\nStart writing…"
                st.rerun()

        selected_note = None
        for title in list(st.session_state.notes.keys()):
            cols = st.columns([4, 1])
            with cols[0]:
                if st.button(f"📄 {title}", key=f"note_{title}", use_container_width=True):
                    st.session_state["_active_note"] = title
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"del_{title}"):
                    del st.session_state.notes[title]
                    if st.session_state.get("_active_note") == title:
                        st.session_state.pop("_active_note", None)
                    st.rerun()

    with col_editor:
        active = st.session_state.get("_active_note")
        if active and active in st.session_state.notes:
            st.markdown(f"**Editing:** `{active}`")
            tabs = st.tabs(["✏️ Edit", "👁️ Preview"])
            with tabs[0]:
                content = st.text_area("", value=st.session_state.notes[active],
                                       height=380, label_visibility="collapsed",
                                       key="note_editor")
                st.session_state.notes[active] = content
            with tabs[1]:
                st.markdown(st.session_state.notes[active])

            # Stats
            words = len(st.session_state.notes[active].split())
            chars = len(st.session_state.notes[active])
            st.markdown(f"""
            <div style="display:flex;gap:.8rem;margin-top:.5rem;">
              <span class="nx-badge nx-badge-purple">{words} words</span>
              <span class="nx-badge nx-badge-cyan">{chars} chars</span>
            </div>
            """, unsafe_allow_html=True)

            # Download
            content_bytes = st.session_state.notes[active].encode()
            st.download_button("⬇️ Download .md", content_bytes, file_name=f"{active}.md",
                               mime="text/markdown")
        else:
            st.markdown("""
            <div style="text-align:center;padding:4rem;color:#3a3a5c;">
              <div style="font-size:3rem;">📝</div>
              <div style="margin-top:.5rem;">Select or create a note on the left</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: TASK MANAGER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Task Manager":
    section_header("✅ Task Manager", "Stay on top of your workload")

    col_add, col_tasks = st.columns([1, 2])

    with col_add:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**Add Task**")
        t_name = st.text_input("Task name", placeholder="Finish assignment…")
        t_pri  = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🟢 Low"])
        t_cat  = st.selectbox("Category", ["📚 Study", "💻 Work", "🏠 Personal", "🏋️ Health", "🎯 Goals"])
        t_due  = st.date_input("Due date", value=None)
        if st.button("➕ Add Task", use_container_width=True):
            if t_name.strip():
                st.session_state.tasks.append({
                    "name": t_name, "priority": t_pri, "category": t_cat,
                    "due": str(t_due) if t_due else None, "done": False,
                    "id": len(st.session_state.tasks)
                })
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Summary
        total = len(st.session_state.tasks)
        done  = sum(1 for t in st.session_state.tasks if t["done"])
        pct   = int(done / total * 100) if total else 0
        st.markdown(f"""
        <div class="nx-card" style="margin-top:.5rem;">
          <div style="font-weight:600;font-size:.85rem;margin-bottom:.8rem;">Progress</div>
          <div class="nx-progress-wrap">
            <div class="nx-progress-bar" style="width:{pct}%"></div>
          </div>
          <div style="font-size:.78rem;color:#6b6b8a;margin-top:.5rem;">{done}/{total} completed · {pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_tasks:
        filter_cat = st.selectbox("Filter", ["All", "📚 Study", "💻 Work", "🏠 Personal", "🏋️ Health", "🎯 Goals"],
                                   label_visibility="collapsed")
        show_done = st.checkbox("Show completed", value=True)

        tasks_to_show = [t for t in st.session_state.tasks
                         if (filter_cat == "All" or t["category"] == filter_cat)
                         and (show_done or not t["done"])]

        # Sort by priority
        pri_order = {"🔴 High": 0, "🟡 Medium": 1, "🟢 Low": 2}
        tasks_to_show.sort(key=lambda x: pri_order.get(x["priority"], 9))

        if not tasks_to_show:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#3a3a5c;">
              <div style="font-size:2.5rem;">🎉</div>
              <div>No tasks here!</div>
            </div>
            """, unsafe_allow_html=True)

        for i, task in enumerate(tasks_to_show):
            idx = st.session_state.tasks.index(task)
            col_chk, col_info, col_del = st.columns([1, 6, 1])
            with col_chk:
                checked = st.checkbox("", value=task["done"], key=f"task_chk_{idx}")
                st.session_state.tasks[idx]["done"] = checked
            with col_info:
                done_style = "opacity:.5;text-decoration:line-through;" if task["done"] else ""
                due_str = f" · Due {task['due']}" if task.get("due") else ""
                st.markdown(f"""
                <div style="padding:.3rem 0;{done_style}">
                  <div style="font-weight:500;font-size:.9rem;">{task['name']}</div>
                  <div style="font-size:.76rem;color:#6b6b8a;">
                    {task['priority']} · {task['category']}{due_str}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"task_del_{idx}"):
                    st.session_state.tasks.pop(idx)
                    st.rerun()

        if st.session_state.tasks:
            st.markdown("---")
            if st.button("🗑️ Clear completed"):
                st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: POMODORO
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Pomodoro":
    section_header("⏱️ Pomodoro Timer", "Deep focus with structured breaks")

    col_timer, col_settings = st.columns([1, 1])

    with col_settings:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**Timer Settings**")
        work_min  = st.slider("Work (min)", 1, 60, 25)
        break_min = st.slider("Break (min)", 1, 30, 5)
        long_break = st.slider("Long break (min)", 5, 45, 15)
        st.markdown("**Session Goal**")
        goal_text = st.text_input("What will you work on?", placeholder="Chapter 4 revision…")
        st.markdown("</div>", unsafe_allow_html=True)

        # Pomodoro tips
        st.markdown("""
        <div class="nx-card" style="margin-top:.5rem;">
          <div style="font-weight:600;font-size:.85rem;margin-bottom:.6rem;">📖 Pomodoro Tips</div>
          <div style="font-size:.78rem;color:#6b6b8a;line-height:1.7;">
            • Work for 25 minutes, then take a 5-minute break<br>
            • After 4 pomodoros, take a 15-30 min break<br>
            • Remove all distractions before starting<br>
            • Track what you accomplish each session
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_timer:
        st.markdown('<div class="nx-card" style="text-align:center;padding:2.5rem;">', unsafe_allow_html=True)

        mode = st.radio("Mode", ["🎯 Work", "☕ Short Break", "🌙 Long Break"], horizontal=True)

        mins = work_min if "Work" in mode else long_break if "Long" in mode else break_min

        now = datetime.datetime.now()
        if st.session_state.pomodoro_running and st.session_state.pomodoro_end:
            remaining = st.session_state.pomodoro_end - now
            secs = max(0, int(remaining.total_seconds()))
        else:
            secs = mins * 60

        m, s = divmod(secs, 60)
        st.markdown(f'<div class="nx-timer">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)

        progress_pct = max(0, secs / (mins * 60)) if mins > 0 else 0
        st.markdown(f"""
        <div class="nx-progress-wrap" style="margin: 1.2rem 0;">
          <div class="nx-progress-bar" style="width:{int((1-progress_pct)*100)}%"></div>
        </div>
        """, unsafe_allow_html=True)

        if goal_text:
            st.markdown(f'<div style="font-size:.82rem;color:#6b6b8a;margin-bottom:.8rem;">🎯 {goal_text}</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶ Start", use_container_width=True):
                st.session_state.pomodoro_running = True
                st.session_state.pomodoro_end = now + datetime.timedelta(minutes=mins)
                st.rerun()
        with c2:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state.pomodoro_running = False
                st.rerun()
        with c3:
            if st.button("↺ Reset", use_container_width=True):
                st.session_state.pomodoro_running = False
                st.session_state.pomodoro_end = None
                st.rerun()

        if st.session_state.pomodoro_running and secs == 0:
            st.success("🎉 Timer complete! Time for a break.")
            st.session_state.pomodoro_running = False

        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.pomodoro_running:
            time.sleep(1)
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: FLASHCARDS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Flashcards":
    section_header("🃏 Flashcards", "Create, study and track your learning")

    tab_create, tab_study, tab_quiz = st.tabs(["➕ Create", "📖 Study", "🧠 Quiz Mode"])

    with tab_create:
        col1, col2 = st.columns(2)
        with col1:
            fc_q = st.text_area("Question / Front", height=120)
        with col2:
            fc_a = st.text_area("Answer / Back", height=120)

        fc_tag = st.text_input("Tag / Subject", placeholder="Biology, Math, History…")

        if st.button("➕ Add Flashcard", use_container_width=True):
            if fc_q.strip() and fc_a.strip():
                st.session_state.flashcards.append({
                    "q": fc_q, "a": fc_a, "tag": fc_tag,
                    "reviewed": 0, "correct": 0
                })
                st.success(f"Card added! Total: {len(st.session_state.flashcards)}")
                st.rerun()

        if st.session_state.flashcards:
            st.markdown("---")
            st.markdown(f"**All Cards ({len(st.session_state.flashcards)})**")
            for i, fc in enumerate(st.session_state.flashcards):
                with st.expander(f"{'📌 ' + fc['tag'] + ' · ' if fc['tag'] else ''}Q: {fc['q'][:60]}…"):
                    st.markdown(f"**Q:** {fc['q']}")
                    st.markdown(f"**A:** {fc['a']}")
                    col_tag, col_del = st.columns([4, 1])
                    with col_tag:
                        if fc["tag"]:
                            st.markdown(f'<span class="nx-badge nx-badge-purple">{fc["tag"]}</span>', unsafe_allow_html=True)
                    with col_del:
                        if st.button("Delete", key=f"fc_del_{i}"):
                            st.session_state.flashcards.pop(i)
                            st.rerun()

    with tab_study:
        if not st.session_state.flashcards:
            st.info("Create some flashcards first!")
        else:
            tags = list(set(fc["tag"] for fc in st.session_state.flashcards if fc["tag"]))
            filter_tag = st.selectbox("Filter by tag", ["All"] + tags) if tags else "All"

            deck = [fc for fc in st.session_state.flashcards
                    if filter_tag == "All" or fc["tag"] == filter_tag]

            if not deck:
                st.warning("No cards in this filter.")
            else:
                idx = st.session_state.active_card % len(deck)
                card = deck[idx]

                if not st.session_state.show_answer:
                    st.markdown(f"""
                    <div class="flashcard">
                      <div style="font-size:.75rem;color:#6b6b8a;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.08em;">Question</div>
                      <div class="flashcard-q">{card['q']}</div>
                      <div style="font-size:.78rem;color:#3a3a5c;margin-top:1rem;">Click to reveal answer</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="flashcard">
                      <div style="font-size:.75rem;color:#6b6b8a;margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.08em;">Answer</div>
                      <div class="flashcard-q">{card['q']}</div>
                      <div style="width:40px;height:2px;background:rgba(124,106,247,.3);margin:.6rem auto;"></div>
                      <div class="flashcard-a">{card['a']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👁️ Flip card", use_container_width=True):
                        st.session_state.show_answer = not st.session_state.show_answer
                        st.rerun()
                with col2:
                    if st.button("← Previous", use_container_width=True):
                        st.session_state.active_card = (idx - 1) % len(deck)
                        st.session_state.show_answer = False
                        st.rerun()
                with col3:
                    if st.button("Next →", use_container_width=True):
                        st.session_state.active_card = (idx + 1) % len(deck)
                        st.session_state.show_answer = False
                        st.rerun()

                st.markdown(f'<div style="text-align:center;color:#6b6b8a;font-size:.78rem;margin-top:.6rem;">Card {idx+1} of {len(deck)}</div>', unsafe_allow_html=True)

    with tab_quiz:
        if not st.session_state.flashcards:
            st.info("Create some flashcards first!")
        else:
            st.markdown(f"""
            <div class="nx-card">
              <div style="font-size:.85rem;margin-bottom:.5rem;">📊 Quiz Stats</div>
              <div style="display:flex;gap:2rem;">
                <div><div class="nx-stat-num" style="font-size:1.8rem;">{st.session_state.quiz_score}</div><div class="nx-stat-label">Correct</div></div>
                <div><div class="nx-stat-num" style="font-size:1.8rem;">{st.session_state.quiz_total}</div><div class="nx-stat-label">Total</div></div>
                <div><div class="nx-stat-num" style="font-size:1.8rem;">{int(st.session_state.quiz_score/st.session_state.quiz_total*100) if st.session_state.quiz_total else 0}%</div><div class="nx-stat-label">Accuracy</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if "_quiz_idx" not in st.session_state:
                st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards)-1)

            q_idx = st.session_state["_quiz_idx"] % len(st.session_state.flashcards)
            quiz_card = st.session_state.flashcards[q_idx]

            st.markdown(f"**Q: {quiz_card['q']}**")
            guess = st.text_area("Your answer", height=80)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Mark Correct"):
                    st.session_state.quiz_score += 1
                    st.session_state.quiz_total += 1
                    st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards)-1)
                    st.rerun()
            with c2:
                if st.button("❌ Mark Wrong"):
                    st.session_state.quiz_total += 1
                    st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards)-1)
                    st.rerun()

            with st.expander("👁️ Reveal Answer"):
                st.markdown(f"**{quiz_card['a']}**")

            if st.button("Reset Stats"):
                st.session_state.quiz_score = 0
                st.session_state.quiz_total = 0
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: DATA EXPLORER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Data Explorer":
    section_header("📊 Data Explorer", "Upload a CSV and generate instant visualisations")

    uploaded = st.file_uploader("Upload CSV file", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.markdown(f'<div style="display:flex;gap:.6rem;margin-bottom:.8rem;">{badge(f"{len(df)} rows","purple")}{badge(f"{len(df.columns)} cols","cyan")}</div>', unsafe_allow_html=True)

        tab_data, tab_stats, tab_viz, tab_corr = st.tabs(["🗃️ Data", "📈 Statistics", "🎨 Visualise", "🔗 Correlations"])

        with tab_data:
            search = st.text_input("🔍 Search / filter rows", placeholder="Type to filter…")
            if search:
                mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                st.dataframe(df[mask], use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

        with tab_stats:
            st.dataframe(df.describe(), use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Missing Values**")
                nulls = df.isnull().sum()
                st.dataframe(nulls[nulls > 0].rename("Missing"), use_container_width=True)
            with col2:
                st.markdown("**Data Types**")
                st.dataframe(df.dtypes.rename("Type"), use_container_width=True)

        with tab_viz:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            cat_cols = df.select_dtypes(exclude="number").columns.tolist()
            all_cols = df.columns.tolist()

            chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Box", "Pie", "Area"])
            c1, c2 = st.columns(2)
            with c1:
                x_col = st.selectbox("X axis", all_cols)
            with c2:
                y_col = st.selectbox("Y axis", num_cols if num_cols else all_cols)

            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols)
            clr = None if color_col == "None" else color_col

            try:
                fig = None
                if chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=y_col, color=clr, template="plotly_dark")
                elif chart_type == "Line":
                    fig = px.line(df, x=x_col, y=y_col, color=clr, template="plotly_dark")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_col, y=y_col, color=clr, template="plotly_dark")
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_col, color=clr, template="plotly_dark")
                elif chart_type == "Box":
                    fig = px.box(df, x=x_col, y=y_col, color=clr, template="plotly_dark")
                elif chart_type == "Pie":
                    fig = px.pie(df, names=x_col, values=y_col, template="plotly_dark")
                elif chart_type == "Area":
                    fig = px.area(df, x=x_col, y=y_col, color=clr, template="plotly_dark")

                if fig:
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(22,22,31,.8)",
                        font_family="Poppins", margin=dict(t=30, b=30)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart error: {e}")

        with tab_corr:
            if num_cols:
                corr = df[num_cols].corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                                template="plotly_dark", title="Correlation Matrix")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Poppins")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns for correlation.")
    else:
        # Demo with random data
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#3a3a5c;">
          <div style="font-size:2.5rem;">📂</div>
          <div>Upload a CSV to get started</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Or try a demo dataset:**")
        if st.button("📊 Load Demo Data"):
            demo = pd.DataFrame({
                "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                "Revenue": [4500,5200,4800,6100,5800,7200,6900,7800,8100,7400,8600,9200],
                "Expenses": [3200,3500,3100,4200,3900,4800,4500,5100,5300,4800,5600,6100],
                "Users": [120,145,138,167,158,192,185,210,225,198,234,251],
                "Region": ["N","N","S","S","E","E","W","W","N","S","E","W"],
            })
            buf = io.StringIO()
            demo.to_csv(buf, index=False)
            st.download_button("⬇️ Download demo CSV", buf.getvalue(), "demo.csv", "text/csv")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: MATH SOLVER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Math Solver":
    section_header("🧮 Math Solver", "Algebra, calculus, statistics and more")

    tab_algebra, tab_calc, tab_stats_t, tab_matrix = st.tabs(
        ["🔢 Algebra", "∫ Calculus", "📊 Statistics", "⬜ Matrix"])

    with tab_algebra:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Equation Solver**")
            eq = st.text_input("Equation (use x)", placeholder="x**2 - 5*x + 6 = 0")
            if st.button("Solve", key="solve_eq"):
                try:
                    x = symbols('x')
                    if "=" in eq:
                        lhs, rhs = eq.split("=", 1)
                        expr = parse_expr(lhs.strip()) - parse_expr(rhs.strip())
                    else:
                        expr = parse_expr(eq)
                    sols = solve(expr, x)
                    st.success(f"Solutions: {sols}")
                    st.markdown(f"**LaTeX:** ${'  ,  '.join(latex(s) for s in sols)}$")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.markdown("**Expression Simplifier**")
            expr_in = st.text_input("Expression", placeholder="(x+1)**2 - x**2")
            if st.button("Simplify", key="simplify"):
                try:
                    x = symbols('x')
                    result = simplify(parse_expr(expr_in))
                    st.success(f"Simplified: {result}")
                    st.markdown(f"Expanded: {expand(result)}")
                    st.markdown(f"Factored: {factor(result)}")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**Quadratic Formula Calculator**")
        c1, c2, c3 = st.columns(3)
        with c1: qa = st.number_input("a", value=1.0)
        with c2: qb = st.number_input("b", value=-5.0)
        with c3: qc = st.number_input("c", value=6.0)
        if st.button("Calculate Roots"):
            disc = qb**2 - 4*qa*qc
            if disc > 0:
                r1 = (-qb + math.sqrt(disc)) / (2*qa)
                r2 = (-qb - math.sqrt(disc)) / (2*qa)
                st.success(f"Two real roots: x₁ = {r1:.4f}, x₂ = {r2:.4f}")
            elif disc == 0:
                r = -qb / (2*qa)
                st.success(f"One real root: x = {r:.4f}")
            else:
                real = -qb / (2*qa)
                imag = math.sqrt(-disc) / (2*qa)
                st.warning(f"Complex roots: {real:.4f} ± {imag:.4f}i")

    with tab_calc:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Differentiation**")
            diff_expr = st.text_input("f(x) =", placeholder="x**3 + 2*x**2", key="diff_in")
            diff_order = st.selectbox("Order", [1, 2, 3, 4])
            if st.button("Differentiate"):
                try:
                    x = symbols('x')
                    result = diff(parse_expr(diff_expr), x, diff_order)
                    st.success(f"f{'′'*diff_order}(x) = {result}")
                    st.latex(f"f^{{({'′'*diff_order})}}(x) = {latex(result)}")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.markdown("**Integration**")
            int_expr = st.text_input("f(x) =", placeholder="x**2 + 3*x", key="int_in")
            use_limits = st.checkbox("Definite integral")
            if use_limits:
                c_a, c_b = st.columns(2)
                with c_a: lower = st.number_input("Lower", value=0.0)
                with c_b: upper = st.number_input("Upper", value=1.0)
            if st.button("Integrate"):
                try:
                    x = symbols('x')
                    expr = parse_expr(int_expr)
                    if use_limits:
                        result = integrate(expr, (x, lower, upper))
                        st.success(f"∫f dx = {result}")
                    else:
                        result = integrate(expr, x)
                        st.success(f"∫f dx = {result} + C")
                    st.latex(f"\\int f\\,dx = {latex(result)}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_stats_t:
        st.markdown("**Statistical Calculator**")
        data_in = st.text_area("Enter numbers (comma or newline separated)", height=100,
                                placeholder="1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        if st.button("Calculate Stats"):
            try:
                nums = [float(x.strip()) for x in re.split(r'[,\n]+', data_in) if x.strip()]
                if not nums:
                    st.error("No valid numbers found.")
                else:
                    n = len(nums)
                    mean = sum(nums) / n
                    sorted_n = sorted(nums)
                    median = (sorted_n[n//2-1] + sorted_n[n//2]) / 2 if n % 2 == 0 else sorted_n[n//2]
                    variance = sum((x - mean)**2 for x in nums) / n
                    std_dev = math.sqrt(variance)

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Mean", f"{mean:.4f}")
                    c2.metric("Median", f"{median:.4f}")
                    c3.metric("Std Dev", f"{std_dev:.4f}")
                    c4.metric("Range", f"{max(nums)-min(nums):.4f}")

                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric("Min", f"{min(nums):.4f}")
                    c6.metric("Max", f"{max(nums):.4f}")
                    c7.metric("Count", n)
                    c8.metric("Sum", f"{sum(nums):.4f}")

                    # Histogram
                    fig = px.histogram(x=nums, nbins=max(5, n//3),
                                       template="plotly_dark",
                                       labels={"x": "Value"},
                                       title="Distribution")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(22,22,31,.8)",
                                      font_family="Poppins",
                                      showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_matrix:
        st.markdown("**Matrix Operations**")
        import numpy as np
        size = st.selectbox("Matrix size", ["2×2", "3×3"])
        n = 2 if "2" in size else 3

        col1, col2 = st.columns(2)
        matrices = []
        for mi, col in enumerate([col1, col2]):
            with col:
                st.markdown(f"**Matrix {'AB'[mi]}**")
                rows = []
                for r in range(n):
                    cols_vals = st.columns(n)
                    row = []
                    for c_idx, c in enumerate(cols_vals):
                        v = c.number_input(f"", value=float(r==c_idx),
                                           key=f"m{mi}_{r}_{c_idx}",
                                           label_visibility="collapsed")
                        row.append(v)
                    rows.append(row)
                matrices.append(np.array(rows))

        op = st.selectbox("Operation", ["A + B", "A - B", "A × B", "det(A)", "inv(A)", "transpose(A)"])
        if st.button("Calculate"):
            try:
                A, B = matrices
                if op == "A + B":    result = A + B
                elif op == "A - B":  result = A - B
                elif op == "A × B":  result = A @ B
                elif op == "det(A)": result = np.linalg.det(A); st.success(f"det(A) = {result:.4f}"); result = None
                elif op == "inv(A)": result = np.linalg.inv(A)
                elif op == "transpose(A)": result = A.T
                if result is not None:
                    st.markdown("**Result:**")
                    st.dataframe(pd.DataFrame(result).round(4), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: CONVERTER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Converter":
    section_header("🔄 Converter", "Units, number bases, and more")

    tab_unit, tab_base, tab_time = st.tabs(["📏 Units", "🔢 Number Bases", "🌍 Timezone"])

    with tab_unit:
        category = st.selectbox("Category", [
            "Length", "Weight/Mass", "Temperature", "Area", "Volume",
            "Speed", "Data Storage", "Energy", "Pressure"
        ])

        CONVERSIONS = {
            "Length": {"mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                       "inch": 0.0254, "foot": 0.3048, "yard": 0.9144, "mile": 1609.344},
            "Weight/Mass": {"mg": 1e-6, "g": 0.001, "kg": 1, "tonne": 1000,
                            "oz": 0.0283495, "lb": 0.453592},
            "Area": {"mm²": 1e-6, "cm²": 1e-4, "m²": 1, "km²": 1e6,
                     "acre": 4046.86, "hectare": 10000, "ft²": 0.0929, "in²": 6.452e-4},
            "Volume": {"ml": 1e-6, "l": 0.001, "m³": 1, "cm³": 1e-6,
                       "cup": 2.365e-4, "pint": 4.732e-4, "quart": 9.464e-4, "gallon": 3.785e-3},
            "Speed": {"m/s": 1, "km/h": 1/3.6, "mph": 0.44704, "knot": 0.514444},
            "Data Storage": {"bit": 1, "byte": 8, "KB": 8*1024, "MB": 8*1024**2,
                             "GB": 8*1024**3, "TB": 8*1024**4},
            "Energy": {"J": 1, "kJ": 1000, "cal": 4.184, "kcal": 4184, "Wh": 3600, "kWh": 3.6e6},
            "Pressure": {"Pa": 1, "kPa": 1000, "MPa": 1e6, "bar": 1e5, "psi": 6894.76, "atm": 101325},
        }

        if category == "Temperature":
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                t_val = st.number_input("Value", value=100.0)
                t_from = st.selectbox("From", ["Celsius", "Fahrenheit", "Kelvin"])
            with col2:
                st.markdown('<div style="text-align:center;padding-top:2rem;font-size:1.5rem;">→</div>', unsafe_allow_html=True)
            with col3:
                t_to = st.selectbox("To", ["Fahrenheit", "Celsius", "Kelvin"])
                if st.button("Convert"):
                    if t_from == "Celsius":
                        c = t_val
                    elif t_from == "Fahrenheit":
                        c = (t_val - 32) * 5 / 9
                    else:
                        c = t_val - 273.15

                    if t_to == "Celsius": res = c
                    elif t_to == "Fahrenheit": res = c * 9/5 + 32
                    else: res = c + 273.15
                    st.success(f"{t_val} {t_from} = **{res:.4f} {t_to}**")
        else:
            units = list(CONVERSIONS[category].keys())
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                val = st.number_input("Value", value=1.0)
                from_u = st.selectbox("From", units)
            with col2:
                st.markdown('<div style="text-align:center;padding-top:2rem;font-size:1.5rem;">→</div>', unsafe_allow_html=True)
            with col3:
                to_u = st.selectbox("To", units, index=1)
                if st.button("Convert"):
                    base = val * CONVERSIONS[category][from_u]
                    result = base / CONVERSIONS[category][to_u]
                    st.success(f"{val} {from_u} = **{result:.6g} {to_u}**")

            # Conversion table
            st.markdown("**Full conversion table:**")
            base = 1 * CONVERSIONS[category][from_u]
            rows = {u: f"{base/CONVERSIONS[category][u]:.6g}" for u in units}
            st.dataframe(pd.DataFrame.from_dict(rows, orient="index", columns=["Value"]),
                         use_container_width=True)

    with tab_base:
        st.markdown("**Number Base Converter**")
        num_input = st.text_input("Enter number", placeholder="255, FF, 11111111…")
        from_base = st.selectbox("From base", ["Decimal (10)", "Binary (2)", "Octal (8)", "Hexadecimal (16)"])
        base_map = {"Decimal (10)": 10, "Binary (2)": 2, "Octal (8)": 8, "Hexadecimal (16)": 16}

        if num_input and st.button("Convert All"):
            try:
                decimal = int(num_input, base_map[from_base])
                st.markdown(f"""
                <div class="nx-card">
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;">
                    <div><div style="color:#6b6b8a;font-size:.75rem;">Decimal (10)</div><div style="font-size:1.2rem;font-weight:700;color:#7c6af7;">{decimal}</div></div>
                    <div><div style="color:#6b6b8a;font-size:.75rem;">Binary (2)</div><div style="font-size:1.2rem;font-weight:700;color:#4dd0e1;">{bin(decimal)[2:]}</div></div>
                    <div><div style="color:#6b6b8a;font-size:.75rem;">Octal (8)</div><div style="font-size:1.2rem;font-weight:700;color:#f06292;">{oct(decimal)[2:]}</div></div>
                    <div><div style="color:#6b6b8a;font-size:.75rem;">Hexadecimal (16)</div><div style="font-size:1.2rem;font-weight:700;color:#a78bfa;">{hex(decimal)[2:].upper()}</div></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_time:
        import pytz
        ZONES = ["UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London",
                 "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai",
                 "Asia/Kolkata", "Asia/Kathmandu", "Australia/Sydney", "America/Sao_Paulo"]
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        st.markdown("**Current time across timezones:**")
        cols = st.columns(3)
        for i, tz_name in enumerate(ZONES):
            try:
                tz = pytz.timezone(tz_name)
                local = now_utc.astimezone(tz)
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="nx-stat" style="margin-bottom:.5rem;">
                      <div style="font-size:.72rem;color:#6b6b8a;margin-bottom:.2rem;">{tz_name}</div>
                      <div style="font-size:1.1rem;font-weight:700;color:#e2e2f0;">{local.strftime('%H:%M:%S')}</div>
                      <div style="font-size:.72rem;color:#6b6b8a;">{local.strftime('%b %d, %Y')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                pass


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: PASSWORD GEN
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Password Gen":
    section_header("🔐 Password Generator", "Create strong, secure passwords")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**⚙️ Options**")
        length = st.slider("Password length", 8, 128, 20)
        use_upper = st.checkbox("Uppercase (A–Z)", value=True)
        use_lower = st.checkbox("Lowercase (a–z)", value=True)
        use_digits = st.checkbox("Numbers (0–9)", value=True)
        use_symbols = st.checkbox("Symbols (!@#$…)", value=True)
        exclude_ambig = st.checkbox("Exclude ambiguous chars (0, O, l, 1)", value=False)
        num_passwords = st.slider("Generate count", 1, 10, 3)

        if st.button("🔑 Generate Passwords", use_container_width=True):
            charset = ""
            if use_lower:   charset += string.ascii_lowercase
            if use_upper:   charset += string.ascii_uppercase
            if use_digits:  charset += string.digits
            if use_symbols: charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if exclude_ambig:
                for ch in "0O1lI":
                    charset = charset.replace(ch, "")

            if not charset:
                st.error("Select at least one character type.")
            else:
                passwords = []
                for _ in range(num_passwords):
                    pw = ''.join(random.SystemRandom().choice(charset) for _ in range(length))
                    passwords.append(pw)
                st.session_state["_passwords"] = passwords

        st.markdown("</div>", unsafe_allow_html=True)

        # Passphrase
        st.markdown('<div class="nx-card" style="margin-top:.5rem;">', unsafe_allow_html=True)
        st.markdown("**🗣️ Passphrase Generator**")
        word_count = st.slider("Words", 3, 8, 4)
        separator = st.text_input("Separator", value="-")
        if st.button("Generate Passphrase"):
            words_pool = ["correct", "horse", "battery", "staple", "purple", "monkey",
                          "forest", "quantum", "river", "solar", "cosmic", "delta",
                          "echo", "flame", "globe", "harbor", "ivory", "jungle"]
            phrase = separator.join(random.choices(words_pool, k=word_count))
            st.code(phrase)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        passwords = st.session_state.get("_passwords", [])
        if passwords:
            st.markdown('<div class="nx-card">', unsafe_allow_html=True)
            st.markdown("**Generated Passwords**")
            for pw in passwords:
                # Strength
                strength = 0
                if any(c.isupper() for c in pw): strength += 1
                if any(c.islower() for c in pw): strength += 1
                if any(c.isdigit() for c in pw): strength += 1
                if any(c in "!@#$%^&*()" for c in pw): strength += 1
                if len(pw) >= 16: strength += 1
                strength_labels = {1: ("Weak", "#f44336"), 2: ("Fair", "#ff9800"),
                                   3: ("Good", "#ffc107"), 4: ("Strong", "#4caf50"), 5: ("Very Strong", "#00bcd4")}
                s_label, s_color = strength_labels.get(strength, ("Weak", "#f44336"))

                st.code(pw)
                st.markdown(f'<div style="font-size:.75rem;color:{s_color};margin-top:-.5rem;margin-bottom:.8rem;">Strength: {s_label} · Entropy: {len(pw) * math.log2(max(len(set(pw)),1)):.0f} bits</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Hash generator
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**#️⃣ Hash Generator**")
        hash_input = st.text_input("Text to hash", placeholder="Enter text…")
        if hash_input:
            algos = {"MD5": "md5", "SHA-1": "sha1", "SHA-256": "sha256", "SHA-512": "sha512"}
            for name, algo in algos.items():
                h = hashlib.new(algo, hash_input.encode()).hexdigest()
                st.markdown(f"**{name}:** `{h}`")
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: COLOR TOOLS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Color Tools":
    section_header("🎨 Color Tools", "Palettes, gradients and colour theory")

    tab_picker, tab_palette, tab_grad = st.tabs(["🎯 Color Info", "🎨 Palette Gen", "🌈 Gradients"])

    with tab_picker:
        hex_color = st.color_picker("Pick a color", "#7c6af7")
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        # HSL
        r_, g_, b_ = r/255, g/255, b/255
        cmax, cmin = max(r_,g_,b_), min(r_,g_,b_)
        l = (cmax + cmin) / 2
        s = 0 if cmax == cmin else (cmax-cmin)/(1-abs(2*l-1))
        if cmax == cmin: h = 0
        elif cmax == r_: h = 60 * ((g_-b_)/(cmax-cmin) % 6)
        elif cmax == g_: h = 60 * ((b_-r_)/(cmax-cmin) + 2)
        else:            h = 60 * ((r_-g_)/(cmax-cmin) + 4)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background:{hex_color};border-radius:14px;height:120px;"></div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="nx-card">
              <div class="nx-stat-label">HEX</div><div style="font-weight:700;">{hex_color.upper()}</div>
              <div class="nx-stat-label" style="margin-top:.5rem;">RGB</div><div style="font-weight:700;">rgb({r}, {g}, {b})</div>
              <div class="nx-stat-label" style="margin-top:.5rem;">HSL</div><div style="font-weight:700;">hsl({h:.0f}°, {s*100:.0f}%, {l*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            # Complementary
            cr = 255 - r; cg = 255 - g; cb = 255 - b
            comp = f"#{cr:02x}{cg:02x}{cb:02x}"
            st.markdown(f"""
            <div class="nx-card">
              <div class="nx-stat-label">Complementary</div>
              <div style="background:{comp};border-radius:8px;height:40px;margin:.4rem 0;"></div>
              <div style="font-weight:700;font-size:.82rem;">{comp.upper()}</div>
              <div class="nx-stat-label" style="margin-top:.5rem;">Luminance</div>
              <div style="font-weight:700;">{l*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # Tints and shades
        st.markdown("**Tints & Shades**")
        cols = st.columns(11)
        for i, col in enumerate(cols):
            factor = i / 10
            tr = int(r + (255 - r) * factor)
            tg = int(g + (255 - g) * factor)
            tb = int(b + (255 - b) * factor)
            tc = f"#{tr:02x}{tg:02x}{tb:02x}"
            col.markdown(f'<div style="background:{tc};height:40px;border-radius:6px;"></div>', unsafe_allow_html=True)

    with tab_palette:
        st.markdown("**Generate Color Palette**")
        base_c = st.color_picker("Base color", "#7c6af7", key="pal_base")
        scheme = st.selectbox("Scheme", ["Analogous", "Triadic", "Complementary", "Split-Complementary", "Random Beautiful"])
        n_colors = st.slider("Colors", 3, 10, 5)

        if st.button("🎨 Generate Palette"):
            def hex_to_hsl(h):
                r_, g_, b_ = int(h[1:3],16)/255, int(h[3:5],16)/255, int(h[5:7],16)/255
                mx, mn = max(r_,g_,b_), min(r_,g_,b_)
                l = (mx+mn)/2
                s = 0 if mx==mn else (mx-mn)/(1-abs(2*l-1))
                if mx==mn: hue=0
                elif mx==r_: hue=60*((g_-b_)/(mx-mn)%6)
                elif mx==g_: hue=60*((b_-r_)/(mx-mn)+2)
                else: hue=60*((r_-g_)/(mx-mn)+4)
                return hue, s, l

            def hsl_to_hex(h, s, l):
                h=h%360; c=(1-abs(2*l-1))*s; x=c*(1-abs((h/60)%2-1)); m=l-c/2
                if h<60: r_,g_,b_=c,x,0
                elif h<120: r_,g_,b_=x,c,0
                elif h<180: r_,g_,b_=0,c,x
                elif h<240: r_,g_,b_=0,x,c
                elif h<300: r_,g_,b_=x,0,c
                else: r_,g_,b_=c,0,x
                return f"#{int((r_+m)*255):02x}{int((g_+m)*255):02x}{int((b_+m)*255):02x}"

            bh, bs, bl = hex_to_hsl(base_c)
            palette = []
            if scheme == "Analogous":
                step = 30 / (n_colors - 1) if n_colors > 1 else 0
                for i in range(n_colors):
                    palette.append(hsl_to_hex(bh - 15 + step*i, bs, bl))
            elif scheme == "Triadic":
                for i in range(n_colors):
                    palette.append(hsl_to_hex(bh + 120*i, bs, bl))
                palette = palette[:n_colors]
            elif scheme == "Complementary":
                for i in range(n_colors):
                    palette.append(hsl_to_hex(bh + (i % 2) * 180 + i*5, bs, bl*(0.7+0.1*i)))
            elif scheme == "Split-Complementary":
                for i in range(n_colors):
                    hues = [bh, bh+150, bh+210]
                    palette.append(hsl_to_hex(hues[i % 3], bs, bl*(0.8+0.05*i)))
            else:
                palette = [hsl_to_hex(random.uniform(0,360), random.uniform(0.5,0.9), random.uniform(0.3,0.7)) for _ in range(n_colors)]

            cols = st.columns(len(palette))
            for i, (col, c) in enumerate(zip(cols, palette)):
                col.markdown(f"""
                <div style="background:{c};border-radius:10px;height:80px;"></div>
                <div style="text-align:center;font-size:.75rem;margin-top:.3rem;font-weight:600;">{c.upper()}</div>
                """, unsafe_allow_html=True)

            palette_css = ", ".join(palette)
            st.code(f"/* Palette */\n{'  '.join(f'--color-{i+1}: {c};' for i,c in enumerate(palette))}", language="css")

    with tab_grad:
        st.markdown("**Gradient Generator**")
        col1, col2 = st.columns(2)
        with col1:
            g1 = st.color_picker("Color 1", "#7c6af7")
        with col2:
            g2 = st.color_picker("Color 2", "#4dd0e1")

        g3_enable = st.checkbox("Add third color stop")
        g3 = st.color_picker("Color 3", "#f06292") if g3_enable else None

        direction = st.select_slider("Direction", options=["0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"])

        colors_str = f"{g1}, {g3}, {g2}" if g3 else f"{g1}, {g2}"
        css_grad = f"linear-gradient({direction}, {colors_str})"
        st.markdown(f"""
        <div style="background:{css_grad};border-radius:16px;height:120px;margin:1rem 0;"></div>
        """, unsafe_allow_html=True)
        st.code(f"background: {css_grad};", language="css")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: BUDGET TRACKER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Budget Tracker":
    section_header("💰 Budget Tracker", "Track income, expenses and savings")

    col_form, col_summary = st.columns([1, 2])

    with col_form:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**Add Entry**")
        b_type = st.radio("Type", ["💚 Income", "❤️ Expense"], horizontal=True)
        b_amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        b_cat = st.selectbox("Category",
            ["🍔 Food", "🏠 Housing", "🚗 Transport", "📚 Education",
             "🎮 Entertainment", "💊 Health", "👗 Clothing", "📱 Tech",
             "💰 Salary", "💼 Freelance", "🎁 Gift", "Other"])
        b_desc = st.text_input("Description", placeholder="Coffee at Café…")
        b_date = st.date_input("Date", value=datetime.date.today())

        if st.button("➕ Add Entry", use_container_width=True):
            if b_amount > 0:
                st.session_state.budget_items.append({
                    "type": b_type, "amount": b_amount, "category": b_cat,
                    "desc": b_desc, "date": str(b_date)
                })
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Delete
        if st.session_state.budget_items:
            if st.button("🗑️ Clear all entries"):
                st.session_state.budget_items = []
                st.rerun()

    with col_summary:
        items = st.session_state.budget_items
        income = sum(i["amount"] for i in items if "Income" in i["type"])
        expense = sum(i["amount"] for i in items if "Expense" in i["type"])
        balance = income - expense

        c1, c2, c3 = st.columns(3)
        c1.metric("💚 Income", f"${income:,.2f}")
        c2.metric("❤️ Expense", f"${expense:,.2f}")
        c3.metric("💰 Balance", f"${balance:,.2f}",
                  delta=f"{'+'if balance>=0 else ''}{balance:,.2f}")

        if items:
            df_budget = pd.DataFrame(items)

            tab_log, tab_chart = st.tabs(["📋 Log", "📊 Charts"])
            with tab_log:
                for item in reversed(items[-20:]):
                    color = "#4caf50" if "Income" in item["type"] else "#f44336"
                    sign = "+" if "Income" in item["type"] else "-"
                    st.markdown(f"""
                    <div class="task-item">
                      <div style="color:{color};font-weight:700;min-width:80px;">{sign}${item['amount']:,.2f}</div>
                      <div style="flex:1;">
                        <div style="font-size:.88rem;font-weight:500;">{item['category']} {item['desc'] and '· '+item['desc']}</div>
                        <div style="font-size:.74rem;color:#6b6b8a;">{item['date']}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab_chart:
                exp_only = df_budget[df_budget["type"].str.contains("Expense")]
                if not exp_only.empty:
                    fig = px.pie(exp_only, values="amount", names="category",
                                 title="Expense Breakdown", template="plotly_dark")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Poppins")
                    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: QR GENERATOR
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "QR Generator":
    section_header("📱 QR Code Generator", "Instant QR codes for any text or URL")

    col1, col2 = st.columns([1, 1])

    with col1:
        qr_type = st.selectbox("Type", ["URL / Link", "Plain Text", "Email", "Phone", "WiFi", "vCard"])

        qr_data = ""
        if qr_type == "URL / Link":
            qr_data = st.text_input("URL", placeholder="https://example.com")
        elif qr_type == "Plain Text":
            qr_data = st.text_area("Text", height=100)
        elif qr_type == "Email":
            email = st.text_input("Email address")
            subject = st.text_input("Subject (optional)")
            qr_data = f"mailto:{email}?subject={subject}" if email else ""
        elif qr_type == "Phone":
            phone = st.text_input("Phone number", placeholder="+1234567890")
            qr_data = f"tel:{phone}" if phone else ""
        elif qr_type == "WiFi":
            ssid = st.text_input("Network Name (SSID)")
            password = st.text_input("Password", type="password")
            enc = st.selectbox("Encryption", ["WPA", "WEP", "nopass"])
            qr_data = f"WIFI:T:{enc};S:{ssid};P:{password};;" if ssid else ""
        elif qr_type == "vCard":
            name = st.text_input("Full Name")
            phone_v = st.text_input("Phone")
            email_v = st.text_input("Email")
            org = st.text_input("Organization")
            qr_data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone_v}\nEMAIL:{email_v}\nORG:{org}\nEND:VCARD" if name else ""

        # Style options
        st.markdown("**Style**")
        qr_fg = st.color_picker("Foreground", "#7c6af7")
        qr_bg = st.color_picker("Background", "#ffffff")
        qr_size = st.slider("Size", 100, 400, 200, step=50)
        error_corr = st.selectbox("Error correction", ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"])
        ec_map = {"L (7%)": qrcode.constants.ERROR_CORRECT_L,
                  "M (15%)": qrcode.constants.ERROR_CORRECT_M,
                  "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
                  "H (30%)": qrcode.constants.ERROR_CORRECT_H}

        if st.button("🔲 Generate QR Code", use_container_width=True) and qr_data:
            qr = qrcode.QRCode(
                version=1,
                error_correction=ec_map[error_corr],
                box_size=10, border=4
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_fg, back_color=qr_bg)
            img = img.resize((qr_size, qr_size), Image.NEAREST)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.session_state["_qr_img"] = buf.getvalue()
            st.session_state["_qr_data"] = qr_data
            st.rerun()

    with col2:
        if st.session_state.get("_qr_img"):
            st.markdown('<div class="nx-card" style="text-align:center;">', unsafe_allow_html=True)
            st.image(st.session_state["_qr_img"], caption="Your QR Code", use_column_width=False)
            st.download_button("⬇️ Download PNG", st.session_state["_qr_img"],
                               file_name="qrcode.png", mime="image/png",
                               use_container_width=True)
            st.markdown(f'<div style="font-size:.78rem;color:#6b6b8a;margin-top:.5rem;word-break:break-all;">{st.session_state["_qr_data"][:100]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:5rem;color:#3a3a5c;">
              <div style="font-size:4rem;">📱</div>
              <div>Configure and generate your QR code</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: TEXT TOOLS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Text Tools":
    section_header("✍️ Text Tools", "Analyse, transform and generate text")

    tab_analyze, tab_transform, tab_gen, tab_diff = st.tabs(
        ["📊 Analyse", "🔄 Transform", "🎲 Generate", "🔍 Diff"])

    with tab_analyze:
        text_in = st.text_area("Enter text", height=200, placeholder="Paste or type your text here…")
        if text_in:
            words = len(text_in.split())
            sentences = len(re.split(r'[.!?]+', text_in))
            paragraphs = len([p for p in text_in.split('\n\n') if p.strip()])
            chars_no_space = len(text_in.replace(" ", ""))
            reading_time = max(1, words // 200)
            unique_words = len(set(text_in.lower().split()))

            c1,c2,c3,c4,c5,c6 = st.columns(6)
            c1.metric("Words", words)
            c2.metric("Chars", len(text_in))
            c3.metric("Chars (no space)", chars_no_space)
            c4.metric("Sentences", sentences)
            c5.metric("Paragraphs", paragraphs)
            c6.metric("Read time", f"{reading_time} min")

            st.metric("Unique words", unique_words)

            # Word frequency
            word_freq = {}
            for w in re.findall(r'\b[a-zA-Z]+\b', text_in.lower()):
                if len(w) > 3:
                    word_freq[w] = word_freq.get(w, 0) + 1
            if word_freq:
                top_words = sorted(word_freq.items(), key=lambda x: -x[1])[:15]
                fig = px.bar(x=[w[0] for w in top_words], y=[w[1] for w in top_words],
                             template="plotly_dark", labels={"x":"Word","y":"Count"},
                             title="Top Words")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(22,22,31,.8)",
                                  font_family="Poppins")
                st.plotly_chart(fig, use_container_width=True)

    with tab_transform:
        text_t = st.text_area("Text to transform", height=150)
        cols = st.columns(3)
        transforms = [
            ("UPPERCASE", lambda t: t.upper()),
            ("lowercase", lambda t: t.lower()),
            ("Title Case", lambda t: t.title()),
            ("Sentence case", lambda t: t.capitalize()),
            ("camelCase", lambda t: ''.join(w.capitalize() if i else w.lower() for i,w in enumerate(t.split()))),
            ("snake_case", lambda t: '_'.join(t.lower().split())),
            ("kebab-case", lambda t: '-'.join(t.lower().split())),
            ("Reverse text", lambda t: t[::-1]),
            ("Remove extra spaces", lambda t: ' '.join(t.split())),
            ("Remove line breaks", lambda t: t.replace('\n', ' ')),
            ("Sort lines A–Z", lambda t: '\n'.join(sorted(t.splitlines()))),
            ("Remove duplicates", lambda t: '\n'.join(list(dict.fromkeys(t.splitlines())))),
        ]
        for i, (name, fn) in enumerate(transforms):
            with cols[i % 3]:
                if st.button(name, key=f"tx_{i}", use_container_width=True):
                    if text_t:
                        st.session_state["_transformed"] = fn(text_t)
                        st.session_state["_tx_name"] = name

        if st.session_state.get("_transformed"):
            st.markdown(f"**Result ({st.session_state.get('_tx_name')}):**")
            st.text_area("", value=st.session_state["_transformed"], height=120)
            st.download_button("⬇️ Download", st.session_state["_transformed"].encode(),
                               file_name="transformed.txt")

    with tab_gen:
        gen_type = st.selectbox("Generate", ["Lorem Ipsum", "Random Names", "Random Emails",
                                              "Random UUIDs", "Random Numbers", "Fake Addresses"])
        count = st.slider("Count", 1, 20, 5)

        if st.button("🎲 Generate", use_container_width=True):
            result_lines = []
            if gen_type == "Lorem Ipsum":
                lorem = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                         "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                         "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. ")
                for i in range(count):
                    result_lines.append(lorem * random.randint(1, 2))
            elif gen_type == "Random Names":
                firsts = ["Alice","Bob","Charlie","Diana","Ethan","Fiona","George","Hannah","Ivan","Julia"]
                lasts = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore"]
                for _ in range(count):
                    result_lines.append(f"{random.choice(firsts)} {random.choice(lasts)}")
            elif gen_type == "Random Emails":
                domains = ["gmail.com","yahoo.com","outlook.com","proton.me","hey.com"]
                firsts = ["alice","bob","charlie","diana","ethan","fiona","george"]
                for _ in range(count):
                    result_lines.append(f"{random.choice(firsts)}{random.randint(10,999)}@{random.choice(domains)}")
            elif gen_type == "Random UUIDs":
                import uuid
                for _ in range(count):
                    result_lines.append(str(uuid.uuid4()))
            elif gen_type == "Random Numbers":
                mn = st.number_input("Min", value=1)
                mx = st.number_input("Max", value=1000)
                for _ in range(count):
                    result_lines.append(str(random.randint(int(mn), int(mx))))
            elif gen_type == "Fake Addresses":
                streets = ["Oak St","Maple Ave","Pine Rd","Cedar Blvd","Elm Dr"]
                cities = ["New York","Los Angeles","Chicago","Houston","Phoenix","Austin"]
                states = ["NY","CA","IL","TX","AZ"]
                for _ in range(count):
                    result_lines.append(f"{random.randint(100,9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000,99999)}")

            output = "\n".join(result_lines)
            st.text_area("Generated Output", value=output, height=200)
            st.download_button("⬇️ Download", output.encode(), file_name="generated.txt")

    with tab_diff:
        st.markdown("**Text Difference Checker**")
        col1, col2 = st.columns(2)
        with col1:
            text_a = st.text_area("Original text", height=200, key="diff_a")
        with col2:
            text_b = st.text_area("Modified text", height=200, key="diff_b")

        if st.button("🔍 Compare") and text_a and text_b:
            import difflib
            diff = list(difflib.unified_diff(
                text_a.splitlines(keepends=True),
                text_b.splitlines(keepends=True),
                fromfile="Original", tofile="Modified", lineterm=""
            ))
            if diff:
                diff_str = "".join(diff)
                st.code(diff_str, language="diff")
                st.markdown(f'<span class="nx-badge nx-badge-cyan">{len(diff)} lines changed</span>', unsafe_allow_html=True)
            else:
                st.success("✅ Texts are identical!")


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: HABIT TRACKER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Habit Tracker":
    section_header("🎯 Habit Tracker", "Build streaks and track your consistency")

    col_add, col_track = st.columns([1, 2])

    with col_add:
        st.markdown('<div class="nx-card">', unsafe_allow_html=True)
        st.markdown("**Add Habit**")
        h_name = st.text_input("Habit name", placeholder="Exercise, Read, Meditate…")
        h_icon = st.text_input("Icon (emoji)", placeholder="🏋️")
        h_goal = st.text_input("Goal", placeholder="30 min / day")
        if st.button("➕ Add Habit", use_container_width=True):
            if h_name.strip() and h_name not in st.session_state.habits:
                st.session_state.habits[h_name] = {
                    "icon": h_icon or "⭐",
                    "goal": h_goal,
                    "dates": []
                }
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Legend
        st.markdown("""
        <div class="nx-card" style="margin-top:.5rem;">
          <div style="font-size:.82rem;font-weight:600;margin-bottom:.6rem;">📅 Calendar Legend</div>
          <div style="font-size:.76rem;color:#6b6b8a;">
            ✅ Completed today<br>
            🔥 Streak active<br>
            ⭕ Missed
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_track:
        today = str(datetime.date.today())
        habits = st.session_state.habits

        if not habits:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#3a3a5c;">
              <div style="font-size:2.5rem;">🎯</div>
              <div>Add your first habit!</div>
            </div>
            """, unsafe_allow_html=True)

        for h_name, h_data in list(habits.items()):
            done_today = today in h_data.get("dates", [])

            # Streak calc
            dates = sorted(h_data.get("dates", []))
            streak = 0
            if dates:
                current = datetime.date.today()
                while str(current) in dates:
                    streak += 1
                    current -= datetime.timedelta(days=1)

            col_icon, col_info, col_btn, col_del = st.columns([1, 4, 2, 1])
            with col_icon:
                st.markdown(f'<div style="font-size:1.8rem;text-align:center;padding:.5rem 0;">{h_data["icon"]}</div>', unsafe_allow_html=True)
            with col_info:
                goal_str = f" · {h_data['goal']}" if h_data.get("goal") else ""
                st.markdown(f"""
                <div style="padding:.4rem 0;">
                  <div style="font-weight:600;font-size:.92rem;">{h_name}<span style="color:#6b6b8a;font-size:.8rem;">{goal_str}</span></div>
                  <div style="font-size:.78rem;color:#6b6b8a;">🔥 {streak} day streak · {len(dates)} total</div>
                  <div style="margin-top:.3rem;">
                    <div class="nx-progress-wrap" style="height:5px;">
                      <div class="nx-progress-bar" style="width:{min(100,streak*5)}%;"></div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                label = "✅ Done!" if done_today else "○ Mark done"
                if st.button(label, key=f"habit_{h_name}", use_container_width=True):
                    if done_today:
                        habits[h_name]["dates"].remove(today)
                    else:
                        habits[h_name]["dates"].append(today)
                    st.rerun()
            with col_del:
                if st.button("✕", key=f"hdel_{h_name}"):
                    del st.session_state.habits[h_name]
                    st.rerun()

        # Heatmap
        if habits:
            st.markdown("---")
            st.markdown("**Last 30 Days Overview**")
            today_dt = datetime.date.today()
            last_30 = [today_dt - datetime.timedelta(days=i) for i in range(29, -1, -1)]

            cols = st.columns(30)
            for i, (col, day) in enumerate(zip(cols, last_30)):
                day_str = str(day)
                completed = sum(1 for h in habits.values() if day_str in h.get("dates", []))
                total_h = len(habits)
                if completed == 0:
                    color = "#16161f"
                elif completed == total_h:
                    color = "#7c6af7"
                else:
                    pct = completed / total_h
                    color = f"rgba(124,106,247,{0.2+pct*0.6:.2f})"
                col.markdown(f'<div title="{day_str}: {completed}/{total_h}" style="background:{color};border-radius:3px;height:18px;"></div>', unsafe_allow_html=True)

            st.markdown(f'<div style="font-size:.72rem;color:#6b6b8a;margin-top:.3rem;">Darker = more habits completed · Today is {today}</div>', unsafe_allow_html=True)
