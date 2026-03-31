# math_solver.py — Math tools with Algebra, Calculus, Statistics, and Matrix tabs
import math
import html
import streamlit as st
import numpy as np

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state, success_card


def render():
    """Render the Math Solver page."""
    inject_css()
    init_state()

    page_header("Math Solver", "Algebra, calculus, statistics, and matrix operations")

    tab_algebra, tab_calc, tab_stats, tab_matrix = st.tabs(
        ["🔢 Algebra", "∫ Calculus", "📊 Statistics", "⊞ Matrix"]
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # ALGEBRA TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_algebra:
        mode = st.radio("Mode", ["Equation Solver", "Expression Simplifier", "Quadratic Formula"],
                         horizontal=True, key="algebra_mode")

        if mode == "Equation Solver":
            st.markdown(
                '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
                'Enter an equation (use = for equality, e.g. x**2 - 4 = 0)</div>',
                unsafe_allow_html=True,
            )
            eq_input = st.text_input("Equation", placeholder="e.g. x**2 - 4 = 0", label_visibility="collapsed",
                                      key="alg_eq")
            if st.button("Solve", key="alg_solve_btn", use_container_width=True) and eq_input.strip():
                try:
                    from sympy import symbols, solve, sympify

                    # Split on = sign
                    parts = eq_input.split("=")
                    if len(parts) == 2:
                        lhs = sympify(parts[0].strip())
                        rhs = sympify(parts[1].strip())
                        expr = lhs - rhs
                    else:
                        expr = sympify(eq_input.strip())

                    x = symbols("x")
                    result = solve(expr, x)

                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        'border-radius:var(--r);padding:1rem 1.2rem;">'
                        '<div style="font-size:.72rem;font-weight:700;color:var(--teal);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">Solutions</div>'
                        f'<div style="font-size:1rem;font-weight:600;color:var(--ink);font-family:DM Mono,monospace;">'
                        f'{html.escape(str(result))}</div></div>',
                        unsafe_allow_html=True,
                    )
                except ImportError:
                    st.error("Install sympy: pip install sympy")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif mode == "Expression Simplifier":
            st.markdown(
                '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
                'Enter an expression to simplify, expand, or factor</div>',
                unsafe_allow_html=True,
            )
            expr_input = st.text_input("Expression", placeholder="e.g. (x+1)**2 - x**2",
                                        label_visibility="collapsed", key="alg_expr")
            op_col1, op_col2, op_col3 = st.columns(3)
            with op_col1:
                if st.button("Simplify", key="alg_simplify", use_container_width=True) and expr_input.strip():
                    _try_sympy_op("Simplified", expr_input.strip(), "simplify")
            with op_col2:
                if st.button("Expand", key="alg_expand", use_container_width=True) and expr_input.strip():
                    _try_sympy_op("Expanded", expr_input.strip(), "expand")
            with op_col3:
                if st.button("Factor", key="alg_factor", use_container_width=True) and expr_input.strip():
                    _try_sympy_op("Factored", expr_input.strip(), "factor")

        elif mode == "Quadratic Formula":
            st.markdown(
                '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
                'Solve ax² + bx + c = 0</div>',
                unsafe_allow_html=True,
            )
            q_col1, q_col2, q_col3 = st.columns(3)
            with q_col1:
                a_val = st.number_input("a", value=1.0, step=0.1, key="quad_a")
            with q_col2:
                b_val = st.number_input("b", value=0.0, step=0.1, key="quad_b")
            with q_col3:
                c_val = st.number_input("c", value=-4.0, step=0.1, key="quad_c")

            if st.button("Solve Quadratic", key="quad_solve", use_container_width=True):
                if a_val == 0:
                    st.error("'a' cannot be zero in a quadratic equation.")
                else:
                    discriminant = b_val ** 2 - 4 * a_val * c_val
                    if discriminant > 0:
                        x1 = (-b_val + math.sqrt(discriminant)) / (2 * a_val)
                        x2 = (-b_val - math.sqrt(discriminant)) / (2 * a_val)
                        result = f"x₁ = {x1:.6g},  x₂ = {x2:.6g}"
                    elif discriminant == 0:
                        x1 = -b_val / (2 * a_val)
                        result = f"x = {x1:.6g}  (repeated root)"
                    else:
                        real = -b_val / (2 * a_val)
                        imag = math.sqrt(abs(discriminant)) / (2 * a_val)
                        result = f"x₁ = {real:.6g} + {imag:.6g}i,  x₂ = {real:.6g} - {imag:.6g}i"

                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        'border-radius:var(--r);padding:1rem 1.2rem;">'
                        f'<div style="font-size:.72rem;font-weight:700;color:var(--amber);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.3rem;">'
                        f'Discriminant: {discriminant:.4g}</div>'
                        f'<div style="font-size:1rem;font-weight:600;color:var(--ink);'
                        f'font-family:DM Mono,monospace;margin-top:.4rem;">{html.escape(result)}</div></div>',
                        unsafe_allow_html=True,
                    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CALCULUS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_calc:
        calc_mode = st.radio("Operation", ["Differentiation", "Integration"],
                              horizontal=True, key="calc_mode")

        st.markdown(
            '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
            'Enter expression in terms of x (e.g. x**3 + 2*x)</div>',
            unsafe_allow_html=True,
        )
        calc_expr = st.text_input("Expression", placeholder="e.g. x**3 + 2*x",
                                   label_visibility="collapsed", key="calc_expr")

        if calc_mode == "Integration":
            st.markdown(
                '<div style="font-size:.78rem;color:var(--ink3);margin-bottom:.5rem;">'
                'Leave bounds empty for indefinite integral</div>',
                unsafe_allow_html=True,
            )
            bnd_col1, bnd_col2 = st.columns(2)
            with bnd_col1:
                lower = st.text_input("Lower bound", placeholder="e.g. 0", label_visibility="collapsed",
                                       key="calc_lower")
            with bnd_col2:
                upper = st.text_input("Upper bound", placeholder="e.g. 1", label_visibility="collapsed",
                                       key="calc_upper")

            btn_label = "Integrate"
            btn_key = "calc_integrate"
        else:
            btn_label = "Differentiate"
            btn_key = "calc_diff"
            lower = ""
            upper = ""

        if st.button(btn_label, key=btn_key, use_container_width=True) and calc_expr.strip():
            try:
                from sympy import symbols, diff, integrate, sympify, Integral

                x = symbols("x")
                expr = sympify(calc_expr.strip())

                if calc_mode == "Differentiation":
                    result = diff(expr, x)
                    label = "Derivative (d/dx)"
                    result_str = str(result)
                else:
                    if lower.strip() and upper.strip():
                        a = sympify(lower.strip())
                        b = sympify(upper.strip())
                        result = integrate(expr, (x, a, b))
                        label = f"Definite integral [{lower.strip()}, {upper.strip()}]"
                        result_str = str(result)
                    else:
                        result = integrate(expr, x)
                        label = "Indefinite integral"
                        result_str = str(result) + " + C"

                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    'border-radius:var(--r);padding:1rem 1.2rem;">'
                    '<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
                    'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                    f'{html.escape(label)}</div>'
                    '<div style="font-size:1.05rem;font-weight:600;color:var(--ink);'
                    f'font-family:DM Mono,monospace;">{html.escape(result_str)}</div></div>',
                    unsafe_allow_html=True,
                )
            except ImportError:
                st.error("Install sympy: pip install sympy")
            except Exception as e:
                st.error(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_stats:
        st.markdown(
            '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
            'Enter numbers separated by commas</div>',
            unsafe_allow_html=True,
        )
        nums_input = st.text_input("Numbers", placeholder="e.g. 12, 45, 23, 67, 34, 89, 56",
                                    label_visibility="collapsed", key="stat_nums")

        if st.button("Compute Statistics", key="stat_compute", use_container_width=True) and nums_input.strip():
            try:
                nums = [float(n.strip()) for n in nums_input.split(",") if n.strip()]
                if not nums:
                    st.error("No valid numbers found.")
                else:
                    nums.sort()
                    n = len(nums)
                    mean = sum(nums) / n
                    median = nums[n // 2] if n % 2 == 1 else (nums[n // 2 - 1] + nums[n // 2]) / 2
                    variance = sum((x - mean) ** 2 for x in nums) / n
                    std_dev = math.sqrt(variance)
                    data_range = max(nums) - min(nums)

                    # Display stats in a grid
                    stats_items = [
                        ("Count", f"{n}", "var(--sol)"),
                        ("Sum", f"{sum(nums):.6g}", "var(--teal)"),
                        ("Mean", f"{mean:.6g}", "var(--amber)"),
                        ("Median", f"{median:.6g}", "var(--green)"),
                        ("Std Dev", f"{std_dev:.6g}", "var(--rose)"),
                        ("Range", f"{data_range:.6g}", "var(--sol2)"),
                        ("Min", f"{min(nums):.6g}", "#818cf8"),
                        ("Max", f"{max(nums):.6g}", "#ec4899"),
                    ]

                    grid_cols = st.columns(4)
                    for i, (label, val, color) in enumerate(stats_items):
                        with grid_cols[i % 4]:
                            st.markdown(
                                f'<div style="background:var(--card);border:1px solid var(--border);'
                                'border-radius:var(--r2);padding:.7rem .8rem;margin-bottom:.4rem;text-align:center;">'
                                f'<div style="font-size:.68rem;font-weight:700;color:var(--ink3);'
                                'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.2rem;">'
                                f'{label}</div>'
                                f'<div style="font-size:1rem;font-weight:700;color:{color};'
                                'font-family:DM Mono,monospace;">{val}</div></div>',
                                unsafe_allow_html=True,
                            )

                    # Distribution histogram
                    st.markdown('<div style="margin-top:.6rem;"></div>', unsafe_allow_html=True)
                    st.markdown(
                        '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
                        'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
                        'Distribution</div>',
                        unsafe_allow_html=True,
                    )
                    try:
                        import plotly.express as px
                        fig = px.histogram(x=nums, nbins=min(30, max(5, n // 2)),
                                           marginal="box")
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font={"color": "#e8e8f8", "family": "DM Sans, sans-serif"},
                            xaxis={"gridcolor": "#1c1c3a", "tickfont": {"color": "#9090b8"}},
                            yaxis={"gridcolor": "#1c1c3a", "tickfont": {"color": "#9090b8"}},
                            margin={"t": 30, "r": 20, "b": 50, "l": 50},
                        )
                        st.plotly_chart(fig, use_container_width=True, height=350)
                    except ImportError:
                        st.info("Install plotly for histogram: pip install plotly")

            except ValueError:
                st.error("Invalid number format. Use comma-separated numbers.")

    # ═══════════════════════════════════════════════════════════════════════════
    # MATRIX TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_matrix:
        size = st.radio("Matrix size", ["2×2", "3×3"], horizontal=True, key="mat_size")
        n = 2 if size == "2×2" else 3

        operation = st.selectbox(
            "Operation",
            options=["Determinant", "Inverse", "Transpose", "Add", "Subtract", "Multiply"],
            label_visibility="collapsed",
            key="mat_op",
        )

        # Determine how many matrices we need
        needs_two = operation in ("Add", "Subtract", "Multiply")

        st.markdown(
            f'<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            f'Matrix A ({n}×{n})</div>',
            unsafe_allow_html=True,
        )
        mat_a = _matrix_input(n, "mat_a")

        if needs_two:
            st.markdown(
                f'<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
                'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
                f'Matrix B ({n}×{n})</div>',
                unsafe_allow_html=True,
            )
            mat_b = _matrix_input(n, "mat_b")

        if st.button("Compute", key="mat_compute", use_container_width=True):
            try:
                arr_a = np.array(mat_a, dtype=float)

                if needs_two:
                    arr_b = np.array(mat_b, dtype=float)

                if operation == "Determinant":
                    result = np.linalg.det(arr_a)
                    result_str = f"{result:.6g}"
                    display_label = "Determinant"
                elif operation == "Inverse":
                    result = np.linalg.inv(arr_a)
                    result_str = None  # will display as matrix
                    display_label = "Inverse"
                elif operation == "Transpose":
                    result = arr_a.T
                    result_str = None
                    display_label = "Transpose"
                elif operation == "Add":
                    result = arr_a + arr_b
                    result_str = None
                    display_label = "A + B"
                elif operation == "Subtract":
                    result = arr_a - arr_b
                    result_str = None
                    display_label = "A - B"
                elif operation == "Multiply":
                    result = arr_a @ arr_b
                    result_str = None
                    display_label = "A × B"

                if result_str is not None:
                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        'border-radius:var(--r);padding:1rem 1.2rem;">'
                        f'<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                        f'{html.escape(display_label)}</div>'
                        f'<div style="font-size:1.2rem;font-weight:700;color:var(--ink);'
                        'font-family:DM Mono,monospace;">{html.escape(result_str)}</div></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    # Display matrix result
                    formatted = "\n".join(
                        ["[" + "  ".join(f"{v:10.4f}" for v in row) + "]" for row in result.tolist()]
                    )
                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        'border-radius:var(--r);padding:1rem 1.2rem;">'
                        f'<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                        f'{html.escape(display_label)}</div>'
                        f'<pre style="font-size:.95rem;color:var(--ink);font-family:DM Mono,monospace;'
                        f'line-height:1.6;margin:0;">{html.escape(formatted)}</pre></div>',
                        unsafe_allow_html=True,
                    )

            except np.linalg.LinAlgError:
                st.error("Matrix is singular — cannot compute inverse or determinant.")
            except Exception as e:
                st.error(f"Error: {e}")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _try_sympy_op(label: str, expr_str: str, func_name: str):
    """Attempt a sympy operation and display the result."""
    try:
        from sympy import parse_expr, simplify, expand, factor, sympify

        expr = parse_expr(expr_str)
        func_map = {"simplify": simplify, "expand": expand, "factor": factor}
        result = func_map[func_name](expr)

        st.markdown(
            f'<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1rem 1.2rem;">'
            '<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
            'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
            f'{html.escape(label)}</div>'
            '<div style="font-size:1.05rem;font-weight:600;color:var(--ink);'
            f'font-family:DM Mono,monospace;">{html.escape(str(result))}</div></div>',
            unsafe_allow_html=True,
        )
    except ImportError:
        st.error("Install sympy: pip install sympy")
    except Exception as e:
        st.error(f"Error: {e}")


def _matrix_input(n: int, prefix: str) -> list:
    """Render an n×n matrix input grid and return the values as a list of lists."""
    matrix = []
    for i in range(n):
        cols = st.columns(n)
        row = []
        for j in range(n):
            with cols[j]:
                val = st.number_input(
                    f"a{i+1}{j+1}",
                    value=0.0,
                    step=0.5,
                    label_visibility="collapsed",
                    key=f"{prefix}_{i}{j}",
                    format="%g",
                )
                row.append(val)
        matrix.append(row)
    return matrix
