import streamlit as st
import os
import sys
import uuid
from datetime import datetime

# Add RAG Engine to path
BASE_DIR = os.path.abspath(os.curdir)
sys.path.append(BASE_DIR)
from Phases.Phase_2_RAG.src.chatbot.rag_engine import RAGEngine

# Page Configuration
st.set_page_config(
    page_title="Mutual Fund AI Assistant",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0c0c0c !important;
        border-right: 1px solid #1e1e1e;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #f0f0f0 !important;
    }

    /* Brand Name */
    .brand-title {
        color: #6b46c1;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Buttons Visibility Fix */
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
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Active State Mock */
    .sidebar-active {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 5px 10px;
    }

    /* Resource Cards */
    .resource-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #f2f2f2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
    }
    
    .resource-card h3 {
        color: #333;
        font-size: 18px;
        margin-bottom: 15px;
        border-bottom: 2px solid #4ade80;
        display: inline-block;
    }
    
    /* Source Footer */
    .source-footer {
        font-size: 0.8rem;
        color: #666;
        margin-top: 10px;
        padding-top: 5px;
        border-top: 1px solid #eee;
    }
    
    /* Dark Theme Support */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #0c0c0c; }
        .resource-card { background-color: #1a1a1a; border-color: #333; }
        .resource-card h3 { color: #fff; }
    }
</style>
""", unsafe_allow_html=True)

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
        # Save current chat to history
        chat_id = str(uuid.uuid4())[:8]
        title = st.session_state.messages[0]['content'][:30] + "..." if len(st.session_state.messages[0]['content']) > 30 else st.session_state.messages[0]['content']
        st.session_state.history.insert(0, {"id": chat_id, "title": title, "messages": st.session_state.messages.copy()})
    st.session_state.messages = []
    st.session_state.view = 'chat'

def load_chat(chat_idx):
    st.session_state.messages = st.session_state.history[chat_idx]['messages'].copy()
    st.session_state.view = 'chat'

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="brand-title">✳ AI ASSISTANT</div>', unsafe_allow_html=True)
    
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

# Main Views
if st.session_state.view == 'home':
    st.title("Mutual Fund Resources")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="resource-card">
            <h3>Official Portals</h3>
            <ul>
                <li><a href="https://www.amfiindia.com/" target="_blank">AMFI India</a></li>
                <li><a href="https://www.sebi.gov.in/" target="_blank">SEBI Portal</a></li>
                <li><a href="https://www.amfiindia.com/net-asset-value" target="_blank">Latest NAVs</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="resource-card">
            <h3>AMC Factsheets</h3>
            <ul>
                <li><a href="https://www.sbimf.com/en-us/factsheets" target="_blank">SBI Mutual Fund</a></li>
                <li><a href="https://www.hdfcfund.com/mutual-funds/factsheets" target="_blank">HDFC Mutual Fund</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="resource-card">
            <h3>Market Data</h3>
            <ul>
                <li><a href="https://groww.in/mutual-funds" target="_blank">Groww Explorer</a></li>
                <li><a href="https://www.moneycontrol.com/mutual-funds/" target="_blank">Moneycontrol</a></li>
                <li><a href="https://www.valueresearchonline.com/" target="_blank">Value Research</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    # Main Header with GROWW Branding
    st.markdown('<h1 style="font-size: 32px; font-weight: 800;"><span style="color: #4ade80;">GROWW</span> Mutual Fund AI Assistant</h1>', unsafe_allow_html=True)
    
    # Display Welcome Message if empty
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="✳"):
            st.write("Hello! I am your Mutual Fund AI Assistant. I can help you with factual data about mutual funds and SEBI regulations. How can I help you today?")

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✳" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Chat Input
    if prompt := st.chat_input("Ask about fund costs, returns, or SEBI rules..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get Response from RAG Engine
        with st.chat_message("assistant", avatar="✳"):
            try:
                response_full = st.session_state.engine.handle_query(prompt)
                
                # Split source for UI footer
                import re
                source = "Mutual Fund Data Repository"
                source_match = re.search(r"Source:\s*(https?://\S+)", response_full, re.IGNORECASE)
                
                if source_match:
                    source = source_match.group(1).strip().rstrip('.,;)]')
                    answer_text = re.sub(r"Source:\s*https?://\S+.*?\n?", "", response_full, flags=re.IGNORECASE).strip()
                else:
                    answer_text = response_full
                
                # Render answer
                st.markdown(answer_text, unsafe_allow_html=True)
                
                # Render source footer
                if source.startswith("http"):
                    st.markdown(f'<div class="source-footer">Source: <a href="{source}" target="_blank">{source}</a></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="source-footer">Source: {source}</div>', unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": response_full})
                
            except Exception as e:
                st.error(f"Error connecting to AI: {str(e)}")

# Footer
st.markdown("""
<div style="position: fixed; bottom: 10px; right: 10px; font-size: 10px; color: #999;">
    Facts-only. No investment advice.
</div>
""", unsafe_allow_html=True)
