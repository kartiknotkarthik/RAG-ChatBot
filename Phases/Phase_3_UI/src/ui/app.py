import streamlit as st
import sys
import os

# Add root folder to path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Page Config
st.set_page_config(page_title="MF RAG Guide", page_icon="📈", layout="wide")

# Custom CSS to match the provided image (Qubi Design)
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling - Pitch Black */
    [data-testid="stSidebar"] {
        background-color: #0c0c0c;
        color: #f0f0f0;
        border-right: 1px solid #1e1e1e;
    }
    
    /* Sidebar Section Headers */
    .sidebar-header {
        color: #666;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        margin: 20px 0 10px 10px;
    }

    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent;
        color: #d0d0d0;
        border: none;
        border-radius: 8px;
        width: 100%;
        text-align: left;
        padding: 8px 15px;
        margin: 2px 0;
        font-weight: 500;
        font-size: 14px;
        justify-content: flex-start;
    }
    
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #222;
        color: #fff;
    }

    /* Main Area Styling - Pure White */
    .stApp {
        background-color: #ffffff;
    }

    /* Top Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 20px;
        border-bottom: 1px solid #f2f2f2;
        margin-bottom: 25px;
    }
    .brand-name {
        font-size: 22px;
        font-weight: 700;
        color: #6b46c1; /* Qubi Purple */
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-icon {
        width: 24px; height: 24px;
        background-color: #6b46c1;
        mask: url('https://api.iconify.design/material-symbols:asterisk.svg') no-repeat center;
        -webkit-mask: url('https://api.iconify.design/material-symbols:asterisk.svg') no-repeat center;
    }

    .action-buttons { display: flex; gap: 12px; }
    .btn-action {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #e0e0e0;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
    .btn-update { background-color: #d8f5d8; color: #1e6e1e; border: none; }
    .btn-settings { background-color: #252525; color: #fff; border: none; }

    /* Chat Bubbles */
    .chat-container {
        display: flex; flex-direction: column;
        gap: 20px; max-width: 900px;
        margin: 0 auto; padding: 20px;
    }
    .message {
        padding: 18px 25px;
        border-radius: 12px;
        font-size: 14.5px;
        line-height: 1.6;
        min-width: 100px;
        max-width: 85%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .ai-message {
        background-color: #ffffff;
        align-self: flex-start;
        color: #333;
        border: 1px solid #f0f0f0;
        position: relative;
    }
    .user-message {
        background-color: #f8f6ff;
        align-self: flex-end;
        color: #333;
        border: 1px solid #ecebff;
    }
    
    .ai-bubble-icon {
        width: 20px; height: 20px;
        background-color: #4ade80; /* Qubi Green */
        border-radius: 50%;
        display: inline-block;
        margin-right: 12px;
        vertical-align: middle;
        mask: url('https://api.iconify.design/material-symbols:asterisk.svg') no-repeat center;
        -webkit-mask: url('https://api.iconify.design/material-symbols:asterisk.svg') no-repeat center;
    }

    /* Input Styling */
    [data-testid="stChatInput"] {
        border-radius: 40px !important;
        background-color: #f7f7f7 !important;
        border: 1px solid #eeeeee !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">Main</div>', unsafe_allow_html=True)
    st.button("➕ New Chat")
    st.button("🔍 Search")
    st.button("🏠 Home")
    st.button("💬 Chats")
    
    st.markdown('<div class="sidebar-header">Pinned Folders</div>', unsafe_allow_html=True)
    st.button("📁 General")
    st.button("📁 Design")
    st.button("📁 Management")

    st.markdown('<div class="sidebar-header">Today</div>', unsafe_allow_html=True)
    st.button("🗨️ HDFC Performance...")
    st.button("🗨️ SBI Gold Strategy...")
    
    st.markdown('<div class="sidebar-header">Yesterday</div>', unsafe_allow_html=True)
    st.button("🗨️ SEBI Rules...")

# Top Bar
st.markdown("""
<div class="top-bar">
    <div class="brand-name"><div class="brand-icon"></div> MF RAG Guide</div>
    <div class="action-buttons">
        <button class="btn-action btn-update">✳️ Update</button>
        <button class="btn-action btn-settings">⚙️ Settings</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Chat History Initialization
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Mutual fund Assistant. How can I help you today?"}
    ]

# Display Messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"""
        <div class="message ai-message">
            <span class="ai-bubble-icon"></span>
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message user-message">
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Spacing
st.write("")
st.write("")

# Main Disclaimer - Subtle but constant
st.info("⚠️ Facts-only. No investment advice. Citation links provided for all data.")

# Input
if prompt := st.chat_input("type your prompt here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Live Backend Integration
    import requests
    try:
        # Call the FastAPI backend on port 8005
        backend_url = "http://127.0.0.1:8005/query"
        payload = {"query": prompt}
        response = requests.post(backend_url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            ans = data.get("answer", "No answer returned.")
            src = data.get("source", "Unknown Source")
            
            bot_response = f"{ans}\n\n**Source:** {src}"
        else:
            bot_response = f"Backend Error (Status {response.status_code})"
    except Exception as e:
        bot_response = f"Could not reach backend: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()

# Note for Phase 3 -> Phase 4 transition
# In Phase 4, we will replace this dummy response with a real call to the FastAPI Backend.
