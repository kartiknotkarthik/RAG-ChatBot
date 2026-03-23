import streamlit as st
import sys
import os

# Add root folder to path for absolute imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.chatbot.rag_engine import RAGEngine

# Page Config
st.set_page_config(page_title="MF RAG Chatbot", page_icon="📈", layout="centered")

# Custom Styling (Dark Mode aesthetics, premium look)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput>div>div>input {
        background-color: #1e2130;
        color: #ffffff;
        border: 1px solid #4ade80;
    }
    .stButton>button {
        background-color: #4ade80;
        color: #0e1117;
        font-weight: bold;
    }
    .disclaimer-box {
        padding: 10px;
        background-color: #ff4b4b22;
        border-radius: 5px;
        border: 1px solid #ff4b4b;
        margin-bottom: 20px;
        text-align: center;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# App Layout
st.title("📈 Mutual Fund RAG Guide")
st.markdown("##### Personalized Mutual Fund Insight – Facts & Regulations")

# Header Disclaimer
st.markdown('<div class="disclaimer-box">⚠️ <b>Facts-only. No investment advice.</b><br>I provide factual data and regulatory answers. I do not recommend funds for investment.</div>', unsafe_allow_html=True)

# Initialization
if 'chat_engine' not in st.session_state:
    try:
        st.session_state.chat_engine = RAGEngine()
        st.session_state.ready = True
    except Exception as e:
        st.error(f"Error initializing RAG engine: {e}")
        st.session_state.ready = False

# Query Input
user_query = st.text_input("Ask a question about HDFC/SBI funds, NAV, or SEBI regulations:", placeholder="e.g., What is the expense ratio for HDFC Large and Mid Cap Fund?")

# Example Questions
st.markdown("**Example Questions:**")
cols = st.columns(2)
examples = [
    "What is the exit load for HDFC Large and Mid Cap Fund?",
    "Tell me the strategy of SBI Gold Fund.",
    "What are SEBI regulations on expense ratios?",
    "What is the performance of HDFC Silver ETF FOF?"
]

for i, ex in enumerate(examples):
    if cols[i % 2].button(ex):
        user_query = ex

# Process Query
if user_query and st.session_state.ready:
    with st.spinner("Analyzing facts..."):
        ans = st.session_state.chat_engine.handle_query(user_query)
        st.markdown("### Answer")
        st.write(ans)

# Footer
st.divider()
st.markdown("Built with ChromaDB, OpenAI, and Mutual Fund Data.")
