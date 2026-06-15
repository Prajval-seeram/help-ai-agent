import streamlit as st

st.title("📍 Location Setup")

st.subheader("Choose your location")

location_method = st.radio(
    "Location Method",
    [
        "Auto Detect",
        "Enter Manually"
    ]
)

if location_method == "Auto Detect":
    st.info(
        "Auto detection will be implemented next."
    )

if location_method == "Enter Manually":
    location_name = st.text_input(
        "Enter Location"
    )

    if st.button("Save Location"):
        st.session_state["location_name"] = location_name

        st.success(
            f"Location saved: {location_name}"
        )