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

# Custom CSS for Aesthetics and Gap Reduction
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }

    /* Reduce Top Margin/Padding of the whole page */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* Heading Margin */
    .brand-header {
        margin-top: -30px !important;
        margin-bottom: 10px !important;
        font-size: 32px;
        font-weight: 800;
        color: #1a1a1a;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0c0c0c !important;
        border-right: 1px solid #1e1e1e;
    }
    
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {
        color: #f0f0f0 !important;
    }

    /* Navigation Buttons Fix */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        color: #ffffff !important;
        background-color: #1e1e1e !important;
        border: 1px solid #333 !important;
    }
    
    .stButton > button:hover {
        border-color: #4ade80 !important;
        background-color: #222 !important;
    }

    /* Chat Messages - Reducing Gaps and Colors */
    [data-testid="stChatMessage"] {
        padding: 5px 12px !important;
        margin-bottom: 5px !important;
        border-radius: 10px;
        border: none !important;
    }

    /* Chatbot Bubble Color #cefad0 */
    [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarAssistant"]),
    .stChatMessage.assistant {
        background-color: #cefad0 !important;
    }

    [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarUser"]),
    .stChatMessage.user {
        background-color: #f7f9fa !important;
    }

    /* Source Footer inside bubble */
    .source-footer {
        font-size: 0.8rem;
        color: #666;
        margin-top: 5px;
        padding-top: 5px;
        border-top: 1px solid rgba(0,0,0,0.05);
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #0c0c0c; }
        .brand-header { color: #fff; }
        [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarAssistant"]),
        .stChatMessage.assistant { background-color: #1b3a2a !important; color: #fff; }
        [data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatarUser"]),
        .stChatMessage.user { background-color: #222 !important; color: #fff; }
    }
</style>
""", unsafe_allow_html=True)

# Main Brand Heading
st.markdown('<div class="brand-header"><span style="color: #4ade80;">GROWW</span> Mutual Fund AI Assistant</div>', unsafe_allow_html=True)

# Initialize Session State
if 'engine' not in st.session_state:
    st.session_state.engine = RAGEngine()
if 'view' not in st.session_state:
    st.session_state.view = 'chat'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'history' not in st.session_state:
    st.session_state.history = []

# Helper Functions
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
        source_match = re.search(r"Source:\s*(https?://\S+)", content, re.IGNORECASE)
        if source_match:
            source = source_match.group(1).strip().rstrip('.,;)]')
            answer_text = re.sub(r"Source:\s*https?://\S+.*?\n?", "", content, flags=re.IGNORECASE).strip()
            st.markdown(answer_text, unsafe_allow_html=True)
            st.markdown(f'<div class="source-footer">Source: <a href="{source}" target="_blank">{source}</a></div>', unsafe_allow_html=True)
        else:
            st.markdown(content, unsafe_allow_html=True)
    else:
        st.markdown(content, unsafe_allow_html=True)

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

# Layout
if st.session_state.view == 'home':
    st.title("Mutual Fund Resources")
    st.write("Browse official portals and documents from the links below.")
    st.markdown("- [SEBI Portal](https://www.sebi.gov.in/)\n- [AMFI India](https://www.amfiindia.com/)")
else:
    # Chat Loop
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="✳"):
            st.write("Hello! I am your Mutual Fund AI Assistant. How can I help you today?")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✳" if msg["role"] == "assistant" else "👤"):
            format_message(msg["role"], msg["content"])

    # Chat Input
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

# Bottom Label
st.markdown('<div style="position: fixed; bottom: 10px; right: 10px; font-size: 10px; color: #999;">Facts-only. No investment advice.</div>', unsafe_allow_html=True)
