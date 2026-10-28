# ⚓⚽ Harbourline FC: AI-Assisted Player Health & Injury Early-Warning System
**Course:** Foundations of AI for Business | Final Project (Healthcare)  
**Group:** A1 | **Author:** Astu Mehta (10289708)  
**Live Streamlit Deployment:** Streamlit Community Cloud  

---

## 🌟 Executive Overview & The 3-Step Clinical Workflow

Professional football clubs lose an average of **£45M per season** to preventable soft-tissue muscle strains. Harbourline FC's early-warning system replaces uncalibrated dashboard clutter with a **medically grounded, human-in-the-loop decision framework**:

```
[ Step 1: Spot the Risk (Predictive ML) ]
Trained Logistic Regression model evaluates ACWR workload, sleep debt, soreness, and prior injuries.
Rates athlete into: 🟢 Low Risk (<5%), 🟡 Moderate Risk (5-15%), or 🔴 High Risk (≥15%).
             │
             ▼
[ Step 2: Explain What to Do (Club Rulebook Grounding) ]
AI matches player metrics against Harbourline FC's official 45-clause Medical Protocol (protocol.md).
Cites exact rule clauses (e.g. Rule LM-3.4 Workload Spike, Rule WEL-4.2 Sleep Deficit).
Never diagnoses or benches autonomously; provides safety escalation under Rule GOV-1.4.
             │
             ▼
[ Step 3: A Human Decides (Doctor Sign-Off Checkpoint) ]
Under Rule AI-6.4 & GOV-1.5: The AI NEVER benches or clears anyone automatically.
The Club Doctor reviews physical symptoms, inputs clinical rationale, and signs off.
Only after doctor approval does the Head Coach's Matchday Squad Sheet finalize!
```

---

## 🚀 Key System Modules (4 Hub Views)

1. **📋 Head Coach's Matchday & Training Squad Sheet:**
   - 🏟️ **Tactical 4-3-3 Lineup Board:** Formation health status across Attackers, Midfielders, Defensive Line, and Goalkeeper.
   - 🎴 **Tactical Squad Cards:** Physical status, return-to-play timelines, and doctor-prescribed drill instructions for the coach.
   - 📊 **3 Real-time Matchday KPIs:** Cleared for 90 Mins, Modified Training Only, and Sidelined/Benched.

2. **⚡ Squad Morning Readiness Scan (All 60 Players):**
   - High-throughput batch morning screening of all 60 senior squad athletes across Squad A and Squad B.
   - Live filters by Tactical Readiness and Squad.
   - CSV Export for matchday team sheets.

3. **👉 Individual Player 3-Step Deep-Dive & Clinical Sign-Off:**
   - Interactive parameters check-in (ACWR, sleep, soreness, wellness).
   - 1-Click Pre-fill shortcuts for official rehearsal cases (Low Risk fit starter, High Risk spike, Rule Conflicts).
   - Official human doctor sign-off form with permanent audit logging.

4. **💡 Sports Science Math & Google Colab Pipeline:**
   - Full 11-parameter logistic regression mathematical breakdown ($z = b_0 + \sum w_i x_i$).
   - Interactive simulation sandbox with slider controls.
   - Complete Google Colab training notebook (`Harbourline_Injury_Model_Season_Colab.ipynb`).

---

## 📊 Dataset Specifications & Machine Learning Performance

- **Dataset Source:** Harbourline Football Club Performance Analytics (`team_assets/player_weeks.csv`). Integrates Catapult/STATSports GPS tracking, daily morning subjective questionnaires, and Premier League match appearance records.
- **Dataset Size:** **2,400 player-weeks** across **60 professional squad players** over **22 columns**.
- **Active Training Size:** **2,077 player-weeks** (after excluding 323 weeks where players were already out with an existing injury).
- **Time Period:** Full **40-week competitive season** (Weeks 1 to 40).
- **Target Variable (`injury_next_7d`):** Binary classification label (1 if the player sustained a new time-loss strain within the next 7 days, 0 otherwise). Total **94 observed injuries** across 37 players (**4.53% active incidence rate**).
- **Model Evaluation on Held-Out Test Set (395 player-weeks across 12 unseen players):**
  - **Test ROC-AUC Score:** **`0.8981` (~89.8%)** *(High clinical discrimination)*
  - **Test Accuracy:** **`90.89%`** *(At $P \ge 15\%$ high-risk alert threshold)*
  - **Base Intercept ($b_0$):** **`-4.900`** *(Calibrated baseline injury prevalence)*

---

## 💻 Local Setup & Execution

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/player_injury_risk_system.git
cd player_injury_risk_system

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Run the Streamlit web application
streamlit run app.py
```

---

## 📂 Repository Structure

```
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Python dependencies for Streamlit Cloud
├── .streamlit/
│   └── config.toml            # Premier League dark stadium theme configuration
├── data/
│   ├── harbourline_player_weeks.csv # 2,400 player-weeks dataset
│   └── player_weeks.csv       # Matchday season CSV
├── models/
│   ├── harbourline_logistic_season.pkl # Trained logistic regression bundle
│   ├── harbourline_predictor.py # Multi-stage prediction engine
│   └── transparent_model.py   # Mathematical logit breakdown
├── notebooks/
│   └── Harbourline_Injury_Model_Season_Colab.ipynb # Google Colab notebook
├── scripts/
│   ├── train_season_model.py  # Model training pipeline
│   └── Harbourline_Injury_Model_Colab.py # Standalone Colab script
├── state/
│   └── workflow_store.py      # Human doctor sign-off state manager
├── team_assets/
│   ├── player_weeks.csv       # Original season data
│   ├── protocol.md            # Club medical & load protocol (45 clauses)
│   └── DATA_README.md         # Comprehensive data dictionary
└── ui/
    ├── coach_roster.py        # 60-player directory with jersey numbers
    ├── coach_insights.py      # Coach drill translation engine
    └── harbourline_cases.py   # Pre-configured rehearsal scenarios
```
