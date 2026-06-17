import streamlit as st

st.title("⚙️ Settings")

# ==========================
# Gemini API Key (BYOK)
# ==========================

st.header("🔑 Gemini API Key")

current_key = st.session_state.get(
    "USER_GEMINI_KEY",
    ""
)

user_api_key = st.text_input(
    "Google Gemini API Key",
    value=current_key,
    type="password",
    placeholder="AIzaSy..."
)

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Save API Key"):
        if user_api_key.strip():
            st.session_state["USER_GEMINI_KEY"] = (
                user_api_key.strip()
            )
            st.success(
                "API Key saved for this session."
            )
        else:
            st.warning(
                "Please enter a valid API key."
            )

with col2:
    if st.button("🗑️ Clear API Key"):
        st.session_state.pop(
            "USER_GEMINI_KEY",
            None
        )
        st.success(
            "Custom API Key removed."
        )

if st.session_state.get(
        "USER_GEMINI_KEY"
):
    st.success(
        "Custom Gemini API Key Active"
    )
else:
    st.info(
        "Using default server Gemini API Key"
    )

st.divider()

# ==========================
# Account
# ==========================

st.header("👤 Account")

if st.button("🚪 Logout"):
    st.session_state.clear()
    st.success(
        "Logged out successfully."
    )
    st.rerun()