"""
High-End Sports Performance UI Components & Custom Styling
AI-Assisted Player Health and Injury Risk System
Designed for elite club medical & performance departments.
Includes custom dark-mode glassmorphism cards, Plotly gauges, radar charts, and banners.
"""

import streamlit as st
import plotly.graph_objects as go

# Custom CSS for dark-mode elite athletic SaaS look
FANCY_CSS = """
<style>
/* Main container styling */
.main {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Prototype Banner */
.proto-banner {
    background: linear-gradient(90deg, #1e1b4b 0%, #311042 50%, #1e1b4b 100%);
    border: 1px solid #6366f1;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
}
.proto-banner-text {
    font-size: 0.88rem;
    font-weight: 600;
    color: #e0e7ff;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.proto-pill {
    background: #4f46e5;
    color: #ffffff;
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 700;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.glass-card-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 8px;
}

/* Metric KPI badge */
.kpi-container {
    display: flex;
    flex-direction: column;
    background: rgba(30, 41, 59, 0.6);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 14px;
    text-align: center;
}
.kpi-val {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.kpi-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 4px;
}

/* Status Badges */
.badge-cleared {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid #10b981;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}
.badge-modified {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid #f59e0b;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}
.badge-benched {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid #ef4444;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}
.badge-conflict {
    background: rgba(168, 85, 247, 0.15);
    color: #a855f7;
    border: 1px solid #a855f7;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}

/* Clause quote callout */
.protocol-clause-callout {
    background: rgba(6, 182, 212, 0.08);
    border-left: 4px solid #06b6d4;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    font-size: 0.9rem;
    color: #e2e8f0;
}

/* Checkpoint Callout */
.checkpoint-gate {
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 10px;
    padding: 16px;
    margin: 14px 0;
}
</style>
"""

def render_header_banner():
    st.markdown(FANCY_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="proto-banner">
            <div class="proto-banner-text">
                🛡️ AI-ASSISTED PLAYER HEALTH & INJURY RISK SYSTEM • B2B SQUAD EDITION
            </div>
            <div>
                <span class="proto-pill">EDUCATIONAL PROTOTYPE — NOT MEDICAL ADVICE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_risk_gauge(risk_score_pct, threshold_pct=15.0):
    """
    Renders an elite circular gauge for soft-tissue injury risk probability.
    """
    is_high = risk_score_pct >= threshold_pct
    needle_color = "#ef4444" if is_high else "#10b981"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score_pct,
        number={'suffix': "%", 'font': {'size': 38, 'color': '#ffffff'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "7-Day Soft-Tissue Risk Probability", 'font': {'size': 16, 'color': '#94a3b8'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': needle_color, 'thickness': 0.28},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 15], 'color': 'rgba(16, 185, 129, 0.25)'},
                {'range': [15, 40], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [40, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "#f43f5e", 'width': 3},
                'thickness': 0.75,
                'value': threshold_pct
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=240
    )
    return fig

def create_drivers_bar_chart(drivers):
    """
    Renders horizontal bar chart of top risk contributors.
    """
    labels = [d["label"] for d in reversed(drivers)]
    impacts = [d["impact"] for d in reversed(drivers)]
    colors = ["#ef4444" if imp > 0 else "#10b981" for imp in impacts]
    
    fig = go.Figure(go.Bar(
        x=impacts,
        y=labels,
        orientation='h',
        marker=dict(color=colors, cornerradius=6),
        text=[f"{imp:+.2f}" for imp in impacts],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=12)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="Top Factor Influence (Attribution Weights)", font=dict(color="#94a3b8", size=14)),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.08)',
            zerolinecolor='rgba(255, 255, 255, 0.3)',
            color='#94a3b8'
        ),
        yaxis=dict(color='#f8fafc', tickfont=dict(size=12)),
        margin=dict(l=20, r=40, t=40, b=20),
        height=240
    )
    return fig

def create_acwr_bullet_chart(acwr_val):
    """
    Renders sweet-spot ACWR visualizer.
    """
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        value=acwr_val,
        number={'font': {'size': 32, 'color': '#ffffff'}},
        title={'text': "Acute:Chronic Workload Ratio (ACWR)", 'font': {'size': 14, 'color': '#94a3b8'}},
        gauge={
            'shape': "bullet",
            'axis': {'range': [0.4, 2.2], 'tickcolor': "#94a3b8"},
            'threshold': {
                'line': {'color': "#ef4444", 'width': 3},
                'thickness': 0.75,
                'value': 1.50
            },
            'bar': {'color': "#38bdf8", 'thickness': 0.5},
            'steps': [
                {'range': [0.4, 0.8], 'color': 'rgba(148, 163, 184, 0.2)'},     # Under-trained
                {'range': [0.8, 1.3], 'color': 'rgba(16, 185, 129, 0.35)'},   # Sweet spot
                {'range': [1.3, 1.5], 'color': 'rgba(245, 158, 11, 0.35)'},   # Caution
                {'range': [1.5, 2.2], 'color': 'rgba(239, 68, 68, 0.35)'}     # Danger zone
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=130
    )
    return fig
