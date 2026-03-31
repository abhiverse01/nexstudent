# notes.py — Smart Notes with Markdown editor/preview
import html
import hashlib
import streamlit as st
from io import StringIO

from config import inject_css
from state import init_state
from components import page_header, badge, empty_state


def _hash_key(title: str) -> str:
    """Return a short hash of the title for use as a Streamlit widget key."""
    return hashlib.md5(title.encode()).hexdigest()[:10]


def render():
    """Render the Smart Notes page."""
    inject_css()
    init_state()

    page_header("Smart Notes", "Create, edit, and preview Markdown notes")

    notes = st.session_state.notes
    active_note = st.session_state._active_note

    col_list, col_editor = st.columns([1, 2])

    # ── Note list panel ───────────────────────────────────────────────────────
    with col_list:
        st.markdown(
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.6rem;letter-spacing:.04em;text-transform:uppercase;">'
            'Your Notes</div>',
            unsafe_allow_html=True,
        )

        # Create new note
        new_title = st.text_input(
            "New note title",
            placeholder="Note title…",
            label_visibility="collapsed",
            key="notes_new_title",
        )
        if st.button("➕ Create Note", use_container_width=True, key="notes_create_btn"):
            if new_title.strip():
                notes[new_title.strip()] = ""
                st.session_state.notes = notes
                st.session_state._active_note = new_title.strip()
                st.rerun()

        st.markdown('<div style="margin-bottom:.5rem;"></div>', unsafe_allow_html=True)

        # Note list
        if not notes:
            empty_state("📝", "No notes yet. Create one above!")
        else:
            for title in list(notes.keys()):
                is_active = title == active_note
                bg = "rgba(91,94,244,.15)" if is_active else "var(--card)"
                border = "var(--sol)" if is_active else "var(--border)"
                word_count = len(notes[title].split())
                char_count = len(notes[title])

                st.markdown(
                    f'<div style="background:{bg};border:1px solid {border};border-radius:var(--r2);'
                    f'padding:.6rem .8rem;margin-bottom:.35rem;cursor:pointer;">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                    f'<span style="font-weight:600;font-size:.84rem;color:var(--ink);'
                    f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:55%;">'
                    f'{html.escape(title)}</span>'
                    f'<span style="color:var(--ink3);font-size:.68rem;">{word_count}w · {char_count}c</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                btn_row_col1, btn_row_col2, btn_row_col3 = st.columns([1, 1, 1])
                with btn_row_col1:
                    if st.button("✏️", key=f"note_edit_{_hash_key(title)}", help="Edit"):
                        st.session_state._active_note = title
                        st.rerun()
                with btn_row_col2:
                    if st.button("📋", key=f"note_copy_{_hash_key(title)}", help="Duplicate"):
                        new_name = f"{title} (copy)"
                        idx = 2
                        while new_name in notes:
                            new_name = f"{title} (copy {idx})"
                            idx += 1
                        notes[new_name] = notes[title]
                        st.session_state.notes = notes
                        st.rerun()
                with btn_row_col3:
                    if st.button("🗑️", key=f"note_del_{_hash_key(title)}", help="Delete"):
                        del notes[title]
                        st.session_state.notes = notes
                        if active_note == title:
                            st.session_state._active_note = None
                        st.rerun()

    # ── Editor panel ──────────────────────────────────────────────────────────
    with col_editor:
        if not active_note or active_note not in notes:
            empty_state("📝", "Select a note from the list to start editing", icon_size="2.4rem")
            return

        title = active_note
        content = notes[title]

        # Title display and actions
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'margin-bottom:.8rem;">'
            f'<div style="display:flex;align-items:center;gap:.5rem;">'
            f'<span style="font-size:1.15rem;font-weight:700;color:var(--ink);">'
            f'{html.escape(title)}</span>'
            f'{badge("editing", "var(--sol)")}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Word / char count badges
        words = content.split()
        word_count = len(words)
        char_count = len(content)
        line_count = content.count("\n") + 1 if content else 0

        st.markdown(
            f'<div style="display:flex;gap:.5rem;margin-bottom:.8rem;">'
            f'{badge(f"{word_count} words", "var(--sol2)")}'
            f'{badge(f"{char_count} chars", "var(--teal)")}'
            f'{badge(f"{line_count} lines", "var(--amber)")}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Tab interface: Edit / Preview
        tab_edit, tab_preview = st.tabs(["✏️ Edit", "👁️ Preview"])

        with tab_edit:
            textarea_key = f"note_content_{_hash_key(title)}"
            new_content = st.text_area(
                "Content",
                value=content,
                height=420,
                label_visibility="collapsed",
                key=textarea_key,
                placeholder="Start writing in Markdown…",
            )
            if new_content != content:
                notes[title] = new_content
                st.session_state.notes = notes

        with tab_preview:
            if not content.strip():
                empty_state("👁️", "Nothing to preview yet")
            else:
                # Render Markdown content
                st.markdown(
                    f'<div style="background:var(--surface);border:1px solid var(--border);'
                    f'border-radius:var(--r);padding:1.2rem 1.4rem;min-height:420px;'
                    f'max-height:520px;overflow-y:auto;">'
                    f'<div style="color:var(--ink);font-size:.88rem;line-height:1.75;">'
                    f'{st.markdown(content)}</div></div>',
                    unsafe_allow_html=True,
                )

        # Download button
        st.markdown('<div style="margin-top:.6rem;"></div>', unsafe_allow_html=True)
        md_data = StringIO(content)
        md_data.seek(0)
        st.download_button(
            label="⬇️ Download as .md",
            data=content.encode("utf-8"),
            file_name=f"{title}.md",
            mime="text/markdown",
            use_container_width=True,
        )
