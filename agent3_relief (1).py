"""
SAHARA - Agent 3: Relief Coordinator
Finds nearest hospitals/shelters, suggests evacuation advice, generates SOS report.
Uses OpenStreetMap (Overpass API) — completely free, no key needed.
"""

import requests
import json
import os
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")


def get_nearby_facilities(lat: float, lon: float, disaster_type: str) -> dict:
    """
    Queries OpenStreetMap Overpass API for nearby hospitals, shelters, pharmacies.
    No API key required.
    """
    # Search radius in meters (5km)
    radius = 5000

    # Query hospitals AND pharmacies AND emergency services
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      node["amenity"="clinic"](around:{radius},{lat},{lon});
      node["amenity"="pharmacy"](around:{radius},{lat},{lon});
      node["amenity"="shelter"](around:{radius},{lat},{lon});
      node["emergency"="assembly_point"](around:{radius},{lat},{lon});
    );
    out body;
    """

    facilities = {
        "hospitals":  [],
        "pharmacies": [],
        "shelters":   []
    }

    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": overpass_query},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        for element in data.get("elements", []):
            tags     = element.get("tags", {})
            name     = tags.get("name", "Unnamed Facility")
            amenity  = tags.get("amenity", "")
            fac_lat  = element.get("lat")
            fac_lon  = element.get("lon")

            # Calculate rough distance (simple approximation)
            dist_km = round(
                ((fac_lat - lat)**2 + (fac_lon - lon)**2)**0.5 * 111, 2
            )

            entry = {
                "name":    name,
                "lat":     fac_lat,
                "lon":     fac_lon,
                "dist_km": dist_km,
                "phone":   tags.get("phone", tags.get("contact:phone", "N/A")),
                "maps_url": f"https://www.openstreetmap.org/?mlat={fac_lat}&mlon={fac_lon}#map=16/{fac_lat}/{fac_lon}"
            }

            if amenity in ["hospital", "clinic"]:
                facilities["hospitals"].append(entry)
            elif amenity == "pharmacy":
                facilities["pharmacies"].append(entry)
            elif amenity in ["shelter", "assembly_point"]:
                facilities["shelters"].append(entry)

        # Sort each list by distance
        for key in facilities:
            facilities[key].sort(key=lambda x: x["dist_km"])
            facilities[key] = facilities[key][:3]  # Top 3 nearest only

    except Exception as e:
        print(f"⚠️  Overpass API error: {e}")

    return facilities


EVACUATION_ADVICE = {
    "flood":    "🏃 Move to higher ground immediately — do not wait.\n💧 Avoid walking in floodwater — even shallow water can knock you over.\n🔦 Keep torch and phone fully charged.\n📞 Call 112 if trapped and cannot move.\n❌ Do NOT drive through flooded roads.",
    "heatwave": "🏠 Stay indoors during 11am-4pm — peak danger hours.\n💧 Drink water every 20 minutes even if not thirsty.\n🧊 Apply cold compress to neck, wrists, and forehead.\n📞 Call 108 immediately if someone collapses.\n❌ Do NOT exercise or go outdoors in peak heat.",
    "fire":     "🚪 Evacuate immediately — use stairs, NOT the lift.\n👃 Cover mouth and nose with a wet cloth.\n🔽 Stay low to the ground — smoke rises.\n📞 Call 101 (Fire Brigade) immediately.\n❌ Do NOT go back inside for any belongings.",
    "storm":    "🏠 Stay indoors and away from windows.\n⚡ Unplug all electronics — lightning risk.\n🌊 Move away from rivers, drains, and the coast.\n📞 Call 112 for emergencies.\n❌ Do NOT shelter under trees or near metal structures.",
    "normal":   "✅ No evacuation needed — stay alert for updates.\n📻 Monitor local news and weather alerts.\n🔦 Keep an emergency kit ready.\n📞 Save 112 on speed dial.\n❌ Do NOT ignore official weather warnings."
}

def get_evacuation_advice(city: str, disaster_type: str, urgency: str) -> str:
    return EVACUATION_ADVICE.get(disaster_type, EVACUATION_ADVICE["normal"])


def generate_sos_report(env_report: dict, triage_result: dict,
                         facilities: dict, evacuation_advice: str) -> str:
    """
    Generates a plain-text SOS report that can be shared via WhatsApp/SMS.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    city      = env_report["city"]
    disaster  = env_report["disaster_type"].upper()
    severity  = env_report["severity"]
    urgency   = triage_result.get("urgency", "Unknown")
    symptoms  = triage_result.get("symptoms", "Not provided")

    nearest_hospital = (
        facilities["hospitals"][0]["name"]
        if facilities["hospitals"]
        else "Search on Google Maps"
    )
    hospital_dist = (
        f"{facilities['hospitals'][0]['dist_km']} km"
        if facilities["hospitals"]
        else "Unknown"
    )

    report = f"""
╔══════════════════════════════════════════╗
║         SAHARA - SOS REPORT              ║
╚══════════════════════════════════════════╝

🕐 Generated: {timestamp}
📍 Location:  {city}, India
⚠️  Disaster:  {disaster} (Severity: {severity}/10)
🚨 Urgency:   {urgency}

── SURVIVOR STATUS ──────────────────────────
Symptoms: {symptoms}

── NEAREST HELP ─────────────────────────────
🏥 Hospital: {nearest_hospital} ({hospital_dist})
"""
    if facilities["hospitals"]:
        h = facilities["hospitals"][0]
        report += f"   📞 Phone: {h['phone']}\n"
        report += f"   🗺️  Map:   {h['maps_url']}\n"

    if facilities["pharmacies"]:
        p = facilities["pharmacies"][0]
        report += f"\n💊 Pharmacy: {p['name']} ({p['dist_km']} km)\n"

    report += f"""
── EVACUATION ADVICE ────────────────────────
{evacuation_advice}

── EMERGENCY NUMBERS (INDIA) ────────────────
🆘 National Emergency:  112
🚑 Ambulance:           108
🚒 Fire:                101
🌊 NDRF Helpline:       011-24363260
🏥 Health Helpline:     104

── SHARE THIS REPORT ────────────────────────
Forward this message to rescuers or family.
Powered by SAHARA AI | HiGen Labs Agentathon
╚══════════════════════════════════════════╝
"""
    return report


def run_relief_coordinator(env_report: dict, triage_result: dict) -> dict:
    """
    Main entry point for Agent 3.
    """
    print("🆘 SAHARA - Relief Coordinator")
    print("─" * 45)

    result = {
        "facilities":        {},
        "evacuation_advice": "",
        "sos_report":        "",
        "error":             None
    }

    lat = env_report.get("weather", {}).get("lat")
    lon = env_report.get("weather", {}).get("lon")

    # ── Step 1: Find nearby facilities ──────────────────────────────────────
    if lat and lon:
        print(f"🗺️  Searching for facilities near {env_report['city']}...")
        facilities = get_nearby_facilities(lat, lon, env_report["disaster_type"])
        result["facilities"] = facilities

        print(f"   ✅ Found {len(facilities['hospitals'])} hospitals nearby")
        print(f"   ✅ Found {len(facilities['pharmacies'])} pharmacies nearby")
        print(f"   ✅ Found {len(facilities['shelters'])} shelters nearby")

        if facilities["hospitals"]:
            h = facilities["hospitals"][0]
            print(f"\n🏥 Nearest Hospital: {h['name']} — {h['dist_km']} km")
            print(f"   🗺️  {h['maps_url']}")
    else:
        print("⚠️  Coordinates unavailable, skipping facility search.")
        facilities = {"hospitals": [], "pharmacies": [], "shelters": []}

    # ── Step 2: Get evacuation advice ────────────────────────────────────────
    print("\n📋 Generating evacuation advice...")
    evacuation_advice        = get_evacuation_advice(
        city          = env_report["city"],
        disaster_type = env_report["disaster_type"],
        urgency       = triage_result.get("urgency", "Unknown")
    )
    result["evacuation_advice"] = evacuation_advice
    print(evacuation_advice)

    # ── Step 3: Generate SOS report ──────────────────────────────────────────
    print("\n📄 Generating shareable SOS report...")
    sos_report        = generate_sos_report(
        env_report        = env_report,
        triage_result     = triage_result,
        facilities        = facilities,
        evacuation_advice = evacuation_advice
    )
    result["sos_report"] = sos_report

    print("\n" + sos_report)
    print("✅ Agent 3 complete. SAHARA response cycle finished.\n")

    # Save SOS report to file
    filename = f"SOS_{env_report['city']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w") as f:
        f.write(sos_report)
    print(f"💾 SOS report saved: {filename}")

    return result


# ─── DEMO RUN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mock_env = {
        "city":         "Silchar",
        "disaster_type":"flood",
        "severity":     8,
        "health_risks": ["Leptospirosis", "Cholera", "Skin infections"],
        "weather":      {"lat": 24.8333, "lon": 92.7789}
    }
    mock_triage = {
        "symptoms": "fever and leg pain",
        "urgency":  "High"
    }
    run_relief_coordinator(mock_env, mock_triage)
