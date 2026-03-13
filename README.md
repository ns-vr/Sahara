# 🌍 SAHARA
### Survival & Health Agent for Relief and Recovery Aid
**AgentathonX 2026 — HiGen Labs India's First Online AI Agent Hackathon**

---

## What is SAHARA?

SAHARA is a **multi-agent AI system** that activates the moment a disaster hits — simultaneously handling environmental detection, health triage, and relief coordination in a single unified pipeline.

Every existing disaster tool does ONE thing. SAHARA connects all three:

```
🌍 Agent 1          🏥 Agent 2            🆘 Agent 3
Environment   →    Health Triage    →    Relief Coordinator
Scanner            (disaster-aware)       (hospitals + SOS)
```

---

## The Problem

When disasters hit India (floods, heatwaves, cyclones), three systems collapse **at the same time**:
- Environmental monitoring (where is it bad?)
- Medical triage (who needs what help?)
- Relief coordination (where do they go?)

No existing tool connects all three. Survivors are left navigating three different systems during the most stressful moments of their lives.

**SAHARA solves this in one conversation.**

---

## Key Innovation

Most health AI gives generic advice. SAHARA gives **disaster-specific** advice.

Example: A flood survivor reporting "fever and leg pain" gets advice specific to **leptospirosis** (a flood-borne disease) — not just generic fever advice. The health agent knows what disaster just happened and reasons accordingly.

---

## Agent Architecture

### Agent 1: Environment Scanner
- Fetches live weather data (OpenWeatherMap API)
- Fetches real-time Air Quality Index (AQICN API)
- Detects disaster type: flood, heatwave, fire, storm
- Calculates severity score (0–10)
- Maps disaster → known health risks (passed to Agent 2)

### Agent 2: Health Triage Agent
- Takes symptoms from user
- Cross-references with disaster type and known health risks
- Uses Claude AI for intelligent, context-aware triage
- Outputs: likely condition, urgency level, immediate steps, red flags

### Agent 3: Relief Coordinator
- Finds nearest hospitals/pharmacies (OpenStreetMap Overpass API — free)
- Uses Claude AI to generate evacuation advice specific to disaster type
- Generates a shareable plain-text SOS report
- Lists Indian emergency numbers (112, 108, 101, NDRF)

---

## Setup

### 1. Get Free API Keys (5 minutes)
| Service | URL | Cost |
|---|---|---|
| OpenWeatherMap | https://openweathermap.org/api | Free tier |
| AQICN | https://aqicn.org/data-platform/token/ | Free |
| Anthropic Claude | https://console.anthropic.com | Free credits |

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
export OPENWEATHER_API_KEY="your_key_here"
export AQICN_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

### 4. Run the App
```bash
streamlit run app.py
```

Or run individual agents for testing:
```bash
python agent1_environment.py
python agent2_health_triage.py
python agent3_relief.py
```

---

## Demo Scenario

> *A flood has just hit Silchar, Assam. A survivor opens SAHARA.*

1. **Agent 1** detects: Active flood, AQI unhealthy, severity 8/10, flags leptospirosis risk
2. Survivor types: *"I have high fever and leg pain since yesterday"*
3. **Agent 2** responds: "Given the flood conditions, your symptoms match leptospirosis exposure — a bacterial infection from floodwater. Do NOT drink local water. Immediate steps: [prioritized first aid]"
4. **Agent 3** finds nearest hospital (2.3 km), provides evacuation route, generates downloadable SOS report

Total time from input to full report: **~15 seconds**

---

## Impact

- **600M+** Indians affected by climate disasters annually
- **70%** of rural India lacks adequate healthcare access
- **Leptospirosis, cholera, heat stroke** — all preventable with early, correct guidance
- SAHARA gives the right information, to the right person, at the right time

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| UI | Streamlit |
| AI Engine | Claude (Anthropic) |
| Weather | OpenWeatherMap API |
| Air Quality | AQICN API |
| Facility Search | OpenStreetMap Overpass API |
| Agent Orchestration | Custom Python pipeline |

---

## File Structure

```
sahara/
├── app.py                    # Main Streamlit UI + orchestrator
├── agent1_environment.py     # Agent 1: Environment Scanner
├── agent2_health_triage.py   # Agent 2: Health Triage
├── agent3_relief.py          # Agent 3: Relief Coordinator
├── requirements.txt
└── README.md
```

---

## Built For
**AgentathonX 2026** — India's First Online AI Agent Hackathon by HiGen Labs

*Innovation • Impact • Intelligence*
