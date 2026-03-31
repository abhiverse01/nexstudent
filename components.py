# components.py — Shared UI helpers used across all pages
import streamlit as st


def page_header(title: str, subtitle: str = ""):
    """Render a styled page header with optional subtitle."""
    sub = (
        f'<p style="color:var(--ink3);font-size:.85rem;margin:.1rem 0 1.4rem;'
        f'font-weight:400;">{subtitle}</p>'
        if subtitle
        else '<div style="margin-bottom:1.2rem;"></div>'
    )
    st.markdown(
        f'<div style="margin-bottom:.1rem;">'
        f'<h1 style="font-size:1.55rem;font-weight:700;color:#e8e8f8;'
        f'letter-spacing:-.03em;margin:0 0 .1rem;">{title}</h1>'
        f'{sub}</div>',
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = "#5b5ef4") -> str:
    """Return an inline badge <span> as raw HTML."""
    bg = color + "22"
    border = color + "44"
    return (
        f'<span style="display:inline-block;padding:2px 9px;border-radius:99px;'
        f'font-size:.7rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;'
        f'background:{bg};color:{color};border:1px solid {border};">{text}</span>'
    )


def progress_bar(pct: int, color: str = "var(--sol)") -> str:
    """Return a CSS progress-bar <div> as raw HTML."""
    pct = max(0, min(100, pct))
    return (
        f'<div style="background:var(--surface);border-radius:99px;height:5px;'
        f'overflow:hidden;border:1px solid var(--border);">'
        f'<div style="background:{color};border-radius:99px;height:100%;'
        f'width:{pct}%;transition:width .4s ease;"></div></div>'
    )


def empty_state(icon: str, message: str, icon_size: str = "2.8rem"):
    """Render a centered placeholder when no data exists."""
    st.markdown(
        f'<div style="text-align:center;padding:3.5rem 2rem;color:#1c1c3a;">'
        f'<div style="font-size:{icon_size};margin-bottom:.6rem;">{icon}</div>'
        f'<div style="color:#4a4a72;">{message}</div></div>',
        unsafe_allow_html=True,
    )


def success_card(title: str, body: str, accent: str = "#22c55e"):
    """Render a compact success/info card."""
    bg = accent + "11"
    border = accent + "33"
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
        f'padding:.8rem 1rem;margin-bottom:.6rem;">'
        f'<div style="color:{accent};font-weight:700;font-size:.82rem;margin-bottom:.2rem;">{title}</div>'
        f'<div style="font-size:.78rem;color:var(--ink2);line-height:1.5;">{body}</div></div>',
        unsafe_allow_html=True,
    )
