# text_tools.py — Text analysis, transformation, generation, and diff
import difflib
import html
import io
import re
import random
import string
import uuid
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


# ── Random name/address data ──────────────────────────────────────────────────

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Paul", "Dorothy", "Andrew", "Kimberly", "Joshua", "Emily", "Kenneth", "Donna",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "example.com", "mail.com"]

STREET_NAMES = [
    "Maple", "Oak", "Cedar", "Pine", "Elm", "Birch", "Walnut", "Cherry",
    "Willow", "Spruce", "Ash", "Hickory", "Magnolia", "Sycamore", "Poplar",
]

STREET_TYPES = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Ct", "Way"]

CITIES = [
    "Springfield", "Franklin", "Clinton", "Georgetown", "Salem", "Fairview",
    "Madison", "Portland", "Arlington", "Chester", "Harrison", "Kingston",
]

STATES = [
    "AL", "AK", "AZ", "CA", "CO", "CT", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
]


def _word_freq(text: str, top_n: int = 15) -> list:
    """Return top N words by frequency as (word, count) list."""
    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    freq = {}
    for w in words:
        if len(w) > 1:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq.items(), key=lambda x: -x[1])[:top_n]


def _to_camel(text: str) -> str:
    """Convert space-separated text to camelCase."""
    parts = re.split(r"[\s_\-]+", text.strip())
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.title() for p in parts[1:] if p)


def _to_snake(text: str) -> str:
    """Convert text to snake_case."""
    s = re.sub(r"([A-Z])", r"_\1", text)
    s = re.sub(r"[\s\-]+", "_", s)
    return re.sub(r"_+", "_", s.strip("_")).lower()


def _to_kebab(text: str) -> str:
    """Convert text to kebab-case."""
    s = re.sub(r"([A-Z])", r"-\1", text)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s.strip("-")).lower()


def _to_sentence_case(text: str) -> str:
    """Convert text to sentence case."""
    sentences = re.split(r"([.!?]+\s*)", text)
    result = []
    for i, part in enumerate(sentences):
        if i % 2 == 0 and part.strip():
            result.append(part[0].upper() + part[1:].lower() if part else part)
        else:
            result.append(part)
    return "".join(result)


def _generate_lorem(count: int) -> str:
    """Generate lorem ipsum paragraphs."""
    base = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
        "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
        "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
        "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
        "mollit anim id est laborum."
    )
    paras = []
    for _ in range(count):
        sentences = base.split(". ")
        random.shuffle(sentences)
        paras.append(". ".join(sentences) + ".")
    return "\n\n".join(paras)


def _generate_names(count: int) -> str:
    """Generate random full names."""
    names = []
    for _ in range(count):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        names.append(name)
    return "\n".join(names)


def _generate_emails(count: int) -> str:
    """Generate random email addresses."""
    emails = []
    for _ in range(count):
        first = random.choice(FIRST_NAMES).lower()
        sep = random.choice(["", ".", "_"])
        last = random.choice(LAST_NAMES).lower()
        num = random.choice(["", str(random.randint(1, 999))])
        emails.append(f"{first}{sep}{last}{num}@{random.choice(DOMAINS)}")
    return "\n".join(emails)


def _generate_uuids(count: int) -> str:
    """Generate random UUIDs."""
    return "\n".join(str(uuid.uuid4()) for _ in range(count))


def _generate_numbers(count: int, min_val: int, max_val: int) -> str:
    """Generate random numbers."""
    return "\n".join(str(random.randint(min_val, max_val)) for _ in range(count))


def _generate_addresses(count: int) -> str:
    """Generate random US-style addresses."""
    addrs = []
    for _ in range(count):
        num = random.randint(100, 9999)
        street = f"{num} {random.choice(STREET_NAMES)} {random.choice(STREET_TYPES)}"
        city = random.choice(CITIES)
        state = random.choice(STATES)
        zipcode = f"{random.randint(10000, 99999)}"
        addrs.append(f"{street}\n{city}, {state} {zipcode}")
    return "\n\n".join(addrs)


def render():
    """Render the Text Tools page."""
    inject_css()
    init_state()

    page_header("Text Tools", "Analyse, transform, generate, and diff text")

    tab_analyse, tab_transform, tab_generate, tab_diff = st.tabs(
        ["🔍 Analyse", "✨ Transform", "🎲 Generate", "🔀 Diff"]
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSE TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_analyse:
        text = st.text_area(
            "Enter text to analyse",
            placeholder="Paste or type your text here…",
            height=180,
            label_visibility="collapsed",
            key="tt_analyse_input",
        )

        if not text.strip():
            empty_state("📝", "Paste some text to analyse")
            return

        words = re.findall(r"\b\w+\b", text)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        read_time = max(1, len(words) // 200)
        unique_words = set(w.lower() for w in words if len(w) > 1)
        chars_nospace = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

        # Metrics grid
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(_metric_card("Words", str(len(words)), "var(--sol)"), unsafe_allow_html=True)
            st.markdown(_metric_card("Characters", str(len(text)), "var(--teal)"), unsafe_allow_html=True)
        with m_col2:
            st.markdown(_metric_card("Chars (no space)", str(chars_nospace), "var(--amber)"), unsafe_allow_html=True)
            st.markdown(_metric_card("Sentences", str(len(sentences)), "var(--rose)"), unsafe_allow_html=True)
        with m_col3:
            st.markdown(_metric_card("Paragraphs", str(len(paragraphs)), "var(--green)"), unsafe_allow_html=True)
            st.markdown(_metric_card("Read time", f"~{read_time} min", "var(--sol2)"), unsafe_allow_html=True)

        st.markdown(
            f'<div style="margin:.6rem 0;">{badge(f"{len(unique_words)} unique words", "var(--ink3)")}</div>',
            unsafe_allow_html=True,
        )

        # Top words bar chart
        top_words = _word_freq(text, 15)
        if top_words:
            st.markdown(
                '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
                'margin:.6rem 0 .4rem;letter-spacing:.04em;text-transform:uppercase;">'
                'Top Words</div>',
                unsafe_allow_html=True,
            )
            max_count = top_words[0][1] if top_words else 1
            for word, count in top_words:
                pct = int((count / max_count) * 100) if max_count > 0 else 0
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.25rem;">'
                    f'<span style="font-size:.78rem;color:var(--ink2);min-width:80px;font-family:DM Mono,monospace;'
                    f'text-align:right;">{html.escape(word)}</span>'
                    f'<div style="flex:1;background:var(--surface);border-radius:99px;height:14px;'
                    f'overflow:hidden;border:1px solid var(--border);position:relative;">'
                    f'<div style="background:var(--sol);border-radius:99px;height:100%;'
                    f'width:{pct}%;transition:width .4s ease;"></div>'
                    f'<span style="position:absolute;right:6px;top:50%;transform:translateY(-50%);'
                    f'font-size:.65rem;color:var(--ink);font-family:DM Mono,monospace;font-weight:600;">'
                    f'{count}</span></div></div>',
                    unsafe_allow_html=True,
                )

    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSFORM TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_transform:
        tx_input = st.text_area(
            "Enter text to transform",
            placeholder="Paste or type your text here…",
            height=150,
            label_visibility="collapsed",
            key="tt_transform_input",
        )

        transforms = [
            ("UPPERCASE", lambda t: t.upper()),
            ("lowercase", lambda t: t.lower()),
            ("Title Case", lambda t: t.title()),
            ("Sentence case", _to_sentence_case),
            ("camelCase", _to_camel),
            ("snake_case", _to_snake),
            ("kebab-case", _to_kebab),
            ("Reverse", lambda t: t[::-1]),
            ("Remove extra spaces", lambda t: re.sub(r" +", " ", t)),
            ("Remove line breaks", lambda t: re.sub(r"\n+", " ", t)),
            ("Sort lines", lambda t: "\n".join(sorted(t.split("\n")))),
            ("Remove duplicates", lambda t: "\n".join(dict.fromkeys(t.split("\n")))),
        ]

        btn_cols = st.columns(4)
        for idx, (name, fn) in enumerate(transforms):
            with btn_cols[idx % 4]:
                if st.button(name, key=f"tx_btn_{idx}", use_container_width=True):
                    st.session_state._transformed = fn(tx_input)
                    st.session_state._tx_name = name
                    st.rerun()

        transformed = st.session_state._transformed
        tx_name = st.session_state._tx_name

        if transformed is not None:
            st.markdown(
                f'<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                'text-transform:uppercase;letter-spacing:.04em;margin:.6rem 0 .3rem;">'
                f'Result — {html.escape(tx_name)}</div>',
                unsafe_allow_html=True,
            )
            st.text_area(
                "Transformed text",
                value=transformed,
                height=180,
                label_visibility="collapsed",
                key="tt_transform_output",
            )
            st.download_button(
                label="⬇️ Download",
                data=transformed,
                file_name=f"transformed_{tx_name.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # GENERATE TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_generate:
        gen_type = st.selectbox(
            "Type",
            options=["Lorem Ipsum", "Random Names", "Random Emails", "Random UUIDs",
                     "Random Numbers", "Fake Addresses"],
            label_visibility="collapsed",
            key="tt_gen_type",
        )
        count = st.slider("Count", min_value=1, max_value=100, value=5, key="tt_gen_count")

        # Show Min/Max BEFORE generate button for Random Numbers
        min_val = 1
        max_val = 1000
        if gen_type == "Random Numbers":
            num_cols = st.columns(2)
            with num_cols[0]:
                min_val = st.number_input("Min", value=1, key="tt_gen_min")
            with num_cols[1]:
                max_val = st.number_input("Max", value=1000, key="tt_gen_max")

        if st.button("🎲 Generate", use_container_width=True, key="tt_gen_btn"):
            gen_map = {
                "Lorem Ipsum": lambda: _generate_lorem(count),
                "Random Names": lambda: _generate_names(count),
                "Random Emails": lambda: _generate_emails(count),
                "Random UUIDs": lambda: _generate_uuids(count),
                "Random Numbers": lambda: _generate_numbers(count, min_val, max_val),
                "Fake Addresses": lambda: _generate_addresses(count),
            }
            result = gen_map[gen_type]()
            st.session_state._gen_output = result
            st.rerun()

        gen_output = getattr(st.session_state, "_gen_output", None)
        if gen_output:
            st.text_area(
                "Generated text",
                value=gen_output,
                height=200,
                label_visibility="collapsed",
                key="tt_gen_output_area",
            )
            st.download_button(
                label="⬇️ Download",
                data=gen_output,
                file_name=f"generated_{gen_type.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # DIFF TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_diff:
        diff_col1, diff_col2 = st.columns(2)
        with diff_col1:
            original = st.text_area(
                "Original",
                placeholder="Paste original text…",
                height=180,
                label_visibility="collapsed",
                key="tt_diff_orig",
            )
        with diff_col2:
            modified = st.text_area(
                "Modified",
                placeholder="Paste modified text…",
                height=180,
                label_visibility="collapsed",
                key="tt_diff_mod",
            )

        if st.button("🔀 Compare", use_container_width=True, key="tt_diff_btn"):
            diff = list(difflib.unified_diff(
                original.splitlines(keepends=True),
                modified.splitlines(keepends=True),
                fromfile="original",
                tofile="modified",
            ))
            diff_text = "".join(diff)
            diff_lines = diff_text.count("\n")

            if not diff_text.strip():
                st.markdown(
                    '<div style="text-align:center;padding:1.5rem;color:var(--green);'
                    'font-weight:600;">✅ No differences found — texts are identical</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="margin-bottom:.4rem;">'
                    f'{badge(f"{diff_lines} changed lines", "var(--amber)")}'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.code(diff_text, language="diff")


def _metric_card(label: str, value: str, color: str) -> str:
    """Return a styled metric card as HTML."""
    return (
        f'<div style="background:var(--card);border:1px solid var(--border);'
        f'border-radius:var(--r2);padding:.6rem .8rem;margin-bottom:.35rem;">'
        f'<div style="font-size:.68rem;font-weight:700;color:var(--ink3);'
        f'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.15rem;">'
        f'{html.escape(label)}</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:{color};'
        f'font-family:DM Mono,monospace;">{html.escape(value)}</div></div>'
    )
