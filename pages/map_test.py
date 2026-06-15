import streamlit as st
import folium

from streamlit_folium import st_folium

from services.location_service import (
    geocode_location
)

st.title("🗺️ Location Map")

location_name = st.text_input(
    "Search Location"
)

if st.button("Search"):

    result = geocode_location(
        location_name
    )

    if result:

        lat = result["latitude"]
        lon = result["longitude"]

        st.success(
            result["address"]
        )

        m = folium.Map(
            location=[lat, lon],
            zoom_start=15
        )

        folium.Marker(
            [lat, lon],
            tooltip="Selected Location"
        ).add_to(m)

        st_folium(
            m,
            width=700,
            height=500
        )

        st.session_state["location_name"] = (
            result["address"]
        )

        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon

    else:
        st.error(
            "Location not found"
        )
st.write(st.session_state)