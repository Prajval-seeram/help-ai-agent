import streamlit as st

from services.gemini_service import analyze_incident
from services.incident_service import (
    create_incident,
    update_incident
)

st.title("🚨 Report Incident")

incident_type = st.selectbox(
    "Incident Type",
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
    "Describe the situation"
)

uploaded_image = st.file_uploader(
    "Upload Image (Optional)",
    type=["jpg", "jpeg", "png"]
)

st.subheader("Selected Location")

location_name = st.session_state.get(
    "location_name",
    "No location selected"
)

st.write(location_name)

if st.button("Create Incident"):

    if not description:

        st.error(
            "Please provide a description."
        )

    elif location_name == "No location selected":

        st.error(
            "Please select a location first."
        )

    else:

        incident_data = {
            "user_id": st.session_state.get("user_id"),
            "incident_type": incident_type,
            "description": description,
            "location_name": location_name,
            "latitude": st.session_state.get("latitude"),
            "longitude": st.session_state.get("longitude"),
            "status": "Pending"
        }

        try:

            result = create_incident(
                incident_data
            )

            incident_id = result.data[0]["id"]

            with st.spinner(
                "🤖 Analyzing incident..."
            ):

                analysis = analyze_incident(
                    incident_type,
                    description
                )

            update_incident(
                incident_id,
                {
                    "severity":
                        analysis["severity"],

                    "confidence":
                        analysis["confidence"],

                    "category":
                        analysis["category"],

                    "recommended_action":
                        analysis["recommended_action"]
                }
            )

            st.success(
                "Incident saved and analyzed successfully ✅"
            )

            st.subheader("AI Assessment")

            st.write(
                f"Severity: {analysis['severity']}"
            )

            st.write(
                f"Category: {analysis['category']}"
            )

            st.write(
                f"Confidence: {analysis['confidence']}%"
            )

            st.write(
                "Recommended Action:"
            )

            st.info(
                analysis["recommended_action"]
            )

            st.subheader("Precautions")

            for precaution in analysis["precautions"]:
                st.write(
                    f"• {precaution}"
                )

        except Exception as e:

            st.error(
                f"Failed: {e}"
            )