# Synthetic season and protocol: Group A1

This folder holds the synthetic dataset and the club protocol for the AI-Assisted Player Health and Injury Risk System. Both are fictional and built to match the specification in our midterm report.

| File | What it is |
|---|---|
| `player_weeks.csv` | 2,400 player-weeks: 60 players, 2 squads, 40 weeks. The modelling dataset. |
| `oracle_probabilities.csv` | The true injury probability the generator used for each row. **Never use it as a feature.** It is only for measuring the ceiling (see "Ceiling check" below). |
| `generate_data.py` | Seeded generator. `python generate_data.py` reproduces the shipped files exactly. `python generate_data.py --seed 7 --calibrate` makes a different season with the same rules. |
| `protocol.md` | Harbourline FC Medical and Load-Management Protocol, the RAG source document. 45 clauses, each with a fixed ID. |

---

## 1. Quick start for modelling

```python
import pandas as pd
df = pd.read_csv("player_weeks.csv")

# 1. Drop weeks when the player is already injured. The label is blank for those rows.
df = df[df["availability"] != "out"]          # leaves 2,077 rows, 94 injuries (4.5%)

# 2. Do not use these columns as features: they describe the injury AFTER it happens.
OUTCOMES = ["injury_next_7d", "injury_type", "weeks_out"]

# 3. Split by player, not by row, so no player is in both train and test.
from sklearn.model_selection import GroupKFold
groups = df["player_id"]
```

The 3.9% injury rate in the report is measured over all 2,400 rows (94 injuries). Among weeks when the player was available it is 4.5%. Say which one you mean on your slides.

---

## 2. Data dictionary

| Column | Type | Description |
|---|---|---|
| `player_id` | text | `P001` to `P060`. Pseudonymised. There are no names anywhere. |
| `squad` | A / B | 30 players each. |
| `week` | 1 to 40 | In-season week. Four hidden pre-season weeks seed the chronic load, so week 1 already has a valid ACWR. |
| `position` | GK / DEF / MID / FWD | Each squad has 3 GK, 10 DEF, 10 MID and 7 FWD. |
| `age` | 18 to 35 | Fixed for the season. |
| `prior_injuries` | 0 to 5 | Soft-tissue injuries in the two previous seasons. Fixed for the season. |
| `availability` | full / modified / out | `out` = injured this week. `modified` = first two weeks back from an injury. |
| `rtp_stage` | 1 to 6 or blank | Return-to-play stage (protocol `RTP-5.1`). Stages 1 to 4 occur while out, 5 in the first week back, 6 in the second. Blank otherwise. |
| `weeks_since_return` | 1, 2 or blank | Only filled for `modified` rows. |
| `matches_in_week` | 0 to 2 | Fixtures the squad played that week. |
| `matches_played` | 0 to 2 | Matches this player appeared in. |
| `match_minutes` | 0 to 180 | Minutes played. Capped at 45 in the second week back (protocol `RTP-5.4`). |
| `weekly_load_au` | AU | Session-RPE load, training plus matches. |
| `chronic_load_au` | AU | Average weekly load over the previous 4 weeks. |
| `acwr` | ratio | `weekly_load_au / chronic_load_au` (uncoupled, protocol `MON-2.3`). |
| `sleep_hours` | 4 to 10 | Average nightly sleep that week. |
| `sleep_quality` | 1 to 10 | Higher is better. |
| `soreness` | 1 to 10 | Higher is worse. |
| `wellness` | 1 to 10 | Higher is better. |
| `injury_next_7d` | 0 / 1 / blank | **Label.** 1 if the player is injured in the next 7 days. Blank for `out` rows. |
| `injury_type` | text | Outcome only. Filled when the label is 1. |
| `weeks_out` | 1 to 8 | Outcome only. Weeks missed. Use it for the business case (cost of a missed injury). |

**Season totals:** 94 injuries across 37 different players. Hamstring 25, calf 23, ankle 20, groin 13, knee 9 and lower back 4. Mean absence is 3.5 weeks, giving 333 player-weeks lost.

---

## 3. How the data was generated

Say this openly in the presentation. Because we wrote the generator, a model can only learn the rules we put in, so any score partly reflects our own assumptions.

**Each player** gets a personal baseline load (about 2,300 AU for outfield players and 1,500 for goalkeepers), sleep baseline, wellness baseline and soreness baseline.

**Each week** is one of the following:
- **Normal:** load = baseline × about 1.0.
- **Load spike** (12% of weeks): load = baseline × 1.45 to 1.9. Sleep, soreness and wellness get worse.
- **Deload or international break** (5%): load = baseline × 0.55 to 0.8.
- **Fixture congestion:** two matches in the week, shared by the whole squad (about 20% of weeks). Load +12% and sleep is slightly worse.
- **Non-load stress** (about 10% of weeks; it can run for consecutive weeks): travel, illness or personal stress. Sleep drops by about 1 hour and wellness by about 1.2 points, **with no change in load.** This is why sleep and wellness carry information that ACWR does not.

**Injury.** The label is drawn from a logistic function of the following:

| Factor | Effect on log-odds |
|---|---|
| ACWR above 1.3 | +1.4 per unit above 1.3 |
| ACWR below 0.8 | +0.9 per unit below 0.8 |
| Prior injuries | +0.55 each |
| Soreness | +0.25 per point above 4 |
| Sleep below 7 h this week | +0.35 per hour short |
| **3-week sleep debt** (hours below 7.5 h/night) | +0.07 per hour. This is **not a column**: build it from `sleep_hours`. |
| Age | +0.04 per year above 26 |
| Position | GK −0.6, MID +0.1, FWD +0.25 |
| Wellness 4 or below | +0.35 |
| First / second week back from injury | +0.7 / +0.4 |
| Intercept | −5.2, chosen to give 94 injuries (3.9%) |

After an injury the player is `out` for `weeks_out` weeks, doing rehab load of about 15 to 35% of baseline. They then come back at about 75 to 95% load. Because their chronic load fell while they were out, **their ACWR on return is usually above 1.5**: this happens in 64 of 85 first weeks back.

---

## 4. Sanity check: rule vs model vs ceiling

These are averages over 10 random player-held-out splits (42 train / 18 test players). Every method flags the same number of player-weeks as the ACWR > 1.5 rule (about 98 per test set, roughly 16%).

| Method | Injuries caught (of about 28.5) | AUC |
|---|---|---|
| Baseline rule: ACWR > 1.5 | 16.9 | 0.74 (ACWR as a score) |
| Logistic regression, raw columns | 17.7 | 0.80 |
| + 3-week sleep debt and an ACWR-above-1.3 term | 17.9 | 0.81 |
| **Ceiling:** true probabilities | 20.0 | 0.85 |

What this means for you:
- The model beats the rule on AUC, but at the same workload it catches only about one extra injury per test set, and the range across splits is wide (the rule caught 7 to 30 depending on the split). Report the mean and the range, not one split.
- Even a perfect model catches only about 70% of injuries at this flag rate, because injury is random. That's a strong, honest point: no model can catch everything.
- **The midterm table numbers will change** with this dataset. Rerun everything before you present.

---

## 5. Things the data is built to expose

- **ACWR above 3 is real.** There are 21 rows with ACWR above 3, and 18 of them are players in their first week back. The midterm plan to reject ACWR > 3 in input validation would reject the returning players, who are among the riskiest. Validate the raw inputs (load, sleep, scales) instead, as protocol `MON-2.4` does, and let the protocol handle high ACWR.
- **Gradient boosting will struggle.** With about 75 injuries in each training set, deep trees overfit. Use shallow trees with class weights, or explain why you dropped it.
- **Squad imbalance:** Squad A had 52 injuries and Squad B 42. This is a useful talking point if anyone asks whether the model is fair across squads.

---

## 6. Protocol notes for the RAG pipeline

- **Chunking:** split `protocol.md` on `### ` headings. Each clause is one chunk, with its ID at the start of the heading (for example `LM-3.4`). Keep the section heading as metadata.
- **Clause families:**

| Family | Topic |
|---|---|
| `GOV` | Governance |
| `MON` | Monitoring |
| `LM` | Load management |
| `WEL` | Sleep and wellness |
| `RTP` | Return to play |
| `AI` | Tool rules |
| `ESC` | Escalation |
| `PRIV` | Privacy |

- **Rules the briefing prompt should enforce:**
  - Cite clause IDs (`AI-6.4`).
  - Never choose between conflicting clauses (`GOV-1.4`).
  - Say "The protocol does not cover this situation" when nothing applies (`AI-6.6`).

### Deliberate conflicts (the edge case)

| Conflict | Clause 1 says | Clause 2 says | When it fires in the data | Correct system behaviour |
|---|---|---|---|---|
| **A: return-to-play vs load spike** | `RTP-5.3`: Stage 5 player may do full, unrestricted training including sprints | `LM-3.4`: ACWR above 1.50 → cap load, no sprints for 48 h | 64 of 85 first weeks back | Show both clauses, apply the more conservative one for now, and escalate to the Medical Lead (`GOV-1.4`). `MON-2.3` warns that ACWR is inflated after absence but deliberately does not settle it. |
| **B: green load vs model High** | `LM-3.2`: Green ACWR → full training, no restrictions | `AI-6.2`: model High → modified training until physio screen | Any High-risk week with ACWR 0.80 to 1.30 | Same as above. This is also where the model adds value over the rule. |

### Out-of-scope tests (should trigger "not covered")
Questions about concussion, chest pain, fever, medication, supplements or mental health should all trigger `GOV-1.2` / `ESC-7.2` and refer to the Club Doctor. The system should not give advice. These make good hallucination tests.

---

## 7. Suggested demo cases

All rows are from `player_weeks.csv`. "True risk" comes from `oracle_probabilities.csv`. **Check that your own model gives the expected tier** before you build the demo around these rows.

| Case | Row | Inputs | True risk | What happened | Protocol clauses the briefing should cite |
|---|---|---|---|---|---|
| **Low** | P046, week 35 | MID, age 18, 0 prior injuries. ACWR 1.12, sleep 8.2 h, sleep quality 8, soreness 1, wellness 8. | 0.2% | No injury | `LM-3.2` Green, `AI-6.3` (Low is not clearance) |
| **High** | P051, week 3 | MID, age 26, 1 prior injury. ACWR 1.77, sleep 6.0 h, sleep quality 5, soreness 7, wellness 3. 3-week sleep debt 35 h. | 51% | Calf strain next week | `LM-3.4` Red, `WEL-4.1` Amber, `WEL-4.2` Amber, `WEL-4.4` Amber, `WEL-4.5` Red → Club Doctor, `WEL-4.6`, `ESC-7.1` |
| **Edge: conflict A** | P006, week 32 | DEF, age 23, 1 prior injury. **RTP Stage 5, first week back.** ACWR 2.85 (load 2,218 vs chronic 778), sleep 7.4 h, soreness 6, wellness 6. | 34% | No injury | `RTP-5.3` vs `LM-3.4`, `MON-2.3`, `GOV-1.4` → Medical Lead |
| **Edge: conflict B** | P020, week 32 | MID, age 30, 1 prior injury. ACWR 1.01 (Green), sleep 5.5 h, sleep quality 4, soreness 6, wellness 4. 3-week sleep debt 41 h. | 45% | No injury | `LM-3.2` vs `AI-6.2`, `WEL-4.1` Red, `WEL-4.2`, `WEL-4.5`, `GOV-1.4`. The rule says fine, the model says High. |
| **Borderline (backup)** | P004, week 26 | DEF, age 23, **3 prior injuries**. ACWR 0.87, sleep 8.1 h, soreness 6, wellness 5. | 5.0% (right at the top-15% threshold) | **Groin strain next week** | Shows a near-miss that a slightly stricter threshold would have missed. Good for the "cost of a missed injury" slide. |
| **Validation trap** | P010, week 18 | DEF, RTP Stage 5, ACWR 3.24 | 32% | No injury | A returning player your ACWR > 3 check would reject. Good to show, or to fix before a challenger finds it. |

For a more extreme high-risk case, use P058 week 10: ACWR 2.83, sleep 5.6 h, soreness 8, wellness 3, 68% true risk, ankle sprain next week.

---

*Generated with an AI assistant (seed 42). Record this in the prompt log appendix.*
