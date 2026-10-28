"""
Harbourline FC — 1,000 Synthetic Football Players Dataset Generator
Group A1: Foundations of AI for Business | Astu Mehta (10289708)

Generates 1,000 realistic synthetic professional football players for model training:
- Demographics: Age (18-36), Position (GK, DEF, MID, FWD)
- Workload: Chronic Load (AU), Weekly Load (AU), ACWR (Acute:Chronic Workload Ratio)
- Physical & Fatigue: Soreness (1-10), Wellness (1-10), Sleep Hours (h), 3-Week Sleep Debt (h)
- Medical History: Prior Soft-Tissue Strains (0-5), Return-to-Play Stage (is_returning)
- Sports Science Ground Truth: True Logit z, True Probability P, and Binary Injury Target (injury_next_7d)
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "training_players_1000.csv")

# First and last names for generating 1,000 realistic football players
FIRST_NAMES = [
    "James", "John", "Liam", "Lucas", "Noah", "Oliver", "Marcus", "Ethan", "Mateo", "David",
    "Jack", "Jordan", "Ben", "Samuel", "Aaron", "Kofi", "Tariq", "Declan", "Mason", "Finnian",
    "Harvey", "Caleb", "Dominic", "Harrison", "Lucas", "George", "Finlay", "Elijah", "Nico", "Oscar",
    "Archie", "Lewis", "Reuben", "Kian", "Elliot", "Isaac", "Gabriel", "Alexander", "Max", "Jude",
    "Flynn", "Theo", "Jayden", "Rory", "Adam", "Corey", "Bradley", "Nathan", "Callum", "Ronan",
    "Miles", "Ewan", "Daniel", "Jamie", "Leon", "Aidan", "Sonny", "Freddie", "Kai", "Hugo"
]

LAST_NAMES = [
    "Vance", "Henderson", "Ward", "Sterling", "Al-Mansoor", "Kalu", "Davies", "Hughes", "Shaw", "Campbell",
    "Brooks", "Taylor", "Mensah", "Silva", "Ross", "Clarke", "O'Shea", "Adebayo", "Ellis", "Baxter",
    "Thorne", "Price", "Cole", "Bailey", "Morales", "Morris", "King", "Van Dijk", "Palmer", "Adams",
    "Wilson", "Martin", "Foster", "Cooper", "Powell", "Bennett", "Wood", "Santos", "Scott", "Fletcher",
    "Harrison", "Graham", "Marshall", "Kelly", "Gallagher", "Wright", "Simpson", "Evans", "Hayes", "Chapman",
    "O'Connor", "Byrne", "Gibson", "Murray", "Crawford", "Walsh", "Kennedy", "Doyle", "Bell", "Fox"
]

def generate_1000_players(seed=42):
    rng = np.random.default_rng(seed)
    N = 1000
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Names and Demographics
    firsts = rng.choice(FIRST_NAMES, size=N)
    lasts = rng.choice(LAST_NAMES, size=N)
    full_names = [f"{f} {l}" for f, l in zip(firsts, lasts)]
    
    positions = rng.choice(['GK', 'DEF', 'MID', 'FWD'], size=N, p=[0.10, 0.35, 0.35, 0.20])
    ages = np.clip(np.round(rng.normal(26.2, 3.8, size=N)), 18, 36).astype(int)
    prior_inj = np.clip(rng.poisson(0.6 + 0.05 * (ages - 22)), 0, 5)

    # 2. Chronic & Acute Workloads
    # Goalkeepers run ~1500 AU/week; outfield players average ~2300 AU/week
    chronic_loads = np.where(positions == 'GK', rng.normal(1500, 140, size=N), rng.normal(2300, 210, size=N))
    chronic_loads = np.round(np.clip(chronic_loads, 1100, 3100)).astype(int)

    # Distribution of training workloads:
    # 70% in normal green band (ACWR 0.85 - 1.28)
    # 18% in acute load spike danger band (ACWR 1.32 - 2.25)
    # 12% in under-loading deconditioned band (ACWR 0.28 - 0.78)
    load_types = rng.choice(['normal', 'spike', 'under'], size=N, p=[0.70, 0.18, 0.12])
    acwrs = []
    for lt in load_types:
        if lt == 'spike':
            acwrs.append(rng.uniform(1.32, 2.25))
        elif lt == 'under':
            acwrs.append(rng.uniform(0.28, 0.78))
        else:
            acwrs.append(rng.uniform(0.85, 1.28))
    acwrs = np.round(np.array(acwrs), 2)
    weekly_loads = np.round(acwrs * chronic_loads).astype(int)

    # 3. Sleep & Fatigue
    sleep_hours = np.clip(np.round(rng.normal(7.4, 0.75, size=N), 1), 4.2, 9.6)
    # Compound 3-week sleep debt (hours below 7.5 over 21 days)
    sleep_debt = np.clip(np.round(rng.exponential(5.5, size=N) + np.where(sleep_hours < 6.5, 12.0, 0.0), 1), 0.0, 45.0)

    # 4. Subjective Wellness & Soreness (1-10)
    # Higher ACWR spikes elevate soreness
    soreness_raw = 3.0 + 1.8 * np.maximum(0, acwrs - 1.25) + rng.normal(0, 1.0, size=N)
    soreness = np.clip(np.round(soreness_raw), 1, 10).astype(int)

    # Low sleep and high debt hurt wellness
    wellness_raw = 7.6 - 1.2 * np.maximum(0, acwrs - 1.30) - 0.05 * sleep_debt + rng.normal(0, 1.0, size=N)
    wellness = np.clip(np.round(wellness_raw), 1, 10).astype(int)

    # 5. Return-to-Play Status (10% of players returning from rehab)
    is_returning = rng.choice([0, 1], size=N, p=[0.90, 0.10])

    # 6. Sports Science True Log-Odds Formula (DATA_README.md Section 3)
    pos_map = {'GK': -0.60, 'DEF': 0.0, 'MID': 0.10, 'FWD': 0.25}
    pos_effects = np.array([pos_map[p] for p in positions])

    z = (-5.20 
         + 1.40 * np.maximum(0.0, acwrs - 1.30)
         + 0.90 * np.maximum(0.0, 0.80 - acwrs)
         + 0.55 * prior_inj
         + 0.25 * np.maximum(0.0, soreness - 4.0)
         + 0.35 * np.maximum(0.0, 7.0 - sleep_hours)
         + 0.07 * sleep_debt
         + 0.04 * np.maximum(0.0, ages - 26.0)
         + 0.35 * (wellness <= 4).astype(float)
         + 0.70 * is_returning
         + pos_effects)

    true_prob = 1.0 / (1.0 + np.exp(-z))

    # Binary outcome sampling (1 = soft-tissue injury in next 7 days, 0 = healthy)
    # Slight calibrated multiplier to give ~45-55 injuries in 1000 rows (4.5% - 5.5% prevalence)
    injury_next_7d = rng.binomial(1, np.clip(true_prob * 1.3, 0, 1))

    # 7. Construct DataFrame
    df = pd.DataFrame({
        "player_id": [f"TRN_{i+1:04d}" for i in range(N)],
        "player_name": full_names,
        "position": positions,
        "age": ages,
        "prior_injuries": prior_inj,
        "weekly_load_au": weekly_loads,
        "chronic_load_au": chronic_loads,
        "acwr": acwrs,
        "sleep_hours": sleep_hours,
        "sleep_debt_3w": sleep_debt,
        "soreness": soreness,
        "wellness": wellness,
        "is_returning": is_returning,
        "true_injury_prob": np.round(true_prob, 4),
        "injury_next_7d": injury_next_7d
    })

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Generated {N} synthetic players and saved to: {OUTPUT_CSV}")
    print(f"Injuries in dataset: {injury_next_7d.sum()} ({injury_next_7d.mean()*100:.1f}% prevalence)")
    print(f"ACWR range: {acwrs.min():.2f} to {acwrs.max():.2f}")
    return df

if __name__ == "__main__":
    generate_1000_players()
