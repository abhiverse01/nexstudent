# budget.py — Budget tracker with income/expense logging, metrics, and charting
import html
import uuid
from datetime import date
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state, progress_bar


CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Education",
    "Health",
    "Salary",
    "Freelance",
    "Gift",
    "Other",
]


def render():
    """Render the Budget Tracker page."""
    inject_css()
    init_state()

    page_header("Budget Tracker", "Track income, expenses, and visualise spending")

    col_left, col_right = st.columns([2, 3])

    # ═══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN — Add entry form
    # ═══════════════════════════════════════════════════════════════════════════
    with col_left:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '💰 Add Entry</div></div>',
            unsafe_allow_html=True,
        )

        entry_type = st.radio("Type", options=["Expense", "Income"], key="budget_type")

        amount = st.number_input(
            "Amount",
            min_value=0.01,
            step=0.01,
            format="%0.2f",
            label_visibility="collapsed",
            placeholder="Enter amount…",
            key="budget_amount",
        )

        category = st.selectbox(
            "Category",
            options=CATEGORIES,
            label_visibility="collapsed",
            key="budget_cat",
        )

        desc = st.text_input(
            "Description",
            placeholder="What was this for?",
            label_visibility="collapsed",
            key="budget_desc",
        )

        entry_date = st.date_input("Date", value=date.today(), key="budget_date")

        st.markdown('<div style="margin:.6rem 0;"></div>', unsafe_allow_html=True)

        if st.button("➕ Add Entry", use_container_width=True, key="budget_add"):
            if amount > 0:
                item = {
                    "type": entry_type,
                    "amount": round(amount, 2),
                    "category": category,
                    "desc": desc.strip() or category,
                    "date": str(entry_date),
                    "id": str(uuid.uuid4()),
                }
                st.session_state.budget_items.append(item)
                st.rerun()

        st.markdown('<div style="margin:.8rem 0;"></div>', unsafe_allow_html=True)

        if st.session_state.budget_items:
            if st.button("🗑️ Clear All", use_container_width=True, key="budget_clear"):
                st.session_state.budget_items = []
                st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN — Summary & display
    # ═══════════════════════════════════════════════════════════════════════════
    with col_right:
        items = st.session_state.budget_items

        if not items:
            empty_state("💳", "No budget entries yet — add your first one")
            return

        # Compute metrics
        total_income = sum(i["amount"] for i in items if i["type"] == "Income")
        total_expense = sum(i["amount"] for i in items if i["type"] == "Expense")
        balance = total_income - total_expense

        m1, m2, m3 = st.columns(3)
        m1.metric("Income", f"${total_income:,.2f}")
        m2.metric("Expense", f"${total_expense:,.2f}")
        bal_color = "normal" if balance >= 0 else "inverse"
        m3.metric("Balance", f"${balance:,.2f}", delta_color=bal_color)

        st.markdown('<div style="margin:.8rem 0;"></div>', unsafe_allow_html=True)

        tab_log, tab_chart = st.tabs(["📋 Log", "📊 Chart"])

        # ── Log tab ─────────────────────────────────────────────────────────
        with tab_log:
            recent = list(reversed(items[-25:]))
            for item in recent:
                sign = "+" if item["type"] == "Income" else "−"
                color = "var(--green)" if item["type"] == "Income" else "var(--rose)"
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    'border-radius:var(--r2);padding:.6rem .9rem;margin-bottom:.35rem;'
                    'display:flex;align-items:center;justify-content:space-between;">'
                    '<div style="display:flex;align-items:center;gap:.6rem;flex:1;min-width:0;">'
                    f'<div style="font-size:1.1rem;font-weight:700;color:{color};'
                    'font-family:DM Mono,monospace;min-width:24px;">{sign}</div>'
                    f'<div style="min-width:0;">'
                    f'<div style="font-size:.82rem;font-weight:600;color:var(--ink);'
                    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                    f'{html.escape(item["desc"])}</div>'
                    f'<div style="font-size:.7rem;color:var(--ink3);margin-top:.1rem;">'
                    f'{html.escape(item["category"])} · {html.escape(item["date"])}</div>'
                    f'</div></div>'
                    f'<div style="font-size:.88rem;font-weight:700;color:{color};'
                    'font-family:DM Mono,monospace;white-space:nowrap;margin-left:.6rem;">'
                    f'{sign}${item["amount"]:,.2f}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

        # ── Chart tab ───────────────────────────────────────────────────────
        with tab_chart:
            expenses = [i for i in items if i["type"] == "Expense"]
            if not expenses:
                empty_state("📊", "No expenses to chart yet")
            else:
                try:
                    import plotly.express as px

                    cat_totals = {}
                    for e in expenses:
                        cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]

                    cats = list(cat_totals.keys())
                    vals = list(cat_totals.values())

                    fig = px.pie(
                        names=cats,
                        values=vals,
                        hole=0.4,
                        color_discrete_sequence=[
                            "#5b5ef4", "#2dd4bf", "#f59e0b", "#f43f5e", "#22c55e",
                            "#818cf8", "#ec4899", "#06b6d4", "#a855f7", "#eab308", "#6366f1",
                        ],
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font={"color": "#e8e8f8", "family": "DM Sans, sans-serif", "size": 12},
                        margin={"t": 20, "r": 20, "b": 20, "l": 20},
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            font={"color": "#9090b8", "size": 11},
                        ),
                    )
                    fig.update_traces(
                        textposition="inside",
                        textfont={"color": "#ffffff", "size": 11},
                    )

                    st.plotly_chart(fig, use_container_width=True, height=420)

                except ImportError:
                    st.warning("Install plotly for charts: pip install plotly")
                    # Fallback: simple text summary
                    for cat, total in sorted(cat_totals.items(), key=lambda x: -x[1]):
                        pct = (total / total_expense * 100) if total_expense > 0 else 0
                        st.markdown(
                            f'<div style="margin-bottom:.3rem;">'
                            f'<span style="font-size:.78rem;color:var(--ink2);">{html.escape(cat)}</span>'
                            f'<span style="font-size:.78rem;color:var(--ink3);float:right;">'
                            f'${total:,.2f} ({pct:.0f}%)</span></div>'
                            f'{progress_bar(int(pct), "var(--sol)")}',
                            unsafe_allow_html=True,
                        )
