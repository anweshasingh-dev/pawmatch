from math import asin, cos, radians, sin, sqrt

from embeddings import calculate_visual_similarity
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim


geocoder = Nominatim(user_agent="pawmatch")


def get_coordinates(address: str) -> tuple[float | None, float | None]:
    """Resolve an address to latitude and longitude when the geocoder is available."""
    if not address or not address.strip():
        return None, None

    try:
        location = geocoder.geocode(address.strip())
    except (GeocoderServiceError, TimeoutError):
        return None, None

    if location is None:
        return None, None
    return location.latitude, location.longitude


def calculate_haversine_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Calculate the great-circle distance between two coordinates in km."""
    earth_radius_km = 6371.0
    lat1 = radians(latitude_1)
    lat2 = radians(latitude_2)
    delta_lat = radians(latitude_2 - latitude_1)
    delta_lon = radians(longitude_2 - longitude_1)

    haversine = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(haversine))

def rank_pet_matches(target_pet: dict, candidate_pets: list[dict], max_radius_km: float = 50.0) -> list[dict]:
    """
    Ranks candidate pets based on a weighted score of visual similarity and geographic proximity.
    
    `target_pet` structure:
    {
        "id": 1,
        "species": "dog",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "embedding": [0.12, -0.45, ...]
    }
    """
    ranked_results = []

    for candidate in candidate_pets:
        # 1. Hard Filter: Species must match
        if target_pet.get("species") != candidate.get("species"):
            continue

        # 2. Calculate Distance
        dist_km = calculate_haversine_distance(
            target_pet["latitude"], target_pet["longitude"],
            candidate["latitude"], candidate["longitude"]
        )

        # 3. Filter out pets found outside max radius
        if dist_km > max_radius_km:
            continue

        # 4. Calculate Visual Similarity (0% - 100%)
        visual_score = calculate_visual_similarity(
            target_pet["embedding"], candidate["embedding"]
        )

        # 5. Hybrid Scoring Algorithm (70% Visual Match + 30% Geographic Distance Weight)
        # Closer distance gives higher score multiplier
        geo_score = max(0.0, 100.0 - (dist_km / max_radius_km * 100.0))
        final_score = round((0.7 * visual_score) + (0.3 * geo_score), 2)

        ranked_results.append({
            "pet_id": candidate["id"],
            "distance_km": dist_km,
            "visual_similarity_%": visual_score,
            "match_confidence_%": final_score,
            "contact_number": candidate.get("contact_number")
        })

    # Sort results highest confidence first
    ranked_results.sort(key=lambda x: x["match_confidence_%"], reverse=True)
    return ranked_results