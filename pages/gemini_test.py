import streamlit as st

from services.gemini_service import (
    analyze_incident
)

st.title("🤖 Gemini Test")

incident_type = st.selectbox(
    "Type",
    [
        "Accident",
        "Medical Emergency",
        "Fire",
        "Flood",
        "Violence",
        "Missing Person",
        "Other"
    ]
)

description = st.text_area(
    "Description"
)

if st.button("Analyze"):

    with st.spinner(
        "🤖 Analyzing incident..."
    ):

        result = analyze_incident(
            incident_type,
            description
        )

    st.success(
        "Analysis complete"
    )

    st.json(result)