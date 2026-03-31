# flashcards.py — Flashcard app with Create, Study, and Quiz modes
import html
import random
import streamlit as st

from config import inject_css
from state import init_state
from components import page_header, badge, progress_bar, empty_state, success_card


def render():
    """Render the Flashcards page."""
    inject_css()
    init_state()

    page_header("Flashcards", "Create, study, and quiz yourself with flashcards")

    cards = st.session_state.flashcards

    tab_create, tab_study, tab_quiz = st.tabs(["✏️ Create", "📖 Study", "🎯 Quiz"])

    # ═══════════════════════════════════════════════════════════════════════════
    # CREATE TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_create:
        st.markdown(
            '<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.1rem 1.2rem;">'
            '<div style="font-size:.82rem;font-weight:700;color:var(--ink2);'
            'margin-bottom:.8rem;letter-spacing:.04em;text-transform:uppercase;">'
            'New Flashcard</div></div>',
            unsafe_allow_html=True,
        )

        with st.form("flashcard_form", clear_on_submit=True):
            question = st.text_area(
                "Question",
                placeholder="Enter the question or prompt…",
                height=100,
                label_visibility="visible",
                key="fc_question",
            )
            answer = st.text_area(
                "Answer",
                placeholder="Enter the answer…",
                height=100,
                label_visibility="visible",
                key="fc_answer",
            )
            tag = st.text_input(
                "Tag",
                placeholder="e.g. Biology, Math, History (optional)",
                label_visibility="visible",
                key="fc_tag",
            )
            submitted = st.form_submit_button("➕ Add Flashcard", use_container_width=True)

        if submitted and question.strip() and answer.strip():
            cards.append({
                "question": question.strip(),
                "answer": answer.strip(),
                "tag": tag.strip() or "General",
            })
            st.session_state.flashcards = cards
            st.session_state.active_card = max(0, len(cards) - 1)
            st.session_state.show_answer = False
            st.rerun()
        elif submitted:
            st.warning("Please fill in both question and answer.")

        # Card list
        st.markdown('<div style="margin-top:.6rem;"></div>', unsafe_allow_html=True)

        if not cards:
            empty_state("🃏", "No flashcards yet. Create one above!")
        else:
            all_tags = sorted(set(c.get("tag", "General") for c in cards))
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem;">'
                f'{badge(f"{len(cards)} cards", "var(--sol)")}'
                f'{badge(f"{len(all_tags)} tags", "var(--teal)")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            for i, card in enumerate(cards):
                tag_color = "var(--amber)" if card.get("tag", "General") != "General" else "var(--ink3)"
                with st.expander(
                    f"Q{i+1}: {html.escape(card['question'][:60])}{'…' if len(card['question']) > 60 else ''}",
                    expanded=False,
                ):
                    st.markdown(
                        f'<div style="background:var(--surface);border:1px solid var(--border);'
                        'border-radius:var(--r2);padding:.8rem 1rem;margin-bottom:.6rem;">'
                        f'<div style="font-size:.72rem;color:var(--ink3);font-weight:700;'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.3rem;">Question</div>'
                        f'<div style="font-size:.88rem;color:var(--ink);line-height:1.6;">'
                        f'{html.escape(card["question"])}</div></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="background:var(--surface);border:1px solid var(--border);'
                        'border-radius:var(--r2);padding:.8rem 1rem;margin-bottom:.8rem;">'
                        f'<div style="font-size:.72rem;color:var(--ink3);font-weight:700;'
                        'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.3rem;">Answer</div>'
                        f'<div style="font-size:.88rem;color:var(--sol2);line-height:1.6;">'
                        f'{html.escape(card["answer"])}</div></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="margin-bottom:.5rem;">'
                        f'{badge(card.get("tag", "General"), tag_color)}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️ Delete", key=f"fc_del_{i}", use_container_width=True):
                        cards.pop(i)
                        st.session_state.flashcards = cards
                        if st.session_state.active_card >= len(cards):
                            st.session_state.active_card = max(0, len(cards) - 1)
                        st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # STUDY TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_study:
        if not cards:
            empty_state("🃏", "Create some flashcards first!")
            return

        all_tags = sorted(set(c.get("tag", "General") for c in cards))
        selected_tag = st.selectbox(
            "Filter by tag",
            options=["All"] + all_tags,
            index=0,
            label_visibility="collapsed",
            key="fc_study_tag",
        )

        filtered = [c for c in cards if selected_tag == "All" or c.get("tag", "General") == selected_tag]

        if not filtered:
            empty_state("🔍", "No cards match the selected tag.")
            return

        # Clamp active_card index
        if st.session_state.active_card >= len(filtered):
            st.session_state.active_card = 0

        idx = st.session_state.active_card
        card = filtered[idx]
        total = len(filtered)
        show = st.session_state.show_answer

        # Progress bar
        pct = int(((idx + 1) / total) * 100) if total else 0
        st.markdown(
            f'<div style="margin-bottom:.8rem;">'
            f'{badge(f"Card {idx + 1} of {total}", "var(--sol)")}'
            f'  '
            f'{badge(card.get("tag", "General"), "var(--amber)")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(progress_bar(pct, "var(--sol)"), unsafe_allow_html=True)

        # Card display
        card_face = card["answer"] if show else card["question"]
        label = "ANSWER" if show else "QUESTION"
        label_color = "var(--sol2)" if show else "var(--teal)"

        st.markdown(
            f'<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:2rem 1.5rem;margin:1.2rem 0;'
            'min-height:200px;display:flex;flex-direction:column;align-items:center;'
            'justify-content:center;text-align:center;box-shadow:var(--glow);">'
            f'<div style="font-size:.72rem;font-weight:700;letter-spacing:.08em;'
            f'text-transform:uppercase;color:{label_color};margin-bottom:.8rem;">'
            f'{label}</div>'
            f'<div style="font-size:1.1rem;font-weight:500;color:var(--ink);line-height:1.7;'
            f'max-width:500px;">{html.escape(card_face)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Navigation buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col1:
            if st.button("⬅️ Prev", use_container_width=True, key="fc_prev"):
                st.session_state.active_card = (idx - 1) % total
                st.session_state.show_answer = False
                st.rerun()
        with btn_col2:
            flip_label = "👁️ Show Answer" if not show else "🔄 Show Question"
            if st.button(flip_label, use_container_width=True, key="fc_flip"):
                st.session_state.show_answer = not show
                st.rerun()
        with btn_col3:
            if st.button("Next ➡️", use_container_width=True, key="fc_next"):
                st.session_state.active_card = (idx + 1) % total
                st.session_state.show_answer = False
                st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # QUIZ TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_quiz:
        if not cards:
            empty_state("🃏", "Create some flashcards first!")
            return

        score = st.session_state.quiz_score
        total_q = st.session_state.quiz_total
        accuracy = (score / total_q * 100) if total_q > 0 else 0

        # Metrics row
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Score", f"{score}")
        with m_col2:
            st.metric("Total", f"{total_q}")
        with m_col3:
            acc_color = "var(--green)" if accuracy >= 70 else ("var(--amber)" if accuracy >= 40 else "var(--rose)")
            st.metric("Accuracy", f"{accuracy:.1f}%")

        # Reset button
        reset_col1, reset_col2 = st.columns([3, 1])
        with reset_col2:
            if st.button("🔄 Reset Stats", use_container_width=True, key="fc_quiz_reset"):
                st.session_state.quiz_score = 0
                st.session_state.quiz_total = 0
                st.rerun()

        st.markdown('<div style="margin-top:.5rem;"></div>', unsafe_allow_html=True)

        # Pick a random card for the quiz
        quiz_card = random.choice(cards)

        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:var(--ink3);'
            'text-transform:uppercase;letter-spacing:.04em;margin-bottom:.5rem;">'
            'Question</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:var(--card);border:1px solid var(--border);'
            'border-radius:var(--r);padding:1.2rem 1.4rem;margin-bottom:.8rem;">'
            f'<div style="font-size:.95rem;font-weight:500;color:var(--ink);line-height:1.65;">'
            f'{html.escape(quiz_card["question"])}</div></div>',
            unsafe_allow_html=True,
        )

        with st.expander("👁️ Reveal Answer", expanded=False):
            st.markdown(
                f'<div style="font-size:.9rem;color:var(--sol2);line-height:1.6;padding:.3rem 0;">'
                f'{html.escape(quiz_card["answer"])}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="margin-top:.5rem;"></div>', unsafe_allow_html=True)

        # Correct / Wrong buttons
        btn_c, btn_w = st.columns(2)
        with btn_c:
            if st.button("✅ Correct", use_container_width=True, key="fc_correct"):
                st.session_state.quiz_score += 1
                st.session_state.quiz_total += 1
                st.rerun()
        with btn_w:
            if st.button("❌ Wrong", use_container_width=True, key="fc_wrong"):
                st.session_state.quiz_total += 1
                st.rerun()
