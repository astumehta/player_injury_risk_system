"""
Synthetic Dataset Generator for AI-Assisted Player Health & Injury Risk System
Compliance: Synthetic data adhering to DPDP Act privacy principles.
Generates 60 players across 2 squads over 40 weeks = 2,400 player-weeks (~3.9% injury rate).
Features include rolling 3-week metrics (sleep debt, load trend) as outlined in Midterm Report.
"""

import json
import os
import numpy as np
import pandas as pd

def generate_season_data(seed=42):
    np.random.seed(seed)
    
    squads = ["First Team Squad", "U23 Reserve Squad"]
    positions = ["Forward", "Midfielder", "Defender", "Goalkeeper"]
    pos_weights = [0.25, 0.35, 0.30, 0.10]
    
    # 60 players: 32 in First Team, 28 in U23
    players = []
    player_id_counter = 1
    
    for sq in squads:
        count = 32 if sq == "First Team Squad" else 28
        for i in range(count):
            p_id = f"PL-{player_id_counter:03d}"
            name = f"Player {player_id_counter}"
            pos = np.random.choice(positions, p=pos_weights)
            age = int(np.random.normal(26, 3.5)) if sq == "First Team Squad" else int(np.random.normal(20, 1.8))
            age = max(17, min(36, age))
            prior_injuries = int(np.random.choice([0, 1, 2, 3], p=[0.45, 0.30, 0.15, 0.10]))
            chronic_baseline_load = np.random.normal(2400, 300) # Arbitrary Workload Units (AU)
            
            players.append({
                "player_id": p_id,
                "name": name,
                "squad": sq,
                "position": pos,
                "age": age,
                "prior_injuries": prior_injuries,
                "chronic_baseline_load": round(chronic_baseline_load, 1)
            })
            player_id_counter += 1
            
    # Generate 40 weeks for each player
    num_weeks = 40
    records = []
    
    for p in players:
        chronic = p["chronic_baseline_load"]
        # History buffers for rolling features
        load_history = []
        sleep_history = []
        soreness_history = []
        
        for w in range(1, num_weeks + 1):
            # 12% probability of an acute load spike (ACWR near 1.6)
            is_spike = np.random.rand() < 0.12
            if is_spike:
                acute_load = chronic * np.random.uniform(1.48, 1.72)
            else:
                acute_load = chronic * np.random.uniform(0.85, 1.25)
                
            acwr = acute_load / max(chronic, 1000)
            
            # Minutes played in match
            if p["position"] == "Goalkeeper":
                minutes = 90 if np.random.rand() > 0.3 else 0
            else:
                minutes = int(np.random.choice([0, 20, 60, 75, 90], p=[0.2, 0.1, 0.2, 0.2, 0.3]))
                
            # Sleep hours: baseline ~7.8h, worse in spike weeks
            if is_spike:
                sleep_hours = np.random.normal(6.1, 0.8)
            else:
                sleep_hours = np.random.normal(7.8, 0.9)
            sleep_hours = float(np.clip(round(sleep_hours, 1), 4.0, 10.5))
            
            # Soreness (1-10): baseline 2.5, worse in spike weeks
            if is_spike:
                soreness = np.random.normal(6.8, 1.4)
            else:
                soreness = np.random.normal(3.0, 1.2)
            soreness = float(np.clip(round(soreness, 1), 1.0, 10.0))
            
            # Wellness score (1-10 composite)
            wellness = float(np.clip(round(10.0 - (soreness * 0.5) + (sleep_hours - 7.0) * 0.6 + np.random.normal(0, 0.4), 1), 1.0, 10.0))
            
            load_history.append(acute_load)
            sleep_history.append(sleep_hours)
            soreness_history.append(soreness)
            
            # Rolling 3-week features
            if len(load_history) >= 3:
                recent_3_loads = load_history[-3:]
                load_trend_3w = (recent_3_loads[-1] - recent_3_loads[0]) / (recent_3_loads[0] + 1e-5) * 100.0
                sleep_debt_3w = sum(max(0.0, 7.5 - s) for s in sleep_history[-3:])
                avg_soreness_3w = np.mean(soreness_history[-3:])
            else:
                load_trend_3w = 0.0
                sleep_debt_3w = max(0.0, 7.5 - sleep_hours)
                avg_soreness_3w = soreness
                
            # Log-odds of soft-tissue injury in next 7 days
            # Logistic function based on sports science factors:
            # ACWR spike > 1.5, soreness > 6, sleep < 6.5, prior injuries, rolling sleep debt
            log_odds = -4.55  # calibrated for ~3.9% injury prevalence across 2,400 player-weeks
            log_odds += 2.8 * max(0.0, acwr - 1.35)
            log_odds += 0.35 * max(0.0, soreness - 5.0)
            log_odds += 0.40 * max(0.0, 6.5 - sleep_hours)
            log_odds += 0.45 * p["prior_injuries"]
            log_odds += 0.08 * sleep_debt_3w
            log_odds += 0.015 * max(0.0, load_trend_3w)
            log_odds += 0.015 * (p["age"] - 25)
            
            prob_injury = 1.0 / (1.0 + np.exp(-log_odds))
            injury_label = int(np.random.rand() < prob_injury)
            
            # Update chronic load with exponential moving average (simulating fitness adaptation)
            chronic = 0.85 * chronic + 0.15 * acute_load
            
            records.append({
                "player_id": p["player_id"],
                "player_name": p["name"],
                "squad": p["squad"],
                "position": p["position"],
                "age": p["age"],
                "prior_injuries": p["prior_injuries"],
                "week": w,
                "acute_load": round(acute_load, 1),
                "chronic_load": round(chronic, 1),
                "acwr": round(acwr, 2),
                "match_minutes": minutes,
                "sleep_hours": sleep_hours,
                "soreness": soreness,
                "wellness_score": wellness,
                "load_trend_3w": round(load_trend_3w, 1),
                "sleep_debt_3w": round(sleep_debt_3w, 1),
                "avg_soreness_3w": round(avg_soreness_3w, 1),
                "true_prob": round(prob_injury, 4),
                "injury_next_7_days": injury_label
            })
            
    df = pd.DataFrame(records)
    
    # Save files
    os.makedirs("/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/data", exist_ok=True)
    df.to_csv("/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/data/synthetic_season.csv", index=False)
    
    with open("/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/data/players.json", "w") as f:
        json.dump(players, f, indent=2)
        
    print(f"Generated {len(df)} player-weeks for {len(players)} players.")
    print(f"Total injuries: {df['injury_next_7_days'].sum()} ({df['injury_next_7_days'].mean()*100:.2f}% rate)")
    
    # Holdout evaluation check: 18 unseen players (test set: 720 player-weeks)
    test_player_ids = [p["player_id"] for p in players[-18:]]
    test_df = df[df["player_id"].isin(test_player_ids)]
    print(f"Test set (18 unseen players): {len(test_df)} weeks, {test_df['injury_next_7_days'].sum()} injuries.")
    
    return df, players

if __name__ == "__main__":
    generate_season_data()
