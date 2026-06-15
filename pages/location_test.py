import streamlit as st
from services.location_service import get_user_location

st.title("📍 Location Test")

location = get_user_location()

if location:
    st.success("Location detected")

    st.write(
        f"Latitude: {location['latitude']}"
    )

    st.write(
        f"Longitude: {location['longitude']}"
    )

    st.write(
        f"Accuracy: {location['accuracy']} meters"
    )

    st.session_state["location"] = location

else:
    st.warning(
        "Allow location permission and refresh."
    )