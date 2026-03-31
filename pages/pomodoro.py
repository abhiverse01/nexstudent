# pomodoro.py — Pomodoro Timer with customizable sessions
import time
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, progress_bar, empty_state


def render():
    """Render the Pomodoro Timer page."""
    inject_css()
    init_state()

    page_header("Pomodoro Timer", "Stay focused with timed work and break sessions")

    col_timer, col_settings = st.columns([2, 1])

    # ── Settings panel ────────────────────────────────────────────────────────
    with col_settings:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Settings</div></div>',
            unsafe_allow_html=True,
        )

        work_mins = st.slider(
            "Work (min)",
            min_value=1,
            max_value=90,
            value=25,
            step=1,
            key="pom_work",
        )
        short_break_mins = st.slider(
            "Short Break (min)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            key="pom_short",
        )
        long_break_mins = st.slider(
            "Long Break (min)",
            min_value=1,
            max_value=60,
            value=15,
            step=1,
            key="pom_long",
        )
        session_goal = st.text_input(
            "Session Goal",
            value="Focus on studying",
            placeholder="What are you working on?",
            label_visibility="visible",
            key="pom_goal",
        )

        # Technique info card
        st.markdown(
            '<div style="background:var(--surface);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1rem 1.1rem;margin-top:.8rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink);margin-bottom:.4rem;">'
            '🍅 Pomodoro Technique</div>'
            '<div style="color:var(--ink2);font-size:.78rem;line-height:1.6;">'
            '1. Pick a task to focus on<br>'
            '2. Set the timer (typically 25 min)<br>'
            '3. Work on the task until the timer rings<br>'
            '4. Take a short break (5 min)<br>'
            '5. After 4 sessions, take a long break (15 min)</div></div>',
            unsafe_allow_html=True,
        )

    # ── Timer panel ───────────────────────────────────────────────────────────
    with col_timer:
        # Mode selector
        modes = ["Work", "Short Break", "Long Break"]
        mode_times = {
            "Work": work_mins * 60,
            "Short Break": short_break_mins * 60,
            "Long Break": long_break_mins * 60,
        }
        mode_colors = {
            "Work": "var(--rose)",
            "Short Break": "var(--teal)",
            "Long Break": "var(--sol)",
        }

        current_mode = st.session_state.get("_pom_mode", "Work")

        mode_col1, mode_col2, mode_col3 = st.columns(3)
        for idx, (col, mode_name) in enumerate(zip(
            [mode_col1, mode_col2, mode_col3], modes
        )):
            is_active = current_mode == mode_name
            accent = mode_colors[mode_name]
            bg = accent if is_active else "var(--card)"
            color = "#fff" if is_active else "var(--ink2)"
            border = accent if is_active else "var(--border)"
            with col:
                st.markdown(
                    f'<div style="text-align:center;background:{bg};border:1px solid {border};'
                    f'border-radius:var(--r2);padding:.6rem .4rem;cursor:pointer;'
                    f'color:{color};font-weight:600;font-size:.8rem;transition:all .2s;">'
                    f'{mode_name}</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    mode_name,
                    key=f"pom_mode_{mode_name}",
                    use_container_width=True,
                ):
                    st.session_state._pom_mode = mode_name
                    st.session_state.pomodoro_running = False
                    st.session_state.pomodoro_end = None
                    st.rerun()

        total_seconds = mode_times[current_mode]

        # Calculate remaining time
        running = st.session_state.pomodoro_running
        end_time = st.session_state.pomodoro_end

        if running and end_time:
            remaining = max(0, end_time - time.time())
        else:
            remaining = total_seconds

        # Check if timer completed
        timer_done = running and remaining <= 0

        if timer_done:
            running = False
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_end = None

            if current_mode == "Work":
                st.session_state.pomodoro_sessions = st.session_state.pomodoro_sessions + 1
                st.session_state.pomodoro_total_mins = (
                    st.session_state.pomodoro_total_mins + work_mins
                )
            remaining = total_seconds

        # Timer display
        mins = int(remaining) // 60
        secs = int(remaining) % 60
        time_str = f"{mins:02d}:{secs:02d}"

        elapsed = total_seconds - remaining
        pct = int((elapsed / total_seconds) * 100) if total_seconds > 0 else 0
        pct = max(0, min(100, pct))

        accent = mode_colors[current_mode]

        st.markdown(
            f'<div style="background:var(--card);border:1px solid var(--border);'
            f'border-radius:var(--r);padding:2.5rem 2rem;text-align:center;margin:1rem 0;">'
            f'<div style="font-family:DM Mono,monospace;font-size:4.5rem;font-weight:700;'
            f'color:var(--ink);letter-spacing:.05em;line-height:1;">{time_str}</div>'
            f'<div style="margin-top:.3rem;">'
            f'{badge(current_mode, accent.replace("var(--", "").replace(")", ""))}</div>'
            f'<div style="margin:1rem auto 0;max-width:320px;">'
            f'{progress_bar(pct, accent)}</div>'
            f'<div style="text-align:right;font-size:.72rem;color:var(--ink3);'
            f'margin-top:.3rem;max-width:320px;margin-left:auto;margin-right:auto;">'
            f'{pct}% elapsed</div></div>',
            unsafe_allow_html=True,
        )

        # Session complete message
        if timer_done and current_mode == "Work":
            st.markdown(
                '<div style="background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.3);'
                'border-radius:var(--r);padding:1rem 1.2rem;text-align:center;margin-bottom:.8rem;">'
                '<div style="font-size:1.4rem;margin-bottom:.3rem;">🎉</div>'
                '<div style="font-weight:700;color:var(--green);font-size:.92rem;">Session complete!</div>'
                '<div style="color:var(--ink2);font-size:.8rem;margin-top:.2rem;">'
                'Great work! Take a break before the next session.</div></div>',
                unsafe_allow_html=True,
            )

        # Control buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            if running:
                if st.button("⏸ Pause", use_container_width=True, key="pom_pause"):
                    st.session_state.pomodoro_running = False
                    # Save remaining time so we can resume
                    st.session_state._pom_remaining = remaining
                    st.rerun()
            else:
                if st.button("▶️ Start", use_container_width=True, key="pom_start"):
                    # Resume from saved remaining or use full duration
                    resume_remaining = st.session_state.get("_pom_remaining", None)
                    start_remaining = resume_remaining if resume_remaining and resume_remaining > 0 else total_seconds
                    st.session_state.pomodoro_end = time.time() + start_remaining
                    st.session_state.pomodoro_running = True
                    st.rerun()

        with btn_col2:
            if st.button("🔄 Reset", use_container_width=True, key="pom_reset"):
                st.session_state.pomodoro_running = False
                st.session_state.pomodoro_end = None
                st.session_state._pom_remaining = None
                st.rerun()

        with btn_col3:
            if st.button("⏭ Skip", use_container_width=True, key="pom_skip"):
                st.session_state.pomodoro_running = False
                st.session_state.pomodoro_end = None
                st.session_state._pom_remaining = None
                remaining = 0
                st.rerun()

        # Stats
        sessions = st.session_state.pomodoro_sessions
        total_mins = st.session_state.pomodoro_total_mins

        st.markdown(
            f'<div style="display:flex;gap:.8rem;margin-top:1rem;">'
            f'<div style="flex:1;background:var(--surface);border:1px solid var(--border);'
            f'border-radius:var(--r2);padding:.7rem .9rem;text-align:center;">'
            f'<div style="color:var(--ink3);font-size:.68rem;font-weight:600;'
            f'letter-spacing:.04em;text-transform:uppercase;margin-bottom:.2rem;">'
            f'Sessions</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:1.4rem;font-weight:700;'
            f'color:var(--ink);">{sessions}</div></div>'
            f'<div style="flex:1;background:var(--surface);border:1px solid var(--border);'
            f'border-radius:var(--r2);padding:.7rem .9rem;text-align:center;">'
            f'<div style="color:var(--ink3);font-size:.68rem;font-weight:600;'
            f'letter-spacing:.04em;text-transform:uppercase;margin-bottom:.2rem;">'
            f'Total Minutes</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:1.4rem;font-weight:700;'
            f'color:var(--ink);">{total_mins}</div></div></div>',
            unsafe_allow_html=True,
        )

    # Auto-update when running
    if st.session_state.pomodoro_running:
        time.sleep(1)
        st.rerun()
