import streamlit as st
import folium

from streamlit_folium import st_folium

from services.location_service import (
    geocode_location
)

st.title("🗺️ Select Location")

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

        st.session_state["map_lat"] = lat
        st.session_state["map_lon"] = lon

        st.session_state["location_name"] = (
            result["address"]
        )

if (
    "map_lat" in st.session_state
    and
    "map_lon" in st.session_state
):

    m = folium.Map(
        location=[
            st.session_state["map_lat"],
            st.session_state["map_lon"]
        ],
        zoom_start=15
    )

    folium.Marker(
        [
            st.session_state["map_lat"],
            st.session_state["map_lon"]
        ],
        tooltip="Current Location"
    ).add_to(m)

    map_data = st_folium(
        m,
        width=700,
        height=500
    )

    if map_data["last_clicked"]:

        clicked_lat = (
            map_data["last_clicked"]["lat"]
        )

        clicked_lon = (
            map_data["last_clicked"]["lng"]
        )

        st.session_state["latitude"] = clicked_lat
        st.session_state["longitude"] = clicked_lon

        st.success(
            "Location Selected"
        )

        st.write(
            f"Latitude: {clicked_lat}"
        )

        st.write(
            f"Longitude: {clicked_lon}"
        )

        if st.button(
            "Save Selected Location"
        ):

            st.success(
                "Location Saved"
            )