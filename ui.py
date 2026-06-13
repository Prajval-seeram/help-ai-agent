import streamlit as st

def apply_custom_css():
    """Injects custom styling for a polished product feel."""
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #cc0000;
            color: white;
            border: 1px solid #ff0000;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    st.title("🚨 HELP Platform")
    st.caption("Humanitarian Emergency Liaison Platform | Autonomous Triage Core")