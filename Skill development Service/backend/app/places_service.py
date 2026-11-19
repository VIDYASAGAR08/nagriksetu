"""
Real-World Places Provider Service for NagrikSetu Skill Development Microservice.

Supports:
1. Google Places API (New) - Places Text Search, Nearby Search, Details
2. OpenStreetMap (OSM / Overpass & Nominatim) Fallback Provider
3. Geocoding Service (Google Geocoding API with Nominatim OpenStreetMap fallback + Built-in Geo Cache)
4. Comprehensive Curated Real-World Training Centre Registry across major Indian cities & IT hubs
   (Bengaluru localities, Karnataka districts, and Major Metros across India)
   covering IT/Software, AI & Data Science, Vocational & NSDC, ITI, Polytechnic, and Core Engineering.
"""

import os
import math
import logging
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any, Optional, Tuple

from app.places_registry import INDIAN_GEOGRAPHIC_CACHE, AUTHENTIC_REAL_WORLD_CENTRES

logger = logging.getLogger("nagriksetu.places")

# Haversine distance calculator
def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class PlacesDiscoveryService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
        self.google_endpoint = "https://places.googleapis.com/v1/places:searchText"
        self.nominatim_endpoint = "https://nominatim.openstreetmap.org"

    def is_google_configured(self) -> bool:
        return bool(self.google_api_key and not self.google_api_key.startswith("AIzaSyDummy"))

    def geocode_address(self, address_or_landmark: str) -> Optional[Tuple[float, float, str]]:
        """
        Geocodes any city, locality, PIN code, landmark or address into (lat, lon, formatted_name).
        1. Fast, highly resilient built-in geographic dictionary (covers all Karnataka districts, Bengaluru localities, PIN codes, and Indian cities).
        2. Google Geocoding API (if key configured).
        3. OpenStreetMap Nominatim with retry protection.
        """
        clean_query = address_or_landmark.strip()
        if not clean_query:
            return None

        normalized = clean_query.lower()
        # Remove common punctuation
        normalized = normalized.replace(",", " ").replace(".", " ").replace("-", " ")
        normalized_key = " ".join(normalized.split())

        # 1. Exact or partial match in verified geographic cache
        if normalized_key in INDIAN_GEOGRAPHIC_CACHE:
            return INDIAN_GEOGRAPHIC_CACHE[normalized_key]

        # Check if any token or key is contained in geographic cache
        for key, geo_tuple in INDIAN_GEOGRAPHIC_CACHE.items():
            if key == normalized_key or (len(key) >= 4 and key in normalized_key):
                return geo_tuple

        # Check PIN codes directly (6 digits)
        tokens = normalized_key.split()
        for tok in tokens:
            if tok.isdigit() and len(tok) == 6 and tok in INDIAN_GEOGRAPHIC_CACHE:
                return INDIAN_GEOGRAPHIC_CACHE[tok]

        # 2. Try Google Geocoding if key configured
        if self.is_google_configured():
            try:
                g_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(clean_query)}&key={self.google_api_key}"
                req = urllib.request.Request(g_url)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("status") == "OK" and data.get("results"):
                        loc = data["results"][0]["geometry"]["location"]
                        formatted = data["results"][0]["formatted_address"]
                        return float(loc["lat"]), float(loc["lng"]), formatted
            except Exception as e:
                logger.warning(f"Google Geocoding failed, falling back to OSM: {e}")

        # 3. Fallback: OpenStreetMap Nominatim with Karnataka priority context
        try:
            target = clean_query
            lower_target = clean_query.lower()
            if "karnataka" not in lower_target and "india" not in lower_target:
                target = f"{clean_query}, Karnataka, India"
            elif "india" not in lower_target:
                target = f"{clean_query}, India"

            url = f"{self.nominatim_endpoint}/search?q={urllib.parse.quote(target)}&format=json&limit=1&addressdetails=1"
            req = urllib.request.Request(url, headers={"User-Agent": "NagrikSetu-SkillPlatform/2.0 (admin@nagriksetu.gov.in)"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    display = data[0].get("display_name", clean_query)
                    parts = [p.strip() for p in display.split(",")]
                    short_display = ", ".join(parts[:3])
                    # Store in dynamic cache for fast reuse
                    INDIAN_GEOGRAPHIC_CACHE[normalized_key] = (lat, lon, short_display)
                    return lat, lon, short_display
        except Exception as e:
            logger.warning(f"Nominatim geocoding error for '{clean_query}': {e}")

        return None

    def reverse_geocode(self, lat: float, lon: float) -> str:
        """
        Reverse geocodes coordinates (lat, lon) to a human-readable locality/address.
        1. Checks proximity against known geographic cache points.
        2. Queries Nominatim reverse geocoding API with fallback.
        """
        # Proximity check in verified cache (within ~3 km)
        closest_name = None
        min_d = 9999.0
        for name, entry in INDIAN_GEOGRAPHIC_CACHE.items():
            d = calculate_haversine(lat, lon, entry[0], entry[1])
            if d < min_d:
                min_d = d
                closest_name = entry[2]

        if min_d <= 3.0 and closest_name:
            return closest_name

        # Query Nominatim reverse endpoint
        try:
            url = f"{self.nominatim_endpoint}/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
            req = urllib.request.Request(url, headers={"User-Agent": "NagrikSetu-SkillPlatform/2.0 (admin@nagriksetu.gov.in)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                addr = data.get("address", {})
                loc_part = (
                    addr.get("suburb")
                    or addr.get("neighbourhood")
                    or addr.get("residential")
                    or addr.get("city_district")
                    or addr.get("town")
                    or addr.get("city")
                    or addr.get("state_district")
                )
                city_part = addr.get("city") or addr.get("county") or addr.get("state")
                if loc_part and city_part and loc_part != city_part:
                    return f"{loc_part}, {city_part}, Karnataka, India" if "karnataka" in str(addr.get("state", "")).lower() else f"{loc_part}, {city_part}, India"
                display = data.get("display_name", "")
                if display:
                    parts = [p.strip() for p in display.split(",")]
                    return ", ".join(parts[:3])
        except Exception as e:
            logger.warning(f"Reverse geocode error for ({lat}, {lon}): {e}")

        if closest_name and min_d <= 15.0:
            return f"Near {closest_name}"

        return f"Coordinates ({round(lat, 4)}, {round(lon, 4)})"

    def search_google_places(self, lat: float, lon: float, radius_km: float, query_text: str = "training institute") -> List[Dict[str, Any]]:
        """
        Searches Google Places API (New) for establishments matching training institutes within radius.
        """
        if not self.is_google_configured():
            return []

        results = []
        try:
            url = self.google_endpoint
            payload = {
                "textQuery": f"{query_text}",
                "locationBias": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lon},
                        "radius": float(radius_km * 1000.0)
                    }
                },
                "maxResultCount": 20
            }
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.google_api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.websiteUri,places.nationalPhoneNumber,places.primaryType"
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                places = data.get("places", [])
                for p in places:
                    loc = p.get("location", {})
                    p_lat = loc.get("latitude")
                    p_lon = loc.get("longitude")
                    if p_lat is None or p_lon is None:
                        continue
                    
                    dist = calculate_haversine(lat, lon, p_lat, p_lon)
                    if dist <= radius_km:
                        name = p.get("displayName", {}).get("text", "Training Centre")
                        place_id = p.get("id")
                        results.append({
                            "id": f"google-{place_id}",
                            "place_id": place_id,
                            "name": name,
                            "address": p.get("formattedAddress", "Address not specified"),
                            "latitude": p_lat,
                            "longitude": p_lon,
                            "distance_km": round(dist, 2),
                            "distance_label": f"{round(dist, 1)} km (approx. straight-line)",
                            "category": (p.get("primaryType") or "Skill Training").replace("_", " ").title(),
                            "phone": p.get("nationalPhoneNumber") or "N/A",
                            "website": p.get("websiteUri") or "",
                            "rating": p.get("rating"),
                            "review_count": p.get("userRatingCount"),
                            "source": "Google Places",
                            "source_type": "Google Places (Verified)",
                            "verification_status": "External listing"
                        })
        except Exception as e:
            logger.warning(f"Google Places API query error: {e}")

        return results

    def discover_training_centres(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        mysql_centres: Optional[List[Any]] = None,
        locality_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unified Real-World Places Discovery:
        1. Includes existing NagrikSetu MySQL accredited centres within radius.
        2. Queries Google Places API if configured with geographic location restriction.
        3. Merges verified real-world institute directory matching within radius.
        4. Calculates exact Haversine distance, filters within radius_km, deduplicates.
        5. Evaluates locality matching (is_exact_locality_match) against user-entered locality hint.
        6. Separates results into exact_locality_results and outside_locality_results.
        """
        all_found: Dict[str, Dict[str, Any]] = {}
        provider_statuses: Dict[str, str] = {
            "official_mysql": "OK",
            "government_registry": "OK",
            "google_places": "OK" if self.is_google_configured() else "SKIPPED_UNCONFIGURED"
        }

        # 1. Include verified NagrikSetu centres from MySQL
        if mysql_centres:
            for c in mysql_centres:
                c_lat = getattr(c, "latitude", None)
                c_lon = getattr(c, "longitude", None)
                if c_lat is not None and c_lon is not None:
                    dist = calculate_haversine(lat, lon, float(c_lat), float(c_lon))
                    if dist <= radius_km:
                        c_id = getattr(c, "code", str(getattr(c, "id")))
                        all_found[f"ns-{c_id}"] = {
                            "id": f"ns-{c_id}",
                            "place_id": f"ns-{c_id}",
                            "code": getattr(c, "code", ""),
                            "name": getattr(c, "name", ""),
                            "address": getattr(c, "address", ""),
                            "locality": getattr(c, "district", ""),
                            "district": getattr(c, "district", ""),
                            "state": getattr(c, "state", ""),
                            "latitude": float(c_lat),
                            "longitude": float(c_lon),
                            "distance_km": round(dist, 2),
                            "distance_label": f"{round(dist, 1)} km (approx. straight-line)",
                            "category": "NagrikSetu Accredited Centre",
                            "phone": getattr(c, "contact_phone", "N/A"),
                            "email": getattr(c, "contact_email", ""),
                            "website": "https://nagriksetu.gov.in/skill",
                            "facilities": getattr(c, "facilities", "Computer Lab, Audio-Visual Classroom"),
                            "delivery_modes": getattr(c, "delivery_modes", "Offline, Hybrid"),
                            "source": "NagrikSetu Registry",
                            "source_type": "Official Government Accredited Centre",
                            "verification_status": "Officially verified",
                            "is_official_centre": True
                        }

        # 2. Try Google Places if configured
        if self.is_google_configured():
            try:
                for query in ["skill development centre", "vocational training institute", "IT training institute"]:
                    res = self.search_google_places(lat, lon, radius_km, query)
                    for item in res:
                        item["is_official_centre"] = False
                        key = item.get("place_id") or item["name"].lower().strip()
                        if key not in all_found:
                            all_found[key] = item
            except Exception as e:
                logger.warning(f"Google Places search error: {e}")
                provider_statuses["google_places"] = "FAILED"

        # 3. Merge authentic real-world verified institute registry (fallback & guaranteed coverage)
        for inst in AUTHENTIC_REAL_WORLD_CENTRES:
            dist = calculate_haversine(lat, lon, inst["latitude"], inst["longitude"])
            if dist <= radius_km:
                key = inst["name"].lower().strip()
                if key not in all_found:
                    entry = {
                        "id": inst["id"],
                        "place_id": inst["id"],
                        "name": inst["name"],
                        "address": inst["address"],
                        "locality": inst["locality"],
                        "district": inst.get("district", ""),
                        "city": inst["city"],
                        "state": inst["state"],
                        "latitude": inst["latitude"],
                        "longitude": inst["longitude"],
                        "distance_km": round(dist, 2),
                        "distance_label": f"{round(dist, 1)} km (approx. straight-line)",
                        "category": inst["category"],
                        "phone": inst.get("phone", "N/A"),
                        "website": inst.get("website", ""),
                        "facilities": inst.get("facilities", "Equipped Classroom, Labs"),
                        "source": inst.get("source", "Government Training Directory"),
                        "source_type": inst.get("source_type", "Government Accredited Institute"),
                        "verification_status": inst.get("verification_status", "Officially verified"),
                        "is_official_centre": False
                    }
                    # Only include rating/review_count if genuinely provided
                    if "rating" in inst:
                        entry["rating"] = inst["rating"]
                    if "review_count" in inst:
                        entry["review_count"] = inst["review_count"]
                    all_found[key] = entry

        # 4. Determine locality matching tokens with spelling & alias normalization
        hint_clean = (locality_hint or "").strip().lower()
        stopwords = {"bengaluru", "bangalore", "karnataka", "india", "road", "main", "cross", "phase", "near", "opp", "opposite", "layout", "park", "nagar"}
        raw_tokens = [t.strip(",. ") for t in hint_clean.replace(",", " ").split() if len(t.strip(",. ")) >= 3]
        
        # Karnataka name variation map
        alias_map = {
            "mysore": "mysuru",
            "mysuru": "mysore",
            "hubli": "hubballi",
            "hubballi": "hubli",
            "belgaum": "belagavi",
            "belagavi": "belgaum",
            "gulbarga": "kalaburagi",
            "kalaburagi": "gulbarga",
            "bellary": "ballari",
            "ballari": "bellary",
            "bijapur": "vijayapura",
            "vijayapura": "bijapur",
            "shimoga": "shivamogga",
            "shivamogga": "shimoga",
            "mangalore": "mangaluru",
            "mangaluru": "mangalore",
            "tumkur": "tumakuru",
            "tumakuru": "tumkur",
            "chikmagalur": "chikkamagaluru",
            "chikkamagaluru": "chikmagalur",
            "whitefield": "whitefield",
            "kengeri": "kengeri",
            "marathahalli": "marathahalli",
            "electronic": "electronic",
            "indiranagar": "indiranagar",
            "rajajinagar": "rajajinagar",
            "jayanagar": "jayanagar",
            "malleswaram": "malleshwaram",
            "malleshwaram": "malleswaram"
        }

        specific_tokens = set()
        for tok in raw_tokens:
            if tok not in stopwords:
                specific_tokens.add(tok)
                if tok in alias_map:
                    specific_tokens.add(alias_map[tok])

        if not specific_tokens and raw_tokens:
            specific_tokens = set(raw_tokens)

        exact_results = []
        outside_results = []

        for item in all_found.values():
            loc_text = f"{item.get('locality', '')} {item.get('address', '')} {item.get('district', '')} {item.get('city', '')} {item.get('name', '')}".lower()
            
            is_exact = False
            if specific_tokens:
                for token in specific_tokens:
                    if token in loc_text:
                        is_exact = True
                        break
            
            item["is_exact_locality_match"] = is_exact
            if is_exact:
                exact_results.append(item)
            else:
                outside_results.append(item)

        # Sort both lists by distance ascending
        exact_results.sort(key=lambda x: x["distance_km"])
        outside_results.sort(key=lambda x: x["distance_km"])

        # Combined results list has exact locality matches first, followed by nearby outside locality
        combined_results = exact_results + outside_results

        return {
            "status": "success",
            "provider": "Google Places (New)" if self.is_google_configured() else "Government & Accredited Institutions Registry (DGT / KSDC / NSDC)",
            "google_configured": self.is_google_configured(),
            "provider_statuses": provider_statuses,
            "search_coordinates": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "locality_hint": locality_hint,
            "count": len(combined_results),
            "exact_count": len(exact_results),
            "outside_count": len(outside_results),
            "exact_locality_results": exact_results,
            "outside_locality_results": outside_results,
            "results": combined_results
        }

places_service = PlacesDiscoveryService()
