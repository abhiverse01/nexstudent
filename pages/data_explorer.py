# data_explorer.py — CSV data tool with upload, stats, visualisation, and correlations
import io
import streamlit as st
import pandas as pd
import numpy as np

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


# Consistent dark-theme styling for Plotly charts
PLOTLY_THEME = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#e8e8f8", "family": "DM Sans, sans-serif", "size": 13},
        "xaxis": {
            "gridcolor": "#1c1c3a",
            "zerolinecolor": "#252550",
            "tickfont": {"color": "#9090b8"},
        },
        "yaxis": {
            "gridcolor": "#1c1c3a",
            "zerolinecolor": "#252550",
            "tickfont": {"color": "#9090b8"},
        },
        "colorway": [
            "#5b5ef4", "#2dd4bf", "#f59e0b", "#f43f5e", "#22c55e",
            "#818cf8", "#ec4899", "#06b6d4", "#a855f7", "#eab308",
        ],
        "margin": {"t": 40, "r": 20, "b": 50, "l": 50},
    },
}


def _demo_csv() -> bytes:
    """Generate a small demo CSV for download."""
    buf = io.StringIO()
    buf.write("Name,Age,Score,Grade,Subject,Passed\n")
    rows = [
        ("Alice", 20, 92, "A", "Math", True),
        ("Bob", 22, 78, "C", "Physics", True),
        ("Charlie", 21, 65, "D", "Chemistry", False),
        ("Diana", 23, 88, "B", "Math", True),
        ("Eve", 20, 95, "A", "Physics", True),
        ("Frank", 24, 55, "F", "Chemistry", False),
        ("Grace", 22, 82, "B", "Math", True),
        ("Hank", 21, 71, "C", "Physics", True),
        ("Ivy", 23, 98, "A", "Chemistry", True),
        ("Jack", 20, 60, "D", "Math", False),
        ("Karen", 22, 85, "B", "Physics", True),
        ("Leo", 21, 73, "C", "Chemistry", True),
    ]
    for name, age, score, grade, subject, passed in rows:
        buf.write(f"{name},{age},{score},{grade},{subject},{passed}\n")
    return buf.getvalue().encode("utf-8")


def render():
    """Render the Data Explorer page."""
    inject_css()
    init_state()

    page_header("Data Explorer", "Upload, explore, and visualise CSV data")

    # ── File uploader ──────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload a CSV file",
        type=["csv", "tsv"],
        label_visibility="collapsed",
        key="data_uploader",
    )

    # Demo download button when no file is uploaded
    if uploaded is None:
        st.markdown(
            '<div style="text-align:center;margin:.6rem 0;">'
            '<span style="color:var(--ink3);font-size:.82rem;">No file uploaded — try with sample data:</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label="⬇️ Download Demo CSV",
            data=_demo_csv(),
            file_name="demo_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
        empty_state("📊", "Upload a CSV or try the demo file above")
        return

    # ── Read CSV ───────────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return

    # ── Row badges ─────────────────────────────────────────────────────────────
    rows, cols = df.shape
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    num_count = len(numeric_cols)

    st.markdown(
        f'<div style="display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;">'
        f'{badge(f"{rows} rows", "var(--sol)")}'
        f'{badge(f"{cols} columns", "var(--teal)")}'
        f'{badge(f"{num_count} numeric", "var(--amber)")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_data, tab_stats, tab_viz, tab_corr = st.tabs(
        ["📋 Data", "📈 Statistics", "📊 Visualise", "🔗 Correlations"]
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DATA TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_data:
        search = st.text_input(
            "Search / filter rows",
            placeholder="Type to filter across all columns…",
            label_visibility="collapsed",
            key="data_search",
        )
        if search.strip():
            mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            filtered_df = df[mask]
            st.markdown(f'<div style="margin-bottom:.4rem;">{badge(f"{len(filtered_df)} matching rows", "var(--green)")}</div>', unsafe_allow_html=True)
        else:
            filtered_df = df

        st.dataframe(filtered_df, use_container_width=True, height=420)

    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_stats:
        # Describe
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Summary Statistics</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df.describe(include="all"), use_container_width=True, height=300)

        st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)

        # Missing values
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Missing Values</div>',
            unsafe_allow_html=True,
        )
        missing = df.isnull().sum()
        if missing.sum() == 0:
            success_msg = '<span style="color:var(--green);font-weight:600;">✅ No missing values found!</span>'
            st.markdown(success_msg, unsafe_allow_html=True)
        else:
            missing_df = missing[missing > 0].reset_index()
            missing_df.columns = ["Column", "Missing Count"]
            missing_df["% Missing"] = (missing_df["Missing Count"] / rows * 100).round(1).astype(str) + "%"
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

        st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)

        # Column types
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Column Types</div>',
            unsafe_allow_html=True,
        )
        types_df = pd.DataFrame({
            "Column": df.columns,
            "Dtype": df.dtypes.values,
            "Non-Null": df.notnull().sum().values,
        })
        st.dataframe(types_df, use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # VISUALISE TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_viz:
        chart_type = st.selectbox(
            "Chart type",
            options=["Bar", "Line", "Scatter", "Histogram", "Box", "Pie", "Area"],
            label_visibility="collapsed",
            key="viz_chart_type",
        )

        all_cols = df.columns.tolist()

        sel_col1, sel_col2, sel_col3 = st.columns([1, 1, 1])
        with sel_col1:
            x_col = st.selectbox("X axis / Column", options=all_cols, key="viz_x")
        with sel_col2:
            numeric_cols_list = df.select_dtypes(include=np.number).columns.tolist()
            y_options = ["None"] + numeric_cols_list
            y_col = st.selectbox("Y axis / Value", options=y_options, key="viz_y")
        with sel_col3:
            color_options = ["None"] + all_cols
            color_col = st.selectbox("Color by (optional)", options=color_options, key="viz_color")

        try:
            import plotly.express as px

            y_data = None if y_col == "None" else y_col
            color_data = color_col if color_col != "None" else None

            # Build kwargs — only include y / color when meaningful
            if chart_type == "Histogram":
                kwargs = {"x": x_col}
            elif chart_type == "Pie":
                kwargs = {"names": x_col}
            else:
                kwargs = {"x": x_col}
                if y_data is not None:
                    kwargs["y"] = y_data
                # Only pass color when a real column is selected (never None)
                if color_data is not None:
                    kwargs["color"] = color_data

            # Create the figure with the built kwargs
            chart_fn = {
                "Bar": px.bar,
                "Line": px.line,
                "Scatter": px.scatter,
                "Histogram": px.histogram,
                "Box": px.box,
                "Area": px.area,
            }.get(chart_type, px.bar)

            fig = chart_fn(df, **kwargs)

            # Apply dark theme
            fig.update_layout(**PLOTLY_THEME["layout"])

            st.plotly_chart(fig, use_container_width=True, height=500)

        except ImportError:
            st.warning("Install plotly for charts: pip install plotly")
        except Exception as e:
            st.error(f"Chart error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # CORRELATIONS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_corr:
        if num_count < 2:
            empty_state("🔗", "Need at least 2 numeric columns for correlation analysis")
        else:
            try:
                import plotly.express as px

                corr_matrix = df[numeric_cols].corr().round(3)

                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    aspect="auto",
                )
                fig.update_layout(**PLOTLY_THEME["layout"])
                fig.update_traces(
                    textfont={"size": 11, "color": "#e8e8f8"},
                    colorbar=dict(title="Correlation", tickfont=dict(color="#9090b8")),
                )

                st.plotly_chart(fig, use_container_width=True, height=500)

                # Show correlation table
                st.markdown(
                    '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
                    'margin:1rem 0 .6rem;letter-spacing:.04em;text-transform:uppercase;">'
                    'Correlation Matrix</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(corr_matrix, use_container_width=True)

            except ImportError:
                st.warning("Install plotly for charts: pip install plotly")
            except Exception as e:
                st.error(f"Correlation error: {e}")
