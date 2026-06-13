import streamlit as st
from ui import apply_custom_css

# MUST be the first command in Streamlit
st.set_page_config(
    page_title="HELP | AI Triage",
    page_icon="🚨",
    layout="centered"
)

# Apply global CSS
apply_custom_css()

# Native Streamlit Multi-Page Routing
pages = {
    "Operations": [
        st.Page("pages/chat.py", title="Triage Dashboard", icon="🎙️"),
    ],
    "System": [
        st.Page("pages/settings.py", title="Configuration", icon="⚙️"),
    ]
}

pg = st.navigation(pages)
pg.run()