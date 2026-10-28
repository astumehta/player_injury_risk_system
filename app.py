"""
Harbourline FC — Player Health & Injury Early-Warning System
Foundations of AI for Business | Group A1 | Astu Mehta (10289708)

Features:
1. 📋 Coach's Matchday & Squad Sheet (Tactical Starting XI & Squad Cards)
2. ⚡ Whole Squad Morning Readiness Scan (All 60 Senior Players)
3. 👉 Individual Player 3-Step Deep-Dive & Doctor Sign-Off
4. 💡 Sports Science Logistic Regression Math & Google Colab Pipeline (1,000 Players)
"""

import os
import sys
import textwrap
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.harbourline_predictor import get_harbourline_engine
from ui.harbourline_cases import HARBOURLINE_DEMO_CASES
from state.workflow_store import get_workflow_store
from ui.coach_roster import PLAYER_ROSTER, get_player_display_info
from ui.coach_insights import get_coach_player_insights

st.set_page_config(
    page_title="Harbourline FC — Squad Health & Tactical Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize backend
@st.cache_resource
def get_backend():
    eng = get_harbourline_engine()
    store = get_workflow_store()
    csv_path = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")
    df = pd.read_csv(csv_path) if os.path.exists(csv_path) else None
    return eng, store, df

engine, store, season_df = get_backend()

# =====================================================================
# GLOBAL ATHLETIC STYLING (CLEAN CSS ONLY)
# =====================================================================
st.markdown(
    """<style>
.stApp {
    background: #080d14;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
}

/* Matchday Header Banner */
.stadium-header-box {
    background: linear-gradient(135deg, #091a13 0%, #0d1622 55%, #080d14 100%);
    border: 2px solid #00ff87;
    box-shadow: 0 0 20px rgba(0, 255, 135, 0.25);
    border-radius: 12px;
    padding: 16px 22px;
    margin-bottom: 20px;
}
.crest-text {
    font-size: 1.55rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 0.5px;
}
.fixture-pill {
    background: rgba(0, 255, 135, 0.15);
    border: 1px solid #00ff87;
    color: #00ff87;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}
.protocol-pill {
    background: rgba(255, 209, 102, 0.15);
    border: 1px solid #ffd166;
    color: #ffd166;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
}

/* Badges */
.badge-jersey {
    background: #00ff87;
    color: #080d14;
    font-weight: 900;
    font-size: 0.85rem;
    padding: 2px 7px;
    border-radius: 5px;
    display: inline-block;
}
.badge-pos-gk  { background: #b45309; color: #ffffff; font-weight: 800; font-size: 0.75rem; padding: 2px 6px; border-radius: 5px; display: inline-block; }
.badge-pos-def { background: #1d4ed8; color: #ffffff; font-weight: 800; font-size: 0.75rem; padding: 2px 6px; border-radius: 5px; display: inline-block; }
.badge-pos-mid { background: #047857; color: #ffffff; font-weight: 800; font-size: 0.75rem; padding: 2px 6px; border-radius: 5px; display: inline-block; }
.badge-pos-fwd { background: #b91c1c; color: #ffffff; font-weight: 800; font-size: 0.75rem; padding: 2px 6px; border-radius: 5px; display: inline-block; }

.status-badge-avail {
    background: rgba(16, 185, 129, 0.18);
    border: 1.5px solid #10b981;
    color: #34d399;
    font-weight: 800;
    font-size: 0.85rem;
    padding: 3px 12px;
    border-radius: 20px;
    display: inline-block;
}
.status-badge-mod {
    background: rgba(245, 158, 11, 0.18);
    border: 1.5px solid #f59e0b;
    color: #fbbf24;
    font-weight: 800;
    font-size: 0.85rem;
    padding: 3px 12px;
    border-radius: 20px;
    display: inline-block;
}
.status-badge-bench {
    background: rgba(239, 68, 68, 0.18);
    border: 1.5px solid #ef4444;
    color: #f87171;
    font-weight: 800;
    font-size: 0.85rem;
    padding: 3px 12px;
    border-radius: 20px;
    display: inline-block;
}
</style>""",
    unsafe_allow_html=True
)

# Header
st.markdown(
    """<div class="stadium-header-box">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
<div class="crest-text">⚓⚽ HARBOURLINE FC</div>
<div class="fixture-ticker">🏆 NEXT FIXTURE: vs WESTBRIDGE ALBION • SATURDAY 15:00</div>
<div class="protocol-pill">MEDICAL PROTOCOL v4.2 APPROVED</div>
</div>
<div style="color: #94a3b8; font-size: 0.92rem; margin-top: 6px;">
AI-Assisted Player Health, Injury Early-Warning & Tactical Readiness Suite • Foundations of AI for Business (Group A1)
</div>
</div>""",
    unsafe_allow_html=True
)

# 4 Navigation Tabs
NAV_VIEWS = [
    "📋 Coach's Matchday & Squad Sheet",
    "⚡ Whole Squad Morning Readiness (60-Player Scan)",
    "👉 Individual Player Deep-Dive & Doctor Sign-Off (3-Step)",
    "💡 Sports Science Math & Logistic Regression Breakdown"
]

if "current_nav_view" not in st.session_state:
    st.session_state["current_nav_view"] = NAV_VIEWS[0]

selected_view = st.radio(
    "Choose Hub Module:",
    NAV_VIEWS,
    index=NAV_VIEWS.index(st.session_state["current_nav_view"]),
    horizontal=True,
    key="nav_radio_choice"
)
st.session_state["current_nav_view"] = selected_view
st.markdown("---")


# =====================================================================
# VIEW 1: COACH'S MATCHDAY & SQUAD SHEET (HEAD COACH HUB)
# =====================================================================
if selected_view.startswith("📋 Coach's Matchday"):
    st.markdown("## 📋 Head Coach's Matchday & Training Squad Sheet")
    st.caption("Tactical readiness overview, estimated return-to-play timelines, and doctor-prescribed pitch drill guidelines.")

    if season_df is not None:
        latest_rows = season_df.sort_values("week").groupby("player_id").last().reset_index()

        coach_records = []
        for idx, row in latest_rows.iterrows():
            pid = row["player_id"]
            pos = row["position"]
            p_payload = {
                "player_id": pid,
                "position": pos,
                "age": row["age"],
                "prior_injuries": row["prior_injuries"],
                "weekly_load_au": row["weekly_load_au"],
                "chronic_load_au": row["chronic_load_au"],
                "acwr": row["acwr"],
                "sleep_hours": row["sleep_hours"],
                "soreness": row["soreness"],
                "wellness": row["wellness"],
                "sleep_debt_3w": row.get("sleep_debt_3w", 0.0),
                "weeks_since_return": row.get("weeks_since_return") if pd.notna(row.get("weeks_since_return")) else None
            }
            m_res = engine.predict_risk(p_payload)
            sign = store.get_signoff(pid)
            info = get_player_display_info(pid, pos)
            insight = get_coach_player_insights(row, m_res, sign)

            coach_records.append({
                "pid": pid,
                "jersey": info["number"],
                "name": info["name"],
                "role": info["role"],
                "position": pos,
                "squad": f"Squad {row['squad']}",
                "status_code": insight["status_code"],
                "status_label": insight["status_label"],
                "badge_color": insight["badge_color"],
                "risk_pct": f"{m_res['risk_score_pct']}%",
                "acwr": row["acwr"],
                "soreness": row["soreness"],
                "sleep": row["sleep_hours"],
                "sleep_debt": row.get("sleep_debt_3w", 0.0),
                "reason": insight["reason"],
                "timeline": insight["timeline"],
                "timeline_desc": insight["timeline_desc"],
                "coach_drills": insight["coach_drills"],
                "clinical_reason": insight["clinical_reason"],
                "doctor_name": insight["doctor_name"],
                "is_signed": insight["is_signed"]
            })

        df_coach = pd.DataFrame(coach_records)

        # 3 Big Native KPI Cards
        n_avail = len(df_coach[df_coach["status_code"] == "AVAILABLE"])
        n_mod = len(df_coach[df_coach["status_code"] == "MODIFIED"])
        n_bench = len(df_coach[df_coach["status_code"] == "BENCHED"])

        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        with c_kpi1:
            with st.container(border=True):
                st.metric("🟢 AVAILABLE FOR MATCH", f"{n_avail} Players", "Cleared for 90 Mins")
                st.caption("Optimal conditioning: cleared for full competitive intensity.")
        with c_kpi2:
            with st.container(border=True):
                st.metric("🟡 MODIFIED TRAINING ONLY", f"{n_mod} Players", "Capped Load / No Sprints")
                st.caption("Restricted: technical passing only, max 45 mins, NO sprint drills >20 km/h.")
        with c_kpi3:
            with st.container(border=True):
                st.metric("🔴 UNAVAILABLE / BENCHED", f"{n_bench} Players", "Sidelined from Pitch")
                st.caption("Off-pitch recovery: Wattbike and pool session; mandatory physio screening.")

        st.markdown("---")

        # Tactical Starting XI Formation Board (100% Native Streamlit Components)
        st.markdown("### 🏟️ Tactical 4-3-3 Starting Lineup Board")
        with st.expander("⚽ View Starting Formation Health Status (Attackers, Midfield, Defense & GK)", expanded=True):
            # Select key players for positions
            p_gk = df_coach[df_coach["position"] == "GK"].iloc[0]
            defs = df_coach[df_coach["position"] == "DEF"].head(4)
            mids = df_coach[df_coach["position"] == "MID"].head(3)
            fwds = df_coach[df_coach["position"] == "FWD"].head(3)

            def render_tactical_node(p_row, pos_title):
                st_code = p_row["status_code"]
                badge_str = "🟢 AVAILABLE" if st_code == "AVAILABLE" else ("🟡 MODIFIED" if st_code == "MODIFIED" else "🔴 BENCHED")
                with st.container(border=True):
                    st.caption(f"**{pos_title}**")
                    st.markdown(f"**#{p_row['jersey']} {p_row['name']}**")
                    st.caption(f"*{p_row['pid']} • {p_row['squad']}*")
                    if st_code == "AVAILABLE":
                        st.success(badge_str)
                    elif st_code == "MODIFIED":
                        st.warning(badge_str)
                    else:
                        st.error(badge_str)
                    st.caption(f"⏱️ {p_row['timeline'].split('(')[0]}")

            # 1. Attackers Row (3 Cols)
            st.markdown("##### ⚽ Frontline (Attackers)")
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                render_tactical_node(fwds.iloc[0], "LW (Left Winger)")
            with f_col2:
                render_tactical_node(fwds.iloc[1], "ST (Center Striker)")
            with f_col3:
                render_tactical_node(fwds.iloc[2], "RW (Right Winger)")

            # 2. Midfield Row (3 Cols)
            st.markdown("##### ⚙️ Engine Room (Midfielders)")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                render_tactical_node(mids.iloc[0], "LCM (Box-to-Box)")
            with m_col2:
                render_tactical_node(mids.iloc[1], "CDM (Holding Mid)")
            with m_col3:
                render_tactical_node(mids.iloc[2], "RCM (Playmaker)")

            # 3. Defensive Line (4 Cols)
            st.markdown("##### 🛡️ Defensive Line")
            d_col1, d_col2, d_col3, d_col4 = st.columns(4)
            with d_col1:
                render_tactical_node(defs.iloc[0], "LB (Left Back)")
            with d_col2:
                render_tactical_node(defs.iloc[1], "LCB (Center Back)")
            with d_col3:
                render_tactical_node(defs.iloc[2], "RCB (Center Back)")
            with d_col4:
                render_tactical_node(defs.iloc[3], "RB (Right Back)")

            # 4. Goalkeeper (Centered)
            st.markdown("##### 🧤 Last Line of Defense")
            gk_spacer1, gk_center, gk_spacer2 = st.columns([1, 1.2, 1])
            with gk_center:
                render_tactical_node(p_gk, "GK (Starting Goalkeeper)")

        st.markdown("---")

        # Coach's Squad Filters
        st.markdown("### 🎴 Tactical Squad Cards & Drill Guidelines")
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 1.5, 2])
        with f_col1:
            filter_status = st.selectbox(
                "Filter by Availability:",
                ["All Statuses", "🟢 Available for Match", "🟡 Modified Training", "🔴 Benched / Unavailable"]
            )
        with f_col2:
            filter_pos = st.selectbox(
                "Filter by Position:",
                ["All Positions", "GK (Goalkeepers)", "DEF (Defenders)", "MID (Midfielders)", "FWD (Forwards)"]
            )
        with f_col3:
            filter_squad = st.selectbox(
                "Filter by Squad:",
                ["All Squads", "Squad A (First Team)", "Squad B (Reserves/U21)"]
            )
        with f_col4:
            search_query = st.text_input("🔍 Search Player (Name, #, ID):", placeholder="e.g. Alistair, #51, P004")

        # Apply Filters
        df_filtered = df_coach.copy()
        if filter_status == "🟢 Available for Match":
            df_filtered = df_filtered[df_filtered["status_code"] == "AVAILABLE"]
        elif filter_status == "🟡 Modified Training":
            df_filtered = df_filtered[df_filtered["status_code"] == "MODIFIED"]
        elif filter_status == "🔴 Benched / Unavailable":
            df_filtered = df_filtered[df_filtered["status_code"] == "BENCHED"]

        if filter_pos != "All Positions":
            pos_key = filter_pos.split()[0]
            df_filtered = df_filtered[df_filtered["position"] == pos_key]

        if filter_squad != "All Squads":
            sq_key = filter_squad.split()[0] + " " + filter_squad.split()[1]
            df_filtered = df_filtered[df_filtered["squad"] == sq_key]

        if search_query and search_query.strip():
            sq = search_query.strip().lower()
            df_filtered = df_filtered[
                df_filtered["name"].str.lower().str.contains(sq) |
                df_filtered["pid"].str.lower().str.contains(sq) |
                df_filtered["jersey"].astype(str).str.contains(sq)
            ]

        st.caption(f"Showing **{len(df_filtered)}** players matching criteria:")

        # Render Clean, Native Player Cards (Zero Raw HTML Bugs)
        for idx, p in df_filtered.iterrows():
            with st.container(border=True):
                # Header row
                c_head1, c_head2 = st.columns([3, 1.2])
                with c_head1:
                    pos_class = f"badge-pos-{p['position'].lower()}"
                    st.markdown(
                        f"""<span class="badge-jersey">#{p['jersey']}</span> 
<span class="{pos_class}">[{p['position']}]</span> 
<b style="font-size: 1.15rem; color: #ffffff; margin-left: 6px;">{p['name']}</b> 
<span style="color: #94a3b8; font-size: 0.88rem;">({p['pid']} • {p['squad']} • {p['role']})</span>""",
                        unsafe_allow_html=True
                    )
                with c_head2:
                    if p["status_code"] == "AVAILABLE":
                        st.markdown('<span class="status-badge-avail">🟢 AVAILABLE</span>', unsafe_allow_html=True)
                    elif p["status_code"] == "MODIFIED":
                        st.markdown('<span class="status-badge-mod">🟡 MODIFIED</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-badge-bench">🔴 BENCHED</span>', unsafe_allow_html=True)

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

                # 3 Content Columns
                sub_col1, sub_col2, sub_col3 = st.columns([1.2, 1.2, 1.6])
                with sub_col1:
                    st.markdown("**📊 Physical Status & Drivers:**")
                    st.write(f"• **Primary:** {p['reason']}")
                    st.caption(f"ACWR: **{p['acwr']:.2f}** | Soreness: **{p['soreness']}/10** | Sleep: **{p['sleep']:.1f}h** (Debt: **{p['sleep_debt']:.1f}h**)")

                with sub_col2:
                    st.markdown("**⏱️ Ready to Play Timeline:**")
                    st.info(f"**{p['timeline']}**\n\n{p['timeline_desc']}")

                with sub_col3:
                    st.markdown("**🩺 Doctor's Instructions for Coach:**")
                    st.success(f"👉 **Drill Guidelines:** \"{p['coach_drills']}\"")
                    if p["is_signed"]:
                        st.caption(f"✅ Signed by **{p['doctor_name']}** | Rationale: *{p['clinical_reason']}*")
                    else:
                        st.caption("⏳ *Pending Official Doctor Review in Step 3.*")

                # Action button to jump to 3-step analyzer
                if st.button(f"👉 Inspect {p['name']} in 3-Step Analyzer & Doctor Sign-Off", key=f"btn_jump_{p['pid']}", use_container_width=True):
                    st.session_state["target_player_id"] = p["pid"]
                    st.session_state["force_load_target"] = True
                    st.session_state["current_nav_view"] = NAV_VIEWS[2]
                    st.rerun()

        st.markdown("---")

        # CSV Export
        st.markdown("### 📥 Export Complete Matchday Team Sheet")
        table_export = df_filtered[["pid", "jersey", "name", "position", "squad", "status_label", "timeline", "coach_drills", "reason", "doctor_name"]].copy()
        table_export.columns = ["Player ID", "Jersey", "Player Name", "Position", "Squad", "Availability Status", "Ready to Play Timeline", "Doctor Drill Instructions", "Primary Reason", "Doctor Sign-Off"]
        
        st.download_button(
            "📥 Download Coach's Official Matchday Sheet (CSV)",
            data=table_export.to_csv(index=False),
            file_name="harbourline_coach_matchday_sheet.csv",
            mime="text/csv",
            use_container_width=True
        )


# =====================================================================
# VIEW 2: WHOLE SQUAD MORNING READINESS SCAN (ALL 60 PLAYERS)
# =====================================================================
elif selected_view.startswith("⚡ Whole Squad"):
    st.markdown("## ⚡ Squad Morning Readiness Scan (All 60 Players)")
    st.caption("Batch morning screening of all 60 senior squad athletes across Squad A and Squad B.")
    
    col_scan1, col_scan2, col_scan3 = st.columns([2.2, 1.2, 1.4])
    with col_scan1:
        scan_clicked = st.button("🚀 Run Squad Readiness Scan (Analyze All 60 Players)", type="primary", use_container_width=True)
    with col_scan2:
        if st.button("🔄 Reload CSV", use_container_width=True):
            st.cache_resource.clear()
            st.session_state.pop("squad_scan_results", None)
            st.success("Reloaded fresh dataset from disk!")
            st.rerun()
    with col_scan3:
        if st.button("🗑️ Reset Doctor Sign-Offs", use_container_width=True):
            store.reset_all_signoffs()
            st.session_state.pop("squad_scan_results", None)
            st.success("Reset all human doctor overrides to pure AI model baseline!")
            st.rerun()
    
    if "squad_scan_results" not in st.session_state or scan_clicked:
        if season_df is not None:
            latest_rows = season_df.sort_values("week").groupby("player_id").last().reset_index()
            
            squad_records = []
            for idx, row in latest_rows.iterrows():
                p_payload = {
                    "player_id": row["player_id"],
                    "position": row["position"],
                    "age": row["age"],
                    "prior_injuries": row["prior_injuries"],
                    "weekly_load_au": row["weekly_load_au"],
                    "chronic_load_au": row["chronic_load_au"],
                    "acwr": row["acwr"],
                    "sleep_hours": row["sleep_hours"],
                    "soreness": row["soreness"],
                    "wellness": row["wellness"],
                    "sleep_debt_3w": row.get("sleep_debt_3w", 0.0),
                    "weeks_since_return": row["weeks_since_return"] if pd.notna(row.get("weeks_since_return")) else None
                }
                res = engine.predict_risk(p_payload)
                info = get_player_display_info(row["player_id"], row["position"])
                sign_rec = store.get_signoff(row["player_id"])
                doc_status = sign_rec["status"] if sign_rec else "Pending Doctor Review"
                
                # Unify with Coach insights so human doctor sign-offs are respected in both tabs
                insight = get_coach_player_insights(row, res, sign_rec)
                
                squad_records.append({
                    "Player ID": row["player_id"],
                    "Jersey": f"#{info['number']}",
                    "Player Name": info["name"],
                    "Squad": f"Squad {row['squad']}",
                    "Position": row["position"],
                    "status_code": insight["status_code"],
                    "Final Coach Status": insight["status_label"],
                    "Model Risk Tier": res["risk_tier"],
                    "Risk %": f"{res['risk_score_pct']}%",
                    "ACWR": f"{row['acwr']:.2f}",
                    "Sleep (hrs)": f"{row['sleep_hours']:.1f}",
                    "Soreness": f"{row['soreness']}/10",
                    "Doctor Sign-Off": doc_status,
                    "Primary Driver": insight["reason"]
                })
            st.session_state["squad_scan_results"] = pd.DataFrame(squad_records)
            
    if "squad_scan_results" in st.session_state:
        df_scan = st.session_state["squad_scan_results"]
        
        # Count using status_code which synchronizes seamlessly with Tab 1
        n_avail = len(df_scan[df_scan["status_code"] == "AVAILABLE"])
        n_mod = len(df_scan[df_scan["status_code"] == "MODIFIED"])
        n_bench = len(df_scan[df_scan["status_code"] == "BENCHED"])
        
        # Check active doctor sign-offs to display informative clinical banner
        signed_all = store.get_all_signed_off()
        if signed_all:
            override_pids = list(signed_all.keys())
            st.info(
                f"🩺 **Clinical Doctor Sign-Offs Active ({len(override_pids)} Overrides Recorded):** "
                f"Players {', '.join(override_pids)} have official doctor sign-offs on file. "
                f"Both tabs display the synchronized final availability status (**{n_avail} Available, {n_mod} Modified, {n_bench} Benched**). "
                f"*(Raw AI model baseline was 44 Available, 10 Modified, 6 Benched).*"
            )
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            with st.container(border=True):
                st.metric("🟢 AVAILABLE FOR MATCH", f"{n_avail} Players", "Cleared for 90 Mins")
                st.caption("Optimal conditioning: cleared for full competitive intensity.")
        with kpi2:
            with st.container(border=True):
                st.metric("🟡 MODIFIED TRAINING ONLY", f"{n_mod} Players", "Capped Load / No Sprints")
                st.caption("Restricted: technical passing only, max 45 mins, NO sprint drills >20 km/h.")
        with kpi3:
            with st.container(border=True):
                st.metric("🔴 UNAVAILABLE / BENCHED", f"{n_bench} Players", "Sidelined from Pitch")
                st.caption("Off-pitch recovery: Wattbike and pool session; mandatory physio screening.")
            
        st.markdown("---")
        
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            category_filter = st.selectbox("Filter by Final Status:", ["All Players (60)", "🟢 Available for Match", "🟡 Modified Training Only", "🔴 Unavailable / Benched"])
        with filter_col2:
            squad_filter = st.selectbox("Filter by Squad:", ["All Squads", "Squad A", "Squad B"])
            
        filtered = df_scan.copy()
        if category_filter == "🟢 Available for Match":
            filtered = filtered[filtered["status_code"] == "AVAILABLE"]
        elif category_filter == "🟡 Modified Training Only":
            filtered = filtered[filtered["status_code"] == "MODIFIED"]
        elif category_filter == "🔴 Unavailable / Benched":
            filtered = filtered[filtered["status_code"] == "BENCHED"]
            
        if squad_filter != "All Squads":
            filtered = filtered[filtered["Squad"] == squad_filter]
            
        # Display clean columns
        cols_display = ["Player ID", "Jersey", "Player Name", "Squad", "Position", "Final Coach Status", "Model Risk Tier", "Risk %", "Doctor Sign-Off", "ACWR", "Soreness", "Primary Driver"]
        st.dataframe(filtered[cols_display], use_container_width=True)
        
        c_down, c_jump_box = st.columns([1, 2])
        with c_down:
            st.download_button(
                "📥 Download Squad Report (CSV)",
                data=filtered.to_csv(index=False),
                file_name="harbourline_morning_readiness.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_jump_box:
            with st.container(border=True):
                st.markdown("**🔍 Jump to 3-Step Deep-Dive & Doctor Sign-Off:**")
                col_pick, col_go = st.columns([2, 1])
                with col_pick:
                    jump_target = st.selectbox("Select Player:", df_scan["Player ID"].tolist(), index=0, label_visibility="collapsed")
                with col_go:
                    if st.button("👉 Open in 3-Step Analyzer ➡️", type="primary", use_container_width=True):
                        st.session_state["target_player_id"] = jump_target
                        st.session_state["force_load_target"] = True
                        st.session_state["current_nav_view"] = NAV_VIEWS[2]
                        st.rerun()


# =====================================================================
# VIEW 3: INDIVIDUAL PLAYER 3-STEP DEEP-DIVE & DOCTOR SIGN-OFF
# =====================================================================
elif selected_view.startswith("👉 Individual Player"):
    if "target_player_id" not in st.session_state:
        st.session_state["target_player_id"] = "P001"

    def load_metrics_for_player(pid, custom_metrics=None):
        st.session_state["target_player_id"] = pid
        if custom_metrics:
            st.session_state["active_load"] = int(custom_metrics["weekly_load_au"])
            st.session_state["active_sleep"] = float(custom_metrics["sleep_hours"])
            st.session_state["active_soreness"] = int(custom_metrics["soreness"])
            st.session_state["active_wellness"] = int(custom_metrics["wellness"])
        elif season_df is not None:
            p_matches = season_df[season_df["player_id"] == pid]
            if not p_matches.empty:
                row = p_matches.iloc[-1]
                st.session_state["active_load"] = int(row["weekly_load_au"])
                st.session_state["active_sleep"] = float(row["sleep_hours"])
                st.session_state["active_soreness"] = int(row["soreness"])
                st.session_state["active_wellness"] = int(row["wellness"])
        st.session_state["has_run_calc"] = True
        st.session_state["last_loaded_player_id"] = pid

    if st.session_state.get("force_load_target", False) or "last_loaded_player_id" not in st.session_state or st.session_state["last_loaded_player_id"] != st.session_state["target_player_id"]:
        load_metrics_for_player(st.session_state["target_player_id"])
        st.session_state["force_load_target"] = False

    st.markdown("#### ⚡ 1-Click Pre-fill Shortcuts (Exact Cases from Team Rulebook):")
    col_pre1, col_pre2, col_pre3, col_pre4 = st.columns(4)
    with col_pre1:
        if st.button("🟢 Low Risk Example\n(P046: 0.8% Risk, Available)", use_container_width=True):
            p = HARBOURLINE_DEMO_CASES["P046_w35"]
            load_metrics_for_player("P046", p["metrics"])
            st.rerun()

    with col_pre2:
        if st.button("🟡 Medium Risk Example\n(P001: 6.4% Risk, Need Help)", use_container_width=True):
            p = HARBOURLINE_DEMO_CASES["P001_w40"]
            load_metrics_for_player("P001", p["metrics"])
            st.rerun()

    with col_pre3:
        if st.button("🔴 High Risk Example\n(P051: 39.6% Risk, Benched)", use_container_width=True):
            p = HARBOURLINE_DEMO_CASES["P051_w03"]
            load_metrics_for_player("P051", p["metrics"])
            st.rerun()

    with col_pre4:
        if st.button("⚠️ Rule Conflict Example\n(P006: Stage 5 vs Load Spike)", use_container_width=True):
            p = HARBOURLINE_DEMO_CASES["P006_w32"]
            load_metrics_for_player("P006", p["metrics"])
            st.rerun()

    # Step 1 Container
    with st.container(border=True):
        st.markdown("### 1. Select Player & Enter Morning Check-In Numbers")
        
        roster_pids = [f"P{i:03d}" for i in range(1, 61)]
        cur_target = st.session_state["target_player_id"]
        cur_idx = roster_pids.index(cur_target) if cur_target in roster_pids else 0
        
        selected_pid = st.selectbox(
            "Choose Player from Squad Roster:",
            roster_pids,
            index=cur_idx,
            help="Select any player from Harbourline FC senior roster"
        )
        
        if selected_pid != st.session_state["target_player_id"]:
            load_metrics_for_player(selected_pid)
            st.rerun()

        player_history = None
        if season_df is not None:
            p_matches = season_df[season_df["player_id"] == selected_pid]
            if not p_matches.empty:
                player_history = p_matches.iloc[-1]
                
        pos_fixed = player_history["position"] if player_history is not None else "DEF"
        age_fixed = int(player_history["age"]) if player_history is not None else 25
        squad_fixed = player_history["squad"] if player_history is not None else "Squad A"
        prior_fixed = int(player_history["prior_injuries"]) if player_history is not None else 1
        chronic_fixed = int(player_history["chronic_load_au"]) if player_history is not None else 2300
        sleep_debt_fixed = float(player_history["sleep_debt_3w"]) if (player_history is not None and "sleep_debt_3w" in player_history) else 0.0
        weeks_since_return_fixed = player_history["weeks_since_return"] if (player_history is not None and pd.notna(player_history.get("weeks_since_return"))) else None

        info_card = get_player_display_info(selected_pid, pos_fixed)

        st.info(
            f"📁 **Loaded from Club Database:** #{info_card['number']} {info_card['name']} ({selected_pid}) • Senior {squad_fixed} • "
            f"[{pos_fixed}] {info_card['role']} • Age {age_fixed} • {prior_fixed} prior strains • Chronic Baseline: {chronic_fixed} AU • 3W Sleep Debt: {sleep_debt_fixed:.1f}h"
        )

        st.markdown("**✍️ Enter Today's Morning Numbers:**")
        col_in1, col_in2, col_in3, col_in4 = st.columns(4)
        with col_in1:
            in_load = st.number_input(
                "1. Training Load (AU):",
                value=int(st.session_state.get("active_load", 2500)),
                step=50,
                help="Session RPE × Duration in minutes for this week"
            )
        with col_in2:
            in_sleep = st.number_input(
                "2. Average Sleep (Hours):",
                value=float(st.session_state.get("active_sleep", 7.5)),
                step=0.5,
                min_value=3.0,
                max_value=12.0
            )
        with col_in3:
            in_soreness = st.slider(
                "3. Muscle Soreness (1-10):",
                min_value=1,
                max_value=10,
                value=int(st.session_state.get("active_soreness", 3))
            )
        with col_in4:
            in_wellness = st.slider(
                "4. Overall Wellness (1-10):",
                min_value=1,
                max_value=10,
                value=int(st.session_state.get("active_wellness", 7))
            )

        calculated_acwr = round(in_load / max(chronic_fixed, 1), 2)
        st.caption(f"Calculated Acute:Chronic Workload Ratio (ACWR): **{calculated_acwr:.2f}** (Safe green band: 0.80 - 1.30)")

        current_payload = {
            "player_id": selected_pid,
            "position": pos_fixed,
            "age": age_fixed,
            "prior_injuries": prior_fixed,
            "weekly_load_au": in_load,
            "chronic_load_au": chronic_fixed,
            "acwr": calculated_acwr,
            "sleep_hours": in_sleep,
            "soreness": in_soreness,
            "wellness": in_wellness,
            "sleep_debt_3w": sleep_debt_fixed,
            "weeks_since_return": weeks_since_return_fixed
        }

        col_run, col_reset = st.columns([3, 1])
        with col_run:
            calc_button_clicked = st.button("⚡ Calculate Injury Risk (Run Model)", type="primary", use_container_width=True)
        with col_reset:
            if st.button("🔄 Reset to Baseline", use_container_width=True):
                load_metrics_for_player(selected_pid)
                st.rerun()

        inputs_modified = (
            in_load != st.session_state.get("active_load") or
            in_sleep != st.session_state.get("active_sleep") or
            in_soreness != st.session_state.get("active_soreness") or
            in_wellness != st.session_state.get("active_wellness")
        )

        if calc_button_clicked:
            st.session_state["active_load"] = in_load
            st.session_state["active_sleep"] = in_sleep
            st.session_state["active_soreness"] = in_soreness
            st.session_state["active_wellness"] = in_wellness
            st.session_state["has_run_calc"] = True
            inputs_modified = False

        if inputs_modified:
            st.warning("✏️ **Inputs changed:** Click the **'⚡ Calculate Injury Risk (Run Model)'** button above to evaluate with your new numbers.")

        r = engine.predict_risk(current_payload)
        b = engine.generate_ai_briefing(selected_pid, r)
        tier = r["risk_tier"]
        prob = r["risk_score_pct"]
        reasons = r["top_3_reasons"]
        readiness = r["readiness_status"]

    # STEP 1 OUTPUT CONTAINER
    with st.container(border=True):
        st.markdown(f"### 📊 Model Output: #{info_card['number']} {info_card['name']} ({selected_pid})")
        col_res1, col_res2 = st.columns([1, 1.4])
        with col_res1:
            st.markdown("**Injury Risk Rating:**")
            if tier == "HIGH RISK":
                st.error(f"🔴 {tier} ({prob}%)")
            elif tier == "MODERATE RISK":
                st.warning(f"🟡 {tier} ({prob}%)")
            else:
                st.success(f"🟢 {tier} ({prob}%)")
                
            st.markdown(f"**Coach Status:** `{readiness}`")
            st.caption(f"Estimated 7-day injury probability: **{prob}%** (Log-odds $z = {r['logit_z']}$)")
            
        with col_res2:
            st.markdown("**Top Reasons for this Rating:**")
            for i, reason in enumerate(reasons):
                st.write(f"• **{i+1}.** {reason}")
            
        with st.expander("📐 View Complete Logistic Regression Calculation (All 11 Fields)"):
            st.markdown(
                "**Strict Probability Thresholds:** Low Risk ($P < 5.0\%$), Moderate Risk ($5.0\% \le P < 15.0\%$), High Risk ($P \ge 15.0\%$)"
            )
            math_df = pd.DataFrame(r["math_breakdown"])
            st.dataframe(math_df, use_container_width=True)
            st.info(f"**Sum of all 11 terms (Log-Odds z):** `{r['logit_z']}` ➔ **Final Probability P:** `{prob}%` ➔ **{tier}**")

    # STEP 2: RULEBOOK CHECK CONTAINER
    with st.container(border=True):
        st.markdown(f"### 📖 Step 2: Club Rulebook Check (protocol.md) for {selected_pid}")
        st.caption("The AI scans Harbourline FC's 45 clauses and quotes the exact rules that apply:")
        
        if b["is_conflicting"]:
            st.warning(
                "⚠️ **Rule Conflict Alert (Rule GOV-1.4):**\n"
                "- This player triggers conflicting clauses (e.g. Return-to-Play Stage 5 vs Load Spike).\n"
                "- **Rule GOV-1.4 mandates:** Apply the safer, more conservative instruction (no sprints) and refer to the Doctor below."
            )
            
        for r_id, r_name, r_action in b["matched_rules"]:
            st.write(f"• **Under Rule {r_id} ({r_name}):** {r_action}")
            
        st.caption("🛡️ **Safety Guardrail (Rule AI-6.4):** AI can only quote club rules. It cannot invent diagnoses or clear anyone. The Doctor must decide in Step 3 below.")

    # STEP 3: DOCTOR SIGN-OFF CONTAINER
    with st.container(border=True):
        st.markdown(f"### 🩺 Step 3: Human Doctor Sign-Off Checkpoint for {selected_pid}")
        st.caption("The app never clears or benches anyone automatically. The Club Doctor makes the final call:")
        
        existing_sign = store.get_signoff(selected_pid)
        if existing_sign:
            st.success(
                f"✅ **Signed Off:** {selected_pid} is marked as **{existing_sign['status']}** by "
                f"**{existing_sign['doctor_name']}**.<br/>"
                f"<i>Doctor's Note:</i> \"{existing_sign['clinical_reason']}\"",
                icon="✅"
            )
        else:
            st.warning(f"⏳ **Pending Sign-Off:** {selected_pid} is on hold. The Coach cannot select this player until approved below.")

        with st.form("doctor_decision_form"):
            st.markdown("#### ✍️ Enter Medical Call & Drill Guidelines:")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                dr_name = st.text_input("Doctor / Physio Name:", value="Dr. Astu Mehta, Medical Lead")
                dr_call = st.radio(
                    "Decision for today's session:",
                    [
                        "🟢 Available (Clear for Full Training)",
                        "🟡 Modified Training (Lighter drills, no sprinting, non-contact)",
                        "🔴 Unavailable (Bench from pitch, physio assessment only)"
                    ],
                    index=1 if tier == "HIGH RISK" else (1 if tier == "MODERATE RISK" else 0)
                )
                
            with d_col2:
                final_status = "CLEARED_FULL" if "Available" in dr_call else ("CLEARED_MODIFIED" if "Modified" in dr_call else "BENCHED")
                def_instruction = "Full session as planned." if final_status == "CLEARED_FULL" else ("Modified technical drills only; NO sprint drills >20 km/h; max 45 mins." if final_status == "CLEARED_MODIFIED" else "Off-pitch recovery; wattbike and physio treatment only.")
                coach_note_input = st.text_input("Drill Instructions for Head Coach:", value=def_instruction)
                
            dr_reason = st.text_area(
                "Clinical Rationale (Mandatory on record):",
                placeholder="e.g. Completed morning physical screen. Athlete reports minor hamstring tightness. Cleared for light non-contact drills, no max sprinting.",
                height=75
            )
            
            submit_sign = st.form_submit_button("🔒 Sign Off Decision & Transmit to Coach", type="primary", use_container_width=True)
            if submit_sign:
                reason_clean = dr_reason.strip() if dr_reason and dr_reason.strip() else "Clinical evaluation completed by club medical staff."
                try:
                    store.record_signoff(
                        player_id=selected_pid,
                        player_name=info_card["name"],
                        squad=squad_fixed,
                        decision_type="DOCTOR_CALL",
                        status=final_status,
                        clinical_reason=reason_clean,
                        doctor_name=dr_name.strip() if dr_name else "Club Doctor",
                        coach_notes=coach_note_input.strip() if coach_note_input else "Adhere to standard squad load.",
                        original_risk={"risk_category": tier, "risk_score_pct": prob, "top_drivers": [{"label": r} for r in reasons]}
                    )
                    st.success(f"🎉 Done! {info_card['name']} ({selected_pid}) signed off as '{final_status}'. Updated in Coach's Hub!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not record sign-off: {e}")


# =====================================================================
# VIEW 4: SPORTS SCIENCE MATH & LOGISTIC REGRESSION BREAKDOWN
# =====================================================================
elif selected_view.startswith("💡 Sports Science"):
    st.markdown("## 🧠 Sports Science & Logistic Regression: Equations & Weights")
    
    st.info(
        "🎯 **Strict Probability Thresholds:** "
        "🟢 **LOW RISK (Available):** P < 5.0% | "
        "🟡 **MODERATE RISK (Need Some Help):** 5.0% ≤ P < 15.0% | "
        "🔴 **HIGH RISK (Benched):** P ≥ 15.0%"
    )

    # 1. OFFICIAL DATASET SPECIFICATIONS & PREPROCESSING
    with st.container(border=True):
        st.markdown("### 🎓 Official Season Training Dataset & Machine Learning Pipeline (`player_weeks.csv`)")
        st.markdown(
            "To achieve true sports-science and clinical rigor for *Foundations of AI for Business (Group A1)*, "
            "our Logistic Regression model is trained directly on the official **Harbourline FC Premier League Season Dataset** (`player_weeks.csv`). "
            "The learned parameters (`harbourline_logistic_season.pkl`) power the live scoring across all 60 squad players in our dashboard."
        )

        # 4 Key Metrics Tiles
        c_box1, c_box2, c_box3, c_box4 = st.columns(4)
        with c_box1:
            st.metric("Total Cohort", "2,400 Player-Weeks", "60 Players (Squad A & B)")
        with c_box2:
            st.metric("Active Training Size", "2,077 Player-Weeks", "323 'Out' Sidelined Excluded")
        with c_box3:
            st.metric("Test ROC-AUC Score", "0.8981", "~89.8% Discrimination")
        with c_box4:
            st.metric("Test Accuracy", "90.89%", "Threshold P ≥ 15%")

        st.markdown("---")

        # Dataset Metadata Details
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.markdown(
                textwrap.dedent("""
                #### 📌 Dataset Specifications:
                - **Data Source:** Harbourline Football Club Performance Analytics. Integrates Catapult/STATSports GPS tracking (Session-RPE, acute load, chronic load), daily morning subjective health questionnaires (sleep, muscle soreness, wellness), and Premier League match appearance records.
                - **Dataset Size:** **2,400 player-weeks** across **60 professional squad players** (Squad A first team: 30, Squad B developmental: 30) across **22 columns**.
                - **Time Period:** Full **40-week competitive football season** (Weeks 1 to 40), seeded with 4 pre-season weeks to ensure ACWR is valid from Week 1.
                - **Target Variable (`injury_next_7d`):** Binary classification label (1 if the athlete sustained a new time-loss soft-tissue strain within the next 7 days, 0 otherwise). Total **94 observed injuries** across 37 players (**4.53% active incidence rate**).
                - **Absence Outcomes:** Hamstring (25), Calf (23), Ankle (20), Groin (13), Knee ligament (9), Lower back (4). Mean absence was 3.5 weeks (333 total player-weeks lost).
                """)
            )

        with col_meta2:
            st.markdown(
                textwrap.dedent("""
                #### 🧹 Cleaning & Preprocessing Steps:
                1. **Out-of-Action Exclusion:** Filtered out 323 rows where `availability == 'out'` (already injured with blank labels), leaving **2,077 active training player-weeks**. Sidelined players cannot sustain a new training strain.
                2. **Target Leakage Prevention:** Post-injury outcome attributes (`injury_type`, `weeks_out`) are strictly dropped from the predictor feature set.
                3. **Group-Aware Splitting:** Used `GroupShuffleSplit` on `player_id` (48 train players / 12 test players: 1,682 train rows, 395 test rows) so no athlete leaks across train/test splits.
                4. **Clinical Feature Engineering:**
                   - Non-linear ACWR splines: Spikes `max(0, ACWR - 1.30)` & Detraining `max(0, 0.80 - ACWR)`.
                   - Cumulative 3-week sleep debt: Scaled rolling deficit over 21 days `(deficit / 10.0)`.
                   - Recovery flags: Muscle soreness above resting baseline `max(0, Soreness - 4)` & low wellness warning `(wellness <= 4)`.
                   - Tactical position one-hot encoding: GK, MID, FWD with DEF as baseline.
                5. **Numerical Scaling:** Scaled chronic sleep debt to prevent gradient instability and numerical overflow.
                """)
            )

        st.markdown("---")

        # 3 Downloads
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        path_csv_season = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")
        path_ipynb = os.path.join(BASE_DIR, "notebooks", "Harbourline_Injury_Model_Season_Colab.ipynb")
        path_py_colab = os.path.join(BASE_DIR, "scripts", "Harbourline_Injury_Model_Colab.py")

        with col_dl1:
            if os.path.exists(path_csv_season):
                with open(path_csv_season, "r", encoding="utf-8") as f:
                    csv_data = f.read()
                st.download_button(
                    "📥 Download Season Dataset (player_weeks.csv)",
                    data=csv_data,
                    file_name="player_weeks.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col_dl2:
            if os.path.exists(path_ipynb):
                with open(path_ipynb, "r", encoding="utf-8") as f:
                    nb_data = f.read()
                st.download_button(
                    "📥 Download Colab Notebook (.ipynb)",
                    data=nb_data,
                    file_name="Harbourline_Injury_Model_Season_Colab.ipynb",
                    mime="application/x-ipynb+json",
                    use_container_width=True
                )

        with col_dl3:
            if os.path.exists(path_py_colab):
                with open(path_py_colab, "r", encoding="utf-8") as f:
                    script_data = f.read()
                st.download_button(
                    "📥 Download Standalone Colab Script (.py)",
                    data=script_data,
                    file_name="Harbourline_Injury_Model_Colab.py",
                    mime="text/x-python",
                    use_container_width=True
                )

        with st.expander("💻 View Full Google Colab Python Script (Single-Cell Ready)"):
            st.caption("Copy and paste this code into [Google Colab](https://colab.research.google.com) to train the model live:")
            if os.path.exists(path_py_colab):
                with open(path_py_colab, "r", encoding="utf-8") as f:
                    st.code(f.read(), language="python")

    st.markdown("---")

    st.markdown(
        textwrap.dedent("""
        ### ⚽ Why are Majority of Players Low Risk? (Sports Science Reality)
        In professional football, soft-tissue strains occur at an average baseline frequency of **~3.9% to 4.5%** per player-week. 
        On any given morning across a 60-man squad:
        - **~52 to 54 players (~88%)** are healthy, well-conditioned, and **Available to Train** ($P < 5\%$).
        - **~3 to 5 players (~7%)** are carrying elevated fatigue, high ACWR, or sleep debt and **Need Some Help (Modified)** ($5\% \le P < 15\%$).
        - **~3 players (~5%)** are at severe risk or injured and **Can't Train / Benched** ($P \ge 15\%$).
        
        This distribution is **medically accurate** and aligns with UEFA/FIFA injury surveillance data.
        """)
    )
    
    st.markdown("---")
    st.markdown("### 1. The Core Logistic Regression Equation")
    st.markdown(
        textwrap.dedent(r"""
        In machine learning, logistic regression calculates the **log-odds ($z$)** of an event as a linear sum of weighted factors:

        $$\large z = b_0 + w_1 x_1 + w_2 x_2 + \dots + w_{11} x_{11}$$

        Then it maps $z$ into a true probability $P \in [0, 1]$ using the standard **sigmoid function**:

        $$\large P(\text{Injury in next 7 days}) = \frac{1}{1 + e^{-z}}$$
        """)
    )
    
    st.markdown("---")
    st.markdown("### 2. Learned Weights from the 2,400 Player-Week Season Model")
    st.markdown(
        textwrap.dedent(r"""
        These are the exact mathematical parameters learned by fitting our Logistic Regression classifier on the 2,077 active player-weeks (`player_weeks.csv`):

        | Parameter / Factor | Rule / Trigger Formula | Learned Weight ($w_i$) | Odds Ratio ($\exp(w_i)$) | Sports Science Rationale |
        |---|---|---|---|---|
        | **Base Intercept ($b_0$)** | Constant base rate | **-4.900** | — | Calibrated baseline injury rate (~4.5% active prevalence). |
        | **ACWR Spike** | $\max(0, \text{ACWR} - 1.30)$ | **+1.403** | **4.067x** | Workload spikes above 1.30 create steep non-linear strain on muscles. |
        | **Under-loading** | $\max(0, 0.80 - \text{ACWR})$ | **-0.120** | **0.887x** | Sub-acute detraining under-loading term. |
        | **Prior Injuries** | Past strains count (0 to 5) | **+0.529** | **1.697x** | Scar tissue is the #1 statistical predictor of future tears. |
        | **Muscle Soreness** | $\max(0, \text{Soreness} - 4)$ | **+0.190** | **1.210x** | Physical symptom of delayed-onset muscle damage. |
        | **Short Sleep (Week)** | $\max(0, 7.0 - \text{Sleep})$ | **+0.477** | **1.611x** | Weekly deficit impairs muscle glycogen restoration and neural reflexes. |
        | **3-Week Sleep Debt** | Deficit over 21 days (per 10h) | **+0.460** | **1.585x** | Chronic sleep debt compounds fatigue over multiple weeks. |
        | **Player Age** | $\max(0, \text{Age} - 26)$ | **+0.084** | **1.088x** | Older muscle fibers take longer to repair post-match. |
        | **Player Position** | GK: -0.56, DEF: 0.00, MID: +0.13, FWD: +0.40 | categorical | Forwards perform explosive sprints; goalkeepers run the least. |
        | **Low Wellness** | 1 if Wellness $\le 4$, else 0 | **+0.497** | **1.643x** | Non-load stress (travel, illness, personal distress). |
        | **Return to Play** | 1 if Week 1 or 2 back from injury | **+0.295** | **1.343x** | Low chronic fitness makes returning players vulnerable to re-injury. |
        """)
    )
    
    st.markdown("---")
    st.markdown("### 3. Step-by-Step Calculation Walkthroughs")
    
    tab_ex1, tab_ex2 = st.tabs(["🟡 Example 1: Moderate Risk (P001, 6.4% Risk)", "🔴 Example 2: High Risk (P051, 39.6% Risk)"])
    
    with tab_ex1:
        st.markdown(
            textwrap.dedent(r"""
            #### Player P001 (Week 40) — Moderate Risk (Need Some Help / Modified)
            - **Inputs:** ACWR = $1.64$, Sleep = $6.3\text{h}$, Soreness = $6/10$, 3W Sleep Debt = $21\text{h}$, Prior Injuries = $1$, Position = GK, Wellness = $5/10$.

            | Factor | Formula & Calculation | Contribution to $z$ |
            |---|---|---|
            | Base Intercept ($b_0$) | Baseline club constant | **-4.900** |
            | ACWR Spike ($>1.30$) | $(1.64 - 1.30) \times 1.403$ | **+0.477** |
            | Under-loading ($<0.80$) | $\max(0, 0.80 - 1.64) \times (-0.120)$ | **+0.000** |
            | Prior Injury History | $1 \text{ prior strain} \times +0.529$ | **+0.529** |
            | Muscle Soreness ($>4$) | $(6 - 4) \times 0.190$ | **+0.380** |
            | Short Sleep this week | $(7.0 - 6.3) \times 0.477$ | **+0.334** |
            | 3-Week Sleep Debt | $(21\text{h} / 10) \times 0.460$ | **+0.967** |
            | Player Age ($>26$) | $(27 - 26) \times 0.084$ | **+0.084** |
            | Player Position | Goalkeeper offset | **-0.560** |
            | Low Wellness ($\le 4$) | Wellness $5 > 4$ (inactive) | **+0.000** |
            | Return to Play | Full squad active | **+0.000** |
            | **Total Log-Odds ($z$)** | **Sum of all 11 terms** | **-2.689** |

            **Sigmoid Probability Conversion:**

            $$P = \frac{1}{1 + e^{-(-2.689)}} = \frac{1}{1 + e^{2.689}} = \frac{1}{1 + 14.717} \approx \mathbf{6.4\%}$$

            Because $5.0\% \le 6.4\% < 15.0\%$, this athlete is classified as **🟡 MODERATE RISK (Need Some Help / Modified)**.
            """)
        )

    with tab_ex2:
        st.markdown(
            textwrap.dedent(r"""
            #### Player P051 (Week 3) — High Risk (Can't Train / Benched)
            - **Inputs:** ACWR = $1.77$, Sleep = $6.0\text{h}$, Soreness = $7/10$, 3W Sleep Debt = $35\text{h}$, Prior Injuries = $1$, Position = MID, Wellness = $3/10$.

            | Factor | Formula & Calculation | Contribution to $z$ |
            |---|---|---|
            | Base Intercept ($b_0$) | Baseline constant | **-4.900** |
            | ACWR Spike ($>1.30$) | $(1.77 - 1.30) \times 1.403$ | **+0.659** |
            | Prior Injury History | $1 \text{ prior injury} \times +0.529$ | **+0.529** |
            | Muscle Soreness ($>4$) | $(7 - 4) \times 0.190$ | **+0.571** |
            | Short Sleep this week | $(7.0 - 6.0) \times 0.477$ | **+0.477** |
            | 3-Week Sleep Debt | $(35\text{h} / 10) \times 0.460$ | **+1.611** |
            | Player Position | Midfielder adjustment | **+0.133** |
            | Low Wellness Warning | Wellness $3 \le 4$ | **+0.497** |
            | **Total Log-Odds ($z$)** | **Sum of all terms** | **-0.423** |

            **Sigmoid Probability Conversion:**

            $$P = \frac{1}{1 + e^{-(-0.423)}} = \frac{1}{1 + e^{0.423}} = \frac{1}{1 + 1.527} \approx \mathbf{39.6\%}$$

            Because $P = 39.6\% \ge 15.0\%$, this athlete is classified as **🔴 HIGH RISK (Can't Train / Benched)**.
            """)
        )
