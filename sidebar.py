# sidebar.py — Navigation sidebar with grouped items and tip widget
import streamlit as st
from components import badge


def render_sidebar():
    """Render the full sidebar: logo, grouped nav, and tip card."""

    # ── Logo ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:.5rem .5rem 1.6rem;display:flex;align-items:center;gap:.7rem;">
          <div style="width:36px;height:36px;background:linear-gradient(135deg,#5b5ef4,#818cf8);
            border-radius:10px;display:flex;align-items:center;justify-content:center;
            font-size:1.1rem;flex-shrink:0;">⚡</div>
          <div>
            <div style="font-size:1rem;font-weight:700;color:#e8e8f8;letter-spacing:-.02em;">Nexus</div>
            <div style="font-size:.7rem;color:#4a4a72;font-weight:500;letter-spacing:.04em;text-transform:uppercase;">Student Toolkit</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Navigation ────────────────────────────────────────────────────────────
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
        ("📷", "OCR Scanner"),
    ]

    groups = {
        "STUDY": NAV[:6],
        "TOOLS": NAV[6:11],
        "LIFE": NAV[11:],
    }

    for group_name, items in groups.items():
        st.markdown(
            f'<div style="font-size:.65rem;font-weight:700;color:#4a4a72;'
            f'letter-spacing:.1em;text-transform:uppercase;'
            f'padding:.3rem .5rem .2rem;margin-top:.5rem;">{group_name}</div>',
            unsafe_allow_html=True,
        )
        for icon, label in items:
            is_active = st.session_state.page == label
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                use_container_width=True,
                type="secondary" if is_active else "tertiary",
            ):
                st.session_state.page = label
                st.rerun()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Tip of the day ────────────────────────────────────────────────────────
    import random
    tips = [
        "Pair Pomodoro + Flashcards for maximum retention. Study in 25-min sprints.",
        "Use Smart Notes to summarise lectures right after class — retention boosts 40%.",
        "Break tasks into < 30 min chunks. Your brain estimates time more accurately.",
        "Review flashcards right before sleep. Consolidation happens during deep sleep.",
        "Use the OCR Scanner to digitise handwritten notes and add them to Smart Notes.",
        "Set a daily calorie budget — awareness alone improves spending decisions.",
        "Use keyboard shortcut 1-9 in the sidebar for quick page switching.",
        "Habits tracked for 21+ days become automatic. Start small, stay consistent.",
    ]
    tip = random.choice(tips)
    st.markdown(
        f"""
        <div style="background:rgba(91,94,244,.07);border:1px solid rgba(91,94,244,.15);
          border-radius:10px;padding:.75rem 1rem;font-size:.75rem;color:#4a4a72;margin:.3rem .2rem 0;">
          <div style="color:#818cf8;font-weight:700;margin-bottom:.3rem;font-size:.76rem;">
            💡 Tip of the day
          </div>
          {tip}
        </div>
        """,
        unsafe_allow_html=True,
    )
