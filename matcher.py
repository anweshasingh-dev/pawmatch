from database import get_db_connection
from datetime import datetime
import json
from embeddings import calculate_visual_similarity
from geocoding import calculate_haversine_distance

def calculate_match_score(lost_report: dict, found_report: dict) -> dict:
    if lost_report["species"].lower() != found_report["species"].lower():
        return {"total_score": 0, "distance_km": None}

    # Location Scoring via Haversine Distance
    geo_score = 0
    distance_km = None

    lat1, lon1 = lost_report.get("latitude"), lost_report.get("longitude")
    lat2, lon2 = found_report.get("latitude"), found_report.get("longitude")

    if lat1 and lon1 and lat2 and lon2:
        distance_km = calculate_haversine_distance(lat1, lon1, lat2, lon2)
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
        lost_words = set(lost_report["address"].lower().split())
        found_words = set(found_report["address"].lower().split())
        if len(lost_words.intersection(found_words)) >= 2:
            geo_score = 15

    # Visual & Species scores...
    visual_sim = calculate_visual_similarity(
        lost_report.get("image_vector"), 
        found_report.get("image_vector")
    )
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
            opposite_type = "FOUND" if target_dict["type"] == "LOST" else "LOST"

            cursor.execute(
                "SELECT * FROM reports WHERE type = %s AND species = %s AND status = 'ACTIVE'",
                (opposite_type, target_dict["species"])
            )
            candidates = [dict(r) for r in cursor.fetchall()]

            results = []
            for candidate in candidates:
                match_info = calculate_match_score(target_dict, candidate)
                if match_info["total_score"] > 0:
                    results.append({
                        "candidate_report": candidate,
                        "match_score": match_info["total_score"]
                    })

            results.sort(key=lambda x: x["match_score"], reverse=True)
            return results[:top_n]