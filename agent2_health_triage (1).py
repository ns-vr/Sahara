"""
SAHARA - Agent 2: Health Triage Agent
Works with OR without Anthropic API key.
If no key: uses smart disaster-aware rule-based triage.
If key present: uses Claude for richer analysis.
"""

import requests
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

# ─── RULE-BASED TRIAGE (no API needed) ───────────────────────────────────────
SYMPTOM_RULES = {
    "flood": {
        "keywords": {
            "fever":    ("Leptospirosis or waterborne infection",  "High"),
            "leg pain": ("Leptospirosis (flood water exposure)",   "High"),
            "diarrhea": ("Cholera or waterborne disease",          "High"),
            "vomiting": ("Waterborne infection / cholera",         "High"),
            "rash":     ("Skin infection from contaminated water", "Medium"),
            "eye":      ("Leptospirosis — red eyes are a key sign","High"),
            "breathe":  ("Mold/respiratory infection",             "Medium"),
            "wound":    ("Infected wound from floodwater",         "High"),
        },
        "default":    ("General flood-related illness",            "Medium"),
        "steps": [
            "Do NOT drink tap or floodwater — only sealed bottled water",
            "Clean any wounds immediately with clean water and bandage them",
            "Move to dry elevated ground if still in flooded area",
            "Take oral rehydration salts (ORS) if vomiting or diarrhea",
        ],
        "red_flags": ["difficulty breathing", "chest pain", "unconsciousness", "blood in stool"],
        "warning": "Leptospirosis from floodwater is life-threatening if untreated — see a doctor within 24hrs"
    },
    "heatwave": {
        "keywords": {
            "headache": ("Heat exhaustion",                        "Medium"),
            "dizzy":    ("Heat exhaustion / early heat stroke",    "High"),
            "faint":    ("Heat stroke — EMERGENCY",                "EMERGENCY"),
            "no sweat": ("Heat stroke — body cooling failed",      "EMERGENCY"),
            "confused": ("Heat stroke affecting brain",            "EMERGENCY"),
            "cramp":    ("Heat cramps from dehydration",           "Low"),
            "nausea":   ("Heat exhaustion",                        "Medium"),
        },
        "default":    ("Heat-related illness",                     "Medium"),
        "steps": [
            "Move to shade or air-conditioned room IMMEDIATELY",
            "Drink cool water slowly — small sips every few minutes",
            "Apply wet cloth to neck, armpits, and forehead",
            "Loosen or remove tight clothing",
        ],
        "red_flags": ["stopped sweating", "confusion", "fainting", "temperature above 40C"],
        "warning": "Heat stroke is fatal — if the person stops sweating and becomes confused, call 108 NOW"
    },
    "fire": {
        "keywords": {
            "cough":   ("Smoke inhalation",                        "Medium"),
            "breathe": ("Smoke inhalation / lung irritation",      "High"),
            "chest":   ("Carbon monoxide or smoke inhalation",     "High"),
            "eye":     ("Eye irritation from smoke",               "Low"),
            "burn":    ("Burn injury",                             "High"),
            "dizzy":   ("Carbon monoxide poisoning",               "High"),
            "headache":("Carbon monoxide poisoning",               "Medium"),
        },
        "default":    ("Smoke/fire exposure effects",              "Medium"),
        "steps": [
            "Get to fresh air immediately — away from smoke",
            "Do NOT go back inside the building",
            "For burns: cool with running water 10 mins, do NOT use ice",
            "Cover mouth with wet cloth if still near smoke",
        ],
        "red_flags": ["difficulty breathing", "blue lips", "loss of consciousness", "severe burns"],
        "warning": "Carbon monoxide is odorless — if multiple people feel dizzy, evacuate immediately"
    },
    "storm": {
        "keywords": {
            "wound":   ("Debris injury / laceration",              "Medium"),
            "bleeding":("Trauma from debris",                      "High"),
            "head":    ("Head injury from debris",                 "High"),
            "cold":    ("Hypothermia risk from exposure",          "Medium"),
            "shiver":  ("Hypothermia",                             "Medium"),
            "chest":   ("Trauma injury",                           "High"),
        },
        "default":    ("Storm-related injury",                     "Medium"),
        "steps": [
            "Stay indoors — do not go outside until storm passes",
            "Apply pressure to any bleeding wounds with clean cloth",
            "Stay warm and dry — hypothermia risk is high",
            "Do not touch downed power lines under any circumstances",
        ],
        "red_flags": ["severe bleeding", "head injury", "unconsciousness", "difficulty breathing"],
        "warning": "Downed power lines after storms are live and fatal — stay 10 meters away"
    },
    "normal": {
        "keywords": {},
        "default":    ("General illness — no active disaster",     "Low"),
        "steps": [
            "Rest and stay hydrated",
            "Monitor symptoms for 24 hours",
            "Visit a local clinic if symptoms worsen",
        ],
        "red_flags": ["high fever above 103F", "difficulty breathing", "chest pain"],
        "warning": "No active disaster detected — standard medical advice applies"
    }
}


def rule_based_triage(disaster_type: str, symptoms: str, health_risks: list) -> str:
    symptoms_lower = symptoms.lower()
    rules          = SYMPTOM_RULES.get(disaster_type, SYMPTOM_RULES["normal"])

    condition, urgency = rules["default"]
    for keyword, (cond, urg) in rules["keywords"].items():
        if keyword in symptoms_lower:
            condition = cond
            urgency   = urg
            if urg == "EMERGENCY":
                break

    steps_text     = "\n".join(f"{i+1}. {s}" for i, s in enumerate(rules["steps"]))
    red_flags_text = "\n".join(f"- {r}" for r in rules["red_flags"])

    return f"""Likely Condition: {condition}
Urgency Level: {urgency}

IMMEDIATE STEPS:
{steps_text}

SEEK EMERGENCY CARE IF:
{red_flags_text}

DISASTER-SPECIFIC WARNING:
{rules["warning"]}"""


def build_triage_prompt(city, disaster_type, severity, health_risks, symptoms):
    risks_text = "\n".join(f"- {r}" for r in health_risks)
    return f"""You are SAHARA's Health Triage Agent — an AI first responder during disasters.

DISASTER CONTEXT:
- Location: {city}, India
- Disaster: {disaster_type.upper()} (severity {severity}/10)
- Known health risks:
{risks_text}

SURVIVOR SYMPTOMS: "{symptoms}"

Respond in this exact format:
Likely Condition: [assessment]
Urgency Level: [Low / Medium / High / EMERGENCY]

IMMEDIATE STEPS:
1. [step]
2. [step]
3. [step]
4. [step]

SEEK EMERGENCY CARE IF:
- [red flag]
- [red flag]

DISASTER-SPECIFIC WARNING:
[one critical warning for {disaster_type}]

Be calm, clear, and direct. Give real actionable steps first."""


def run_health_triage_agent(env_report: dict, symptoms: str) -> dict:
    print("Health Triage Agent")
    print("-" * 45)
    print(f"City: {env_report['city']}")
    print(f"Disaster: {env_report['disaster_type'].upper()}")
    print(f"Symptoms: {symptoms}\n")

    triage_result = {
        "symptoms":     symptoms,
        "urgency":      None,
        "raw_response": None,
        "error":        None
    }

    use_ai = (ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "YOUR_ANTHROPIC_API_KEY")

    if use_ai:
        prompt = build_triage_prompt(
            env_report["city"], env_report["disaster_type"],
            env_report["severity"], env_report["health_risks"], symptoms
        )
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json"
                },
                json={
                    "model":      "claude-sonnet-4-20250514",
                    "max_tokens": 800,
                    "messages":   [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            resp.raise_for_status()
            ai_response = resp.json()["content"][0]["text"]
        except Exception as e:
            print(f"AI failed, using rule-based: {e}")
            ai_response = rule_based_triage(
                env_report["disaster_type"], symptoms, env_report["health_risks"]
            )
    else:
        print("No Anthropic key — using disaster-aware rule-based triage\n")
        ai_response = rule_based_triage(
            env_report["disaster_type"], symptoms, env_report["health_risks"]
        )

    triage_result["raw_response"] = ai_response

    for level in ["EMERGENCY", "High", "Medium", "Low"]:
        if level.upper() in ai_response.upper():
            triage_result["urgency"] = level
            break

    print("=" * 45)
    print(ai_response)
    print("=" * 45)
    print("Agent 2 complete.\n")

    return triage_result


if __name__ == "__main__":
    mock_env = {
        "city": "Silchar", "disaster_type": "flood", "severity": 8,
        "health_risks": ["Leptospirosis", "Cholera", "Skin infections"]
    }
    symptoms = input("Describe symptoms: ").strip() or "fever and leg pain since yesterday"
    result = run_health_triage_agent(mock_env, symptoms)
    print(f"\nUrgency: {result['urgency']}")
