# converter.py — Unit converter with Units, Number Bases, and Timezones tabs
import html
import streamlit as st
from datetime import datetime

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


# ── Conversion tables ──────────────────────────────────────────────────────────
# Each category maps unit_name -> factor relative to the base unit.
CONVERSIONS = {
    "Length": {
        "Millimeter (mm)": 0.001,
        "Centimeter (cm)": 0.01,
        "Meter (m)": 1.0,
        "Kilometer (km)": 1000.0,
        "Inch (in)": 0.0254,
        "Foot (ft)": 0.3048,
        "Yard (yd)": 0.9144,
        "Mile (mi)": 1609.344,
    },
    "Weight / Mass": {
        "Milligram (mg)": 0.000001,
        "Gram (g)": 0.001,
        "Kilogram (kg)": 1.0,
        "Metric Ton (t)": 1000.0,
        "Ounce (oz)": 0.0283495,
        "Pound (lb)": 0.453592,
        "Stone (st)": 6.35029,
    },
    "Area": {
        "Square Millimeter (mm²)": 1e-6,
        "Square Centimeter (cm²)": 1e-4,
        "Square Meter (m²)": 1.0,
        "Hectare (ha)": 10000.0,
        "Square Kilometer (km²)": 1e6,
        "Square Inch (in²)": 6.4516e-4,
        "Square Foot (ft²)": 0.092903,
        "Acre": 4046.86,
        "Square Mile (mi²)": 2.59e6,
    },
    "Volume": {
        "Milliliter (mL)": 0.001,
        "Liter (L)": 1.0,
        "Cubic Meter (m³)": 1000.0,
        "Gallon (US)": 3.78541,
        "Quart (US)": 0.946353,
        "Pint (US)": 0.473176,
        "Cup (US)": 0.236588,
        "Fluid Ounce (US fl oz)": 0.0295735,
        "Tablespoon (tbsp)": 0.0147868,
        "Teaspoon (tsp)": 0.00492892,
    },
    "Speed": {
        "m/s": 1.0,
        "km/h": 0.277778,
        "mph (mi/h)": 0.44704,
        "knot": 0.514444,
        "ft/s": 0.3048,
    },
    "Data Storage": {
        "Bit (b)": 1.0,
        "Byte (B)": 8.0,
        "Kilobyte (KB)": 8192.0,
        "Megabyte (MB)": 8388608.0,
        "Gigabyte (GB)": 8589934592.0,
        "Terabyte (TB)": 8796093022208.0,
        "Kibibyte (KiB)": 8192.0,
        "Mebibyte (MiB)": 8388608.0,
        "Gibibyte (GiB)": 8589934592.0,
    },
    "Energy": {
        "Joule (J)": 1.0,
        "Kilojoule (kJ)": 1000.0,
        "Calorie (cal)": 4.184,
        "Kilocalorie (kcal)": 4184.0,
        "Watt-hour (Wh)": 3600.0,
        "Kilowatt-hour (kWh)": 3600000.0,
        "Electronvolt (eV)": 1.602e-19,
        "BTU": 1055.06,
    },
    "Pressure": {
        "Pascal (Pa)": 1.0,
        "Kilopascal (kPa)": 1000.0,
        "Megapascal (MPa)": 1e6,
        "Bar": 100000.0,
        "Atmosphere (atm)": 101325.0,
        "mmHg (Torr)": 133.322,
        "PSI": 6894.76,
    },
}

# Temperature units (special handling)
TEMP_UNITS = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]

# All categories (including temperature)
ALL_CATEGORIES = ["Length", "Weight / Mass", "Temperature", "Area", "Volume",
                  "Speed", "Data Storage", "Energy", "Pressure"]

# Timezones list
TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
    "Pacific/Auckland",
]


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between Celsius, Fahrenheit, and Kelvin."""
    # First convert to Celsius
    if "Celsius" in from_unit:
        c = value
    elif "Fahrenheit" in from_unit:
        c = (value - 32) * 5.0 / 9.0
    elif "Kelvin" in from_unit:
        c = value - 273.15
    else:
        return value

    # Then convert from Celsius to target
    if "Celsius" in to_unit:
        return c
    elif "Fahrenheit" in to_unit:
        return c * 9.0 / 5.0 + 32
    elif "Kelvin" in to_unit:
        return c + 273.15
    return c


def _convert_generic(value: float, category: str, from_unit: str, to_unit: str) -> float:
    """Convert using a factor table for non-temperature categories."""
    table = CONVERSIONS[category]
    base_value = value * table[from_unit]
    return base_value / table[to_unit]


def _format_result(value: float) -> str:
    """Format a numeric result for display."""
    if abs(value) >= 1e9 or (abs(value) < 1e-6 and value != 0):
        return f"{value:.6e}"
    elif abs(value) >= 100:
        return f"{value:.4f}"
    elif abs(value) >= 1:
        return f"{value:.6f}"
    else:
        return f"{value:.8f}"


def render():
    """Render the Converter page."""
    inject_css()
    init_state()

    page_header("Converter", "Units, number bases, and timezone conversions")

    tab_units, tab_bases, tab_tz = st.tabs(["📏 Units", "🔢 Number Bases", "🌍 Timezones"])

    # ═══════════════════════════════════════════════════════════════════════════
    # UNITS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_units:
        category = st.selectbox(
            "Category",
            options=ALL_CATEGORIES,
            label_visibility="collapsed",
            key="conv_category",
        )

        is_temp = category == "Temperature"
        if is_temp:
            units = TEMP_UNITS
        else:
            units = list(CONVERSIONS[category].keys())

        u_col1, u_col2 = st.columns(2)
        with u_col1:
            from_unit = st.selectbox("From", options=units, key="conv_from")
        with u_col2:
            to_unit = st.selectbox("To", options=units, key="conv_to")

        value = st.number_input("Value", value=1.0, step=0.1, format="%g",
                                 label_visibility="collapsed", key="conv_value")

        if st.button("Convert", key="conv_btn", use_container_width=True):
            if from_unit == to_unit:
                result = value
            elif is_temp:
                result = _convert_temperature(value, from_unit, to_unit)
            else:
                result = _convert_generic(value, category, from_unit, to_unit)

            formatted = _format_result(result)

            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                'border-radius:var(--r);padding:1.2rem 1.4rem;margin-top:.5rem;">'
                '<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">Result</div>'
                '<div style="display:flex;align-items:baseline;gap:.5rem;">'
                f'<span style="font-size:1.6rem;font-weight:700;color:var(--sol);'
                'font-family:DM Mono,monospace;">{html.escape(formatted)}</span>'
                f'<span style="font-size:.88rem;color:var(--ink2);">{html.escape(to_unit)}</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )

            # Show conversion formula
            st.markdown(
                f'<div style="margin-top:.6rem;font-size:.78rem;color:var(--ink3);">'
                f'{html.escape(str(value))} {html.escape(from_unit)} = '
                f'{html.escape(formatted)} {html.escape(to_unit)}</div>',
                unsafe_allow_html=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # NUMBER BASES TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_bases:
        st.markdown(
            '<div style="font-size:.82rem;color:var(--ink3);margin-bottom:.6rem;">'
            'Enter a number in any base to convert between Decimal, Binary, Octal, and Hexadecimal</div>',
            unsafe_allow_html=True,
        )

        base_input = st.selectbox(
            "Input base",
            options=["Decimal (10)", "Binary (2)", "Octal (8)", "Hexadecimal (16)"],
            label_visibility="collapsed",
            key="base_input_type",
        )

        num_input = st.text_input(
            "Number",
            placeholder="Enter a number…",
            label_visibility="collapsed",
            key="base_num_input",
        )

        if st.button("Convert", key="base_btn", use_container_width=True) and num_input.strip():
            try:
                base_map = {
                    "Decimal (10)": 10,
                    "Binary (2)": 2,
                    "Octal (8)": 8,
                    "Hexadecimal (16)": 16,
                }
                input_base = base_map[base_input]
                raw = num_input.strip()

                # Parse from input base
                decimal_val = int(raw, input_base)

                conversions = [
                    ("Decimal", str(decimal_val), "var(--sol)"),
                    ("Binary", bin(decimal_val), "var(--teal)"),
                    ("Octal", oct(decimal_val), "var(--amber)"),
                    ("Hexadecimal", hex(decimal_val).upper(), "var(--green)"),
                ]

                # 2x2 grid
                grid_cols = st.columns(2)
                for i, (label, val, color) in enumerate(conversions):
                    with grid_cols[i % 2]:
                        is_input = label.startswith(base_input.split(" ")[0])
                        border = "var(--sol)" if is_input else "var(--border)"
                        st.markdown(
                            f'<div style="background:var(--card);border:1px solid {border};'
                            'border-radius:var(--r2);padding:.8rem 1rem;margin-bottom:.4rem;">'
                            f'<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                            'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.3rem;">'
                            f'{label}'
                            f'{" (input)" if is_input else ""}</div>'
                            f'<div style="font-size:1.05rem;font-weight:700;color:{color};'
                            'font-family:DM Mono,monospace;word-break:break-all;">'
                            f'{html.escape(val)}</div></div>',
                            unsafe_allow_html=True,
                        )

            except ValueError:
                st.error(f"Invalid number for {base_input}. Check your input.")

    # ═══════════════════════════════════════════════════════════════════════════
    # TIMEZONES TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_tz:
        try:
            import pytz

            tz_col1, tz_col2 = st.columns(2)
            with tz_col1:
                from_tz = st.selectbox("From timezone", options=TIMEZONES, key="tz_from")
            with tz_col2:
                to_tz = st.selectbox("To timezone", options=TIMEZONES, key="tz_to")

            now = datetime.now(pytz.timezone(from_tz))
            target = now.astimezone(pytz.timezone(to_tz))

            st.markdown('<div style="margin-top:.6rem;"></div>', unsafe_allow_html=True)

            # Display both times
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    'border-radius:var(--r);padding:1rem 1.2rem;text-align:center;">'
                    f'<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                    'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                    f'{html.escape(from_tz)}</div>'
                    f'<div style="font-size:1.4rem;font-weight:700;color:var(--sol);'
                    'font-family:DM Mono,monospace;">'
                    f'{now.strftime("%Y-%m-%d<br>%H:%M:%S")}</div></div>',
                    unsafe_allow_html=True,
                )
            with t_col2:
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--sol);'
                    'border-radius:var(--r);padding:1rem 1.2rem;text-align:center;">'
                    f'<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
                    'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                    f'{html.escape(to_tz)}</div>'
                    f'<div style="font-size:1.4rem;font-weight:700;color:var(--teal);'
                    'font-family:DM Mono,monospace;">'
                    f'{target.strftime("%Y-%m-%d<br>%H:%M:%S")}</div></div>',
                    unsafe_allow_html=True,
                )

            # Show offset info
            offset_from = now.strftime("%z")
            offset_to = target.strftime("%z")
            diff_hours = (target.utcoffset() - now.utcoffset()).total_seconds() / 3600
            diff_sign = "+" if diff_hours >= 0 else ""

            st.markdown(
                f'<div style="margin-top:.5rem;font-size:.78rem;color:var(--ink3);text-align:center;">'
                f'{html.escape(from_tz)} ({offset_from}) → {html.escape(to_tz)} ({offset_to})  |  '
                f'Difference: {diff_sign}{diff_hours:.1f} hours</div>',
                unsafe_allow_html=True,
            )

            # Refresh button
            if st.button("🔄 Refresh", key="tz_refresh", use_container_width=True):
                st.rerun()

        except ImportError:
            st.warning("Install pytz for timezone support: pip install pytz")
            st.markdown(
                '<div style="margin-top:.5rem;">'
                '<span style="font-size:.82rem;color:var(--ink3);">'
                'Alternatively, you can use the built-in <code>zoneinfo</code> module (Python 3.9+).'
                '</span></div>',
                unsafe_allow_html=True,
            )

            # Fallback using zoneinfo
            try:
                from zoneinfo import ZoneInfo

                tz_col1, tz_col2 = st.columns(2)
                with tz_col1:
                    from_tz = st.selectbox("From timezone (fallback)", options=TIMEZONES, key="tz_from_f")
                with tz_col2:
                    to_tz = st.selectbox("To timezone (fallback)", options=TIMEZONES, key="tz_to_f")

                now = datetime.now(ZoneInfo(from_tz))
                target = now.astimezone(ZoneInfo(to_tz))

                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--border);'
                        'border-radius:var(--r);padding:1rem 1.2rem;text-align:center;">'
                        f'<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                        f'{html.escape(from_tz)}</div>'
                        f'<div style="font-size:1.4rem;font-weight:700;color:var(--sol);'
                        'font-family:DM Mono,monospace;">'
                        f'{now.strftime("%Y-%m-%d<br>%H:%M:%S")}</div></div>',
                        unsafe_allow_html=True,
                    )
                with t_col2:
                    st.markdown(
                        f'<div style="background:var(--card);border:1px solid var(--sol);'
                        'border-radius:var(--r);padding:1rem 1.2rem;text-align:center;">'
                        f'<div style="font-size:.72rem;font-weight:700;color:var(--sol2);'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem;">'
                        f'{html.escape(to_tz)}</div>'
                        f'<div style="font-size:1.4rem;font-weight:700;color:var(--teal);'
                        'font-family:DM Mono,monospace;">'
                        f'{target.strftime("%Y-%m-%d<br>%H:%M:%S")}</div></div>',
                        unsafe_allow_html=True,
                    )
            except ImportError:
                st.error("No timezone library available. Install pytz or use Python 3.9+.")
