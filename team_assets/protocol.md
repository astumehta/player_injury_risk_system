# Harbourline FC: Medical and Load-Management Protocol

**Version:** 1.0 | **Effective:** 1 November 2026 | **Next review:** 1 May 2027
**Owner:** Medical Lead | **Approved by:** Medical Lead and Head of Performance
**Applies to:** Senior Squad A and Senior Squad B

> Harbourline FC is a fictional club. This protocol was written by Group A1 for an educational prototype (Foundations of AI for Business, Project 4). It is not medical advice and has not been reviewed by a clinician.

Every clause has a fixed ID (for example `LM-3.4`). Briefings produced by the AI risk tool must cite these IDs. Thresholds are repeated inside each clause on purpose, so that each clause can be read on its own.

---

## Section 1: Governance (GOV)

### GOV-1.1 Purpose
This protocol sets out how Harbourline FC monitors training load, sleep and wellness, how staff respond to warning signs, how injured players return to play, and how the AI risk tool may be used. Its aim is to reduce avoidable non-contact soft-tissue injuries while keeping players available for selection.

### GOV-1.2 Scope
This protocol covers non-contact soft-tissue injury risk (for example hamstring, groin and calf strains), load management, sleep and wellness monitoring, and return to play after soft-tissue injury and ankle sprains.

It does **not** cover concussion or head injury, cardiac symptoms, illness or infection, medication or supplements, surgery, mental health crises, or safeguarding. Those are handled by separate club protocols held by the Club Doctor. Any question in those areas must be referred to the Club Doctor (see `ESC-7.2`).

### GOV-1.3 Roles
- **Medical Lead:** final authority on availability. Approves or overrides every clear, modify or bench recommendation.
- **Club Doctor:** deputy to the Medical Lead. Handles anything outside this protocol's scope.
- **Lead Physiotherapist:** carries out physio screens and runs return-to-play progression.
- **Head of Performance:** plans training load and owns ACWR monitoring.
- **Head Coach:** selects the team from players the medical team has made available. Cannot override a medical decision.
- **Performance Analyst:** enters and checks monitoring data.

### GOV-1.4 When clauses give different instructions
If two clauses in this protocol give different instructions for the same player in the same week:
1. Apply the more conservative instruction until a decision is made.
2. Escalate the case to the Medical Lead the same day, naming both clauses.
3. The Medical Lead decides and records the decision and the reason in the sign-off log.

The AI risk tool must never choose between conflicting clauses itself. It must list both clauses and refer the case to the Medical Lead.

### GOV-1.5 Medical decision authority
No player is cleared, modified or benched for health reasons without sign-off from the Medical Lead, Club Doctor or Lead Physiotherapist. Coaches, analysts and the AI risk tool can recommend but cannot decide.

---

## Section 2: Monitoring (MON)

### MON-2.1 What is collected
The Performance Analyst records the following for every player every week:
- **Weekly load (AU):** the sum of session-RPE for all training sessions and matches (session duration in minutes × player-rated effort from 1 to 10).
- **Sleep hours:** the player's average nightly sleep over the week.
- **Sleep quality:** player-rated, 1 (very poor) to 10 (excellent).
- **Soreness:** player-rated, 1 (none) to 10 (severe).
- **Wellness:** player-rated overall wellbeing, 1 (very poor) to 10 (excellent).
- **Match minutes:** total minutes played in matches that week.

### MON-2.2 Data entry and missing data
Weekly data must be entered by 10:00 on Monday. If a player's sleep, soreness or wellness data is missing for one week, the Lead Physiotherapist checks in with the player before the first high-intensity session. If data is missing for two consecutive weeks, treat the player as Amber (see `WEL-4.6`) until the data is collected.

### MON-2.3 How ACWR is calculated
The acute:chronic workload ratio (ACWR) is this week's load divided by the average weekly load of the previous four weeks. ACWR needs at least four weeks of history to be meaningful.

After a period of absence (injury, illness or international duty), chronic load is low, so ACWR on return can look very high even when the actual load is modest. Staff should note this when interpreting ACWR for returning players.

### MON-2.4 Data quality checks
The Performance Analyst checks that values fall within plausible ranges before data reaches the risk tool: sleep 3 to 12 hours, all player-rated scales 1 to 10, weekly load 0 to 7,000 AU, and match minutes 0 to 200. Values outside these ranges must be confirmed with the player or staff member before they are used.

---

## Section 3: Load management (LM)

### LM-3.1 ACWR bands
| ACWR | Band | Meaning |
|---|---|---|
| Below 0.80 | Amber (under-loaded) | Player is doing less than usual, so not conditioned for a sudden return to full load |
| 0.80 to 1.30 | Green | Load is in line with what the player is used to |
| 1.31 to 1.50 | Amber (high) | Load is rising faster than usual |
| Above 1.50 | Red | Load spike; highest soft-tissue risk |

### LM-3.2 Green band: ACWR 0.80 to 1.30
A player in the Green band is available for full training as planned, including high-speed running and sprint work, with no load restrictions.

### LM-3.3 Amber (high) band: ACWR 1.31 to 1.50
- Next week's planned load must not rise by more than 10% from this week.
- The Head of Performance reviews the player's plan before the next high-intensity session.
- If a second Amber signal is present (see `WEL-4.6`), treat the player as Red.

### LM-3.4 Red band: ACWR above 1.50
- Cap next week's load at no more than 1.2 × the player's chronic load (four-week average).
- Remove high-speed running and sprint blocks for 48 hours.
- The Lead Physiotherapist carries out a physio screen within 24 hours.
- The player may still be selected for a match only with Medical Lead sign-off (`GOV-1.5`).

### LM-3.5 Amber (under-loaded) band: ACWR below 0.80
- Rebuild load gradually: increase weekly load by no more than 15% per week until ACWR is back in the Green band.
- Do not plan a full 90 minutes of match play until the player has had at least one week in the Green band, unless the Medical Lead approves.

### LM-3.6 Weeks with two matches
In a week with two matches, any starter with ACWR above 1.30 does a recovery-only session between the matches. The Head of Performance confirms the session plan with the Lead Physiotherapist.

---

## Section 4: Sleep and wellness warning signs (WEL)

### WEL-4.1 Short sleep
- Average sleep below 6.5 hours a night for the week: Amber. The player has a sleep conversation with the Performance staff.
- Average sleep below 6.0 hours a night for the week: Red. Wellness review with the Lead Physiotherapist before the next high-intensity session.

### WEL-4.2 Accumulated sleep debt
Sleep debt is the total hours below 7.5 hours a night over the last three weeks. A sleep debt above 10 hours is Amber and triggers a sleep-hygiene consultation, even if this week's sleep looks normal.

### WEL-4.3 Poor sleep quality
Sleep quality of 3 or below: Amber. The player has a short check-in with the Lead Physiotherapist to rule out pain, illness or stress as the cause.

### WEL-4.4 Soreness
- Soreness of 7: Amber. Physio check before any high-intensity session.
- Soreness of 8 or above, or soreness the player locates in the hamstring, groin or calf: Red. The player does not train at high intensity until the Lead Physiotherapist has assessed them.

### WEL-4.5 Low wellness
- Wellness of 4: Amber. The player has a conversation with a member of staff that week.
- Wellness of 3 or below: Red. Refer to the Club Doctor, because low wellness can be an early sign of illness. If the player raises personal or emotional difficulties, signpost the Player Welfare Officer. Mental health concerns are outside this protocol's scope (`GOV-1.2`).

### WEL-4.6 Combining warning signs
Two or more Amber signals in the same week, from any section of this protocol (ACWR, sleep, sleep debt, sleep quality, soreness, wellness, AI risk tier), are treated as Red. The Lead Physiotherapist screens the player within 24 hours.

---

## Section 5: Return to play (RTP)

### RTP-5.1 The six stages
| Stage | Name | What the player does |
|---|---|---|
| 1 | Protection | Rest, pain control, protected movement |
| 2 | Rehabilitation | Gym-based strength and mobility work, no running |
| 3 | On-field running | Straight-line running, building to high-speed running |
| 4 | Modified team training | Non-contact team drills, no full-intensity small-sided games |
| 5 | Full training | Full team training |
| 6 | Match play | Available for selection with minutes restrictions |

A player moves up one stage at a time and only with Lead Physiotherapist approval.

### RTP-5.2 Exit criteria before Stage 5
Before moving from Stage 4 to Stage 5, the player must:
- be pain-free in all Stage 4 drills,
- reach at least 90% strength compared with the uninjured side (for muscle injuries),
- have reached at least 80% of their pre-injury peak high-speed running distance in a session, and
- have Lead Physiotherapist sign-off.

### RTP-5.3 Stage 5: full training
A player who has met the Stage 4 exit criteria (`RTP-5.2`) and has Lead Physiotherapist sign-off may return to full, unrestricted team training, including high-speed running and sprint work. This lets the player rebuild match fitness before Stage 6.

### RTP-5.4 Stage 6: match play
- First match back: no more than 45 minutes.
- Second match back: no more than 70 minutes, if the first match caused no symptoms.
- Full match availability from the third match, with Medical Lead sign-off.

### RTP-5.5 Re-injury
If a player injures the same site within 8 weeks of returning to Stage 5, they go back to Stage 1 and are reviewed by the Club Doctor before rehabilitation restarts.

---

## Section 6: Use of the AI risk tool (AI)

### AI-6.1 Purpose
The AI risk tool uses weekly load, sleep, wellness, age, position and injury history to classify each player as Low or High injury risk for the coming week. It is a decision-support tool that helps the medical team decide whom to see first. It does not diagnose injuries and does not decide availability.

### AI-6.2 High-risk tier
When the tool classifies a player as High risk:
- the Lead Physiotherapist carries out a physio screen within 24 hours, and
- the player does modified training (no high-speed running or sprint blocks) until the screen is done.

A High-risk classification counts as one Amber signal under `WEL-4.6`.

### AI-6.3 Low-risk tier
A Low-risk classification is not medical clearance. Every other clause in this protocol still applies to the player.

### AI-6.4 What briefings may and may not say
Briefings generated by the AI risk tool must:
- cite the clause ID for every recommendation,
- name the main reasons behind the risk tier (for example ACWR, soreness, sleep),
- say clearly when the protocol does not cover the situation (`AI-6.6`).

Briefings must not:
- name or suggest a diagnosis,
- recommend medication, supplements or treatment,
- say that a player is "cleared", "fit to play" or "must be benched".

### AI-6.5 Medical sign-off
Every recommendation from the AI risk tool must be approved, edited or rejected by the Medical Lead, Club Doctor or Lead Physiotherapist before coaches see it. Any override needs a written reason, which is stored in the sign-off log. The Medical Lead reviews the override log every month.

### AI-6.6 When the protocol does not cover a situation
If no clause in this protocol applies, the briefing must say "The protocol does not cover this situation" and refer the case to the Medical Lead. The tool must not fill the gap with general medical or sports-science knowledge.

### AI-6.7 Who sees what
Coaches see only the player's status (available, modified, or unavailable) and the approved briefing. Raw sleep, soreness and wellness answers, and medical notes, are visible only to the medical and performance staff.

### AI-6.8 Known limits of the tool
The model was trained on synthetic data and has not been validated on real players. It will miss some injuries and raise many false alarms. Staff must not treat its output as more reliable than their own clinical judgement.

### AI-6.9 Uses that are not allowed
Risk scores and monitoring data must not be used for contract negotiations, transfer decisions, disciplinary action, or any purpose other than player health and load management. They must not be shared outside the club.

---

## Section 7: Escalation (ESC)

### ESC-7.1 Escalation matrix
| Trigger | Who is informed | By when |
|---|---|---|
| Any Red signal | Lead Physiotherapist | Within 24 hours |
| Two or more Amber signals (`WEL-4.6`) | Lead Physiotherapist | Within 24 hours |
| AI risk tool: High risk | Lead Physiotherapist | Within 24 hours |
| Clauses that conflict (`GOV-1.4`) | Medical Lead | Same day |
| Situation not covered by this protocol (`AI-6.6`) | Medical Lead | Same day |
| Wellness of 3 or below | Club Doctor | Same day |
| Re-injury during return to play | Club Doctor | Same day |
| Out-of-scope symptoms (`ESC-7.2`) | Club Doctor | Immediately |

### ESC-7.2 Immediate referral to the Club Doctor
Stop all training and refer the player to the Club Doctor immediately for any of the following: head injury or concussion symptoms, chest pain, fainting, breathlessness out of proportion to effort, fever, or any symptom the staff member is unsure about. These are outside this protocol's scope (`GOV-1.2`), and the AI risk tool must not give guidance on them.

### ESC-7.3 When the Medical Lead is unavailable
If the Medical Lead is unavailable, the Club Doctor takes their role. On match days, the Lead Physiotherapist on the bench makes in-match decisions and the Medical Lead reviews them within 24 hours.

### ESC-7.4 Key-match requests from the Head Coach
The Head Coach may ask the Medical Lead to consider making a Red-band or High-risk player available for a key fixture. The Medical Lead decides. The request, the decision and the reason are recorded in the sign-off log. The Head Coach cannot make the player available without that sign-off.

### ESC-7.5 Player review requests
A player who disagrees with a decision about their availability may ask the Medical Lead for a review. The Medical Lead responds within 48 hours.

---

## Section 8: Data privacy (PRIV)

### PRIV-8.1 Consent and purpose
Monitoring data and risk scores are health information about the player. The club collects them only with each player's informed consent and only for player health and load management, in line with the Digital Personal Data Protection Act, 2023. Players can withdraw consent at any time. The Medical Lead then explains how this affects how the medical team can monitor them.

### PRIV-8.2 Pseudonymisation
Player names are replaced with player IDs (for example `P017`) before any data is sent to an external service, including the language model used to write briefings. Only the club's own systems hold the link between ID and name.

### PRIV-8.3 Access control
Access follows `AI-6.7`. Every access to raw monitoring data is logged.

### PRIV-8.4 Retention
Monitoring data is kept while the player is at the club and for three years after they leave, then deleted. Players can ask to see the data held about them.

### PRIV-8.5 Data incidents
Any suspected loss, leak or misuse of player data must be reported to the Medical Lead and the club's Data Protection contact within 24 hours.

---

## Appendix A: Quick reference

| Signal | Amber | Red |
|---|---|---|
| ACWR (`LM-3.1`) | Below 0.80, or 1.31 to 1.50 | Above 1.50 |
| Sleep hours (`WEL-4.1`) | Below 6.5 | Below 6.0 |
| Sleep debt, 3 weeks (`WEL-4.2`) | Above 10 hours | n/a |
| Sleep quality (`WEL-4.3`) | 3 or below | n/a |
| Soreness (`WEL-4.4`) | 7 | 8 or above, or hamstring/groin/calf |
| Wellness (`WEL-4.5`) | 4 | 3 or below |
| AI risk tier (`AI-6.2`) | High | n/a |
| Two or more Ambers (`WEL-4.6`) | n/a | Treated as Red |

## Appendix B: Glossary
- **AU (arbitrary units):** the unit of session-RPE load.
- **Session-RPE:** session minutes × the player's effort rating (1 to 10).
- **Chronic load:** average weekly load over the previous four weeks.
- **ACWR:** acute:chronic workload ratio, this week's load divided by chronic load.
- **High-speed running:** running above 19.8 km/h.
- **Physio screen:** a short assessment by the Lead Physiotherapist of muscle tightness, range of movement and pain.
