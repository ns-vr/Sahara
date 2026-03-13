"""
SAHARA - Agent 2: Health Triage Agent
Takes disaster context from Agent 1 + user symptoms → gives prioritized medical guidance.
Uses Claude API for intelligent, context-aware triage.
"""

import requests
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")
# Get your key at https://console.anthropic.com


def build_triage_prompt(city: str, disaster_type: str, severity: int,
                         health_risks: list, symptoms: str) -> str:
    """
    Builds a precise prompt that gives Claude full disaster context
    so it can give disaster-specific (not generic) medical advice.
    """
    risks_text = "\n".join(f"- {r}" for r in health_risks)

    return f"""You are SAHARA's Health Triage Agent — an AI medical first responder deployed during disaster situations.

CURRENT DISASTER CONTEXT:
- Location: {city}, India
- Disaster Type: {disaster_type.upper()}
- Severity: {severity}/10
- Known health risks for this disaster:
{risks_text}

SURVIVOR'S REPORTED SYMPTOMS:
"{symptoms}"

YOUR TASK:
1. Cross-reference the symptoms with the SPECIFIC disaster type and its known health risks
2. Identify the most likely condition(s) — be specific, not generic
3. Give clear, prioritized first aid steps they can do RIGHT NOW
4. Flag any RED FLAG symptoms that mean they need emergency care immediately
5. Give ONE key warning specific to this disaster type

RESPONSE FORMAT (use exactly this structure):
🔍 LIKELY CONDITION: [your assessment]
⚡ URGENCY LEVEL: [Low / Medium / High / EMERGENCY]

🩺 IMMEDIATE STEPS:
1. [step]
2. [step]
3. [step]

🚨 SEEK EMERGENCY CARE IF:
- [red flag symptom]
- [red flag symptom]

⚠️ DISASTER-SPECIFIC WARNING:
[One critical warning specific to {disaster_type}]

Keep language simple. This person may be scared and in a disaster zone. Be calm, clear, and direct.
Do NOT say "consult a doctor" as your main advice — give real actionable steps first."""


def run_health_triage_agent(env_report: dict, symptoms: str) -> dict:
    """
    Main entry point for Agent 2.
    Takes the environment report from Agent 1 + user symptoms.
    Returns triage assessment.
    """
    print("🏥 SAHARA - Health Triage Agent")
    print("─" * 45)
    print(f"📍 City: {env_report['city']}")
    print(f"⚠️  Disaster context: {env_report['disaster_type'].upper()} (severity {env_report['severity']}/10)")
    print(f"💬 Symptoms: {symptoms}")
    print("\n🤖 Analyzing with disaster-aware AI triage...\n")

    triage_result = {
        "symptoms":    symptoms,
        "assessment":  None,
        "urgency":     None,
        "raw_response": None,
        "error":       None
    }

    # Build the disaster-aware prompt
    prompt = build_triage_prompt(
        city         = env_report["city"],
        disaster_type= env_report["disaster_type"],
        severity     = env_report["severity"],
        health_risks = env_report["health_risks"],
        symptoms     = symptoms
    )

    # Call Claude API
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json"
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        ai_response = data["content"][0]["text"]
        triage_result["raw_response"] = ai_response

        # Extract urgency level from response
        for level in ["EMERGENCY", "High", "Medium", "Low"]:
            if level.upper() in ai_response.upper():
                triage_result["urgency"] = level
                break

        print("═" * 45)
        print(ai_response)
        print("═" * 45)
        print("✅ Agent 2 complete. Passing to Relief Coordinator...\n")

    except Exception as e:
        triage_result["error"] = str(e)
        print(f"❌ Triage agent error: {e}")

        # Fallback: basic advice without AI
        fallback = f"""
⚠️ AI triage temporarily unavailable. Basic guidance for {env_report['disaster_type']} survivors:

IMMEDIATE STEPS:
1. Move to higher ground if flooding
2. Do not drink tap/flood water
3. Cover wounds to prevent infection
4. Stay calm and conserve energy

Seek emergency care if: difficulty breathing, chest pain, loss of consciousness.
        """
        triage_result["raw_response"] = fallback
        print(fallback)

    return triage_result


# ─── DEMO RUN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Simulate Agent 1 output for testing Agent 2 standalone
    mock_env_report = {
        "city":         "Silchar",
        "disaster_type":"flood",
        "severity":     8,
        "health_risks": [
            "Leptospirosis (from contaminated water)",
            "Cholera and waterborne diseases",
            "Skin infections from stagnant water",
            "Respiratory infections from mold",
            "Mental health trauma / stress"
        ]
    }

    symptoms = input("Describe your symptoms: ").strip()
    if not symptoms:
        symptoms = "I have high fever, leg pain, and red eyes since yesterday"

    result = run_health_triage_agent(mock_env_report, symptoms)

    print("\n📦 Data package ready for Agent 3:")
    print(f"   Urgency: {result['urgency']}")
