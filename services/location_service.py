from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim


def get_user_location():
    location = streamlit_geolocation()

    if location and location.get("latitude"):
        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "accuracy": location.get("accuracy")
        }

    return None


def geocode_location(location_name):
    try:
        geolocator = Nominatim(
            user_agent="help_app"
        )

        location = geolocator.geocode(
            location_name
        )

        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }

        return None

    except Exception:
        return None