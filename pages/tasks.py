# tasks.py — Task Manager with priorities, categories, and filtering
import html
import uuid as _uuid
import streamlit as st
from datetime import datetime, date

from config import inject_css
from state import init_state
from components import page_header, badge, progress_bar, empty_state


PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_EMOJI = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
PRIORITY_COLORS = {"High": "var(--rose)", "Medium": "var(--amber)", "Low": "var(--green)"}


def render():
    """Render the Task Manager page."""
    inject_css()
    init_state()

    page_header("Task Manager", "Organize, prioritize, and track your tasks")

    tasks = st.session_state.tasks

    col_form, col_list = st.columns([1, 2])

    # ── Add task form ─────────────────────────────────────────────────────────
    with col_form:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Add Task</div></div>',
            unsafe_allow_html=True,
        )

        with st.form("task_form", clear_on_submit=True):
            task_name = st.text_input(
                "Task name",
                placeholder="What needs to be done?",
                label_visibility="collapsed",
                key="task_name_input",
            )

            priority = st.selectbox(
                "Priority",
                options=["High", "Medium", "Low"],
                index=1,
                label_visibility="visible",
            )

            category = st.text_input(
                "Category",
                placeholder="e.g. Homework, Personal, Work",
                label_visibility="visible",
                key="task_category_input",
            )

            due_date = st.date_input(
                "Due date",
                value=None,
                label_visibility="visible",
                key="task_due_input",
            )

            submitted = st.form_submit_button("➕ Add Task", use_container_width=True)

        if submitted and task_name.strip():
            new_task = {
                "name": task_name.strip(),
                "priority": priority,
                "category": category.strip() or "General",
                "due": str(due_date) if due_date else "",
                "done": False,
                "id": str(_uuid.uuid4()),
            }
            tasks.append(new_task)
            st.session_state.tasks = tasks
            st.rerun()

    # ── Task list panel ───────────────────────────────────────────────────────
    with col_list:
        # Filters
        if tasks:
            all_categories = sorted(set(t.get("category", "General") for t in tasks))
            filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

            with filter_col1:
                selected_cat = st.selectbox(
                    "Category",
                    options=["All"] + all_categories,
                    index=0,
                    label_visibility="collapsed",
                    key="task_filter_cat",
                )

            with filter_col2:
                show_done = st.checkbox("Show completed", value=True, key="task_show_done")

            with filter_col3:
                st.markdown('<div style="height:1.7rem;"></div>', unsafe_allow_html=True)
                clear_done_clicked = st.button("Clear done", use_container_width=True, key="task_clear_done")

            if clear_done_clicked:
                tasks = [t for t in tasks if not t.get("done")]
                st.session_state.tasks = tasks
                st.rerun()

        # Filter tasks
        filtered = tasks.copy()
        if tasks and selected_cat != "All":
            filtered = [t for t in filtered if t.get("category") == selected_cat]
        if tasks and not show_done:
            filtered = [t for t in filtered if not t.get("done")]

        # Sort by priority
        filtered.sort(key=lambda t: PRIORITY_ORDER.get(t.get("priority", "Medium"), 1))

        # Progress card
        if tasks:
            done_count = sum(1 for t in tasks if t.get("done"))
            total_count = len(tasks)
            pct = int((done_count / total_count) * 100) if total_count else 0
            bar_color = "var(--green)" if pct >= 75 else ("var(--amber)" if pct >= 40 else "var(--rose)")

            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                f'border-radius:var(--r);padding:1rem 1.2rem;margin-bottom:1rem;">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:.5rem;">'
                f'<span style="font-size:.82rem;font-weight:600;color:var(--ink);">'
                f'Progress</span>'
                f'{badge(f"{done_count}/{total_count} done", bar_color.replace("var(--", "").replace(")", ""))}'
                f'</div>'
                f'{progress_bar(pct, bar_color)}'
                f'<div style="text-align:right;font-size:.72rem;color:var(--ink3);margin-top:.3rem;">'
                f'{pct}%</div></div>',
                unsafe_allow_html=True,
            )

        # Task list
        if not tasks:
            empty_state("✅", "No tasks yet. Add one from the form!")
        elif not filtered:
            empty_state("🔍", "No tasks match your current filters.")
        else:
            for task in filtered:
                task_id = task.get("id", "")
                is_done = task.get("done", False)
                name = html.escape(task.get("name", ""))
                priority = task.get("priority", "Medium")
                category = task.get("category", "General")
                due = task.get("due", "")

                opacity = "opacity:.55;" if is_done else ""

                # Format due date
                due_display = ""
                if due:
                    try:
                        due_dt = datetime.strptime(str(due), "%Y-%m-%d").date()
                        today = date.today()
                        days_diff = (due_dt - today).days
                        if days_diff < 0:
                            due_display = f'<span style="color:var(--rose);font-size:.72rem;">Overdue by {abs(days_diff)}d</span>'
                        elif days_diff == 0:
                            due_display = '<span style="color:var(--amber);font-size:.72rem;">Due today</span>'
                        elif days_diff == 1:
                            due_display = '<span style="color:var(--amber);font-size:.72rem;">Due tomorrow</span>'
                        else:
                            due_display = f'<span style="color:var(--ink3);font-size:.72rem;">Due {due}</span>'
                    except (ValueError, TypeError):
                        due_display = f'<span style="color:var(--ink3);font-size:.72rem;">{html.escape(str(due))}</span>'

                name_style = "text-decoration:line-through;" if is_done else ""
                priority_emoji = PRIORITY_EMOJI.get(priority, "🟡")
                priority_color = PRIORITY_COLORS.get(priority, "var(--amber)")

                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    f'border-radius:var(--r2);padding:.7rem .9rem;margin-bottom:.4rem;'
                    f'{opacity}">'
                    f'<div style="display:flex;align-items:flex-start;gap:.6rem;">'
                    f'<div style="flex:1;">'
                    f'<div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.25rem;">'
                    f'<span style="font-weight:600;font-size:.86rem;color:var(--ink);{name_style}">'
                    f'{name}</span></div>'
                    f'<div style="display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;">'
                    f'<span style="font-size:.72rem;">{priority_emoji} {priority}</span>'
                    f'{badge(category, priority_color)}'
                    f'{due_display}'
                    f'</div></div></div></div>',
                    unsafe_allow_html=True,
                )

                # Checkbox and delete button
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    checked = st.checkbox(
                        "Done",
                        value=is_done,
                        key=f"task_done_{task_id}",
                        label_visibility="collapsed",
                    )
                    if checked != is_done:
                        task["done"] = checked
                        st.session_state.tasks = tasks
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️ Delete", key=f"task_del_{task_id}", use_container_width=True):
                        tasks = [t for t in tasks if t.get("id") != task_id]
                        st.session_state.tasks = tasks
                        st.rerun()
