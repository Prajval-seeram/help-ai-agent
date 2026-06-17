import streamlit as st
from services.auth_service import (
    sign_up,
    sign_in,
    create_user_profile
)

st.title("🔐 HELP Authentication")

tab1, tab2 = st.tabs(["Login", "Register"])

# =========================
# LOGIN
# =========================
with tab1:
    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login"):
        result = sign_in(email, password)

        if hasattr(result, "user") and result.user:
            create_user_profile(result.user)

            st.session_state["user"] = result.user.email
            st.session_state["user_id"] = result.user.id

            st.success("Login successful ✅")
            st.switch_page("Home.py")

        else:
            st.error("Login failed ❌")


# =========================
# REGISTER
# =========================
with tab2:
    email = st.text_input(
        "Email",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="register_password"
    )

    if st.button("Register"):
        result = sign_up(email, password)

        if hasattr(result, "user") and result.user:
            st.success("Account created successfully ✅")
        else:
            st.error("Registration failed ❌")