# ai_assistant.py — AI Chat Assistant (Anthropic Claude)
import html
import streamlit as st
import requests

from config import inject_css
from state import init_state
from components import page_header, empty_state


PERSONAS = {
    "General Assistant": {
        "icon": "🤖",
        "prompt": (
            "You are a helpful, friendly AI assistant. Provide clear, concise, and accurate "
            "answers. Use Markdown formatting when helpful. Be supportive and encouraging."
        ),
    },
    "Study Tutor": {
        "icon": "📚",
        "prompt": (
            "You are an expert study tutor. Explain concepts clearly, break down complex topics "
            "into digestible parts, use analogies, and ask follow-up questions to check "
            "understanding. Use Markdown formatting. Adapt to the student's level."
        ),
    },
    "Code Helper": {
        "icon": "💻",
        "prompt": (
            "You are an expert programming assistant. Help with code in any language. Explain "
            "logic, debug issues, suggest best practices, and provide clean, commented code "
            "examples. Always wrap code in proper Markdown code blocks."
        ),
    },
    "Essay Writer": {
        "icon": "✍️",
        "prompt": (
            "You are a skilled writing assistant. Help brainstorm ideas, structure essays, "
            "improve clarity and flow, check grammar, and suggest vocabulary. Encourage "
            "critical thinking and original expression. Don't write the essay for them — guide them."
        ),
    },
    "Math Wizard": {
        "icon": "🧮",
        "prompt": (
            "You are a math expert. Solve problems step by step, explain formulas and concepts, "
            "show your work clearly, and use LaTeX formatting for equations when appropriate. "
            "Be patient and thorough."
        ),
    },
    "Debate Partner": {
        "icon": "🎯",
        "prompt": (
            "You are a sharp debate partner. Present balanced arguments, challenge assumptions, "
            "offer counter-arguments, and help the user strengthen their reasoning. Play devil's "
            "advocate when appropriate. Be respectful and intellectually honest."
        ),
    },
}


def _call_claude(system_prompt: str, messages: list) -> str:
    """Send a request to the Anthropic Messages API and return the assistant reply."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "⚠️ **API key not configured.** Add `ANTHROPIC_API_KEY` to your Streamlit secrets to use the AI assistant."

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    # Keep last 20 messages for context window
    trimmed = messages[-20:]

    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "system": system_prompt,
        "messages": trimmed,
    }

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    except requests.exceptions.Timeout:
        return "⏱️ **Request timed out.** The server took too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 **Connection error.** Unable to reach the API. Check your internet connection."
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            return "🔑 **Authentication error.** Your API key is invalid or expired."
        elif status == 429:
            return "⏳ **Rate limited.** Too many requests. Please wait a moment and try again."
        elif status == 500:
            return "🔧 **Server error.** The Anthropic API is experiencing issues. Try again later."
        else:
            return f"❌ **API error ({status}).** {e.response.text[:200]}"
    except Exception as e:
        return f"❌ **Unexpected error.** {html.escape(str(e))}"


def render():
    """Render the AI Assistant chat page."""
    inject_css()
    init_state()

    page_header("AI Assistant", "Chat with Claude — your personal study companion")

    # ── Persona selector & clear button ───────────────────────────────────────
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        persona_names = list(PERSONAS.keys())
        default_idx = persona_names.index("General Assistant") if "General Assistant" in persona_names else 0
        selected_persona = st.selectbox(
            "Persona",
            options=persona_names,
            index=default_idx,
            label_visibility="collapsed",
        )
    with top_col2:
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    persona = PERSONAS[selected_persona]

    # ── Chat display ──────────────────────────────────────────────────────────
    chat_history = st.session_state.chat_history

    if not chat_history:
        empty_state(
            f"{persona['icon']}",
            "Start a conversation — type your message below!",
            icon_size="3.2rem",
        )
    else:
        chat_container = st.container()
        with chat_container:
            for msg in chat_history:
                role = msg.get("role", "user")
                content = html.escape(msg.get("content", ""))
                if role == "user":
                    st.markdown(
                        f'<div style="display:flex;justify-content:flex-end;margin-bottom:.7rem;">'
                        f'<div style="background:var(--sol);color:#fff;border-radius:var(--r2) var(--r2) 4px var(--r2);'
                        f'padding:.65rem 1rem;max-width:75%;font-size:.86rem;line-height:1.6;">'
                        f'{content}</div></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="display:flex;justify-content:flex-start;margin-bottom:.7rem;">'
                        f'<div style="background:var(--card);color:var(--ink);border:1px solid var(--border);'
                        f'border-radius:var(--r2) var(--r2) var(--r2) 4px;'
                        f'padding:.65rem 1rem;max-width:75%;font-size:.86rem;line-height:1.6;">'
                        f'{content}</div></div>',
                        unsafe_allow_html=True,
                    )

    # ── Input form ────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="position:sticky;bottom:0;background:var(--bg);padding:.6rem 0 0;">'
        f'<div style="color:var(--ink3);font-size:.72rem;margin-bottom:.4rem;padding-left:.2rem;">'
        f'{persona["icon"]} {selected_persona}</div></div>',
        unsafe_allow_html=True,
    )

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Message",
            placeholder="Type your message…",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send ↵", use_container_width=True)

    if submitted and user_input.strip():
        # Append user message
        chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history = chat_history

        # Call Claude
        system_prompt = persona["prompt"]
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in chat_history
        ]

        reply = _call_claude(system_prompt, api_messages)
        chat_history.append({"role": "assistant", "content": reply})
        st.session_state.chat_history = chat_history
        st.rerun()
