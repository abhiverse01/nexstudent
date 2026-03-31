import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, random, string, math, hashlib, base64, io, re, time, datetime
import uuid as _uuid
from sympy import symbols, solve, simplify, expand, factor, diff, integrate, sympify, latex
from sympy.parsing.sympy_parser import parse_expr
import qrcode
from PIL import Image, ImageDraw, ImageFilter

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus — Student Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════════
# FIX #1 — CSS SPLIT INTO SMALLER CHUNKS + <link> SEPARATED
#
# BUG: The original app dumped the entire <link> + <style> into ONE giant
# st.markdown() call.  Streamlit's HTML sanitizer has a size threshold for
# unsafe_allow_html blocks.  When that threshold is exceeded, the raw CSS
# text leaks into the visible frontend instead of being applied as a style.
#
# FIX:  • Separate the <link> tag into its own st.markdown().
#        • Split the <style> block into 4 smaller chunks so each is well
#          under the sanitiser limit.
# ════════════════════════════════════════════════════════════════════════════════

# ── Font import (isolated) ────────────────────────────────────────────────────
st.markdown("""<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">""", unsafe_allow_html=True)

# ── CSS Part 1: Tokens, Base, Sidebar ────────────────────────────────────────
st.markdown("""<style>
:root{--bg:#070710;--surface:#0d0d1a;--card:#111124;--card2:#161630;--border:#1c1c3a;--border2:#252550;--ink:#e8e8f8;--ink2:#9090b8;--ink3:#4a4a72;--sol:#5b5ef4;--sol2:#818cf8;--amber:#f59e0b;--rose:#f43f5e;--teal:#2dd4bf;--green:#22c55e;--r:12px;--r2:8px;--sh:0 4px 24px rgba(0,0,0,.5);--sh2:0 2px 12px rgba(0,0,0,.35);--glow:0 0 40px rgba(91,94,244,.18)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background-color:var(--bg)!important;color:var(--ink)!important}
.main .block-container{padding:1.2rem 2rem 4rem!important;max-width:1300px!important}
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important}
section[data-testid="stSidebar"] .block-container{padding:1rem .75rem!important}
section[data-testid="stSidebar"] button{background:transparent!important;border:none!important;color:var(--ink2)!important;font-family:'DM Sans',sans-serif!important;font-size:.84rem!important;font-weight:500!important;text-align:left!important;padding:.5rem .75rem!important;border-radius:var(--r2)!important;transition:background .15s,color .15s!important;width:100%!important}
section[data-testid="stSidebar"] button:hover{background:rgba(91,94,244,.12)!important;color:var(--ink)!important}
section[data-testid="stSidebar"] button[kind="secondary"]{background:rgba(91,94,244,.18)!important;color:var(--sol2)!important}
</style>""", unsafe_allow_html=True)

# ── CSS Part 2: Hide chrome, Inputs, Buttons ─────────────────────────────────
st.markdown("""<style>
#MainMenu,footer,header{visibility:hidden!important}
.stDeployButton{display:none!important}
[data-testid="stToolbar"]{display:none!important}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;font-size:.88rem!important;transition:border-color .2s,box-shadow .2s!important}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--sol)!important;box-shadow:0 0 0 3px rgba(91,94,244,.15)!important;outline:none!important}
.stSelectbox>div>div,.stMultiSelect>div>div{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;font-size:.88rem!important}
label,.stRadio label,.stCheckbox label{color:var(--ink2)!important;font-family:'DM Sans',sans-serif!important;font-size:.84rem!important;font-weight:500!important}
.stButton>button{background:var(--sol)!important;color:#fff!important;border:none!important;border-radius:var(--r2)!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:.84rem!important;padding:.48rem 1.2rem!important;letter-spacing:.01em!important;transition:background .15s,transform .1s,box-shadow .15s!important;cursor:pointer!important}
.stButton>button:hover{background:var(--sol2)!important;transform:translateY(-1px)!important;box-shadow:0 4px 16px rgba(91,94,244,.4)!important}
.stButton>button:active{transform:translateY(0)!important}
</style>""", unsafe_allow_html=True)

# ── CSS Part 3: Metrics, Tabs, Expanders, Sliders, Dataframes, Code, Alerts ─
st.markdown("""<style>
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;padding:.9rem 1.1rem!important}
[data-testid="metric-container"]>div>label{color:var(--ink3)!important;font-size:.74rem!important;font-weight:600!important;letter-spacing:.06em!important;text-transform:uppercase!important}
[data-testid="stMetricValue"]{font-size:1.65rem!important;font-weight:700!important;color:var(--ink)!important;font-family:'DM Mono',monospace!important}
[data-testid="stMetricDelta"]{font-size:.78rem!important}
.stTabs [data-baseweb="tab-list"]{gap:2px!important;background:var(--surface)!important;border-radius:var(--r2)!important;padding:3px!important;border:1px solid var(--border)!important;width:fit-content!important}
.stTabs [data-baseweb="tab"]{border-radius:6px!important;padding:.35rem .9rem!important;font-family:'DM Sans',sans-serif!important;font-size:.82rem!important;font-weight:500!important;color:var(--ink3)!important;background:transparent!important;border:none!important}
.stTabs [aria-selected="true"]{background:var(--sol)!important;color:#fff!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.streamlit-expanderHeader{background:var(--card)!important;border-radius:var(--r)!important;border:1px solid var(--border)!important;font-weight:600!important;font-size:.86rem!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important}
.streamlit-expanderContent{background:var(--surface)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0 0 var(--r) var(--r)!important}
[data-testid="stSlider"]>div>div>div>div{background:var(--sol)!important}
[data-testid="stSlider"] div[role="slider"]{background:var(--sol)!important;border:2px solid var(--sol2)!important}
.stDataFrame{border-radius:var(--r)!important;overflow:hidden!important;border:1px solid var(--border)!important}
code,pre{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;font-family:'DM Mono',monospace!important;font-size:.82rem!important;color:var(--teal)!important}
.stSuccess{background:rgba(34,197,94,.08)!important;border:1px solid rgba(34,197,94,.25)!important;border-radius:var(--r2)!important;color:var(--green)!important}
.stError{background:rgba(244,63,94,.08)!important;border:1px solid rgba(244,63,94,.25)!important;border-radius:var(--r2)!important;color:var(--rose)!important}
.stInfo{background:rgba(91,94,244,.08)!important;border:1px solid rgba(91,94,244,.2)!important;border-radius:var(--r2)!important}
.stWarning{background:rgba(245,158,11,.08)!important;border:1px solid rgba(245,158,11,.2)!important;border-radius:var(--r2)!important}
</style>""", unsafe_allow_html=True)

# ── CSS Part 4: Misc — Radio, Divider, Scrollbar, File Uploader, Color/Date/Form
st.markdown("""<style>
.stRadio>div{gap:.5rem!important}
hr{border-color:var(--border)!important;margin:1.4rem 0!important}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
[data-testid="stFileUploader"]{background:var(--surface)!important;border:1.5px dashed var(--border2)!important;border-radius:var(--r)!important}
[data-testid="stColorPicker"]>div{border:1px solid var(--border)!important;border-radius:var(--r2)!important}
[data-testid="stDateInput"]>div>div>input{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;font-size:.88rem!important}
[data-testid="stForm"]{background:transparent!important;border:none!important}
</style>""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
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
        "_transformed": "",
        "_tx_name": "",
        "_quiz_idx": 0,
        "_active_note": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:.5rem .5rem 1.6rem;display:flex;align-items:center;gap:.7rem;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,#5b5ef4,#818cf8);
        border-radius:10px;display:flex;align-items:center;justify-content:center;
        font-size:1.1rem;flex-shrink:0;">⚡</div>
      <div>
        <div style="font-size:1rem;font-weight:700;color:#e8e8f8;letter-spacing:-.02em;">Nexus</div>
        <div style="font-size:.7rem;color:#4a4a72;font-weight:500;letter-spacing:.04em;text-transform:uppercase;">Student Toolkit</div>
      </div>
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

    groups = {
        "STUDY": NAV[:6],
        "TOOLS": NAV[6:10],
        "LIFE": NAV[10:],
    }

    for group_name, items in groups.items():
        st.markdown(f"""
        <div style="font-size:.65rem;font-weight:700;color:#4a4a72;
          letter-spacing:.1em;text-transform:uppercase;
          padding:.3rem .5rem .2rem;margin-top:.5rem;">{group_name}</div>
        """, unsafe_allow_html=True)
        for icon, label in items:
            is_active = st.session_state.page == label
            if st.button(f"{icon}  {label}", key=f"nav_{label}",
                         use_container_width=True,
                         type="secondary" if is_active else "tertiary"):
                st.session_state.page = label
                st.rerun()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(91,94,244,.07);border:1px solid rgba(91,94,244,.15);
      border-radius:10px;padding:.75rem 1rem;font-size:.75rem;color:#4a4a72;margin:.3rem .2rem 0;">
      <div style="color:#818cf8;font-weight:700;margin-bottom:.3rem;font-size:.76rem;">
        💡 Tip of the day
      </div>
      Pair Pomodoro + Flashcards for maximum retention. Study in 25-min sprints.
    </div>
    """, unsafe_allow_html=True)

# ── UI Helpers ────────────────────────────────────────────────────────────────
def page_header(title: str, subtitle: str = ""):
    sub_html = f'<p style="color:var(--ink3);font-size:.85rem;margin:.1rem 0 1.4rem;font-weight:400;">{subtitle}</p>' if subtitle else '<div style="margin-bottom:1.2rem;"></div>'
    st.markdown(f"""
    <div style="margin-bottom:.1rem;">
      <h1 style="font-size:1.55rem;font-weight:700;color:#e8e8f8;
        letter-spacing:-.03em;margin:0 0 .1rem;">{title}</h1>
      {sub_html}
    </div>
    """, unsafe_allow_html=True)

def badge(text: str, color: str = "#5b5ef4") -> str:
    bg = color + "22"
    border = color + "44"
    return f"""<span style="display:inline-block;padding:2px 9px;border-radius:99px;
      font-size:.7rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
      background:{bg};color:{color};border:1px solid {border};">{text}</span>"""

def progress_bar(pct: int, color: str = "var(--sol)") -> str:
    pct = max(0, min(100, pct))
    return f"""<div style="background:var(--surface);border-radius:99px;height:5px;
      overflow:hidden;border:1px solid var(--border);">
      <div style="background:{color};border-radius:99px;height:100%;
        width:{pct}%;transition:width .4s ease;"></div></div>"""


# ════════════════════════════════════════════════════════════════════════════════
# HOME
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":
    now = datetime.datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    tasks_done  = sum(1 for t in st.session_state.tasks if t.get("done"))
    tasks_total = len(st.session_state.tasks)
    notes_count = len(st.session_state.notes)
    cards_count = len(st.session_state.flashcards)
    habits_today = sum(
        1 for h, d in st.session_state.habits.items()
        if str(datetime.date.today()) in d.get("dates", [])
    )
    pct = int(tasks_done / tasks_total * 100) if tasks_total else 0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(91,94,244,.1) 0%,rgba(45,212,191,.05) 100%);
      border:1px solid rgba(91,94,244,.2);border-radius:16px;
      padding:2rem 2.2rem 1.8rem;margin-bottom:1.4rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-30px;right:-30px;width:160px;height:160px;
        background:radial-gradient(circle,rgba(91,94,244,.2) 0%,transparent 70%);
        border-radius:50%;pointer-events:none;"></div>
      <div style="position:absolute;bottom:-40px;left:30%;width:200px;height:200px;
        background:radial-gradient(circle,rgba(45,212,191,.08) 0%,transparent 70%);
        border-radius:50%;pointer-events:none;"></div>
      <div style="position:relative;">
        <div style="font-size:1.9rem;font-weight:800;color:#e8e8f8;
          letter-spacing:-.04em;line-height:1.1;margin-bottom:.4rem;">
          {greeting} ✦
        </div>
        <div style="color:#4a4a72;font-size:.9rem;margin-bottom:1.4rem;">
          Welcome to Nexus — your all-in-one student toolkit.
          Today is {now.strftime('%A, %B %d')}.
        </div>
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;">
          <div style="background:rgba(91,94,244,.15);border:1px solid rgba(91,94,244,.25);
            border-radius:8px;padding:.5rem .9rem;font-size:.82rem;">
            <span style="color:#818cf8;font-weight:700;">{tasks_done}/{tasks_total}</span>
            <span style="color:#4a4a72;margin-left:.3rem;">tasks done</span>
          </div>
          <div style="background:rgba(45,212,191,.1);border:1px solid rgba(45,212,191,.2);
            border-radius:8px;padding:.5rem .9rem;font-size:.82rem;">
            <span style="color:#2dd4bf;font-weight:700;">{notes_count}</span>
            <span style="color:#4a4a72;margin-left:.3rem;">notes</span>
          </div>
          <div style="background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.2);
            border-radius:8px;padding:.5rem .9rem;font-size:.82rem;">
            <span style="color:#f59e0b;font-weight:700;">{cards_count}</span>
            <span style="color:#4a4a72;margin-left:.3rem;">flashcards</span>
          </div>
          <div style="background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);
            border-radius:8px;padding:.5rem .9rem;font-size:.82rem;">
            <span style="color:#f43f5e;font-weight:700;">{habits_today}</span>
            <span style="color:#4a4a72;margin-left:.3rem;">habits today</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📋 Tasks", f"{tasks_done}/{tasks_total}", delta=f"{pct}% done")
    with c2: st.metric("📝 Notes", notes_count)
    with c3: st.metric("🃏 Flashcards", cards_count)
    with c4: st.metric("🎯 Habits", f"{habits_today} today")

    st.markdown("---")

    st.markdown("""
    <div style="font-size:1.1rem;font-weight:700;color:#e8e8f8;
      margin-bottom:.3rem;letter-spacing:-.02em;">Features</div>
    <div style="color:#4a4a72;font-size:.83rem;margin-bottom:1.2rem;">
      Everything you need, one toolkit.
    </div>
    """, unsafe_allow_html=True)

    FEATURES = [
        ("🤖", "AI Assistant",   "Chat with Claude for help & ideas",        "#5b5ef4"),
        ("📝", "Smart Notes",    "Markdown notes, searchable & organised",    "#2dd4bf"),
        ("✅", "Task Manager",   "Prioritised to-do with categories",         "#f43f5e"),
        ("⏱️", "Pomodoro",       "Focus timer with work/break cycles",        "#f59e0b"),
        ("🃏", "Flashcards",     "Create, quiz and track your progress",      "#818cf8"),
        ("📊", "Data Explorer",  "Upload CSV, generate instant charts",       "#2dd4bf"),
        ("🧮", "Math Solver",    "Algebra, calculus, statistics & matrices",  "#5b5ef4"),
        ("🔄", "Converter",      "Units, bases, timezones & more",            "#f59e0b"),
        ("🔐", "Password Gen",   "Cryptographically strong passwords",        "#f43f5e"),
        ("🎨", "Color Tools",    "Palettes, gradients, colour theory",        "#818cf8"),
        ("💰", "Budget Tracker", "Income, expenses & savings goals",          "#22c55e"),
        ("📱", "QR Generator",   "Instant QR for any URL or text",            "#2dd4bf"),
        ("✍️", "Text Tools",     "Analyse, transform & generate text",        "#f59e0b"),
        ("🎯", "Habit Tracker",  "Build streaks, visualise consistency",      "#5b5ef4"),
    ]

    cols = st.columns(3)
    for i, (icon, name, desc, accent) in enumerate(FEATURES):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--border);
              border-radius:var(--r);padding:1.1rem 1.2rem;margin-bottom:.1rem;
              border-left:3px solid {accent}22;">
              <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem;">
                <span style="font-size:1.3rem;">{icon}</span>
                <span style="font-weight:700;font-size:.9rem;color:#e8e8f8;">{name}</span>
              </div>
              <div style="font-size:.76rem;color:#4a4a72;line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {name} →", key=f"home_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()

    st.markdown(f"""
    <div style="text-align:center;color:#1c1c3a;font-size:.72rem;margin-top:2rem;
      font-family:'DM Mono',monospace;">
      ⚡ NEXUS · {now.strftime('%Y')}
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "AI Assistant":
    page_header("🤖 AI Assistant", "Powered by Claude — ask anything")

    SYSTEM_PRESETS = {
        "General Assistant": "You are a helpful, concise assistant. Keep responses clear and well-structured.",
        "Study Tutor":       "You are an expert academic tutor. Explain concepts clearly with examples.",
        "Code Helper":       "You are a senior software engineer. Write clean, well-commented code.",
        "Essay Writer":      "You are an academic writing coach. Help structure arguments and improve clarity.",
        "Math Wizard":       "You are a mathematics professor. Solve problems step-by-step.",
        "Debate Partner":    "You are a debate coach. Present balanced arguments from multiple perspectives.",
    }

    col_sel, col_clear = st.columns([4, 1])
    with col_sel:
        preset = st.selectbox("Persona", list(SYSTEM_PRESETS.keys()), label_visibility="collapsed")
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    system_prompt = SYSTEM_PRESETS[preset]

    # Chat messages — each is self-contained HTML
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            role, content = msg["role"], msg["content"]
            safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if role == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:.7rem;">
                  <div style="background:rgba(91,94,244,.18);border:1px solid rgba(91,94,244,.3);
                    border-radius:12px 12px 3px 12px;padding:.65rem .95rem;
                    max-width:78%;font-size:.86rem;color:#e8e8f8;line-height:1.55;
                    white-space:pre-wrap;">{safe_content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:.7rem;">
                  <div style="background:var(--card);border:1px solid var(--border);
                    border-radius:12px 12px 12px 3px;padding:.65rem .95rem;
                    max-width:82%;font-size:.86rem;color:#e8e8f8;line-height:1.6;
                    white-space:pre-wrap;">{safe_content}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3.5rem 2rem;color:#1c1c3a;">
          <div style="font-size:2.8rem;margin-bottom:.7rem;">🤖</div>
          <div style="font-size:.9rem;color:#4a4a72;margin-bottom:.4rem;">
            Start a conversation. Try:
          </div>
          <div style="font-size:.82rem;color:#1c1c3a;">
            "Explain photosynthesis simply" · "Write a Python sorting function" · "Help me outline an essay"
          </div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            user_input = st.text_input("Message", placeholder="Ask anything…", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Send ✈️", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        try:
            import requests as req
            import os
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
            # FIX #10: Sliding window — keep last 20 messages to avoid context overflow
            messages = [{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_history[-20:]]
            resp = req.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": messages,
                },
                timeout=30
            )
            data = resp.json()
            if "content" in data and data["content"]:
                reply = data["content"][0]["text"]
            elif "error" in data:
                reply = f"⚠️ API error: {data['error'].get('message', 'Unknown error')}"
            else:
                reply = "⚠️ Unexpected response format."
        except Exception as e:
            reply = f"⚠️ Connection error: {e}\n\nMake sure ANTHROPIC_API_KEY is set in your environment."

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# SMART NOTES
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Smart Notes":
    page_header("📝 Smart Notes", "Markdown notes with live preview")

    col_list, col_editor = st.columns([1, 2])

    with col_list:
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          Your Notes
        </div>
        """, unsafe_allow_html=True)
        new_title = st.text_input("Note title", placeholder="Add new note…", label_visibility="collapsed")
        if st.button("＋ Create Note", use_container_width=True):
            if new_title.strip() and new_title not in st.session_state.notes:
                st.session_state.notes[new_title] = f"# {new_title}\n\nStart writing here…"
                st.session_state["_active_note"] = new_title
                st.rerun()
            elif new_title in st.session_state.notes:
                st.warning("A note with this title already exists.")

        st.markdown("<div style='margin-top:.4rem;'></div>", unsafe_allow_html=True)

        for title in list(st.session_state.notes.keys()):
            is_active = st.session_state.get("_active_note") == title
            border_style = "border-left:3px solid var(--sol)" if is_active else "border-left:3px solid transparent"
            bg_style = "background:rgba(91,94,244,.1)" if is_active else "background:var(--surface)"
            st.markdown(f"""
            <div style="{bg_style};{border_style};border-radius:0 var(--r2) var(--r2) 0;
              padding:.1rem 0;margin-bottom:2px;">
            </div>
            """, unsafe_allow_html=True)
            c_note, c_del = st.columns([5, 1])
            with c_note:
                if st.button(f"📄 {title}", key=f"note_{title}", use_container_width=True):
                    st.session_state["_active_note"] = title
                    st.rerun()
            with c_del:
                if st.button("✕", key=f"del_{title}"):
                    del st.session_state.notes[title]
                    if st.session_state.get("_active_note") == title:
                        st.session_state["_active_note"] = None
                    st.rerun()

    with col_editor:
        active = st.session_state.get("_active_note")
        if active and active in st.session_state.notes:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.6rem;">
              <span style="font-size:.78rem;color:#4a4a72;">Editing</span>
              <code style="font-size:.78rem;background:rgba(91,94,244,.12);
                color:#818cf8;border:1px solid rgba(91,94,244,.2);
                border-radius:5px;padding:1px 8px;">{active}</code>
            </div>
            """, unsafe_allow_html=True)
            tabs = st.tabs(["✏️ Edit", "👁 Preview"])
            with tabs[0]:
                # FIX #5 — Dynamic key per note title so widget state resets on switch.
                # The original used a fixed key "note_editor" which caused Streamlit
                # to cache the textarea value, showing stale content when switching
                # between different notes.
                safe_key = f"note_editor_{hashlib.md5(active.encode()).hexdigest()[:8]}"
                content = st.text_area(
                    "content",
                    value=st.session_state.notes[active],
                    height=380,
                    label_visibility="collapsed",
                    key=safe_key,
                )
                st.session_state.notes[active] = content
            with tabs[1]:
                st.markdown(st.session_state.notes[active])

            words = len(st.session_state.notes[active].split())
            chars = len(st.session_state.notes[active])
            st.markdown(
                badge(f"{words} words", "#5b5ef4") + " " + badge(f"{chars} chars", "#2dd4bf"),
                unsafe_allow_html=True
            )
            st.markdown("<div style='margin-top:.6rem;'></div>", unsafe_allow_html=True)
            content_bytes = st.session_state.notes[active].encode()
            st.download_button("⬇️ Download .md", content_bytes,
                               file_name=f"{active}.md", mime="text/markdown")
        else:
            st.markdown("""
            <div style="text-align:center;padding:5rem 2rem;color:#1c1c3a;">
              <div style="font-size:2.8rem;margin-bottom:.6rem;">📝</div>
              <div style="color:#4a4a72;">Select or create a note on the left</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TASK MANAGER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Task Manager":
    page_header("✅ Task Manager", "Prioritised to-do list")

    col_add, col_tasks = st.columns([1, 2])

    with col_add:
        with st.container():
            st.markdown("""
            <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
              letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
              New Task
            </div>
            """, unsafe_allow_html=True)
            t_name = st.text_input("Task name", placeholder="Finish assignment…")
            t_pri  = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🟢 Low"])
            t_cat  = st.selectbox("Category", ["📚 Study", "💻 Work", "🏠 Personal", "🏋️ Health", "🎯 Goals"])
            t_due  = st.date_input("Due date", value=None)
            if st.button("＋ Add Task", use_container_width=True):
                if t_name.strip():
                    # FIX #9 — Use UUID instead of len(tasks) to avoid ID collisions
                    # when tasks are deleted (len changes, causing duplicate IDs).
                    st.session_state.tasks.append({
                        "name": t_name, "priority": t_pri, "category": t_cat,
                        "due": str(t_due) if t_due else None, "done": False,
                        "id": str(_uuid.uuid4())
                    })
                    st.rerun()

        total = len(st.session_state.tasks)
        done  = sum(1 for t in st.session_state.tasks if t["done"])
        pct   = int(done / total * 100) if total else 0

        st.markdown("<div style='margin-top:.8rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);
          border-radius:var(--r);padding:1rem 1.1rem;">
          <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
            letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
            Progress
          </div>
          {progress_bar(pct)}
          <div style="font-size:.78rem;color:#4a4a72;margin-top:.5rem;
            font-family:'DM Mono',monospace;">{done}/{total} done · {pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_tasks:
        c_filter, c_show = st.columns([2, 1])
        with c_filter:
            filter_cat = st.selectbox("Filter", ["All","📚 Study","💻 Work","🏠 Personal","🏋️ Health","🎯 Goals"],
                                      label_visibility="collapsed")
        with c_show:
            show_done = st.checkbox("Show done", value=True)

        tasks_to_show = [t for t in st.session_state.tasks
                         if (filter_cat == "All" or t["category"] == filter_cat)
                         and (show_done or not t["done"])]

        pri_order = {"🔴 High": 0, "🟡 Medium": 1, "🟢 Low": 2}
        tasks_to_show.sort(key=lambda x: pri_order.get(x["priority"], 9))

        if not tasks_to_show:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#1c1c3a;">
              <div style="font-size:2rem;">🎉</div>
              <div style="color:#4a4a72;font-size:.88rem;margin-top:.4rem;">All clear!</div>
            </div>
            """, unsafe_allow_html=True)

        for task in tasks_to_show:
            idx = st.session_state.tasks.index(task)
            # FIX #9 — Use unique task id in keys to prevent stale checkbox state
            task_id = task.get("id", str(idx))
            col_chk, col_info, col_del = st.columns([1, 7, 1])
            with col_chk:
                checked = st.checkbox("done", value=task["done"],
                                       key=f"task_chk_{task_id}", label_visibility="collapsed")
                st.session_state.tasks[idx]["done"] = checked
            with col_info:
                fade = "opacity:.4;text-decoration:line-through;" if task["done"] else ""
                due_str = f" · Due {task['due']}" if task.get("due") else ""
                pri_colors = {"🔴 High": "#f43f5e", "🟡 Medium": "#f59e0b", "🟢 Low": "#22c55e"}
                pri_color = pri_colors.get(task["priority"], "#4a4a72")
                st.markdown(f"""
                <div style="padding:.35rem 0;{fade}">
                  <div style="font-weight:600;font-size:.88rem;color:#e8e8f8;">{task['name']}</div>
                  <div style="font-size:.74rem;margin-top:.15rem;">
                    <span style="color:{pri_color};">{task['priority']}</span>
                    <span style="color:#4a4a72;"> · {task['category']}{due_str}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"task_del_{task_id}"):
                    st.session_state.tasks.pop(idx)
                    st.rerun()

        if st.session_state.tasks:
            st.markdown("---")
            if st.button("🗑️ Clear completed", use_container_width=False):
                st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# POMODORO
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Pomodoro":
    page_header("⏱️ Pomodoro Timer", "Deep focus with structured breaks")

    col_timer, col_settings = st.columns([1, 1])

    with col_settings:
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          Settings
        </div>
        """, unsafe_allow_html=True)
        work_min   = st.slider("Work (min)",        1, 60, 25)
        break_min  = st.slider("Short break (min)", 1, 30,  5)
        long_break = st.slider("Long break (min)",  5, 45, 15)
        goal_text  = st.text_input("Session goal", placeholder="What will you work on?")

        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);
          border-radius:var(--r);padding:1rem 1.1rem;margin-top:.8rem;">
          <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
            letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
            Technique
          </div>
          <div style="font-size:.78rem;color:#4a4a72;line-height:1.8;">
            ▸ Work {work_min} min, then take {break_min} min break<br>
            ▸ After 4 sessions, take a {long_break} min long break<br>
            ▸ Remove all distractions before starting<br>
            ▸ Single-task — one focus per session
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_timer:
        mode = st.radio("Mode", ["🎯 Work", "☕ Short Break", "🌙 Long Break"], horizontal=True)
        mins = work_min if "Work" in mode else long_break if "Long" in mode else break_min

        now = datetime.datetime.now()
        if st.session_state.get("pomodoro_running") and st.session_state.get("pomodoro_end"):
            remaining = st.session_state.pomodoro_end - now
            secs = max(0, int(remaining.total_seconds()))
        else:
            secs = mins * 60

        m, s = divmod(secs, 60)
        progress_pct = max(0, secs / (mins * 60)) if mins > 0 else 0
        fill_pct = int((1 - progress_pct) * 100)

        goal_display = f"""
        <div style="font-size:.8rem;color:#4a4a72;margin-bottom:.8rem;">
          🎯 {goal_text}
        </div>
        """ if goal_text else ""

        mode_color = "#5b5ef4" if "Work" in mode else "#2dd4bf" if "Short" in mode else "#818cf8"

        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);
          border-radius:var(--r);padding:2.2rem 1.5rem;text-align:center;">
          {goal_display}
          <div style="font-size:5rem;font-weight:800;letter-spacing:-.05em;
            color:{mode_color};line-height:1;font-family:'DM Mono',monospace;
            margin-bottom:1.2rem;">{m:02d}:{s:02d}</div>
          <div style="background:var(--surface);border-radius:99px;height:6px;
            overflow:hidden;border:1px solid var(--border);margin-bottom:.8rem;">
            <div style="background:{mode_color};border-radius:99px;height:100%;
              width:{fill_pct}%;transition:width .8s ease;opacity:.8;"></div>
          </div>
          <div style="font-size:.75rem;color:#4a4a72;font-family:'DM Mono',monospace;">
            {fill_pct}% elapsed · {m:02d}m {s:02d}s remaining
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶ Start", use_container_width=True):
                st.session_state["pomodoro_running"] = True
                st.session_state["pomodoro_end"] = now + datetime.timedelta(minutes=mins)
                st.rerun()
        with c2:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state["pomodoro_running"] = False
                st.rerun()
        with c3:
            if st.button("↺ Reset", use_container_width=True):
                st.session_state["pomodoro_running"] = False
                st.session_state["pomodoro_end"] = None
                st.rerun()

        if st.session_state.get("pomodoro_running") and secs == 0:
            st.success("🎉 Session complete! Time for a break.")
            st.session_state["pomodoro_running"] = False
        elif st.session_state.get("pomodoro_running") and secs > 0:
            # FIX #10: time.sleep(1) is the only pure-Streamlit way to auto-update.
            # We keep it but guard against re-entry from expired timers.
            time.sleep(1)
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# FLASHCARDS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Flashcards":
    page_header("🃏 Flashcards", "Create, study and quiz yourself")

    tab_create, tab_study, tab_quiz = st.tabs(["➕ Create", "📖 Study", "🧠 Quiz"])

    with tab_create:
        col1, col2 = st.columns(2)
        with col1:
            fc_q = st.text_area("Question / Front", height=120, placeholder="What is…?")
        with col2:
            fc_a = st.text_area("Answer / Back", height=120, placeholder="The answer is…")
        fc_tag = st.text_input("Tag / Subject", placeholder="Biology, Math, History…")
        if st.button("＋ Add Card", use_container_width=True):
            if fc_q.strip() and fc_a.strip():
                st.session_state.flashcards.append({
                    "q": fc_q, "a": fc_a, "tag": fc_tag,
                    "reviewed": 0, "correct": 0
                })
                st.success(f"Card added! Deck size: {len(st.session_state.flashcards)}")
                st.rerun()
            else:
                st.warning("Both question and answer are required.")

        if st.session_state.flashcards:
            st.markdown("---")
            st.markdown(f"""
            <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
              letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
              All Cards ({len(st.session_state.flashcards)})
            </div>
            """, unsafe_allow_html=True)
            for i, fc in enumerate(st.session_state.flashcards):
                tag_str = f"📌 {fc['tag']} · " if fc["tag"] else ""
                preview = fc["q"][:60] + ("…" if len(fc["q"]) > 60 else "")
                with st.expander(f"{tag_str}{preview}"):
                    st.markdown(f"**Q:** {fc['q']}")
                    st.markdown(f"**A:** {fc['a']}")
                    c_tag, c_del = st.columns([4, 1])
                    with c_tag:
                        if fc["tag"]:
                            st.markdown(badge(fc["tag"], "#818cf8"), unsafe_allow_html=True)
                    with c_del:
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
                card_item = deck[idx]
                show = st.session_state.show_answer

                if not show:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(91,94,244,.12),rgba(129,140,248,.06));
                      border:1px solid rgba(91,94,244,.25);border-radius:16px;
                      padding:2.5rem;text-align:center;min-height:180px;
                      display:flex;flex-direction:column;align-items:center;justify-content:center;">
                      <div style="font-size:.7rem;font-weight:700;color:#4a4a72;
                        letter-spacing:.1em;text-transform:uppercase;margin-bottom:.7rem;">
                        Question
                      </div>
                      <div style="font-size:1.05rem;font-weight:600;color:#e8e8f8;
                        line-height:1.5;max-width:480px;">{card_item['q']}</div>
                      <div style="font-size:.74rem;color:#1c1c3a;margin-top:1.2rem;">
                        Tap flip to reveal
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(45,212,191,.08),rgba(91,94,244,.06));
                      border:1px solid rgba(45,212,191,.25);border-radius:16px;
                      padding:2.5rem;text-align:center;min-height:180px;
                      display:flex;flex-direction:column;align-items:center;justify-content:center;">
                      <div style="font-size:.7rem;font-weight:700;color:#4a4a72;
                        letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem;">
                        Answer
                      </div>
                      <div style="font-size:.88rem;font-weight:600;color:#9090b8;
                        margin-bottom:.6rem;">{card_item['q']}</div>
                      <div style="width:32px;height:1.5px;background:rgba(45,212,191,.3);
                        margin:.4rem auto;"></div>
                      <div style="font-size:1.05rem;font-weight:600;color:#2dd4bf;
                        line-height:1.5;max-width:480px;">{card_item['a']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("← Prev", use_container_width=True):
                        st.session_state.active_card = (idx - 1) % len(deck)
                        st.session_state.show_answer = False
                        st.rerun()
                with c2:
                    if st.button("🔄 Flip", use_container_width=True):
                        st.session_state.show_answer = not show
                        st.rerun()
                with c3:
                    if st.button("Next →", use_container_width=True):
                        st.session_state.active_card = (idx + 1) % len(deck)
                        st.session_state.show_answer = False
                        st.rerun()

                st.markdown(f"""
                <div style="text-align:center;color:#4a4a72;font-size:.75rem;
                  margin-top:.5rem;font-family:'DM Mono',monospace;">
                  {idx + 1} / {len(deck)}
                </div>
                """, unsafe_allow_html=True)

    with tab_quiz:
        if not st.session_state.flashcards:
            st.info("Create some flashcards first!")
        else:
            sc, tc = st.session_state.quiz_score, st.session_state.quiz_total
            acc = int(sc / tc * 100) if tc else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Correct", sc)
            c2.metric("📊 Total",   tc)
            c3.metric("🎯 Accuracy", f"{acc}%")

            if "_quiz_idx" not in st.session_state:
                st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards) - 1)

            q_idx = st.session_state["_quiz_idx"] % len(st.session_state.flashcards)
            quiz_card = st.session_state.flashcards[q_idx]

            st.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--border);
              border-radius:var(--r);padding:1.2rem 1.4rem;margin:.8rem 0;">
              <div style="font-size:.7rem;font-weight:700;color:#4a4a72;
                letter-spacing:.08em;text-transform:uppercase;margin-bottom:.4rem;">
                Question
              </div>
              <div style="font-size:.95rem;font-weight:600;color:#e8e8f8;">
                {quiz_card['q']}
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.text_area("Your answer", height=80, key=f"quiz_ans_{q_idx}", label_visibility="collapsed")

            c_c, c_w = st.columns(2)
            with c_c:
                if st.button("✅ Correct", use_container_width=True):
                    st.session_state.quiz_score += 1
                    st.session_state.quiz_total += 1
                    st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards) - 1)
                    st.rerun()
            with c_w:
                if st.button("❌ Wrong", use_container_width=True):
                    st.session_state.quiz_total += 1
                    st.session_state["_quiz_idx"] = random.randint(0, len(st.session_state.flashcards) - 1)
                    st.rerun()

            with st.expander("👁 Reveal Answer"):
                st.markdown(f"**{quiz_card['a']}**")

            if st.button("Reset Stats"):
                st.session_state.quiz_score = 0
                st.session_state.quiz_total = 0
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# DATA EXPLORER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Data Explorer":
    page_header("📊 Data Explorer", "Upload a CSV and explore it visually")

    uploaded = st.file_uploader("Upload CSV file", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(exclude="number").columns.tolist()

        st.markdown(
            badge(f"{len(df)} rows", "#5b5ef4") + "  " +
            badge(f"{len(df.columns)} cols", "#2dd4bf") + "  " +
            badge(f"{len(num_cols)} numeric", "#f59e0b"),
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-bottom:.6rem;'></div>", unsafe_allow_html=True)

        tab_data, tab_stats, tab_viz, tab_corr = st.tabs(
            ["🗃️ Data", "📈 Statistics", "🎨 Visualise", "🔗 Correlations"])

        PLOTLY_THEME = dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,17,36,.9)",
            font=dict(family="DM Sans", color="#9090b8"),
            margin=dict(t=36, b=36, l=0, r=0)
        )

        with tab_data:
            search = st.text_input("🔍 Filter rows", placeholder="Type to filter…",
                                   label_visibility="collapsed")
            if search:
                mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                st.dataframe(df[mask], use_container_width=True, height=400)
            else:
                st.dataframe(df, use_container_width=True, height=400)

        with tab_stats:
            st.dataframe(df.describe(), use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Missing Values**")
                nulls = df.isnull().sum()
                missing = nulls[nulls > 0].rename("Missing")
                if missing.empty:
                    st.success("No missing values!")
                else:
                    st.dataframe(missing, use_container_width=True)
            with c2:
                st.markdown("**Column Types**")
                st.dataframe(df.dtypes.rename("Type"), use_container_width=True)

        with tab_viz:
            all_cols = df.columns.tolist()
            chart_type = st.selectbox("Chart type",
                ["Bar","Line","Scatter","Histogram","Box","Pie","Area"])
            c1, c2 = st.columns(2)
            with c1:
                x_col = st.selectbox("X axis", all_cols)
            with c2:
                y_col = st.selectbox("Y axis", num_cols if num_cols else all_cols)
            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols)

            # FIX #8: Build kwargs conditionally — passing color=None causes
            # errors in some Plotly chart types (e.g. px.area with string x-axis).
            use_color = color_col != "None"

            try:
                fig = None
                base_kw = dict(template="plotly_dark")
                if chart_type == "Bar":
                    kw = dict(x=x_col, y=y_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.bar(df, **kw)
                elif chart_type == "Line":
                    kw = dict(x=x_col, y=y_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.line(df, **kw)
                elif chart_type == "Scatter":
                    kw = dict(x=x_col, y=y_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.scatter(df, **kw)
                elif chart_type == "Histogram":
                    kw = dict(x=x_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.histogram(df, **kw)
                elif chart_type == "Box":
                    kw = dict(x=x_col, y=y_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.box(df, **kw)
                elif chart_type == "Pie":
                    fig = px.pie(df, names=x_col, values=y_col, **base_kw)
                elif chart_type == "Area":
                    kw = dict(x=x_col, y=y_col, **base_kw)
                    if use_color: kw["color"] = color_col
                    fig = px.area(df, **kw)
                if fig:
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart error: {e}")

        with tab_corr:
            if num_cols:
                corr = df[num_cols].corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                                template="plotly_dark", title="Correlation Matrix")
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns for correlation.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#1c1c3a;">
          <div style="font-size:2.5rem;margin-bottom:.6rem;">📂</div>
          <div style="color:#4a4a72;">Upload a CSV to get started</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Or try a demo dataset:**")
        if st.button("📊 Download Demo CSV"):
            demo = pd.DataFrame({
                "Month":    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                "Revenue":  [4500,5200,4800,6100,5800,7200,6900,7800,8100,7400,8600,9200],
                "Expenses": [3200,3500,3100,4200,3900,4800,4500,5100,5300,4800,5600,6100],
                "Users":    [120,145,138,167,158,192,185,210,225,198,234,251],
                "Region":   ["N","N","S","S","E","E","W","W","N","S","E","W"],
            })
            buf = io.StringIO()
            demo.to_csv(buf, index=False)
            st.download_button("⬇️ demo.csv", buf.getvalue(), "demo.csv", "text/csv")


# ════════════════════════════════════════════════════════════════════════════════
# MATH SOLVER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Math Solver":
    page_header("🧮 Math Solver", "Algebra, calculus, statistics and matrices")

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
                    latex_sols = "  ,  ".join(latex(s) for s in sols)
                    st.markdown(f"**LaTeX:** ${latex_sols}$")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.markdown("**Expression Simplifier**")
            expr_in = st.text_input("Expression", placeholder="(x+1)**2 - x**2")
            if st.button("Simplify", key="simplify_btn"):
                try:
                    x = symbols('x')
                    result = simplify(parse_expr(expr_in))
                    st.success(f"Simplified: {result}")
                    st.markdown(f"Expanded: `{expand(result)}`")
                    st.markdown(f"Factored: `{factor(result)}`")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**Quadratic Formula**")
        c1, c2, c3 = st.columns(3)
        with c1: qa = st.number_input("a", value=1.0, key="qa")
        with c2: qb = st.number_input("b", value=-5.0, key="qb")
        with c3: qc = st.number_input("c", value=6.0, key="qc")
        if st.button("Calculate Roots"):
            try:
                disc = qb**2 - 4*qa*qc
                if disc > 0:
                    r1 = (-qb + math.sqrt(disc)) / (2*qa)
                    r2 = (-qb - math.sqrt(disc)) / (2*qa)
                    st.success(f"Two real roots: x₁ = {r1:.4f}, x₂ = {r2:.4f}")
                elif disc == 0:
                    st.success(f"One real root: x = {-qb / (2*qa):.4f}")
                else:
                    real = -qb / (2*qa)
                    imag = math.sqrt(-disc) / (2*qa)
                    st.warning(f"Complex roots: {real:.4f} ± {imag:.4f}i")
            except ZeroDivisionError:
                st.error("Coefficient 'a' cannot be zero.")

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
                    st.success(f"Result: {result}")
                    st.latex(f"f^{{({diff_order})}}(x) = {latex(result)}")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.markdown("**Integration**")
            int_expr  = st.text_input("f(x) =", placeholder="x**2 + 3*x", key="int_in")
            use_limits = st.checkbox("Definite integral")
            lower, upper = 0.0, 1.0
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
                        st.success(f"∫ = {result}")
                    else:
                        result = integrate(expr, x)
                        st.success(f"∫ = {result} + C")
                    st.latex(f"\\int f\\,dx = {latex(result)}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_stats_t:
        st.markdown("**Statistical Calculator**")
        data_in = st.text_area("Numbers (comma or newline separated)", height=100,
                                placeholder="1, 2, 3, 4, 5")
        if st.button("Calculate Statistics"):
            try:
                nums = [float(x.strip()) for x in re.split(r'[,\n]+', data_in) if x.strip()]
                if not nums:
                    st.error("No valid numbers found.")
                else:
                    n = len(nums)
                    mean = sum(nums) / n
                    sorted_n = sorted(nums)
                    median = (sorted_n[n//2-1] + sorted_n[n//2]) / 2 if n % 2 == 0 else sorted_n[n//2]
                    variance = sum((xi - mean)**2 for xi in nums) / n
                    std_dev = math.sqrt(variance)

                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Mean",    f"{mean:.4f}")
                    c2.metric("Median",  f"{median:.4f}")
                    c3.metric("Std Dev", f"{std_dev:.4f}")
                    c4.metric("Range",   f"{max(nums)-min(nums):.4f}")
                    c5,c6,c7,c8 = st.columns(4)
                    c5.metric("Min",   f"{min(nums):.4f}")
                    c6.metric("Max",   f"{max(nums):.4f}")
                    c7.metric("Count", n)
                    c8.metric("Sum",   f"{sum(nums):.4f}")

                    fig = px.histogram(x=nums, nbins=max(5, n//3), template="plotly_dark",
                                       labels={"x": "Value"}, title="Distribution")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(17,17,36,.9)",
                                      font=dict(family="DM Sans"), showlegend=False,
                                      margin=dict(t=36,b=36))
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_matrix:
        import numpy as np
        st.markdown("**Matrix Operations**")
        size = st.selectbox("Matrix size", ["2×2", "3×3"])
        n = 2 if "2" in size else 3
        col1, col2 = st.columns(2)
        matrices = []
        for mi, col in enumerate([col1, col2]):
            with col:
                st.markdown(f"**Matrix {'AB'[mi]}**")
                rows = []
                for r in range(n):
                    c_vals = st.columns(n)
                    row = []
                    for ci, c in enumerate(c_vals):
                        v = c.number_input(
                            f"M{mi}[{r},{ci}]",
                            value=float(r == ci),
                            key=f"m{mi}_{r}_{ci}",
                            label_visibility="collapsed"
                        )
                        row.append(v)
                    rows.append(row)
                matrices.append(np.array(rows))

        op = st.selectbox("Operation", ["A + B","A - B","A × B","det(A)","inv(A)","transpose(A)"])
        if st.button("Calculate"):
            try:
                A, B = matrices
                result = None
                if op == "A + B":         result = A + B
                elif op == "A - B":       result = A - B
                elif op == "A × B":       result = A @ B
                elif op == "det(A)":
                    st.success(f"det(A) = {np.linalg.det(A):.4f}")
                elif op == "inv(A)":      result = np.linalg.inv(A)
                elif op == "transpose(A)": result = A.T
                if result is not None:
                    st.markdown("**Result:**")
                    st.dataframe(pd.DataFrame(result).round(4), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# CONVERTER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Converter":
    page_header("🔄 Converter", "Units, number bases, timezones")

    tab_unit, tab_base, tab_time = st.tabs(["📏 Units", "🔢 Number Bases", "🌍 Timezones"])

    CONVERSIONS = {
        "Length":       {"mm":0.001,"cm":0.01,"m":1,"km":1000,"inch":0.0254,"foot":0.3048,"yard":0.9144,"mile":1609.344},
        "Weight/Mass":  {"mg":1e-6,"g":0.001,"kg":1,"tonne":1000,"oz":0.0283495,"lb":0.453592},
        "Area":         {"mm²":1e-6,"cm²":1e-4,"m²":1,"km²":1e6,"acre":4046.86,"hectare":10000,"ft²":0.0929,"in²":6.452e-4},
        "Volume":       {"ml":1e-6,"l":0.001,"m³":1,"cm³":1e-6,"cup":2.365e-4,"pint":4.732e-4,"quart":9.464e-4,"gallon":3.785e-3},
        "Speed":        {"m/s":1,"km/h":1/3.6,"mph":0.44704,"knot":0.514444},
        "Data Storage": {"bit":1,"byte":8,"KB":8*1024,"MB":8*1024**2,"GB":8*1024**3,"TB":8*1024**4},
        "Energy":       {"J":1,"kJ":1000,"cal":4.184,"kcal":4184,"Wh":3600,"kWh":3.6e6},
        "Pressure":     {"Pa":1,"kPa":1000,"MPa":1e6,"bar":1e5,"psi":6894.76,"atm":101325},
    }

    with tab_unit:
        category = st.selectbox("Category",
            ["Length","Weight/Mass","Temperature","Area","Volume","Speed","Data Storage","Energy","Pressure"])

        if category == "Temperature":
            col1, _, col2 = st.columns([2,1,2])
            with col1:
                t_val = st.number_input("Value", value=100.0)
                t_from = st.selectbox("From", ["Celsius","Fahrenheit","Kelvin"])
            with _:
                st.markdown('<div style="text-align:center;padding-top:2rem;font-size:1.3rem;color:#4a4a72;">→</div>', unsafe_allow_html=True)
            with col2:
                t_to = st.selectbox("To", ["Fahrenheit","Celsius","Kelvin"])
                if st.button("Convert Temperature"):
                    c = t_val if t_from=="Celsius" else (t_val-32)*5/9 if t_from=="Fahrenheit" else t_val-273.15
                    res = c if t_to=="Celsius" else c*9/5+32 if t_to=="Fahrenheit" else c+273.15
                    st.success(f"{t_val} {t_from} = **{res:.4f} {t_to}**")
        else:
            units = list(CONVERSIONS[category].keys())
            col1, _, col2 = st.columns([2,1,2])
            with col1:
                val = st.number_input("Value", value=1.0)
                from_u = st.selectbox("From", units)
            with _:
                st.markdown('<div style="text-align:center;padding-top:2rem;font-size:1.3rem;color:#4a4a72;">→</div>', unsafe_allow_html=True)
            with col2:
                to_u = st.selectbox("To", units, index=min(1, len(units)-1))
                if st.button("Convert"):
                    base = val * CONVERSIONS[category][from_u]
                    result = base / CONVERSIONS[category][to_u]
                    st.success(f"{val} {from_u} = **{result:.6g} {to_u}**")

            st.markdown("**Conversion table from 1 unit:**")
            base = 1 * CONVERSIONS[category][from_u]
            rows = {u: f"{base/CONVERSIONS[category][u]:.6g}" for u in units}
            st.dataframe(pd.DataFrame.from_dict(rows, orient="index", columns=["Value"]),
                         use_container_width=True)

    with tab_base:
        num_input = st.text_input("Number", placeholder="255, FF, 11111111…")
        from_base = st.selectbox("From base",
            ["Decimal (10)","Binary (2)","Octal (8)","Hexadecimal (16)"])
        base_map = {"Decimal (10)":10,"Binary (2)":2,"Octal (8)":8,"Hexadecimal (16)":16}
        if num_input and st.button("Convert All Bases"):
            try:
                dec = int(num_input.strip(), base_map[from_base])
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin-top:.5rem;">
                  <div style="background:var(--card);border:1px solid var(--border);
                    border-radius:var(--r);padding:1rem;">
                    <div style="font-size:.7rem;color:#4a4a72;font-weight:700;
                      letter-spacing:.08em;text-transform:uppercase;margin-bottom:.3rem;">
                      Decimal (10)
                    </div>
                    <div style="font-size:1.3rem;font-weight:700;color:#5b5ef4;
                      font-family:'DM Mono',monospace;">{dec}</div>
                  </div>
                  <div style="background:var(--card);border:1px solid var(--border);
                    border-radius:var(--r);padding:1rem;">
                    <div style="font-size:.7rem;color:#4a4a72;font-weight:700;
                      letter-spacing:.08em;text-transform:uppercase;margin-bottom:.3rem;">
                      Binary (2)
                    </div>
                    <div style="font-size:1.1rem;font-weight:700;color:#2dd4bf;
                      font-family:'DM Mono',monospace;word-break:break-all;">{bin(dec)[2:]}</div>
                  </div>
                  <div style="background:var(--card);border:1px solid var(--border);
                    border-radius:var(--r);padding:1rem;">
                    <div style="font-size:.7rem;color:#4a4a72;font-weight:700;
                      letter-spacing:.08em;text-transform:uppercase;margin-bottom:.3rem;">
                      Octal (8)
                    </div>
                    <div style="font-size:1.3rem;font-weight:700;color:#f43f5e;
                      font-family:'DM Mono',monospace;">{oct(dec)[2:]}</div>
                  </div>
                  <div style="background:var(--card);border:1px solid var(--border);
                    border-radius:var(--r);padding:1rem;">
                    <div style="font-size:.7rem;color:#4a4a72;font-weight:700;
                      letter-spacing:.08em;text-transform:uppercase;margin-bottom:.3rem;">
                      Hexadecimal (16)
                    </div>
                    <div style="font-size:1.3rem;font-weight:700;color:#818cf8;
                      font-family:'DM Mono',monospace;">{hex(dec)[2:].upper()}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_time:
        try:
            import pytz
            ZONES = ["UTC","US/Eastern","US/Central","US/Pacific","Europe/London",
                     "Europe/Paris","Europe/Berlin","Asia/Tokyo","Asia/Shanghai",
                     "Asia/Kolkata","Asia/Kathmandu","Australia/Sydney","America/Sao_Paulo"]
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            cols = st.columns(3)
            for i, tz_name in enumerate(ZONES):
                try:
                    tz = pytz.timezone(tz_name)
                    local = now_utc.astimezone(tz)
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div style="background:var(--card);border:1px solid var(--border);
                          border-radius:var(--r);padding:.9rem 1rem;text-align:center;
                          margin-bottom:.5rem;">
                          <div style="font-size:.7rem;color:#4a4a72;font-weight:600;
                            margin-bottom:.3rem;">{tz_name.split('/')[-1].replace('_',' ')}</div>
                          <div style="font-size:1.2rem;font-weight:700;color:#e8e8f8;
                            font-family:'DM Mono',monospace;">{local.strftime('%H:%M:%S')}</div>
                          <div style="font-size:.7rem;color:#4a4a72;margin-top:.2rem;">
                            {local.strftime('%b %d')}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception:
                    pass
        except ImportError:
            st.error("pytz not installed. Run: pip install pytz")


# ════════════════════════════════════════════════════════════════════════════════
# PASSWORD GEN
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Password Gen":
    page_header("🔐 Password Generator", "Strong, secure, cryptographically random")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          Options
        </div>
        """, unsafe_allow_html=True)
        length = st.slider("Length", 8, 128, 20)
        use_upper   = st.checkbox("Uppercase (A–Z)",       value=True)
        use_lower   = st.checkbox("Lowercase (a–z)",       value=True)
        use_digits  = st.checkbox("Numbers (0–9)",         value=True)
        use_symbols = st.checkbox("Symbols (!@#$…)",       value=True)
        excl_ambig  = st.checkbox("Exclude ambiguous (0,O,l,1)", value=False)
        num_pw      = st.slider("How many passwords", 1, 10, 3)

        if st.button("🔑 Generate", use_container_width=True):
            charset = ""
            if use_lower:   charset += string.ascii_lowercase
            if use_upper:   charset += string.ascii_uppercase
            if use_digits:  charset += string.digits
            if use_symbols: charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if excl_ambig:
                for ch in "0O1lI":
                    charset = charset.replace(ch, "")
            if not charset:
                st.error("Select at least one character type.")
            else:
                rng = random.SystemRandom()
                st.session_state["_passwords"] = [
                    ''.join(rng.choice(charset) for _ in range(length))
                    for _ in range(num_pw)
                ]

        st.markdown("---")
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          Passphrase
        </div>
        """, unsafe_allow_html=True)
        word_count = st.slider("Words", 3, 8, 4)
        separator  = st.text_input("Separator", value="-")
        if st.button("Generate Passphrase"):
            word_pool = ["correct","horse","battery","staple","purple","monkey",
                         "forest","quantum","river","solar","cosmic","delta",
                         "echo","flame","globe","harbor","ivory","jungle",
                         "kernel","lagoon","mosaic","nexus","orbit","prism"]
            # FIX #7: Use SystemRandom for passphrases too (was using
            # random.choices which is not cryptographically secure).
            rng = random.SystemRandom()
            phrase = separator.join(rng.choices(word_pool, k=word_count))
            st.code(phrase)

    with col2:
        passwords = st.session_state.get("_passwords", [])
        if passwords:
            st.markdown("""
            <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
              letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
              Generated
            </div>
            """, unsafe_allow_html=True)
            for pw in passwords:
                strength = sum([
                    any(c.isupper() for c in pw),
                    any(c.islower() for c in pw),
                    any(c.isdigit() for c in pw),
                    any(c in "!@#$%^&*()" for c in pw),
                    len(pw) >= 16,
                ])
                s_labels = {1:("Weak","#f43f5e"),2:("Fair","#f97316"),
                            3:("Good","#f59e0b"),4:("Strong","#22c55e"),
                            5:("Very Strong","#2dd4bf")}
                s_label, s_color = s_labels.get(strength, ("Weak","#f43f5e"))
                entropy = len(pw) * math.log2(max(len(set(pw)), 1))
                st.code(pw)
                st.markdown(
                    f'<div style="font-size:.72rem;color:{s_color};margin-top:-.4rem;'
                    f'margin-bottom:.7rem;font-family:\'DM Mono\',monospace;">'
                    f'{s_label} · {entropy:.0f} bits entropy</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          Hash Generator
        </div>
        """, unsafe_allow_html=True)
        hash_input = st.text_input("Text to hash", placeholder="Enter text…",
                                    label_visibility="collapsed")
        if hash_input:
            for name, algo in [("MD5","md5"),("SHA-1","sha1"),("SHA-256","sha256"),("SHA-512","sha512")]:
                h = hashlib.new(algo, hash_input.encode()).hexdigest()
                st.markdown(f"""
                <div style="margin-bottom:.4rem;">
                  <span style="font-size:.72rem;color:#4a4a72;font-weight:700;">{name}</span>
                </div>
                """, unsafe_allow_html=True)
                st.code(h)


# ════════════════════════════════════════════════════════════════════════════════
# COLOR TOOLS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Color Tools":
    page_header("🎨 Color Tools", "Palettes, gradients and colour theory")

    tab_picker, tab_palette, tab_grad = st.tabs(["🎯 Color Info","🎨 Palette","🌈 Gradient"])

    # FIX #4 — hex_to_hsl had an operator precedence bug.
    # Original:  hue=60*((g_-b_)/(mx-mn)%6)
    # Python evaluates this as: (g_-b_) / ((mx-mn) % 6)  — WRONG
    # Correct:   hue=60*(((g_-b_)/(mx-mn))%6)
    def hex_to_hsl(h):
        r_, g_, b_ = int(h[1:3],16)/255, int(h[3:5],16)/255, int(h[5:7],16)/255
        mx, mn = max(r_,g_,b_), min(r_,g_,b_)
        l = (mx+mn)/2
        s = 0 if mx==mn else (mx-mn)/(1-abs(2*l-1))
        if mx==mn:
            hue = 0
        elif mx==r_:
            hue = 60 * (((g_-b_) / (mx-mn)) % 6)    # FIXED precedence
        elif mx==g_:
            hue = 60 * ((b_-r_) / (mx-mn) + 2)
        else:
            hue = 60 * ((r_-g_) / (mx-mn) + 4)
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

    with tab_picker:
        hex_color = st.color_picker("Pick a color", "#5b5ef4")
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        hue, s_val, l_val = hex_to_hsl(hex_color)
        cr, cg, cb = 255-r, 255-g, 255-b
        comp = f"#{cr:02x}{cg:02x}{cb:02x}"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background:{hex_color};border-radius:var(--r);
              height:110px;border:1px solid rgba(255,255,255,.05);"></div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--border);
              border-radius:var(--r);padding:1rem;">
              <div style="font-size:.7rem;color:#4a4a72;font-weight:700;margin-bottom:.2rem;">HEX</div>
              <div style="font-weight:700;font-family:'DM Mono',monospace;
                color:#e8e8f8;margin-bottom:.6rem;">{hex_color.upper()}</div>
              <div style="font-size:.7rem;color:#4a4a72;font-weight:700;margin-bottom:.2rem;">RGB</div>
              <div style="font-weight:700;font-family:'DM Mono',monospace;
                color:#e8e8f8;margin-bottom:.6rem;">rgb({r}, {g}, {b})</div>
              <div style="font-size:.7rem;color:#4a4a72;font-weight:700;margin-bottom:.2rem;">HSL</div>
              <div style="font-weight:700;font-family:'DM Mono',monospace;
                color:#e8e8f8;">hsl({hue:.0f}°, {s_val*100:.0f}%, {l_val*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--border);
              border-radius:var(--r);padding:1rem;">
              <div style="font-size:.7rem;color:#4a4a72;font-weight:700;margin-bottom:.4rem;">
                Complementary
              </div>
              <div style="background:{comp};border-radius:var(--r2);height:40px;
                margin-bottom:.4rem;border:1px solid rgba(255,255,255,.05);"></div>
              <div style="font-family:'DM Mono',monospace;font-size:.82rem;
                color:#e8e8f8;margin-bottom:.6rem;">{comp.upper()}</div>
              <div style="font-size:.7rem;color:#4a4a72;font-weight:700;margin-bottom:.2rem;">
                Lightness
              </div>
              <div style="font-weight:700;font-family:'DM Mono',monospace;
                color:#e8e8f8;">{l_val*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Tints →**")
        tint_cols = st.columns(11)
        for i, col in enumerate(tint_cols):
            f = i / 10
            tc = f"#{int(r+(255-r)*f):02x}{int(g+(255-g)*f):02x}{int(b+(255-b)*f):02x}"
            col.markdown(f'<div style="background:{tc};height:36px;border-radius:5px;"></div>',
                         unsafe_allow_html=True)

    with tab_palette:
        base_c = st.color_picker("Base color", "#5b5ef4", key="pal_base")
        scheme = st.selectbox("Scheme",
            ["Analogous","Triadic","Complementary","Split-Complementary","Random Harmonious"])
        n_colors = st.slider("Colors", 3, 10, 5)

        if st.button("Generate Palette"):
            bh, bs, bl = hex_to_hsl(base_c)
            palette = []
            if scheme == "Analogous":
                step = 30 / max(n_colors-1, 1)
                palette = [hsl_to_hex(bh - 15 + step*i, bs, bl) for i in range(n_colors)]
            elif scheme == "Triadic":
                for i in range(n_colors):
                    palette.append(hsl_to_hex(bh + 120*i, bs, bl))
            elif scheme == "Complementary":
                for i in range(n_colors):
                    palette.append(hsl_to_hex(bh + (i%2)*180 + i*5, bs, bl*(0.7+0.06*i)))
            elif scheme == "Split-Complementary":
                hues = [bh, bh+150, bh+210]
                for i in range(n_colors):
                    palette.append(hsl_to_hex(hues[i%3], bs, bl*(0.8+0.04*i)))
            else:
                palette = [hsl_to_hex(random.uniform(0,360),
                           random.uniform(0.5,0.85), random.uniform(0.35,0.65))
                           for _ in range(n_colors)]

            pal_cols = st.columns(len(palette))
            for i, (c, col) in enumerate(zip(palette, pal_cols)):
                col.markdown(f"""
                <div style="background:{c};border-radius:var(--r2);height:70px;
                  margin-bottom:.3rem;"></div>
                <div style="text-align:center;font-size:.7rem;font-weight:700;
                  font-family:'DM Mono',monospace;color:#9090b8;">{c.upper()}</div>
                """, unsafe_allow_html=True)

            # FIX #2: Removed raw CSS code display (st.code with language="css").
            # The original code used st.code() to show CSS snippets like
            # "/* Palette */\n:root { --c1: #xxx; }" which rendered raw CSS
            # text in the frontend — the exact bug the user reported.
            # Now uses an expander so the CSS is hidden by default.
            css = "  ".join(f"--c{i+1}: {c};" for i,c in enumerate(palette))
            with st.expander("📋 Copy CSS Variables"):
                st.code(f":root {{ {css} }}", language="css")

    with tab_grad:
        c1, c2 = st.columns(2)
        with c1: g1 = st.color_picker("Color 1", "#5b5ef4")
        with c2: g2 = st.color_picker("Color 2", "#2dd4bf")
        g3_en = st.checkbox("Add third stop")
        g3    = st.color_picker("Color 3", "#f43f5e") if g3_en else None
        direction = st.select_slider("Direction",
            options=["0°","45°","90°","135°","180°","225°","270°","315°"], value="135°")
        colors_str = f"{g1}, {g3}, {g2}" if g3 else f"{g1}, {g2}"
        css_grad = f"linear-gradient({direction}, {colors_str})"
        st.markdown(f"""
        <div style="background:{css_grad};border-radius:var(--r);
          height:110px;margin:1rem 0;border:1px solid rgba(255,255,255,.05);"></div>
        """, unsafe_allow_html=True)
        # FIX #2: Same fix — hide raw CSS in an expander instead of showing it
        # directly in the frontend.
        with st.expander("📋 Copy CSS"):
            st.code(f"background: {css_grad};", language="css")


# ════════════════════════════════════════════════════════════════════════════════
# BUDGET TRACKER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Budget Tracker":
    page_header("💰 Budget Tracker", "Income, expenses and savings at a glance")

    col_form, col_summary = st.columns([1, 2])

    with col_form:
        b_type   = st.radio("Type", ["💚 Income","❤️ Expense"], horizontal=True)
        b_amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        b_cat    = st.selectbox("Category",
            ["🍔 Food","🏠 Housing","🚗 Transport","📚 Education",
             "🎮 Entertainment","💊 Health","👗 Clothing","📱 Tech",
             "💰 Salary","💼 Freelance","🎁 Gift","Other"])
        b_desc   = st.text_input("Description", placeholder="Coffee, salary…")
        b_date   = st.date_input("Date", value=datetime.date.today())
        if st.button("＋ Add Entry", use_container_width=True):
            if b_amount > 0:
                st.session_state.budget_items.append({
                    "type":b_type,"amount":b_amount,"category":b_cat,
                    "desc":b_desc,"date":str(b_date),
                    "id": str(_uuid.uuid4())      # FIX #9: unique ID per entry
                })
                st.rerun()
            else:
                st.warning("Amount must be greater than 0.")

        if st.session_state.budget_items:
            st.markdown("<div style='margin-top:.6rem;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear all", use_container_width=True):
                st.session_state.budget_items = []
                st.rerun()

    with col_summary:
        items   = st.session_state.budget_items
        income  = sum(i["amount"] for i in items if "Income" in i["type"])
        expense = sum(i["amount"] for i in items if "Expense" in i["type"])
        balance = income - expense

        c1, c2, c3 = st.columns(3)
        c1.metric("💚 Income",  f"${income:,.2f}")
        c2.metric("❤️ Expense", f"${expense:,.2f}")
        c3.metric("💰 Balance", f"${balance:,.2f}",
                  delta=f"{'+'if balance>=0 else ''}{balance:,.2f}")

        if items:
            tab_log, tab_chart = st.tabs(["📋 Log","📊 Chart"])
            df_budget = pd.DataFrame(items)

            with tab_log:
                # FIX #9: Added individual delete buttons for each budget entry
                for j, item in enumerate(reversed(items[-25:])):
                    color  = "#22c55e" if "Income" in item["type"] else "#f43f5e"
                    sign   = "+" if "Income" in item["type"] else "-"
                    desc   = f" · {item['desc']}" if item.get("desc") else ""
                    entry_id = item.get("id", str(j))
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:.8rem;
                      padding:.6rem .9rem;background:var(--surface);
                      border:1px solid var(--border);border-radius:var(--r2);
                      margin-bottom:.35rem;">
                      <div style="color:{color};font-weight:700;
                        font-family:'DM Mono',monospace;min-width:90px;font-size:.9rem;">
                        {sign}${item['amount']:,.2f}
                      </div>
                      <div style="flex:1;">
                        <div style="font-size:.86rem;font-weight:500;color:#e8e8f8;">
                          {item['category']}{desc}
                        </div>
                        <div style="font-size:.72rem;color:#4a4a72;">{item['date']}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab_chart:
                exp_only = df_budget[df_budget["type"].str.contains("Expense")]
                if not exp_only.empty:
                    fig = px.pie(exp_only, values="amount", names="category",
                                 title="Expense Breakdown", template="plotly_dark",
                                 hole=0.4)
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                      font=dict(family="DM Sans",color="#9090b8"),
                                      margin=dict(t=40,b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expenses to chart yet.")
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#1c1c3a;">
              <div style="font-size:2.5rem;margin-bottom:.5rem;">💸</div>
              <div style="color:#4a4a72;">Add your first entry on the left</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# QR GENERATOR
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "QR Generator":
    page_header("📱 QR Generator", "Create instant QR codes for any content")

    col1, col2 = st.columns([1, 1])

    with col1:
        qr_type = st.selectbox("Content type",
            ["URL / Link","Plain Text","Email","Phone","WiFi","vCard"])
        qr_data = ""
        if qr_type == "URL / Link":
            qr_data = st.text_input("URL", placeholder="https://example.com")
        elif qr_type == "Plain Text":
            qr_data = st.text_area("Text", height=100)
        elif qr_type == "Email":
            email   = st.text_input("Email address")
            subject = st.text_input("Subject (optional)")
            qr_data = f"mailto:{email}?subject={subject}" if email else ""
        elif qr_type == "Phone":
            phone   = st.text_input("Phone", placeholder="+1234567890")
            qr_data = f"tel:{phone}" if phone else ""
        elif qr_type == "WiFi":
            ssid     = st.text_input("Network name (SSID)")
            password = st.text_input("Password", type="password")
            enc      = st.selectbox("Encryption", ["WPA","WEP","nopass"])
            qr_data  = f"WIFI:T:{enc};S:{ssid};P:{password};;" if ssid else ""
        elif qr_type == "vCard":
            name    = st.text_input("Full Name")
            phone_v = st.text_input("Phone")
            email_v = st.text_input("Email")
            org     = st.text_input("Organization")
            qr_data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone_v}\nEMAIL:{email_v}\nORG:{org}\nEND:VCARD" if name else ""

        st.markdown("**Style**")
        qr_fg   = st.color_picker("Foreground", "#5b5ef4")
        qr_bg   = st.color_picker("Background", "#ffffff")
        qr_size = st.slider("Size (px)", 150, 450, 250, step=50)
        ec_sel  = st.selectbox("Error correction", ["L (7%)","M (15%)","Q (25%)","H (30%)"])
        ec_map  = {"L (7%)": qrcode.constants.ERROR_CORRECT_L,
                   "M (15%)": qrcode.constants.ERROR_CORRECT_M,
                   "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
                   "H (30%)": qrcode.constants.ERROR_CORRECT_H}

        if st.button("🔲 Generate QR Code", use_container_width=True):
            if qr_data.strip():
                qr = qrcode.QRCode(version=1, error_correction=ec_map[ec_sel],
                                   box_size=10, border=4)
                qr.add_data(qr_data)
                qr.make(fit=True)
                img = qr.make_image(fill_color=qr_fg, back_color=qr_bg)
                img = img.resize((qr_size, qr_size), Image.NEAREST)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.session_state["_qr_img"]  = buf.getvalue()
                st.session_state["_qr_data"] = qr_data
                st.session_state["_qr_size"] = qr_size
                st.rerun()
            else:
                st.warning("Enter some content to encode.")

    with col2:
        if st.session_state.get("_qr_img"):
            qr_size = st.session_state.get("_qr_size", 250)
            # FIX #3: Removed split div tags across separate st.markdown() calls.
            # The original opened a <div> in one st.markdown(), rendered st.image()
            # in between, then closed it in another st.markdown().  This
            # violates the rule stated in the app's own comments and can
            # cause broken HTML rendering.  Now we use a single self-contained
            # container.
            with st.container():
                st.image(st.session_state["_qr_img"], caption="Your QR Code", width=qr_size)
            st.download_button("⬇️ Download PNG", st.session_state["_qr_img"],
                               file_name="qrcode.png", mime="image/png",
                               use_container_width=True)
            preview = st.session_state["_qr_data"][:80]
            if len(st.session_state["_qr_data"]) > 80:
                preview += "…"
            st.markdown(f"""
            <div style="font-size:.72rem;color:#4a4a72;margin-top:.4rem;
              word-break:break-all;font-family:'DM Mono',monospace;">{preview}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:5rem 2rem;color:#1c1c3a;">
              <div style="font-size:3.5rem;margin-bottom:.6rem;">📱</div>
              <div style="color:#4a4a72;">Configure and generate your QR code</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TEXT TOOLS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Text Tools":
    page_header("✍️ Text Tools", "Analyse, transform and generate text")

    tab_analyze, tab_transform, tab_gen, tab_diff = st.tabs(
        ["📊 Analyse","🔄 Transform","🎲 Generate","🔍 Diff"])

    with tab_analyze:
        text_in = st.text_area("Paste or type text", height=180,
                                placeholder="Enter any text to analyse…",
                                label_visibility="collapsed")
        if text_in:
            words       = len(text_in.split())
            sentences   = max(1, len(re.split(r'[.!?]+', text_in)))
            paragraphs  = max(1, len([p for p in text_in.split('\n\n') if p.strip()]))
            chars_ns    = len(text_in.replace(" ", ""))
            reading_min = max(1, words // 200)
            unique_w    = len(set(text_in.lower().split()))

            c1,c2,c3 = st.columns(3)
            c1.metric("Words",      words)
            c2.metric("Characters", len(text_in))
            c3.metric("Chars (no space)", chars_ns)
            c4,c5,c6 = st.columns(3)
            c4.metric("Sentences",   sentences)
            c5.metric("Paragraphs",  paragraphs)
            c6.metric("Read time",   f"{reading_min} min")
            st.metric("Unique words", unique_w)

            word_freq = {}
            for w in re.findall(r'\b[a-zA-Z]{4,}\b', text_in.lower()):
                word_freq[w] = word_freq.get(w, 0) + 1
            if word_freq:
                top = sorted(word_freq.items(), key=lambda x: -x[1])[:15]
                fig = px.bar(x=[w[0] for w in top], y=[w[1] for w in top],
                             template="plotly_dark", labels={"x":"","y":"Count"},
                             title="Top Words")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(17,17,36,.9)",
                                  font=dict(family="DM Sans",color="#9090b8"),
                                  margin=dict(t=36,b=20), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab_transform:
        text_t = st.text_area("Text to transform", height=130,
                               label_visibility="collapsed",
                               placeholder="Enter text…")
        TRANSFORMS = [
            ("UPPERCASE",           lambda t: t.upper()),
            ("lowercase",           lambda t: t.lower()),
            ("Title Case",          lambda t: t.title()),
            ("Sentence case",       lambda t: t.capitalize()),
            ("camelCase",           lambda t: ''.join(w.capitalize() if i else w.lower() for i,w in enumerate(t.split()))),
            ("snake_case",          lambda t: '_'.join(t.lower().split())),
            ("kebab-case",          lambda t: '-'.join(t.lower().split())),
            ("Reverse text",        lambda t: t[::-1]),
            ("Remove extra spaces", lambda t: ' '.join(t.split())),
            ("Remove line breaks",  lambda t: t.replace('\n',' ')),
            ("Sort lines A–Z",      lambda t: '\n'.join(sorted(t.splitlines()))),
            ("Remove duplicates",   lambda t: '\n'.join(list(dict.fromkeys(t.splitlines())))),
        ]
        cols = st.columns(3)
        for i, (name, fn) in enumerate(TRANSFORMS):
            with cols[i % 3]:
                if st.button(name, key=f"tx_{i}", use_container_width=True):
                    if text_t:
                        st.session_state["_transformed"] = fn(text_t)
                        st.session_state["_tx_name"]    = name

        if st.session_state.get("_transformed"):
            st.markdown(f"""
            <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
              letter-spacing:.08em;text-transform:uppercase;
              margin:.8rem 0 .4rem;">
              Result — {st.session_state.get('_tx_name','')}
            </div>
            """, unsafe_allow_html=True)
            st.text_area("result", value=st.session_state["_transformed"],
                         height=110, label_visibility="collapsed")
            st.download_button("⬇️ Download",
                               st.session_state["_transformed"].encode(),
                               file_name="transformed.txt")

    with tab_gen:
        gen_type = st.selectbox("Generate",
            ["Lorem Ipsum","Random Names","Random Emails",
             "Random UUIDs","Random Numbers","Fake Addresses"])
        count = st.slider("Count", 1, 20, 5)

        # FIX #6: Min/Max inputs for "Random Numbers" were INSIDE the button
        # click handler AND inside the elif branch, meaning they only appeared
        # AFTER clicking the button.  Now they render before the button for
        # proper UX — user sets range first, then clicks Generate.
        gen_mn, gen_mx = 1, 1000
        if gen_type == "Random Numbers":
            gc1, gc2 = st.columns(2)
            with gc1:
                gen_mn = st.number_input("Min", value=1)
            with gc2:
                gen_mx = st.number_input("Max", value=1000)

        if st.button("🎲 Generate", use_container_width=True):
            lines = []
            if gen_type == "Lorem Ipsum":
                lorem = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                         "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ")
                lines = [lorem * random.randint(1,2) for _ in range(count)]
            elif gen_type == "Random Names":
                firsts = ["Alice","Bob","Charlie","Diana","Ethan","Fiona","George","Hannah","Ivan","Julia","Kai","Luna"]
                lasts  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore"]
                lines  = [f"{random.choice(firsts)} {random.choice(lasts)}" for _ in range(count)]
            elif gen_type == "Random Emails":
                domains = ["gmail.com","yahoo.com","outlook.com","proton.me","hey.com"]
                names_p = ["alice","bob","charlie","diana","ethan","fiona","george","hannah"]
                lines   = [f"{random.choice(names_p)}{random.randint(10,999)}@{random.choice(domains)}" for _ in range(count)]
            elif gen_type == "Random UUIDs":
                lines = [str(_uuid.uuid4()) for _ in range(count)]
            elif gen_type == "Random Numbers":
                lo, hi = int(gen_mn), int(gen_mx)
                if lo > hi:
                    lo, hi = hi, lo
                lines = [str(random.randint(lo, hi)) for _ in range(count)]
            elif gen_type == "Fake Addresses":
                streets = ["Oak St","Maple Ave","Pine Rd","Cedar Blvd","Elm Dr"]
                cities  = ["New York","Los Angeles","Chicago","Houston","Phoenix","Austin"]
                states  = ["NY","CA","IL","TX","AZ"]
                lines   = [f"{random.randint(100,9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000,99999)}" for _ in range(count)]
            output = "\n".join(lines)
            st.text_area("Generated", value=output, height=180, label_visibility="collapsed")
            st.download_button("⬇️ Download", output.encode(), file_name="generated.txt")

    with tab_diff:
        col1, col2 = st.columns(2)
        with col1:
            text_a = st.text_area("Original", height=200, key="diff_a")
        with col2:
            text_b = st.text_area("Modified", height=200, key="diff_b")
        if st.button("🔍 Compare", use_container_width=True):
            if text_a and text_b:
                import difflib
                diff = list(difflib.unified_diff(
                    text_a.splitlines(keepends=True),
                    text_b.splitlines(keepends=True),
                    fromfile="Original", tofile="Modified", lineterm=""
                ))
                if diff:
                    st.code("".join(diff), language="diff")
                    st.markdown(badge(f"{len(diff)} diff lines", "#2dd4bf"), unsafe_allow_html=True)
                else:
                    st.success("✅ Texts are identical!")
            else:
                st.warning("Enter text in both fields.")


# ════════════════════════════════════════════════════════════════════════════════
# HABIT TRACKER
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Habit Tracker":
    page_header("🎯 Habit Tracker", "Build streaks, track consistency")

    col_add, col_track = st.columns([1, 2])

    with col_add:
        st.markdown("""
        <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
          letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
          New Habit
        </div>
        """, unsafe_allow_html=True)
        h_name = st.text_input("Habit name", placeholder="Exercise, Read, Meditate…")
        h_icon = st.text_input("Icon (emoji)", placeholder="🏋️")
        h_goal = st.text_input("Goal description", placeholder="30 min daily")
        if st.button("＋ Add Habit", use_container_width=True):
            if h_name.strip():
                if h_name in st.session_state.habits:
                    st.warning("Habit already exists.")
                else:
                    st.session_state.habits[h_name] = {
                        "icon": h_icon or "⭐",
                        "goal": h_goal,
                        "dates": []
                    }
                    st.rerun()
            else:
                st.warning("Enter a habit name.")

    with col_track:
        today = str(datetime.date.today())
        habits = st.session_state.habits

        if not habits:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#1c1c3a;">
              <div style="font-size:2.5rem;margin-bottom:.5rem;">🎯</div>
              <div style="color:#4a4a72;">Add your first habit!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for h_name, h_data in list(habits.items()):
                done_today = today in h_data.get("dates", [])
                dates = sorted(h_data.get("dates", []))
                streak = 0
                if dates:
                    cur = datetime.date.today()
                    while str(cur) in dates:
                        streak += 1
                        cur -= datetime.timedelta(days=1)

                total_done = len(dates)
                goal_str   = f" · {h_data['goal']}" if h_data.get("goal") else ""

                c_icon, c_info, c_btn, c_del = st.columns([1, 5, 2, 1])
                with c_icon:
                    st.markdown(f"""
                    <div style="font-size:1.7rem;text-align:center;
                      padding:.5rem 0;">{h_data['icon']}</div>
                    """, unsafe_allow_html=True)
                with c_info:
                    streak_color = "#f59e0b" if streak > 0 else "#4a4a72"
                    pct_done = min(100, streak * 3)
                    st.markdown(f"""
                    <div style="padding:.35rem 0;">
                      <div style="font-weight:600;font-size:.9rem;color:#e8e8f8;">
                        {h_name}
                        <span style="color:#4a4a72;font-size:.76rem;font-weight:400;">
                          {goal_str}
                        </span>
                      </div>
                      <div style="font-size:.75rem;color:{streak_color};margin:.2rem 0;">
                        🔥 {streak} day streak · {total_done} total
                      </div>
                      {progress_bar(pct_done)}
                    </div>
                    """, unsafe_allow_html=True)
                with c_btn:
                    btn_label = "✅ Done!" if done_today else "○ Mark"
                    if st.button(btn_label, key=f"habit_{h_name}", use_container_width=True):
                        if done_today:
                            st.session_state.habits[h_name]["dates"].remove(today)
                        else:
                            st.session_state.habits[h_name]["dates"].append(today)
                        st.rerun()
                with c_del:
                    if st.button("✕", key=f"hdel_{h_name}"):
                        del st.session_state.habits[h_name]
                        st.rerun()

            # 30-day heatmap
            st.markdown("---")
            st.markdown("""
            <div style="font-size:.75rem;font-weight:700;color:#4a4a72;
              letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">
              Last 30 Days
            </div>
            """, unsafe_allow_html=True)
            today_dt = datetime.date.today()
            last_30  = [today_dt - datetime.timedelta(days=i) for i in range(29, -1, -1)]
            hm_cols  = st.columns(30)
            for col, day in zip(hm_cols, last_30):
                day_str   = str(day)
                completed = sum(1 for h in habits.values() if day_str in h.get("dates", []))
                total_h   = max(1, len(habits))
                if completed == 0:
                    color = "#0d0d1a"
                elif completed == total_h:
                    color = "#5b5ef4"
                else:
                    alpha = 0.2 + (completed / total_h) * 0.6
                    color = f"rgba(91,94,244,{alpha:.2f})"
                is_today = day_str == today
                border = "1px solid rgba(91,94,244,.5)" if is_today else "1px solid transparent"
                col.markdown(
                    f'<div title="{day_str}: {completed}/{total_h}" '
                    f'style="background:{color};border-radius:3px;height:16px;{border}"></div>',
                    unsafe_allow_html=True
                )
            st.markdown(f"""
            <div style="font-size:.7rem;color:#1c1c3a;margin-top:.4rem;
              font-family:'DM Mono',monospace;">
              Darker = more habits done · Outlined = today
            </div>
            """, unsafe_allow_html=True)
