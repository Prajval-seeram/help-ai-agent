from geopy.geocoders import Nominatim

def geocode_location(location_name):
    try:
        geolocator = Nominatim(user_agent="help_app")
        location = geolocator.geocode(location_name)

        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }
        return None
    except Exception:
        return None


def reverse_geocode(latitude, longitude):
    try:
        geolocator = Nominatim(user_agent="help_app_reverse")
        location = geolocator.reverse((latitude, longitude), exactly_one=True)

        if location and location.address:
            return location.address
        return None
    except Exception:
        return None