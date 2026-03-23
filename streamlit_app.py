import streamlit as st
import os
import sys
import uuid
import re

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from Phases.Phase_2_RAG.src.chatbot.rag_engine import RAGEngine

# Page Configuration
st.set_page_config(
    page_title="Mutual Fund AI Assistant",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }

    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0px !important;
        max-width: 1000px !important;
    }

    .brand-header {
        margin-top: -45px !important;
        margin-bottom: 0px !important;
        font-size: 30px;
        font-weight: 800;
        color: #1a1a1a;
    }

    section[data-testid="stSidebar"] {
        background-color: #0c0c0c !important;
    }
    
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {
        color: #f0f0f0 !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        color: #ffffff !important;
        background-color: #1e1e1e !important;
        border: 1px solid #333 !important;
        padding: 2px !important;
    }

    [data-testid="stChatMessage"] {
        padding: 1px 10px !important;
        margin-bottom: 0px !important;
        border-radius: 10px;
        border: none !important;
    }

    [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarAssistant"]),
    .stChatMessage.assistant {
        background-color: #cefad0 !important;
    }

    [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarUser"]),
    .stChatMessage.user {
        background-color: #f7f9fa !important;
    }

    p, span, div {
        margin-bottom: 0px !important;
    }

    .source-wrapper {
        font-size: 0.7rem;
        color: #444;
        margin-top: 0px !important;
        padding-top: 1px !important;
        border-top: 1px solid rgba(0,0,0,0.03);
        display: block;
        line-height: 1.1;
    }

    .disclaimer-text {
        font-size: 0.75rem;
        color: #666;
        margin-top: 2px !important;
        display: block;
    }

    /* Resource Card Styles */
    .resource-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #f2f2f2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
        margin-bottom: 15px;
    }
    
    .resource-card h3 {
        color: #333;
        font-size: 18px;
        margin-bottom: 12px;
        border-bottom: 2px solid #4ade80;
        display: inline-block;
    }

    .resource-card ul {
        padding-left: 20px;
        margin-top: 10px;
    }

    .resource-card li {
        margin-bottom: 8px;
        color: #0084ff;
    }
    
    .fixed-footer {
        position: fixed;
        bottom: 0px;
        right: 15px;
        font-size: 8px !important;
        color: #bbb;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        pointer-events: none;
        z-index: 1000;
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #0c0c0c; }
        .brand-header { color: #fff; }
        [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarAssistant"]),
        .stChatMessage.assistant { background-color: #1b3a2a !important; color: #fff; }
        [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarUser"]),
        .stChatMessage.user { background-color: #222 !important; color: #fff; }
        .resource-card { background-color: #1a1a1a; border-color: #333; }
        .resource-card h3 { color: #fff; }
    }
</style>
""", unsafe_allow_html=True)

# Brand Header
st.markdown('<div class="brand-header"><span style="color: #4ade80;">GROWW</span> Mutual Fund AI Assistant</div>', unsafe_allow_html=True)

# Session State
if 'engine' not in st.session_state:
    st.session_state.engine = RAGEngine()
if 'view' not in st.session_state:
    st.session_state.view = 'chat'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'history' not in st.session_state:
    st.session_state.history = []

def start_new_chat():
    if st.session_state.messages:
        chat_id = str(uuid.uuid4())[:8]
        title = st.session_state.messages[0]['content'][:30] + "..."
        st.session_state.history.insert(0, {"id": chat_id, "title": title, "messages": st.session_state.messages.copy()})
    st.session_state.messages = []
    st.session_state.view = 'chat'

def load_chat(chat_idx):
    st.session_state.messages = st.session_state.history[chat_idx]['messages'].copy()
    st.session_state.view = 'chat'

def format_message(role, content):
    if role == "assistant":
        lines = content.split('\n')
        source_url = "https://groww.in"
        disclaimer = "Facts-only. No investment advice."
        main_answer_parts = []
        for line in lines:
            if line.startswith("Source:"):
                source_url = line.replace("Source:", "").strip()
            elif "Facts-only" in line:
                disclaimer = line.strip()
            elif line.strip():
                main_answer_parts.append(line)
        main_answer = "<br>".join(main_answer_parts)
        payload = f"""<div>{main_answer}</div><div class="disclaimer-text">{disclaimer}</div><div class="source-wrapper">Source: <a href="{source_url}" target="_blank">{source_url}</a></div>"""
        st.markdown(payload, unsafe_allow_html=True)
    else:
        st.markdown(content.replace("\n", "<br>"), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h2 style="color: #4ade80; text-align: center;">✳ AI ASSISTANT</h2>', unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.view = 'home'
    st.markdown("---")
    st.markdown("### OLDER CHATS")
    for i, chat in enumerate(st.session_state.history):
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"💬 {chat['title']}", key=f"chat_{i}", use_container_width=True):
                load_chat(i)
        with cols[1]:
            if st.button("✖", key=f"del_{i}"):
                st.session_state.history.pop(i)
                st.rerun()

# Layout Content
if st.session_state.view == 'home':
    st.markdown('<h2 style="margin-top: -10px;">Mutual Fund Resources</h2>', unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="resource-card"><h3>Official Portals</h3><ul><li><a href="https://www.amfiindia.com/">AMFI India</a></li><li><a href="https://www.sebi.gov.in/">SEBI Portal</a></li><li><a href="https://www.amfiindia.com/net-asset-value">Latest NAVs</a></li></ul></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="resource-card"><h3>AMC Factsheets</h3><ul><li><a href="https://www.sbimf.com/">SBI Mutual Fund</a></li><li><a href="https://www.hdfcfund.com/">HDFC Mutual Fund</a></li><li><a href="https://groww.in/mutual-funds/fact-sheets">Groww Factsheets</a></li></ul></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="resource-card"><h3>Market Data</h3><ul><li><a href="https://groww.in/">Groww Explorer</a></li><li><a href="https://www.moneycontrol.com/">Moneycontrol</a></li><li><a href="https://www.valueresearchonline.com/">Value Research</a></li></ul></div>""", unsafe_allow_html=True)
else:
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="✳"):
            st.write("Hello! I am your Mutual Fund AI Assistant. How can I help you today?")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✳" if msg["role"] == "assistant" else "👤"):
            format_message(msg["role"], msg["content"])
    if prompt := st.chat_input("Ask about HDFC, SBI, or other funds..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# RAG
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    try:
        response = st.session_state.engine.handle_query(last_query)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Sticky Footer
st.markdown('<div class="fixed-footer">Facts-only. No investment advice.</div>', unsafe_allow_html=True)
