# color_tools.py — Color Info, Palette Generator, and Gradient Builder
import html
import math
import random
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


# ── Color conversion helpers ──────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert HEX string (#RRGGBB) to (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (R, G, B) tuple to HEX string."""
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b))),
    )


def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """Convert (R, G, B) to (H, S, L) with H in [0,360], S,L in [0,100]."""
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx = max(r_, g_, b_)
    mn = min(r_, g_, b_)
    delta = mx - mn

    # Lightness
    l_ = (mx + mn) / 2.0

    # Saturation
    if delta == 0:
        s_ = 0.0
    else:
        s_ = delta / (1.0 - abs(2.0 * l_ - 1.0)) if (1.0 - abs(2.0 * l_ - 1.0)) != 0 else 0.0

    # Hue — FIX operator precedence: use parentheses around (mx-mn)
    if delta == 0:
        h_ = 0.0
    elif mx == r_:
        h_ = 60.0 * (((g_ - b_) / delta) % 6)
    elif mx == g_:
        h_ = 60.0 * (((b_ - r_) / delta) + 2)
    elif mx == b_:
        h_ = 60.0 * (((r_ - g_) / delta) + 4)

    if h_ < 0:
        h_ += 360.0

    return (round(h_, 1), round(s_ * 100, 1), round(l_ * 100, 1))


def hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    """Convert (H, S, L) with H in [0,360], S,L in [0,100] to (R, G, B)."""
    s_ = s / 100.0
    l_ = l / 100.0
    c = (1.0 - abs(2.0 * l_ - 1.0)) * s_
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = l_ - c / 2.0

    if h < 60:
        r_, g_, b_ = c, x, 0
    elif h < 120:
        r_, g_, b_ = x, c, 0
    elif h < 180:
        r_, g_, b_ = 0, c, x
    elif h < 240:
        r_, g_, b_ = 0, x, c
    elif h < 300:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x

    return (
        int((r_ + m) * 255),
        int((g_ + m) * 255),
        int((b_ + m) * 255),
    )


def complementary_color(hex_color: str) -> str:
    """Return the complementary color."""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    new_h = (h + 180) % 360
    r2, g2, b2 = hsl_to_rgb(new_h, s, l)
    return rgb_to_hex(r2, g2, b2)


def generate_tints(hex_color: str, steps: int = 11) -> list:
    """Generate tints from pure color to white."""
    r, g, b = hex_to_rgb(hex_color)
    tints = []
    for i in range(steps):
        factor = i / (steps - 1)
        nr = int(r + (255 - r) * factor)
        ng = int(g + (255 - g) * factor)
        nb = int(b + (255 - b) * factor)
        tints.append(rgb_to_hex(nr, ng, nb))
    return tints


def _analogous(hex_color: str, count: int) -> list:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    colors = []
    for i in range(count):
        new_h = (h + (i - count // 2) * 30) % 360
        r2, g2, b2 = hsl_to_rgb(new_h, s, l)
        colors.append(rgb_to_hex(r2, g2, b2))
    return colors


def _triadic(hex_color: str, count: int) -> list:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    colors = []
    base_angles = [0, 120, 240]
    for i in range(count):
        angle = base_angles[i % 3]
        new_h = (h + angle) % 360
        lightness = l + (i // 3) * 5
        lightness = min(100, max(0, lightness))
        r2, g2, b2 = hsl_to_rgb(new_h, s, lightness)
        colors.append(rgb_to_hex(r2, g2, b2))
    return colors


def _complementary(hex_color: str, count: int) -> list:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    colors = []
    for i in range(count):
        new_h = (h + 180) % 360 if i % 2 == 1 else h
        lightness = l + (i // 2) * 8
        lightness = min(100, max(0, lightness))
        r2, g2, b2 = hsl_to_rgb(new_h, s, lightness)
        colors.append(rgb_to_hex(r2, g2, b2))
    return colors


def _split_complementary(hex_color: str, count: int) -> list:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    colors = []
    base_angles = [0, 150, 210]
    for i in range(count):
        angle = base_angles[i % 3]
        new_h = (h + angle) % 360
        r2, g2, b2 = hsl_to_rgb(new_h, s, l)
        colors.append(rgb_to_hex(r2, g2, b2))
    return colors


def _random_harmonious(hex_color: str, count: int) -> list:
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    base_h = h
    colors = [hex_color]
    for _ in range(count - 1):
        new_h = (base_h + random.uniform(-60, 60)) % 360
        new_s = max(20, min(100, s + random.uniform(-20, 20)))
        new_l = max(20, min(80, l + random.uniform(-25, 25)))
        r2, g2, b2 = hsl_to_rgb(new_h, new_s, new_l)
        colors.append(rgb_to_hex(r2, g2, b2))
    return colors


PALETTE_SCHEMES = {
    "Analogous": _analogous,
    "Triadic": _triadic,
    "Complementary": _complementary,
    "Split-Complementary": _split_complementary,
    "Random Harmonious": _random_harmonious,
}


def render():
    """Render the Color Tools page."""
    inject_css()
    init_state()

    page_header("Color Tools", "Explore colors, generate palettes, and build gradients")

    tab_info, tab_palette, tab_gradient = st.tabs(["🎨 Color Info", "🎭 Palette", "🌊 Gradient"])

    # ═══════════════════════════════════════════════════════════════════════════
    # COLOR INFO TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_info:
        hex_input = st.color_picker("Pick a color", value="#5b5ef4", key="clr_pick")

        if hex_input:
            r, g, b = hex_to_rgb(hex_input)
            h, s, l = rgb_to_hsl(r, g, b)
            comp = complementary_color(hex_input)
            tints = generate_tints(hex_input, 11)

            # Swatch + info row
            st.markdown(
                f'<div style="display:flex;gap:1rem;margin-bottom:1rem;align-items:stretch;">'
                f'<div style="width:120px;min-height:120px;border-radius:var(--r);'
                f'background:{hex_input};border:2px solid var(--border);flex-shrink:0;"></div>'
                f'<div style="flex:1;display:flex;flex-direction:column;gap:.4rem;">'
                f'<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                f'text-transform:uppercase;letter-spacing:.04em;">Color Values</div>'
                f'{_info_row("HEX", hex_input)}'
                f'{_info_row("RGB", f"rgb({r}, {g}, {b})")}'
                f'{_info_row("HSL", f"hsl({h}, {s}%, {l}%)")}'
                f'{_info_row("Complementary", comp)}'
                f'{_info_row("Lightness", f"{l}%")}'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # Tints row
            st.markdown(
                '<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                'text-transform:uppercase;letter-spacing:.04em;margin:.6rem 0 .4rem;">'
                'Tints</div>',
                unsafe_allow_html=True,
            )
            tints_html = '<div style="display:flex;gap:4px;margin-bottom:1rem;">'
            for t in tints:
                tints_html += (
                    f'<div style="flex:1;height:36px;border-radius:4px;background:{t};'
                    f'border:1px solid var(--border);transition:transform .15s;" '
                    f'title="{t}"></div>'
                )
            tints_html += '</div>'
            st.markdown(tints_html, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PALETTE TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_palette:
        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            base_color = st.color_picker("Base color", value="#5b5ef4", key="pal_base")
            scheme = st.selectbox(
                "Scheme",
                options=list(PALETTE_SCHEMES.keys()),
                label_visibility="collapsed",
                key="pal_scheme",
            )
            count = st.slider("Color count", min_value=3, max_value=10, value=5, key="pal_count")

        with p_col2:
            st.markdown('<div style="margin-top:1.8rem;"></div>', unsafe_allow_html=True)
            if st.button("✨ Generate Palette", use_container_width=True, key="pal_gen"):
                fn = PALETTE_SCHEMES[scheme]
                st.session_state["_palette"] = fn(base_color, count)

        palette = getattr(st.session_state, "_palette", None)
        if not palette:
            empty_state("🎨", "Configure and generate a color palette")
        else:
            # Show palette boxes
            pal_html = '<div style="display:flex;gap:6px;margin-bottom:1rem;flex-wrap:wrap;">'
            for c in palette:
                r_c, g_c, b_c = hex_to_rgb(c)
                h_c, s_c, l_c = rgb_to_hsl(r_c, g_c, b_c)
                fg = "#ffffff" if l_c < 55 else "#000000"
                pal_html += (
                    f'<div style="flex:1;min-width:80px;border-radius:var(--r2);background:{c};'
                    f'border:1px solid var(--border);padding:.8rem .6rem;text-align:center;'
                    f'min-height:90px;display:flex;flex-direction:column;justify-content:center;gap:.3rem;">'
                    f'<div style="font-size:.7rem;font-weight:700;font-family:DM Mono,monospace;'
                    f'color:{fg};">{c}</div>'
                    f'<div style="font-size:.6rem;color:{fg};opacity:.7;">rgb({r_c},{g_c},{b_c})</div>'
                    f'</div>'
                )
            pal_html += '</div>'
            st.markdown(pal_html, unsafe_allow_html=True)

            # CSS variables in expander — NEVER show raw CSS directly
            with st.expander("📋 Copy CSS Variables"):
                css_lines = []
                for i, c in enumerate(palette):
                    r_c, g_c, b_c = hex_to_rgb(c)
                    h_c, s_c, l_c = rgb_to_hsl(r_c, g_c, b_c)
                    css_lines.append(f"  --palette-{i+1}: {c};  /* rgb({r_c}, {g_c}, {b_c}) | hsl({h_c}, {s_c}%, {l_c}%) */")
                css_var_text = ":root {\n" + "\n".join(css_lines) + "\n}"
                st.code(css_var_text, language="css")

    # ═══════════════════════════════════════════════════════════════════════════
    # GRADIENT TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_gradient:
        g_col1, g_col2 = st.columns([1, 1])
        with g_col1:
            color1 = st.color_picker("Start color", value="#5b5ef4", key="grad_c1")
            color2 = st.color_picker("End color", value="#2dd4bf", key="grad_c2")
            use_mid = st.checkbox("Add middle stop", value=False, key="grad_mid")
            color3 = None
            if use_mid:
                color3 = st.color_picker("Middle color", value="#f59e0b", key="grad_c3")

        with g_col2:
            direction = st.slider(
                "Direction (degrees)", min_value=0, max_value=360, value=135, key="grad_dir"
            )

        if color3:
            grad_css = f"linear-gradient({direction}deg, {color1}, {color3}, {color2})"
        else:
            grad_css = f"linear-gradient({direction}deg, {color1}, {color2})"

        # Preview
        st.markdown(
            f'<div style="width:100%;height:180px;border-radius:var(--r);background:{grad_css};'
            f'border:1px solid var(--border);margin-bottom:1rem;"></div>',
            unsafe_allow_html=True,
        )

        # CSS code in expander
        with st.expander("📋 Copy CSS"):
            css_prop = f"background: {grad_css};"
            st.code(css_prop, language="css")


def _info_row(label: str, value: str) -> str:
    """Return a single info row as HTML."""
    return (
        f'<div style="display:flex;align-items:center;gap:.6rem;padding:.25rem 0;'
        f'border-bottom:1px solid var(--border);">'
        f'<span style="font-size:.72rem;color:var(--ink3);min-width:110px;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:.03em;">{label}</span>'
        f'<span style="font-size:.82rem;color:var(--ink);font-family:DM Mono,monospace;'
        f'font-weight:500;">{html.escape(value)}</span>'
        f'</div>'
    )
