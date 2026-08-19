import json
from database import get_db_connection
from datetime import datetime
from embeddings import calculate_visual_similarity
from geocoding import calculate_haversine_distance

def parse_vector(raw_vector) -> list:
    """Ensures image_vector is converted into a list of floats."""
    if not raw_vector:
        return []
    if isinstance(raw_vector, str):
        try:
            return json.loads(raw_vector)
        except Exception:
            return []
    if isinstance(raw_vector, list):
        return raw_vector
    return []

def calculate_match_score(lost_report: dict, found_report: dict) -> dict:
    if lost_report.get("species", "").lower() != found_report.get("species", "").lower():
        return {"total_score": 0, "distance_km": None}

    # Location Scoring via Haversine Distance
    geo_score = 0
    distance_km = None

    lat1, lon1 = lost_report.get("latitude"), lost_report.get("longitude")
    lat2, lon2 = found_report.get("latitude"), found_report.get("longitude")

    if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
        distance_km = calculate_haversine_distance(float(lat1), float(lon1), float(lat2), float(lon2))
        if distance_km <= 2.0:
            geo_score = 30
        elif distance_km <= 5.0:
            geo_score = 20
        elif distance_km <= 15.0:
            geo_score = 10
        elif distance_km <= 30.0:
            geo_score = 5
    else:
        # Fallback to keyword matching if geocoding fails
        lost_addr = lost_report.get("address", "").lower()
        found_addr = found_report.get("address", "").lower()
        lost_words = set(lost_addr.split())
        found_words = set(found_addr.split())
        if len(lost_words.intersection(found_words)) >= 2:
            geo_score = 15

    # Safe Vector Parsing for Image Similarity
    vec1 = parse_vector(lost_report.get("image_vector"))
    vec2 = parse_vector(found_report.get("image_vector"))

    visual_sim = calculate_visual_similarity(vec1, vec2)
    visual_score = (visual_sim / 100) * 40

    total = min(100, round(visual_score + geo_score + 30, 1))

    return {
        "total_score": total,
        "distance_km": distance_km
    }

def find_matches_for_report(report_id: int, top_n: int = 5) -> list[dict]:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            target = cursor.fetchone()
            if not target:
                return []
            
            target_dict = dict(target)
            opposite_type = "FOUND" if target_dict.get("type") == "LOST" else "LOST"

            cursor.execute(
                "SELECT * FROM reports WHERE type = %s AND species = %s AND status = 'ACTIVE'",
                (opposite_type, target_dict.get("species"))
            )
            candidates = [dict(r) for r in cursor.fetchall()]

            results = []
            for candidate in candidates:
                match_info = calculate_match_score(target_dict, candidate)
                if match_info["total_score"] > 0:
                    results.append({
                        "candidate_report": candidate,
                        "match_score": match_info["total_score"],
                        "distance_km": match_info["distance_km"]
                    })

            results.sort(key=lambda x: x["match_score"], reverse=True)
            return results[:top_n]