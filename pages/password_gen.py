# password_gen.py — Password generator, passphrase generator, and hash tools
import math
import html
import string
import hashlib
import random
import streamlit as st
from random import SystemRandom

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state, success_card

_rng = SystemRandom()

# ── Word list for passphrases (common, easy-to-remember words) ────────────────
PASSPHRASE_WORDS = [
    "apple", "banana", "cherry", "dragon", "eagle", "forest", "galaxy", "horizon",
    "island", "jungle", "knight", "legend", "mirror", "nebula", "ocean", "phoenix",
    "quartz", "river", "storm", "thunder", "ultra", "violet", "walnut", "xenon",
    "yellow", "zenith", "alpha", "brave", "coral", "delta", "ember", "frost",
    "grape", "honey", "ivory", "jade", "karma", "lunar", "mango", "noble",
    "orbit", "piano", "queen", "raven", "solar", "tiger", "unity", "vivid",
    "whale", "azure", "blaze", "crypt", "dusk", "echo", "flame", "gleam",
    "haven", "ink", "joy", "kite", "light", "maple", "north", "opal",
    "prism", "quest", "ripple", "spark", "trail", "umbra", "vault", "wave",
    "yarn", "zeal", "anchor", "bloom", "canyon", "drift", "fable", "grove",
    "harbor", "indigo", "jewel", "latch", "marsh", "nova", "plume", "quill",
    "ridge", "shade", "timber", "veil", "whisper", "aqua", "bolt", "crest",
    "dawn", "fern", "glow", "haze", "iris", "jet", "keel", "loom",
    "moss", "nest", "pebble", "reign", "stone", "thorn", "vapor", "wren",
]

# Characters to use
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"
AMBIGUOUS = "Il1O0"


def _generate_password(length: int, use_upper: bool, use_lower: bool,
                        use_digits: bool, use_symbols: bool,
                        exclude_ambiguous: bool) -> str:
    """Generate a secure random password using SystemRandom."""
    pool = ""
    if use_lower:
        pool += LOWERCASE
    if use_upper:
        pool += UPPERCASE
    if use_digits:
        pool += DIGITS
    if use_symbols:
        pool += SYMBOLS

    if exclude_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS)

    if not pool:
        pool = LOWERCASE  # fallback

    return "".join(_rng.choice(pool) for _ in range(length))


def _generate_passphrase(word_count: int, separator: str) -> str:
    """Generate a passphrase from random words."""
    words = _rng.sample(PASSPHRASE_WORDS, min(word_count, len(PASSPHRASE_WORDS)))
    return separator.join(words)


def _calculate_entropy(length: int, pool_size: int) -> float:
    """Calculate password entropy in bits."""
    if pool_size <= 1 or length <= 0:
        return 0.0
    return length * math.log2(pool_size)


def _strength_label(entropy: float) -> tuple:
    """Return (label, color) based on entropy."""
    if entropy < 28:
        return "Very Weak", "var(--rose)"
    elif entropy < 36:
        return "Weak", "#f97316"
    elif entropy < 60:
        return "Fair", "var(--amber)"
    elif entropy < 80:
        return "Strong", "var(--green)"
    else:
        return "Very Strong", "var(--teal)"


def _pool_size(use_upper: bool, use_lower: bool, use_digits: bool,
               use_symbols: bool, exclude_ambiguous: bool) -> int:
    """Calculate the character pool size."""
    pool = 0
    if use_lower:
        pool += len(LOWERCASE)
    if use_upper:
        pool += len(UPPERCASE)
    if use_digits:
        pool += len(DIGITS)
    if use_symbols:
        pool += len(SYMBOLS)
    if exclude_ambiguous:
        # Ambiguous chars may overlap with multiple sets
        pool = max(1, pool - len(set(AMBIGUOUS) & set(LOWERCASE + UPPERCASE + DIGITS)))
    return max(1, pool)


def render():
    """Render the Password Generator page."""
    inject_css()
    init_state()

    page_header("Password Generator", "Generate secure passwords, passphrases, and compute hashes")

    col_left, col_right = st.columns([1, 1])

    # ═══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN — Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    with col_left:
        # ── Password Generator ─────────────────────────────────────────────
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '🔑 Password Generator</div></div>',
            unsafe_allow_html=True,
        )

        length = st.slider("Password length", min_value=4, max_value=128,
                            value=16, step=1, key="pw_length")

        st.markdown('<div style="margin-bottom:.4rem;"></div>', unsafe_allow_html=True)

        use_upper = st.checkbox("Uppercase (A-Z)", value=True, key="pw_upper")
        use_lower = st.checkbox("Lowercase (a-z)", value=True, key="pw_lower")
        use_digits = st.checkbox("Digits (0-9)", value=True, key="pw_digits")
        use_symbols = st.checkbox("Symbols (!@#$…)", value=True, key="pw_symbols")
        exclude_amb = st.checkbox("Exclude ambiguous (Il1O0)", value=False, key="pw_ambig")

        num_pw = st.number_input("Number of passwords", min_value=1, max_value=20,
                                  value=3, step=1, key="pw_count")

        if st.button("🔑 Generate Passwords", use_container_width=True, key="pw_gen_btn"):
            passwords = [
                _generate_password(length, use_upper, use_lower, use_digits,
                                    use_symbols, exclude_amb)
                for _ in range(num_pw)
            ]
            st.session_state._passwords = passwords
            st.session_state._pw_entropy = _calculate_entropy(
                length, _pool_size(use_upper, use_lower, use_digits, use_symbols, exclude_amb)
            )
            st.rerun()

        st.markdown('<div style="margin:1.2rem 0;"></div>', unsafe_allow_html=True)

        # ── Passphrase Generator ───────────────────────────────────────────
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '📜 Passphrase Generator</div></div>',
            unsafe_allow_html=True,
        )

        word_count = st.slider("Number of words", min_value=3, max_value=12,
                                value=5, step=1, key="pp_word_count")
        separator = st.text_input("Separator", value="-", placeholder="e.g. - _ . ",
                                   label_visibility="collapsed", key="pp_sep")

        if st.button("📜 Generate Passphrase", use_container_width=True, key="pp_gen_btn"):
            pp = _generate_passphrase(word_count, separator)
            st.session_state._passwords = [pp]
            st.session_state._pw_entropy = _calculate_entropy(
                word_count * (6.0 if separator else 5.5),  # avg word ~5.5 chars + separator
                52  # lowercase letters
            )
            st.rerun()

        st.markdown('<div style="margin:1.2rem 0;"></div>', unsafe_allow_html=True)

        # ── Hash Generator ─────────────────────────────────────────────────
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            '#️⃣ Hash Generator</div></div>',
            unsafe_allow_html=True,
        )

        hash_input = st.text_area(
            "Text to hash",
            placeholder="Enter text to generate hashes…",
            height=80,
            label_visibility="collapsed",
            key="hash_input",
        )

        if hash_input.strip():
            text_bytes = hash_input.strip().encode("utf-8")
            hashes = {
                "MD5": hashlib.md5(text_bytes).hexdigest(),
                "SHA-1": hashlib.sha1(text_bytes).hexdigest(),
                "SHA-256": hashlib.sha256(text_bytes).hexdigest(),
                "SHA-512": hashlib.sha512(text_bytes).hexdigest(),
            }

            for algo, h in hashes.items():
                badge_color = "var(--rose)" if algo in ("MD5", "SHA-1") else "var(--green)"
                st.markdown(
                    f'<div style="background:var(--surface);border:1px solid var(--border);'
                    'border-radius:var(--r2);padding:.6rem .8rem;margin-bottom:.35rem;">'
                    f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.25rem;">'
                    f'{badge(algo, badge_color)}'
                    f'{badge(f"{len(h)} chars", "var(--ink3)")}'
                    '</div>'
                    f'<div style="font-size:.76rem;color:var(--teal);font-family:DM Mono,monospace;'
                    'word-break:break-all;line-height:1.5;">{html.escape(h)}</div></div>',
                    unsafe_allow_html=True,
                )

    # ═══════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN — Results
    # ═══════════════════════════════════════════════════════════════════════════
    with col_right:
        passwords = st.session_state._passwords
        entropy = getattr(st.session_state, "_pw_entropy", 0)

        if not passwords:
            empty_state("🔒", "Configure options and generate passwords")
        else:
            # Strength indicator
            label, color = _strength_label(entropy)
            entropy_int = int(entropy)

            st.markdown(
                f'<div style="background:var(--card);border:1px solid var(--border);'
                'border-radius:var(--r);padding:1rem 1.2rem;margin-bottom:.8rem;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;'
                'margin-bottom:.5rem;">'
                '<span style="font-size:.72rem;font-weight:700;color:var(--ink3);'
                'text-transform:uppercase;letter-spacing:.04em;">Strength</span>'
                f'{badge(label, color)}'
                '</div>'
                f'<div style="font-size:.82rem;font-weight:600;color:var(--ink2);margin-bottom:.4rem;">'
                f'Entropy: ~{entropy_int} bits</div>'
                f'<div style="background:var(--surface);border-radius:99px;height:6px;'
                'overflow:hidden;border:1px solid var(--border);">'
                f'<div style="background:{color};border-radius:99px;height:100%;'
                f'width:{min(100, entropy_int / 1.28):.1f}%;transition:width .4s ease;"></div>'
                '</div></div>',
                unsafe_allow_html=True,
            )

            # Password list
            for i, pw in enumerate(passwords):
                masked = pw[:4] + "•" * max(0, len(pw) - 8) + pw[-4:] if len(pw) > 8 else "•" * len(pw)
                st.markdown(
                    f'<div style="background:var(--card);border:1px solid var(--border);'
                    'border-radius:var(--r2);padding:.7rem .9rem;margin-bottom:.4rem;">'
                    '<div style="display:flex;align-items:center;justify-content:space-between;">'
                    f'<div style="font-size:.88rem;color:var(--ink);font-family:DM Mono,monospace;'
                    'word-break:break-all;flex:1;">{html.escape(masked)}</div>'
                    f'{badge(f"{len(pw)} chars", "var(--ink3)")}'
                    '</div></div>',
                    unsafe_allow_html=True,
                )

                # Copy buttons (show actual password in code block)
                with st.expander(f"Show / Copy Password {i+1}"):
                    st.code(pw, language=None)
                    st.markdown(
                        f'<div style="font-size:.78rem;color:var(--ink3);margin-top:.3rem;">'
                        f'Entropy: {_calculate_entropy(len(pw), len(set(pw))):.1f} bits '
                        f'(unique chars: {len(set(pw))})</div>',
                        unsafe_allow_html=True,
                    )
