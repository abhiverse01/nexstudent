# habit_tracker.py — Track daily habits with streaks and a 30-day heatmap
import html
from datetime import date, timedelta
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state, progress_bar

DEFAULT_ICONS = ["📚", "💪", "🧘", "💧", "🏃", "🎨", "✍️", "🎸", "🧠", "🍎"]


def _calc_streak(dates: list) -> int:
    """Calculate current streak from a list of date strings."""
    if not dates:
        return 0
    unique = sorted(set(dates), reverse=True)
    today_str = str(date.today())
    yesterday_str = str(date.today() - timedelta(days=1))

    # Streak must include today or yesterday
    if unique[0] not in (today_str, yesterday_str):
        return 0

    streak = 1
    for i in range(len(unique) - 1):
        prev = date.fromisoformat(unique[i])
        curr = date.fromisoformat(unique[i + 1])
        if (prev - curr).days == 1:
            streak += 1
        else:
            break
    return streak


def _calc_total(dates: list) -> int:
    """Return total unique dates completed."""
    return len(set(dates))


def _heatmap_color(level: float) -> str:
    """Return a background color based on completion level (0-1)."""
    if level <= 0:
        return "var(--surface)"
    elif level < 0.25:
        return "rgba(91, 94, 244, 0.2)"
    elif level < 0.5:
        return "rgba(91, 94, 244, 0.4)"
    elif level < 0.75:
        return "rgba(91, 94, 244, 0.65)"
    else:
        return "rgba(91, 94, 244, 0.9)"


def render():
    """Render the Habit Tracker page."""
    inject_css()
    init_state()

    page_header("Habit Tracker", "Build streaks and track daily progress")

    col_left, col_right = st.columns([2, 3])

    # ═══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN — Add habit form
    # ═══════════════════════════════════════════════════════════════════════════
    with col_left:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '➕ Add Habit</div></div>',
            unsafe_allow_html=True,
        )

        habit_name = st.text_input(
            "Habit name",
            placeholder="e.g. Read 30 minutes",
            label_visibility="collapsed",
            key="habit_name",
        )

        icon_cols = st.columns(5)
        selected_icon = "📚"
        for i, ic in enumerate(DEFAULT_ICONS):
            with icon_cols[i]:
                if st.button(ic, key=f"habit_icon_{i}", use_container_width=True):
                    selected_icon = ic

        goal = st.text_input(
            "Goal description",
            placeholder="e.g. Read at least 30 pages",
            label_visibility="collapsed",
            key="habit_goal",
        )

        if st.button("✅ Add Habit", use_container_width=True, key="habit_add"):
            name = habit_name.strip()
            if name:
                if name in st.session_state.habits:
                    st.warning("Habit already exists!")
                else:
                    st.session_state.habits[name] = {
                        "icon": selected_icon,
                        "goal": goal.strip() or "Daily habit",
                        "dates": [],
                    }
                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN — Habit list
    # ═══════════════════════════════════════════════════════════════════════════
    with col_right:
        habits = st.session_state.habits

        if not habits:
            empty_state("🎯", "No habits yet — add your first one")
        else:
            for name, data in habits.items():
                dates = data.get("dates", [])
                icon = data.get("icon", "📚")
                goal = data.get("goal", "")
                streak = _calc_streak(dates)
                total = _calc_total(dates)
                today_str = str(date.today())
                done_today = today_str in dates

                progress_pct = min(100, int((total / 30) * 100))
                streak_color = "var(--amber)" if streak >= 7 else "var(--sol)" if streak >= 3 else "var(--ink3)"

                # Habit card
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    f'border-radius:var(--r);padding:.8rem 1rem;margin-bottom:.5rem;">'
                    f'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:.8rem;">'
                    # Left side: icon + info
                    f'<div style="flex:1;min-width:0;">'
                    f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">'
                    f'<span style="font-size:1.3rem;">{icon}</span>'
                    f'<span style="font-size:.92rem;font-weight:700;color:var(--ink);'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                    f'{html.escape(name)}</span></div>'
                    f'<div style="font-size:.74rem;color:var(--ink3);margin-bottom:.3rem;">'
                    f'{html.escape(goal)}</div>'
                    # Streak + total
                    f'<div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.4rem;">'
                    f'{badge(f"🔥 {streak} day streak", streak_color)}'
                    f'{badge(f"{total} total", "var(--teal)")}'
                    f'{badge("✅ Done today" if done_today else "⬜ Pending", "var(--green)" if done_today else "var(--ink3)")}'
                    f'</div>'
                    # Progress bar
                    f'{progress_bar(progress_pct, "var(--sol)")}'
                    f'</div>'
                    # Right side: action buttons
                    f'<div style="display:flex;flex-direction:column;gap:.3rem;flex-shrink:0;">'
                    f'<div style="font-size:.68rem;color:var(--ink3);text-align:center;">'
                    f'{progress_pct}%</div>'
                    f'</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                # Action buttons in columns
                act_col1, act_col2, act_col3 = st.columns([1, 1, 1])
                with act_col1:
                    if done_today:
                        if st.button("↩️ Undo", key=f"habit_undo_{name}", use_container_width=True):
                            dates_list = data["dates"]
                            if today_str in dates_list:
                                dates_list.remove(today_str)
                            st.rerun()
                    else:
                        if st.button("✅ Done", key=f"habit_done_{name}", use_container_width=True):
                            if today_str not in data["dates"]:
                                data["dates"].append(today_str)
                            st.rerun()
                with act_col2:
                    # Delete button
                    if st.button("🗑️", key=f"habit_del_{name}", use_container_width=True):
                        del st.session_state.habits[name]
                        st.rerun()
                with act_col3:
                    st.markdown("")  # Spacer

    # ═══════════════════════════════════════════════════════════════════════════
    # 30-DAY HEATMAP
    # ═══════════════════════════════════════════════════════════════════════════
    if habits:
        st.markdown('<div style="margin:1.2rem 0 .6rem;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            '📅 30-Day Overview</div>',
            unsafe_allow_html=True,
        )

        # Get all unique dates across habits to determine range
        all_dates = set()
        for data in habits.values():
            all_dates.update(data.get("dates", []))

        # Show last 30 days
        today = date.today()
        heatmap_cols = st.columns(30)
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            day_str = str(day)

            # Count habits completed on this day
            completed = sum(
                1 for data in habits.values() if day_str in data.get("dates", [])
            )
            total_habits = len(habits)
            level = completed / total_habits if total_habits > 0 else 0
            bg = _heatmap_color(level)

            with heatmap_cols[29 - i]:
                is_today = i == 0
                border = "var(--sol)" if is_today else "var(--border)"
                day_label = day.strftime("%d")
                weekday = day.strftime("%a")[0]
                st.markdown(
                    f'<div style="text-align:center;margin-bottom:.15rem;">'
                    f'<div style="font-size:.55rem;color:var(--ink3);margin-bottom:.1rem;">{weekday}</div>'
                    f'<div style="width:100%;aspect-ratio:1;border-radius:4px;background:{bg};'
                    f'border:1px solid {border};display:flex;align-items:center;justify-content:center;'
                    f'font-size:.6rem;font-weight:700;color:{"var(--ink)" if level > 0.25 else "var(--ink3)"};">'
                    f'{day_label}</div>'
                    f'<div style="font-size:.5rem;color:var(--ink3);margin-top:.1rem;">'
                    f'{completed}/{total_habits}</div></div>',
                    unsafe_allow_html=True,
                )
