"""
Synthetic season generator for the AI-Assisted Player Health and Injury Risk System
Group A1, Foundations of AI for Business, Project 4 (Healthcare)

Produces a fictional season: 60 players, 2 squads, 40 in-season weeks = 2,400 player-weeks.
No real player data is used (real medical data is protected health data under the DPDP Act).

Outputs (written next to this script):
  player_weeks.csv          the modelling dataset (features + label + outcome columns)
  oracle_probabilities.csv  the TRUE injury probability the generator used for each row.
                            Never use it as a feature. It exists so you can measure the best
                            AUC any model could reach on this data (the "ceiling").

Run:  python generate_data.py            (default seed 42 reproduces the shipped files)
      python generate_data.py --seed 7 --calibrate   (a different season, same rules, 3.9% injuries)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

N_SQUADS = 2
PLAYERS_PER_SQUAD = 30
N_WEEKS = 40
WARMUP_WEEKS = 4          # pre-season weeks used only to seed chronic load, not written out
SPIKE_RATE = 0.12         # share of available weeks that are load spikes
STRESS_RATE = 0.10        # weeks with non-load stress (travel, illness, personal) that hurt
STRESS_PERSIST = 0.40     #   sleep and wellness without any load spike; chance it continues
TARGET_INJURY_RATE = 0.039

# Position mix per squad of 30
POSITIONS = ["GK"] * 3 + ["DEF"] * 10 + ["MID"] * 10 + ["FWD"] * 7
POS_EFFECT = {"GK": -0.6, "DEF": 0.0, "MID": 0.10, "FWD": 0.25}

# Injury types: (name, probability weight by position group, weeks-out range)
INJURY_TYPES = {
    "hamstring strain": (3, 6),
    "groin strain": (2, 4),
    "calf strain": (2, 4),
    "ankle sprain": (1, 4),
    "knee ligament sprain": (3, 8),
    "lower back pain": (1, 3),
}
INJURY_WEIGHTS = {
    "GK":  [0.10, 0.15, 0.10, 0.20, 0.15, 0.30],
    "DEF": [0.30, 0.20, 0.15, 0.20, 0.08, 0.07],
    "MID": [0.33, 0.20, 0.17, 0.15, 0.08, 0.07],
    "FWD": [0.40, 0.18, 0.15, 0.15, 0.07, 0.05],
}


def true_logit(b0, acwr, prior_inj, soreness, sleep_h, sleep_debt_3wk, age, pos,
               weeks_since_return, wellness):
    """The hidden risk function. Document every term in DATA_README.md."""
    z = b0
    z += 1.4 * max(0.0, acwr - 1.3)          # load spikes: risk rises sharply above ACWR 1.3
    z += 0.9 * max(0.0, 0.8 - acwr)          # under-loading also raises risk (detraining)
    z += 0.55 * prior_inj                    # previous injuries
    z += 0.25 * (soreness - 4)               # muscle soreness
    z += 0.35 * max(0.0, 7.0 - sleep_h)      # short sleep this week
    z += 0.07 * sleep_debt_3wk               # accumulated 3-week sleep debt (not a column!)
    z += 0.04 * (age - 26)                   # age
    z += POS_EFFECT[pos]                     # position
    z += 0.35 * (wellness <= 4)              # poor overall wellness
    if weeks_since_return == 1:
        z += 0.7                             # first week back from injury
    elif weeks_since_return == 2:
        z += 0.4
    return z


def simulate(seed: int, b0: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    # ---------- players ----------
    players = []
    pid = 1
    for s in range(N_SQUADS):
        squad = "A" if s == 0 else "B"
        for pos in POSITIONS:
            age = int(np.clip(round(rng.normal(26, 4)), 18, 35))
            prior = int(np.clip(rng.poisson(0.6 + 0.06 * (age - 22)), 0, 5))
            base_load = rng.normal(1500, 150) if pos == "GK" else rng.normal(2300, 250)
            players.append(dict(
                player_id=f"P{pid:03d}", squad=squad, position=pos, age=age,
                prior_injuries=prior, base_load=base_load,
                sleep_base=float(np.clip(rng.normal(7.6, 0.4), 6.6, 8.6)),
                well_base=float(np.clip(rng.normal(7.0, 0.7), 5.5, 8.8)),
                sore_base=float(np.clip(rng.normal(3.5, 0.7), 2.0, 5.5)),
                starter_p=0.15 if pos == "GK" and pid % 3 else rng.uniform(0.3, 0.85),
            ))
            pid += 1

    # Fixture congestion is shared by the whole squad: 2 matches in ~20% of weeks
    fixtures = {sq: rng.choice([1, 2, 0], size=N_WEEKS, p=[0.75, 0.20, 0.05])
                for sq in ["A", "B"]}

    rows, oracle = [], []
    for p in players:
        loads = list(p["base_load"] * rng.uniform(0.85, 1.0, WARMUP_WEEKS))
        sleeps = list(np.clip(rng.normal(p["sleep_base"], 0.4, WARMUP_WEEKS), 4.5, 10))
        out_left = 0               # weeks remaining out injured
        out_total = 0
        weeks_since_return = None  # None = not returning from an in-season injury
        current_injury = None
        stress = False

        for w in range(1, N_WEEKS + 1):
            stress = rng.random() < (STRESS_PERSIST if stress else STRESS_RATE)
            n_matches = int(fixtures[p["squad"]][w - 1])
            chronic = float(np.mean(loads[-4:]))   # uncoupled: previous 4 weeks only
            spike = False

            if out_left > 0:
                availability = "out"
                # RTP stages 1-4 progress while out
                done = out_total - out_left
                rtp_stage = min(4, 1 + int(4 * done / max(out_total, 1)))
                load = p["base_load"] * rng.uniform(0.15, 0.35) * (0.6 + 0.2 * rtp_stage)
                matches_played, minutes = 0, 0
            else:
                if weeks_since_return in (1, 2):
                    availability = "modified"
                    rtp_stage = 4 + weeks_since_return    # 5 = full training, 6 = match play
                    mult = rng.uniform(0.75, 0.95) if weeks_since_return == 1 else rng.uniform(0.85, 1.05)
                else:
                    availability = "full"
                    rtp_stage = None
                    r = rng.random()
                    if r < SPIKE_RATE:
                        spike = True
                        mult = rng.uniform(1.45, 1.9)
                    elif r < SPIKE_RATE + 0.05:
                        mult = rng.uniform(0.55, 0.8)       # international break / deload
                    else:
                        mult = rng.normal(1.0, 0.09)
                if n_matches == 2:
                    mult *= 1.12
                load = p["base_load"] * max(mult, 0.3)

                # match involvement
                matches_played, minutes = 0, 0
                for _ in range(n_matches):
                    if availability == "modified" and weeks_since_return == 1:
                        continue                              # no match in first week back
                    if rng.random() < p["starter_p"]:
                        matches_played += 1
                        minutes += int(rng.choice([90, 90, 90, 75, 65]))
                    elif p["position"] != "GK" and rng.random() < 0.45:
                        matches_played += 1
                        minutes += int(rng.integers(10, 35))
                if availability == "modified" and weeks_since_return == 2:
                    minutes = min(minutes, 45)

            acwr = load / chronic

            # wellness signals (worse in spike, congested and stress weeks)
            sleep_h = p["sleep_base"] - 0.45 * spike - 0.30 * (n_matches == 2) - 1.0 * stress \
                - 0.2 * (availability == "out") + rng.normal(0, 0.45)
            sleep_h = float(np.clip(sleep_h, 4.0, 10.0))
            sleep_q = int(np.clip(round(5.5 + 1.6 * (sleep_h - 7) + rng.normal(0, 1.0)), 1, 10))
            soreness = p["sore_base"] + 1.8 * spike + 1.2 * max(0.0, acwr - 1.2) \
                + 0.5 * (n_matches == 2) + 0.3 * (p["prior_injuries"] > 2) \
                + 1.5 * (availability == "out") + 0.4 * stress + rng.normal(0, 1.0)
            soreness = int(np.clip(round(soreness), 1, 10))
            wellness = p["well_base"] - 1.0 * spike - 0.35 * (soreness - p["sore_base"]) \
                + 0.4 * (sleep_h - p["sleep_base"]) - 0.8 * (availability == "out") - 1.2 * stress \
                + rng.normal(0, 0.8)
            wellness = int(np.clip(round(wellness), 1, 10))

            sleeps.append(sleep_h)
            sleep_debt = float(sum(max(0.0, 7.5 - s) * 7 for s in sleeps[-3:]))  # hours over 3 wks

            # label
            prob, label, inj_type, inj_weeks = np.nan, np.nan, None, None
            if availability != "out":
                z = true_logit(b0, acwr, p["prior_injuries"], soreness, sleep_h, sleep_debt,
                               p["age"], p["position"], weeks_since_return, wellness)
                prob = 1 / (1 + np.exp(-z))
                label = int(rng.random() < prob)
                if label:
                    names = list(INJURY_TYPES)
                    inj_type = rng.choice(names, p=INJURY_WEIGHTS[p["position"]])
                    lo, hi = INJURY_TYPES[inj_type]
                    inj_weeks = int(rng.integers(lo, hi + 1))

            rows.append(dict(
                player_id=p["player_id"], squad=p["squad"], week=w,
                position=p["position"], age=p["age"], prior_injuries=p["prior_injuries"],
                availability=availability,
                rtp_stage=rtp_stage,
                weeks_since_return=weeks_since_return if availability == "modified" else None,
                matches_in_week=n_matches, matches_played=matches_played, match_minutes=minutes,
                weekly_load_au=round(load), chronic_load_au=round(chronic), acwr=round(acwr, 2),
                sleep_hours=round(sleep_h, 1), sleep_quality=sleep_q,
                soreness=soreness, wellness=wellness,
                injury_next_7d=label, injury_type=inj_type, weeks_out=inj_weeks,
            ))
            oracle.append(dict(player_id=p["player_id"], week=w,
                               true_injury_prob=None if np.isnan(prob) else round(float(prob), 5)))

            # state transitions
            loads.append(load)
            if availability == "out":
                out_left -= 1
                if out_left == 0:
                    weeks_since_return = 1
                    current_injury = None
            else:
                if weeks_since_return is not None:
                    weeks_since_return = weeks_since_return + 1 if weeks_since_return < 2 else None
                if label == 1:
                    out_left = out_total = inj_weeks
                    weeks_since_return = None
                    current_injury = inj_type

    df = pd.DataFrame(rows)
    for c in ["rtp_stage", "weeks_since_return", "injury_next_7d", "weeks_out"]:
        df[c] = df[c].astype("Int64")
    return df, pd.DataFrame(oracle)


def calibrate(seed: int) -> float:
    """Pick the intercept so the realised injury count is closest to 3.9% of all rows."""
    target = TARGET_INJURY_RATE * N_SQUADS * PLAYERS_PER_SQUAD * N_WEEKS
    best = None
    for b0 in np.arange(-6.5, -3.0, 0.02):
        df, _ = simulate(seed, b0)
        n = int(df["injury_next_7d"].sum())
        if best is None or abs(n - target) < abs(best[1] - target):
            best = (b0, n)
    return float(round(best[0], 2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--b0", type=float, default=-5.2,
                    help="logistic intercept (-5.2 gives 3.9%% injuries with seed 42)")
    ap.add_argument("--calibrate", action="store_true",
                    help="search for the intercept that gives a 3.9%% injury rate (~1 min); "
                         "use this with a new --seed")
    args = ap.parse_args()

    b0 = calibrate(args.seed) if args.calibrate else args.b0
    df, oracle = simulate(args.seed, b0)
    out = Path(__file__).parent
    df.to_csv(out / "player_weeks.csv", index=False)
    oracle.to_csv(out / "oracle_probabilities.csv", index=False)

    n_inj = int(df["injury_next_7d"].sum())
    print(f"seed={args.seed}  intercept b0={b0}")
    print(f"rows={len(df)}  injuries={n_inj}  rate={n_inj/len(df):.3%}  "
          f"out-rows={int((df.availability=='out').sum())}")
