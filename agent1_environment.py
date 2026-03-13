"""
SAHARA - Agent 1: Environment Scanner
Detects disaster type, severity, air quality, and health risks for any Indian city.
"""

import requests
import os
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
AQICN_API_KEY       = os.getenv("AQICN_API_KEY", "YOUR_AQICN_API_KEY")
# Get free keys at:
#   OpenWeather → https://openweathermap.org/api
#   AQICN       → https://aqicn.org/data-platform/token/


# ─── DISASTER HEALTH RISK MAP ─────────────────────────────────────────────────
# Maps disaster type → known health risks for Agent 2 to use
DISASTER_HEALTH_RISKS = {
    "flood": [
        "Leptospirosis (from contaminated water)",
        "Cholera and waterborne diseases",
        "Skin infections from stagnant water",
        "Respiratory infections from mold",
        "Mental health trauma / stress"
    ],
    "heatwave": [
        "Heat stroke and heat exhaustion",
        "Severe dehydration",
        "Cardiovascular strain",
        "Kidney stress from dehydration",
        "Worsened respiratory conditions"
    ],
    "fire": [
        "Smoke inhalation and lung damage",
        "Carbon monoxide poisoning",
        "Eye and skin irritation",
        "Asthma and COPD flare-ups",
        "Burns and trauma"
    ],
    "storm": [
        "Physical trauma from debris",
        "Hypothermia from exposure",
        "Waterborne disease from flooding",
        "Mental health trauma",
        "Wound infections"
    ],
    "normal": [
        "No active disaster detected",
        "Standard health precautions apply"
    ]
}

AQI_HEALTH_ADVICE = {
    (0, 50):    ("Good",           "✅ Air is clean. No precautions needed."),
    (51, 100):  ("Moderate",       "⚠️ Sensitive individuals should limit outdoor activity."),
    (101, 150): ("Unhealthy (SG)", "🟠 Children and elderly should stay indoors."),
    (151, 200): ("Unhealthy",      "🔴 Everyone should reduce outdoor exposure. Wear N95 mask."),
    (201, 300): ("Very Unhealthy", "🚨 Stay indoors. Seal windows. Medical attention if breathing issues."),
    (301, 500): ("Hazardous",      "☠️ EMERGENCY. Do not go outside. Evacuate if possible.")
}


# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def get_aqi_category(aqi_value):
    for (low, high), (label, advice) in AQI_HEALTH_ADVICE.items():
        if low <= aqi_value <= high:
            return label, advice
    return "Unknown", "AQI data unavailable."


def detect_disaster_from_weather(weather_data):
    """
    Analyzes raw weather data and returns disaster type + severity score (0-10).
    """
    disaster_type = "normal"
    severity      = 0
    reasons       = []

    weather_id   = weather_data.get("weather_id", 800)
    temp_celsius = weather_data.get("temp", 25)
    wind_speed   = weather_data.get("wind_speed", 0)   # m/s
    rain_1h      = weather_data.get("rain_1h", 0)      # mm
    humidity     = weather_data.get("humidity", 50)
    description  = weather_data.get("description", "").lower()

    # ── Flood Detection ──
    if rain_1h > 50 or weather_id in range(500, 532):
        disaster_type = "flood"
        if rain_1h > 100:
            severity = 9
            reasons.append(f"Extreme rainfall: {rain_1h}mm/hr")
        elif rain_1h > 50:
            severity = 7
            reasons.append(f"Heavy rainfall: {rain_1h}mm/hr")
        else:
            severity = 5
            reasons.append(f"Rain detected: {rain_1h}mm/hr")

    # ── Heatwave Detection ──
    elif temp_celsius >= 42:
        disaster_type = "heatwave"
        severity      = 9
        reasons.append(f"Extreme heat: {temp_celsius}°C")
    elif temp_celsius >= 38:
        disaster_type = "heatwave"
        severity      = 6
        reasons.append(f"High heat: {temp_celsius}°C")

    # ── Storm/Cyclone Detection ──
    elif wind_speed > 20 or weather_id in range(900, 910):
        disaster_type = "storm"
        severity      = min(10, int(wind_speed / 3))
        reasons.append(f"High winds: {wind_speed} m/s")

    # ── Fire Risk (via smoke/haze weather codes) ──
    elif weather_id in [711, 721, 731, 741, 751, 761, 762]:
        disaster_type = "fire"
        severity      = 6
        reasons.append(f"Smoke/haze detected: {description}")

    return disaster_type, severity, reasons


# ─── MAIN AGENT FUNCTION ──────────────────────────────────────────────────────

def run_environment_agent(city: str) -> dict:
    """
    Main entry point for Agent 1.
    Returns a structured environment report for the given city.
    """
    print(f"\n🌍 SAHARA - Environment Scanner")
    print(f"📍 Scanning: {city}")
    print("─" * 45)

    report = {
        "city":          city,
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "disaster_type": "normal",
        "severity":      0,
        "reasons":       [],
        "aqi":           None,
        "aqi_label":     None,
        "aqi_advice":    None,
        "weather":       {},
        "health_risks":  [],
        "error":         None
    }

    # ── Step 1: Fetch Weather Data ──────────────────────────────────────────
    try:
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},IN"
            f"&appid={OPENWEATHER_API_KEY}"
            f"&units=metric"
        )
        resp = requests.get(weather_url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        weather_data = {
            "temp":        raw["main"]["temp"],
            "feels_like":  raw["main"]["feels_like"],
            "humidity":    raw["main"]["humidity"],
            "wind_speed":  raw["wind"]["speed"],
            "description": raw["weather"][0]["description"],
            "weather_id":  raw["weather"][0]["id"],
            "rain_1h":     raw.get("rain", {}).get("1h", 0),
            "lat":         raw["coord"]["lat"],
            "lon":         raw["coord"]["lon"]
        }
        report["weather"] = weather_data

        print(f"🌡️  Temp: {weather_data['temp']}°C  |  Humidity: {weather_data['humidity']}%")
        print(f"💨 Wind: {weather_data['wind_speed']} m/s  |  {weather_data['description'].title()}")
        if weather_data["rain_1h"]:
            print(f"🌧️  Rainfall (last 1hr): {weather_data['rain_1h']} mm")

    except Exception as e:
        report["error"] = f"Weather API error: {e}"
        print(f"❌ Weather fetch failed: {e}")
        return report

    # ── Step 2: Fetch AQI Data ──────────────────────────────────────────────
    try:
        aqi_url = f"https://api.waqi.info/feed/{city}/?token={AQICN_API_KEY}"
        aqi_resp = requests.get(aqi_url, timeout=10)
        aqi_raw  = aqi_resp.json()

        if aqi_raw.get("status") == "ok":
            aqi_value            = aqi_raw["data"]["aqi"]
            aqi_label, aqi_advice = get_aqi_category(aqi_value)
            report["aqi"]        = aqi_value
            report["aqi_label"]  = aqi_label
            report["aqi_advice"] = aqi_advice
            print(f"💨 AQI: {aqi_value} ({aqi_label})")
        else:
            print("⚠️  AQI data unavailable for this city.")

    except Exception as e:
        print(f"⚠️  AQI fetch skipped: {e}")

    # ── Step 3: Detect Disaster ─────────────────────────────────────────────
    disaster_type, severity, reasons = detect_disaster_from_weather(weather_data)
    report["disaster_type"] = disaster_type
    report["severity"]      = severity
    report["reasons"]       = reasons
    report["health_risks"]  = DISASTER_HEALTH_RISKS.get(disaster_type, [])

    # ── Step 4: Print Summary ───────────────────────────────────────────────
    print("\n" + "═" * 45)
    if disaster_type == "normal":
        print("✅ STATUS: No active disaster detected.")
    else:
        emoji = {"flood": "🌊", "heatwave": "🔥", "fire": "🔥", "storm": "🌪️"}.get(disaster_type, "⚠️")
        print(f"{emoji} DISASTER DETECTED: {disaster_type.upper()}")
        print(f"📊 Severity: {severity}/10")
        for r in reasons:
            print(f"   → {r}")

    if report["aqi_advice"]:
        print(f"\n🫁 Air Quality: {report['aqi_advice']}")

    print(f"\n⚕️  Health Risks for {disaster_type.title()}:")
    for risk in report["health_risks"]:
        print(f"   • {risk}")

    print("═" * 45)
    print("✅ Agent 1 complete. Passing to Health Triage Agent...\n")

    return report


# ─── DEMO RUN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with any Indian city
    city = input("Enter city name (e.g. Silchar, Chennai, Mumbai): ").strip()
    if not city:
        city = "Chennai"

    result = run_environment_agent(city)

    # This dict gets passed directly to Agent 2
    print("\n📦 Data package ready for Agent 2:")
    print(f"   City: {result['city']}")
    print(f"   Disaster: {result['disaster_type']} (severity {result['severity']}/10)")
    print(f"   Health risks identified: {len(result['health_risks'])}")
