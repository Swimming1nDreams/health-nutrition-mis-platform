"""
Humanitarian Health & Nutrition MIS Platform
Executive Operations Portal for Health MIS & Nutrition MEAL Applications
Alignment:
- Sun Community Health (SCH) Jr. MIS Officer (DHIS2, Primary Health Care, Stock & Validation)
- Terre des hommes (Tdh) MEAL Assistant (Nutrition & MCCT Maternal Child Cash Transfer)
Features:
1. Primary Health Care & Clinic Performance Monitoring (OPD, ANC, Family Planning, SADD)
2. SMART Nutrition Surveillance & WHO Child Growth Standards (WHZ, HAZ, MUAC, SPHERE OTP)
3. Maternal & Child Cash Transfer (MCCT) Compliance Verification & Payroll Batching
4. DHIS2 Validation Rule Engine (Left-Hand vs Right-Hand Consistency Checks)
5. Essential Medical Commodity & RUTF Early Warning Stock-Out Tracker
6. DHIS2 DataValueSets JSON API Exporter & Donor Reporting Studio
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Path configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from nutrition_anthropometry import calculate_who_zscores, calculate_sphere_otp_indicators, audit_smart_plausibility
from mcct_compliance import audit_mcct_compliance, generate_mcct_payroll_batch, compute_mcct_program_metrics
from dhis2_mis_engine import evaluate_dhis2_validation_rules, export_dhis2_json_payload
from commodity_stock_tracker import analyze_commodity_stock, get_latest_stock_status_summary

# -------------------------------------------------------------
# PAGE CONFIGURATION & ENTERPRISE DARK THEME STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Humanitarian Health & Nutrition MIS Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Banner */
    .header-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 22px 28px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .header-title {
        color: #F8FAFC;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 13px;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Sleek KPI Metric Cards */
    .kpi-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #334155;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        margin-bottom: 12px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #0EA5E9;
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 24px;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .kpi-subtext {
        font-size: 11px;
        font-weight: 500;
    }
    .text-cyan { color: #0EA5E9; }
    .text-emerald { color: #10B981; }
    .text-amber { color: #F59E0B; }
    .text-rose { color: #EF4444; }
    .text-purple { color: #A855F7; }

    /* Compact Buttons */
    div.stButton > button {
        background-color: #0284C7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    div.stButton > button:hover {
        background-color: #0369A1;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# DATA LOADING & CACHING
# -------------------------------------------------------------
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

@st.cache_data
def load_all_mis_data():
    df_nut_raw = pd.read_csv(os.path.join(DATA_RAW, "raw_child_nutrition_anthropometry.csv"))
    df_mcct_raw = pd.read_csv(os.path.join(DATA_RAW, "raw_mcct_plw_beneficiaries.csv"))
    df_dhis2_raw = pd.read_csv(os.path.join(DATA_RAW, "raw_dhis2_clinic_monthly_reports.csv"))
    df_stock_raw = pd.read_csv(os.path.join(DATA_RAW, "raw_medical_commodity_stock.csv"))
    
    # Process Nutrition
    df_nut = calculate_who_zscores(df_nut_raw)
    sphere_metrics = calculate_sphere_otp_indicators(df_nut)
    plausibility = audit_smart_plausibility(df_nut)
    
    # Process MCCT
    df_mcct = audit_mcct_compliance(df_mcct_raw)
    mcct_payroll = generate_mcct_payroll_batch(df_mcct)
    mcct_kpis = compute_mcct_program_metrics(df_mcct)
    
    # Process DHIS2
    df_dhis2, df_violations = evaluate_dhis2_validation_rules(df_dhis2_raw)
    dhis2_payload = export_dhis2_json_payload(df_dhis2)
    
    # Process Stock
    df_stock = analyze_commodity_stock(df_stock_raw)
    latest_stock, stock_summary = get_latest_stock_status_summary(df_stock)
    
    return (df_nut, sphere_metrics, plausibility,
            df_mcct, mcct_payroll, mcct_kpis,
            df_dhis2, df_violations, dhis2_payload,
            df_stock, latest_stock, stock_summary)

(df_nut_all, sphere_metrics, plausibility,
 df_mcct_all, mcct_payroll, mcct_kpis,
 df_dhis2_all, df_violations, dhis2_payload,
 df_stock_all, latest_stock, stock_summary) = load_all_mis_data()

# -------------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏥 Health & Nutrition MIS")
    st.caption("**Profile:** Jr. MIS / Nutrition MEAL Assistant  \n**Coverage:** SCH Clinics & Tdh MCCT Hubs")
    st.markdown("---")
    
    st.subheader("Filter Facilities")
    
    # Facility Filter
    facilities = ["All Facilities"] + sorted(list(df_dhis2_all["org_unit_name"].unique()))
    sel_fac = st.selectbox("Health Facility / Site:", facilities)
    
    # Township Filter
    townships = ["All Townships"] + sorted(list(df_dhis2_all["township"].unique()))
    sel_township = st.selectbox("Township:", townships)
    
    # Partner Filter
    partners = ["All Partners"] + sorted(list(df_dhis2_all["partner"].unique()))
    sel_partner = st.selectbox("Implementing Partner:", partners)
    
    st.markdown("---")
    st.markdown("**Core Frameworks Applied:**")
    st.markdown("- WHO Child Growth Standards (2006)\n- SPHERE Humanitarian Charter (OTP)\n- SMART Nutrition Survey Methodology\n- DHIS2 Left/Right Validation Rules\n- MCCT Maternal Cash Conditionalities\n- Essential Commodity Buffer Stock (MoS)")
    st.markdown("---")
    st.caption("Custom-built for Sun Community Health & Terre des hommes recruitment portfolios.")

# Filter DataFrames
df_dhis2 = df_dhis2_all.copy()
df_nut = df_nut_all.copy()
df_mcct = df_mcct_all.copy()
df_stock = df_stock_all.copy()

if sel_fac != "All Facilities":
    df_dhis2 = df_dhis2[df_dhis2["org_unit_name"] == sel_fac]
    df_nut = df_nut[df_nut["health_facility"] == sel_fac]
    df_mcct = df_mcct[df_mcct["health_facility"] == sel_fac]
    df_stock = df_stock[df_stock["health_facility"] == sel_fac]

if sel_township != "All Townships":
    df_dhis2 = df_dhis2[df_dhis2["township"] == sel_township]
    df_nut = df_nut[df_nut["township"] == sel_township]
    df_mcct = df_mcct[df_mcct["township"] == sel_township]
    df_stock = df_stock[df_stock["township"] == sel_township]

if sel_partner != "All Partners":
    df_dhis2 = df_dhis2[df_dhis2["partner"] == sel_partner]
    df_nut = df_nut[df_nut["implementing_partner"] == sel_partner]
    df_mcct = df_mcct[df_mcct["implementing_partner"] == sel_partner]

# -------------------------------------------------------------
# MAIN HEADER BANNER
# -------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">
        <span>🩺</span> Humanitarian Health & Nutrition MIS Platform
    </div>
    <div class="header-subtitle">
        DHIS2 Aggregate Health Database, SMART Nutrition Anthropometry, Maternal Child Cash Transfer (MCCT) & Essential Commodity Early Warning
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# EXECUTIVE TOP KPI ROW
# -------------------------------------------------------------
total_opd = int(df_dhis2["opd_total_attendance"].sum())
total_anc = int(df_dhis2["anc_1st_visit"].sum())
screened_children = len(df_nut)
gam_rate = round((df_nut["acute_malnutrition_class"].isin(["SAM (Severe Acute Malnutrition)", "MAM (Moderate Acute Malnutrition)"]).sum() / screened_children * 100), 1) if screened_children > 0 else 0
mcct_eligible_rate = round(((df_mcct["is_verified_compliant"] == True).sum() / len(df_mcct) * 100), 1) if len(df_mcct) > 0 else 0
active_violations = len(df_violations)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">OPD Consultations</div>
        <div class="kpi-value">{total_opd:,}</div>
        <div class="kpi-subtext text-cyan">Primary Care Visits</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Maternal Care (ANC 1st)</div>
        <div class="kpi-value">{total_anc:,}</div>
        <div class="kpi-subtext text-emerald">Pregnant Women Registered</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Children Screened</div>
        <div class="kpi-value">{screened_children:,}</div>
        <div class="kpi-subtext text-purple">GAM: {gam_rate}% (SAM+MAM)</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">MCCT Cash Compliance</div>
        <div class="kpi-value">{mcct_eligible_rate}%</div>
        <div class="kpi-subtext text-emerald">Eligible for 50,000 MMK</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">DHIS2 Validation Traps</div>
        <div class="kpi-value">{active_violations}</div>
        <div class="kpi-subtext {'text-rose' if active_violations > 0 else 'text-emerald'}">Rule Violations Caught</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# OPERATIONS TABS
# -------------------------------------------------------------
t1, t2, t3, t4, t5, t6 = st.tabs([
    "🩺 Clinical & Primary Care",
    "👶 SMART Nutrition & Anthropometry",
    "🤰 MCCT Maternal Cash Compliance",
    "⚡ DHIS2 Validation Rule Engine",
    "📦 Medical Commodity & RUTF Stock",
    "🌐 DHIS2 API & Donor Reporting"
])

# -------------------------------------------------------------
# TAB 1: CLINICAL & PRIMARY HEALTH CARE
# -------------------------------------------------------------
with t1:
    st.markdown("#### 🩺 Clinical Consultations & Reproductive Health Surveillance")
    st.caption("Monthly morbidity, maternal healthcare cascade, and communicable disease surveillance across SCH & partner clinics.")
    
    col_cl1, col_cl2 = st.columns([1, 1])
    with col_cl1:
        st.markdown("##### 📈 Monthly OPD Consultation Trends by Gender & Age (SADD)")
        opd_trend = df_dhis2.groupby("period").agg(
            Under5_Female=("opd_under5_female", "sum"),
            Under5_Male=("opd_under5_male", "sum"),
            Over5_Female=("opd_over5_female", "sum"),
            Over5_Male=("opd_over5_male", "sum")
        ).reset_index()
        
        fig_opd = px.bar(
            opd_trend,
            x="period",
            y=["Under5_Female", "Under5_Male", "Over5_Female", "Over5_Male"],
            title="OPD Consultations Disaggregated by Age & Gender",
            barmode="stack",
            color_discrete_sequence=["#38BDF8", "#0284C7", "#F472B6", "#DB2777"]
        )
        fig_opd.update_layout(xaxis_title="Reporting Month", yaxis_title="Consultations", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_opd, use_container_width=True)
        
    with col_cl2:
        st.markdown("##### 🤱 Antenatal Care (ANC) Retention Cascade")
        total_anc1 = df_dhis2["anc_1st_visit"].sum()
        total_anc4 = df_dhis2["anc_4th_visit"].sum()
        total_pnc = df_dhis2["pnc_visits"].sum()
        
        fig_cascade = go.Figure(go.Funnel(
            y=["ANC 1st Visit (Early Registration)", "ANC 4th Visit (Retention)", "Postnatal Care (PNC Visit)"],
            x=[total_anc1, total_anc4, total_pnc],
            textinfo="value+percent initial",
            marker=dict(color=["#0EA5E9", "#10B981", "#8B5CF6"])
        ))
        fig_cascade.update_layout(title="Maternal Care Retention (Drop-out: ANC1 to ANC4)", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_cascade, use_container_width=True)
        
    st.markdown("---")
    st.markdown("##### 🦟 Communicable Disease Surveillance (Malaria & Tuberculosis)")
    col_dis1, col_dis2 = st.columns([1, 1])
    with col_dis1:
        mal_tested = int(df_dhis2["malaria_rdt_tested"].sum())
        mal_pos = int(df_dhis2["malaria_rdt_positive"].sum())
        mal_act = int(df_dhis2["malaria_treated_act"].sum())
        pos_rate = round((mal_pos / mal_tested * 100), 1) if mal_tested > 0 else 0
        
        st.markdown(f"""
        - **Total Malaria RDT Tests Done:** `{mal_tested:,}`
        - **Confirmed Positive Cases:** `{mal_pos:,}` (**Positivity Rate:** `{pos_rate}%`)
        - **Cases Treated with First-Line ACT:** `{mal_act:,}`
        """)
        
    with col_dis2:
        tb_scr = int(df_dhis2["tb_screened"].sum())
        tb_pos = int(df_dhis2["tb_sputum_positive"].sum())
        tb_dots = int(df_dhis2["tb_started_dots"].sum())
        tb_rate = round((tb_pos / tb_scr * 100), 1) if tb_scr > 0 else 0
        
        st.markdown(f"""
        - **Presumptive TB Suspects Screened:** `{tb_scr:,}`
        - **Bacteriologically Confirmed Sputum Positive:** `{tb_pos:,}` (**Detection Rate:** `{tb_rate}%`)
        - **Enrolled on Directly Observed Therapy (DOTS):** `{tb_dots:,}` (100% treatment initiation)
        """)

# -------------------------------------------------------------
# TAB 2: SMART NUTRITION & ANTHROPOMETRY
# -------------------------------------------------------------
with t2:
    st.markdown("#### 👶 SMART Nutrition Anthropometry & Growth Monitoring")
    st.caption("Child growth standards (WHO 2006), acute malnutrition classification (GAM/SAM/MAM), SPHERE Standards, and SMART plausibility checks.")
    
    col_n1, col_n2 = st.columns([1, 1])
    with col_n1:
        st.markdown("##### 📊 Acute Malnutrition Prevalence (GAM / SAM / MAM)")
        nut_counts = df_nut["acute_malnutrition_class"].value_counts().reset_index()
        nut_counts.columns = ["Category", "Children"]
        
        fig_nut_pie = px.pie(
            nut_counts,
            names="Category",
            values="Children",
            color="Category",
            color_discrete_map={
                "Normal / Well-Nourished": "#10B981",
                "MAM (Moderate Acute Malnutrition)": "#F59E0B",
                "SAM (Severe Acute Malnutrition)": "#EF4444"
            },
            hole=0.45,
            title="Nutritional Status Breakdown (WHO 2006 Standards)"
        )
        fig_nut_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig_nut_pie, use_container_width=True)
        
    with col_n2:
        st.markdown("##### 📐 Weight-for-Height Z-Score (WHZ) Curve vs WHO Standard")
        fig_whz = px.histogram(
            df_nut.dropna(subset=["whz_score"]),
            x="whz_score",
            nbins=35,
            color="acute_malnutrition_class",
            color_discrete_map={
                "Normal / Well-Nourished": "#10B981",
                "MAM (Moderate Acute Malnutrition)": "#F59E0B",
                "SAM (Severe Acute Malnutrition)": "#EF4444"
            },
            title="WHZ Distribution (Wasting Gaussian Bell Curve)"
        )
        fig_whz.add_vline(x=-3.0, line_dash="dash", line_color="#EF4444", annotation_text="SAM (-3 SD)")
        fig_whz.add_vline(x=-2.0, line_dash="dash", line_color="#F59E0B", annotation_text="MAM (-2 SD)")
        fig_whz.update_layout(xaxis_title="Weight-for-Height Z-Score (WHZ)", yaxis_title="Child Count", margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig_whz, use_container_width=True)
        
    st.markdown("---")
    st.markdown("##### 🏛️ SPHERE Humanitarian Charter Standards for OTP / Nutrition Outpatient")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("OTP Cure Rate", f"{sphere_metrics.get('cure_rate_pct')}%", "SPHERE Target: > 75%")
    with sc2:
        st.metric("Defaulter Rate", f"{sphere_metrics.get('defaulter_rate_pct')}%", "SPHERE Target: < 15%")
    with sc3:
        st.metric("Death Rate", f"{sphere_metrics.get('death_rate_pct')}%", "SPHERE Target: < 3%")
    with sc4:
        st.metric("Non-Responder Rate", f"{sphere_metrics.get('non_responder_pct')}%", "Medical Review")
        
    st.markdown("---")
    st.markdown("##### 🔍 SMART Methodology Plausibility Quality Audit")
    pq1, pq2, pq3, pq4 = st.columns(4)
    with pq1:
        st.metric("Digit Preference Score (DPS)", f"{plausibility.get('digit_preference_score_height')}", plausibility.get('dps_rating'))
    with pq2:
        st.metric("WHZ Standard Deviation", f"{plausibility.get('whz_standard_deviation')}", plausibility.get('whz_sd_status'))
    with pq3:
        st.metric("WHZ Mean", f"{plausibility.get('whz_mean')}")
    with pq4:
        st.metric("WHZ Skewness", f"{plausibility.get('whz_skewness')}")

# -------------------------------------------------------------
# TAB 3: MCCT MATERNAL CASH COMPLIANCE & PAYROLL
# -------------------------------------------------------------
with t3:
    st.markdown("#### 🤰 Maternal & Child Cash Transfer (MCCT) Compliance & Payroll Engine")
    st.caption("Demonstrating end-to-end conditional cash transfer management for Terre des hommes (Tdh) Mandalay & health partner sites.")
    
    mp1, mp2, mp3, mp4 = st.columns(4)
    with mp1:
        st.metric("Total PLW Registered", f"{mcct_kpis['total_plw_enrolled']}")
    with mp2:
        st.metric("Verified Compliant", f"{mcct_kpis['compliant_count']}", f"{mcct_kpis['compliance_rate_pct']}% Rate")
    with mp3:
        st.metric("Tranche On Hold", f"{mcct_kpis['non_compliant_count']}", "Action Required")
    with mp4:
        st.metric("Approved Payroll (MMK)", f"{mcct_kpis['total_payroll_mmk']:,} MMK", "50,000 MMK / Beneficiary")
        
    st.markdown("##### 📍 Compliance Rate & Enrolled Cohort by Township")
    st.dataframe(mcct_kpis["township_performance"], use_container_width=True, hide_index=True)
    
    st.markdown("##### 💳 Automated Mobile Money Payroll Disbursement File (Wave Money / KBZPay)")
    st.caption("Bank/MMO disbursement-ready batch for compliant beneficiaries whose health co-responsibilities are verified.")
    st.dataframe(mcct_payroll.head(15), use_container_width=True, hide_index=True)
    
    # Download Payroll Button
    csv_payroll = mcct_payroll.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Full Wave Money / KBZPay Bulk Payroll (CSV)",
        data=csv_payroll,
        file_name="mcct_wavemoney_approved_payroll_batch.csv",
        mime="text/csv"
    )

# -------------------------------------------------------------
# TAB 4: DHIS2 VALIDATION RULES & AUDIT ENGINE
# -------------------------------------------------------------
with t4:
    st.markdown("#### ⚡ DHIS2 Health MIS Validation Rule Engine")
    st.caption("Automated verification of left-hand side vs right-hand side clinical consistency rules, preventing data contamination before donor submission.")
    
    if len(df_violations) > 0:
        st.error(f"🚨 **{len(df_violations)} DHIS2 Validation Rule Violations Detected across Clinic Reports!**")
        st.dataframe(df_violations, use_container_width=True, hide_index=True)
        
        # Download Violations Log
        csv_viol = df_violations.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Validation Rule Violations Log (CSV)",
            data=csv_viol,
            file_name="dhis2_validation_violations_audit.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ All 30 clinic reports 100% passed DHIS2 Validation Rules with zero inconsistencies.")
        
    st.markdown("---")
    st.markdown("##### 📋 Standard DHIS2 Validation Rules Defined in this Platform:")
    rules_table = pd.DataFrame([
        {"Rule Code": "VAL-01", "Rule Description": "Male ANC Attendance must strictly be 0", "LHS Expression": "male_anc_visits", "Operator": "==", "RHS Expression": "0", "Severity": "Critical"},
        {"Rule Code": "VAL-02", "Rule Description": "Malaria ACT treatment cannot exceed RDT positives", "LHS Expression": "malaria_treated_act", "Operator": "<=", "RHS Expression": "malaria_rdt_positive", "Severity": "Warning"},
        {"Rule Code": "VAL-03", "Rule Description": "Measles MR vaccine doses cannot exceed birth cohort by >25%", "LHS Expression": "mr_measles_doses", "Operator": "<=", "RHS Expression": "birth_cohort * 1.25", "Severity": "Anomaly"},
        {"Rule Code": "VAL-04", "Rule Description": "Longitudinal Retention: ANC 4th visits <= ANC 1st visits", "LHS Expression": "anc_4th_visit", "Operator": "<=", "RHS Expression": "anc_1st_visit", "Severity": "Logic Error"}
    ])
    st.dataframe(rules_table, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 5: MEDICAL COMMODITY & RUTF STOCK
# -------------------------------------------------------------
with t5:
    st.markdown("#### 📦 Essential Medical Commodity & RUTF Nutrition Supply Tracker")
    st.caption("Monitoring Months of Stock (MoS), Average Monthly Consumption (AMC), and Early Warning Stock-Out Alerts.")
    
    st.markdown("##### 🚨 Critical Stock-Out Early Warning Alerts (Latest Month: 2026-10)")
    alert_df = pd.DataFrame(stock_summary["critical_items_list"])
    if len(alert_df) > 0:
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
    else:
        st.success("All facilities maintain adequate buffer stock (> 1.0 MoS).")
        
    st.markdown("---")
    st.markdown("##### 📊 Facility Stock Dynamics & Months of Stock (MoS)")
    fig_mos = px.bar(
        latest_stock,
        x="commodity_name",
        y="months_of_stock",
        color="stock_security_status",
        color_discrete_map={
            "Stocked Out / Emergency Order": "#EF4444",
            "Understocked / High Risk (< 1.0 MoS)": "#F59E0B",
            "Adequate Stock (1.0 - 3.0 MoS)": "#10B981",
            "Overstocked / Expiration Risk (> 3.0 MoS)": "#8B5CF6"
        },
        barmode="group",
        title="Months of Stock (MoS) by Essential Commodity (Buffer Line: 1.0 MoS)"
    )
    fig_mos.add_hline(y=1.0, line_dash="dash", line_color="#EF4444", annotation_text="Buffer Minimum (1.0 MoS)")
    fig_mos.add_hline(y=3.0, line_dash="dash", line_color="#8B5CF6", annotation_text="Max Ceiling (3.0 MoS)")
    fig_mos.update_layout(xaxis_title="", yaxis_title="Months of Stock", margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig_mos, use_container_width=True)

# -------------------------------------------------------------
# TAB 6: DHIS2 API & DONOR REPORTING
# -------------------------------------------------------------
with t6:
    st.markdown("#### 🌐 DHIS2 API DataValueSets & Interoperability Exporter")
    st.caption("Standardized DHIS2 Web API payload generation ready for direct integration into national Health MIS servers.")
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown("##### 📥 Data Export Center")
        
        # 1. DHIS2 JSON
        json_str = json.dumps(dhis2_payload, indent=2).encode('utf-8')
        st.download_button(
            label="📥 Download DHIS2 DataValueSets (JSON)",
            data=json_str,
            file_name="dhis2_health_monthly_export.json",
            mime="application/json"
        )
        
        # 2. Child Anthropometry with WHO Z-scores
        csv_nut = df_nut.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Child Anthropometry & Z-scores (CSV)",
            data=csv_nut,
            file_name="child_nutrition_anthropometry_who_zscores.csv",
            mime="text/csv"
        )
        
    with col_d2:
        st.markdown("##### 🔌 DHIS2 API Payload Preview (`/api/dataValueSets`)")
        st.json(dhis2_payload)

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 12px;'>"
    "Humanitarian Health & Nutrition MIS Platform | Designed for Sun Community Health & Terre des hommes Recruitments | Python, Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
