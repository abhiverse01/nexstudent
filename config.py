# config.py — CSS theme tokens and injection
# All CSS is split into small chunks to avoid Streamlit's HTML sanitizer
# size threshold. Each chunk is a separate st.markdown() call.

import streamlit as st

# ── Font import (isolated) ────────────────────────────────────────────────────
FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;'
    '0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400'
    '&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">'
)

# ── CSS chunks ───────────────────────────────────────────────────────────────
CSS_PART1 = """<style>
:root{--bg:#070710;--surface:#0d0d1a;--card:#111124;--card2:#161630;--border:#1c1c3a;
--border2:#252550;--ink:#e8e8f8;--ink2:#9090b8;--ink3:#4a4a72;--sol:#5b5ef4;--sol2:#818cf8;
--amber:#f59e0b;--rose:#f43f5e;--teal:#2dd4bf;--green:#22c55e;--r:12px;--r2:8px;
--sh:0 4px 24px rgba(0,0,0,.5);--sh2:0 2px 12px rgba(0,0,0,.35);--glow:0 0 40px rgba(91,94,244,.18)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background-color:var(--bg)!important;color:var(--ink)!important}
.main .block-container{padding:1.2rem 2rem 4rem!important;max-width:1300px!important}
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important}
section[data-testid="stSidebar"] .block-container{padding:1rem .75rem!important}
section[data-testid="stSidebar"] button{background:transparent!important;border:none!important;
color:var(--ink2)!important;font-family:'DM Sans',sans-serif!important;font-size:.84rem!important;
font-weight:500!important;text-align:left!important;padding:.5rem .75rem!important;
border-radius:var(--r2)!important;transition:background .15s,color .15s!important;width:100%!important}
section[data-testid="stSidebar"] button:hover{background:rgba(91,94,244,.12)!important;color:var(--ink)!important}
section[data-testid="stSidebar"] button[kind="secondary"]{background:rgba(91,94,244,.18)!important;color:var(--sol2)!important}
</style>"""

CSS_PART2 = """<style>
#MainMenu,footer,header{visibility:hidden!important}
.stDeployButton{display:none!important}
[data-testid="stToolbar"]{display:none!important}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--surface)!important;
border:1px solid var(--border)!important;border-radius:var(--r2)!important;color:var(--ink)!important;
font-family:'DM Sans',sans-serif!important;font-size:.88rem!important;transition:border-color .2s,box-shadow .2s!important}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--sol)!important;
box-shadow:0 0 0 3px rgba(91,94,244,.15)!important;outline:none!important}
.stSelectbox>div>div,.stMultiSelect>div>div{background:var(--surface)!important;border:1px solid var(--border)!important;
border-radius:var(--r2)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;font-size:.88rem!important}
label,.stRadio label,.stCheckbox label{color:var(--ink2)!important;font-family:'DM Sans',sans-serif!important;
font-size:.84rem!important;font-weight:500!important}
.stButton>button{background:var(--sol)!important;color:#fff!important;border:none!important;
border-radius:var(--r2)!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;
font-size:.84rem!important;padding:.48rem 1.2rem!important;letter-spacing:.01em!important;
transition:background .15s,transform .1s,box-shadow .15s!important;cursor:pointer!important}
.stButton>button:hover{background:var(--sol2)!important;transform:translateY(-1px)!important;
box-shadow:0 4px 16px rgba(91,94,244,.4)!important}
.stButton>button:active{transform:translateY(0)!important}
</style>"""

CSS_PART3 = """<style>
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;
border-radius:var(--r)!important;padding:.9rem 1.1rem!important}
[data-testid="metric-container"]>div>label{color:var(--ink3)!important;font-size:.74rem!important;
font-weight:600!important;letter-spacing:.06em!important;text-transform:uppercase!important}
[data-testid="stMetricValue"]{font-size:1.65rem!important;font-weight:700!important;color:var(--ink)!important;
font-family:'DM Mono',monospace!important}
[data-testid="stMetricDelta"]{font-size:.78rem!important}
.stTabs [data-baseweb="tab-list"]{gap:2px!important;background:var(--surface)!important;
border-radius:var(--r2)!important;padding:3px!important;border:1px solid var(--border)!important;width:fit-content!important}
.stTabs [data-baseweb="tab"]{border-radius:6px!important;padding:.35rem .9rem!important;
font-family:'DM Sans',sans-serif!important;font-size:.82rem!important;font-weight:500!important;
color:var(--ink3)!important;background:transparent!important;border:none!important}
.stTabs [aria-selected="true"]{background:var(--sol)!important;color:#fff!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.streamlit-expanderHeader{background:var(--card)!important;border-radius:var(--r)!important;
border:1px solid var(--border)!important;font-weight:600!important;font-size:.86rem!important;
color:var(--ink)!important;font-family:'DM Sans',sans-serif!important}
.streamlit-expanderContent{background:var(--surface)!important;border:1px solid var(--border)!important;
border-top:none!important;border-radius:0 0 var(--r) var(--r)!important}
[data-testid="stSlider"]>div>div>div>div{background:var(--sol)!important}
[data-testid="stSlider"] div[role="slider"]{background:var(--sol)!important;border:2px solid var(--sol2)!important}
.stDataFrame{border-radius:var(--r)!important;overflow:hidden!important;border:1px solid var(--border)!important}
code,pre{background:var(--surface)!important;border:1px solid var(--border)!important;
border-radius:var(--r2)!important;font-family:'DM Mono',monospace!important;font-size:.82rem!important;color:var(--teal)!important}
.stSuccess{background:rgba(34,197,94,.08)!important;border:1px solid rgba(34,197,94,.25)!important;
border-radius:var(--r2)!important;color:var(--green)!important}
.stError{background:rgba(244,63,94,.08)!important;border:1px solid rgba(244,63,94,.25)!important;
border-radius:var(--r2)!important;color:var(--rose)!important}
.stInfo{background:rgba(91,94,244,.08)!important;border:1px solid rgba(91,94,244,.2)!important;
border-radius:var(--r2)!important}
.stWarning{background:rgba(245,158,11,.08)!important;border:1px solid rgba(245,158,11,.2)!important;
border-radius:var(--r2)!important}
</style>"""

CSS_PART4 = """<style>
.stRadio>div{gap:.5rem!important}
hr{border-color:var(--border)!important;margin:1.4rem 0!important}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
[data-testid="stFileUploader"]{background:var(--surface)!important;border:1.5px dashed var(--border2)!important;
border-radius:var(--r)!important}
[data-testid="stColorPicker"]>div{border:1px solid var(--border)!important;border-radius:var(--r2)!important}
[data-testid="stDateInput"]>div>div>input{background:var(--surface)!important;border:1px solid var(--border)!important;
border-radius:var(--r2)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;font-size:.88rem!important}
[data-testid="stForm"]{background:transparent!important;border:none!important}
</style>"""


def inject_css():
    """Inject all CSS chunks into the page. Must be called once at app start."""
    st.markdown(FONT_LINK, unsafe_allow_html=True)
    st.markdown(CSS_PART1, unsafe_allow_html=True)
    st.markdown(CSS_PART2, unsafe_allow_html=True)
    st.markdown(CSS_PART3, unsafe_allow_html=True)
    st.markdown(CSS_PART4, unsafe_allow_html=True)
