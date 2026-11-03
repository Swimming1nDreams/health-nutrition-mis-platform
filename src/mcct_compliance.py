"""
Humanitarian Health & Nutrition MIS Platform
Module 2: Maternal & Child Cash Transfer (MCCT) Compliance & Payroll Engine
Author: M&E & Data Assistant Candidate
Direct Alignment: Terre des hommes (Tdh) MEAL Assistant - Nutrition & MCCT Project
Functions:
- Tracks PLW co-responsibility milestones (ANC, Facility Delivery, Immunization, IYCF)
- Evaluates monthly tranche compliance eligibility (50,000 MMK/month)
- Generates automated mobile money payroll batches (Wave Money / KBZPay / Cash)
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def audit_mcct_compliance(df):
    """
    Evaluates individual PLW compliance against national & Tdh MCCT conditionalities:
    Condition 1: Pregnant woman must attend >= 2 ANC visits (if gestational weeks >= 24) or on track.
    Condition 2: Lactating mother must have fully immunized child for age.
    Condition 3: Must attend at least 2 community IYCF counseling sessions.
    Returns enriched DataFrame with compliance flags and payment eligibility.
    """
    df = df.copy()
    
    compliance_reasons = []
    eligible_flags = []
    
    for _, row in df.iterrows():
        b_type = row["beneficiary_type"]
        anc = row["anc_visits_completed"]
        iycf = row["iycf_sessions_attended"]
        imm = row["child_immunization_status"]
        
        reasons = []
        is_ok = True
        
        # Check IYCF attendance
        if iycf < 2:
            is_ok = False
            reasons.append(f"Incomplete IYCF ({iycf}/2 sessions attended)")
            
        # Check ANC attendance
        if b_type == "Pregnant Woman":
            if row["gestational_weeks"] >= 24 and anc < 2:
                is_ok = False
                reasons.append(f"Under-target ANC ({anc} visits at {row['gestational_weeks']} weeks)")
        else: # Lactating Mother
            if imm == "Delayed / Defaulter":
                is_ok = False
                reasons.append("Child immunization defaulter / overdue")
                
        if is_ok:
            compliance_reasons.append("All health conditionalities fulfilled")
            eligible_flags.append(True)
        else:
            compliance_reasons.append("; ".join(reasons))
            eligible_flags.append(False)
            
    df["is_verified_compliant"] = eligible_flags
    df["compliance_audit_notes"] = compliance_reasons
    df["payroll_action"] = np.where(df["is_verified_compliant"], "Approve Cash Tranche (50,000 MMK)", "Hold Tranche - Case Worker Follow-up")
    
    return df

def generate_mcct_payroll_batch(df, batch_code="MCCT-PAYROLL-2026-10"):
    """
    Generates banking / mobile money payroll disbursement file for compliant beneficiaries.
    Ready for Wave Money / KBZPay / M-Pitesan bulk payment integration.
    """
    compliant_df = df[df["is_verified_compliant"] == True].copy()
    
    payroll = pd.DataFrame({
        "Batch_ID": batch_code,
        "Beneficiary_ID": compliant_df["beneficiary_id"],
        "Recipient_Name": compliant_df["mother_name"],
        "Township": compliant_df["township"],
        "Clinic_Site": compliant_df["health_facility"],
        "Payment_Channel": compliant_df["payment_channel"],
        "Amount_MMK": compliant_df["monthly_cash_entitlement_mmk"],
        "Disbursement_Status": "Ready for Processing",
        "Approval_Date": "2026-10-31"
    })
    return payroll

def compute_mcct_program_metrics(df):
    """
    Generates summary KPIs for Tdh Project Manager & Donors (LIFT / UNICEF).
    """
    total = len(df)
    compliant = int((df["is_verified_compliant"] == True).sum())
    non_compliant = total - compliant
    compliance_rate = round((compliant / total) * 100, 1) if total > 0 else 0
    
    total_cash_disbursed = compliant * 50000
    
    # Breakdown by township
    township_summary = df.groupby("township").agg(
        Total_Enrolled=("beneficiary_id", "count"),
        Compliant=("is_verified_compliant", "sum")
    ).reset_index()
    township_summary["Compliance_Rate_%"] = (township_summary["Compliant"] / township_summary["Total_Enrolled"] * 100).round(1)
    
    return {
        "total_plw_enrolled": total,
        "compliant_count": compliant,
        "non_compliant_count": non_compliant,
        "compliance_rate_pct": compliance_rate,
        "total_payroll_mmk": total_cash_disbursed,
        "township_performance": township_summary
    }

if __name__ == "__main__":
    raw_path = os.path.join(BASE_DIR, "data", "raw", "raw_mcct_plw_beneficiaries.csv")
    df = pd.read_csv(raw_path)
    df_audited = audit_mcct_compliance(df)
    payroll = generate_mcct_payroll_batch(df_audited)
    metrics = compute_mcct_program_metrics(df_audited)
    
    df_audited.to_csv(os.path.join(PROCESSED_DIR, "mcct_plw_with_compliance.csv"), index=False)
    payroll.to_csv(os.path.join(REPORTS_DIR, "mcct_mobile_money_payroll_batch.csv"), index=False)
    
    print("=== MCCT MATERNAL & CHILD CASH TRANSFER AUDITED ===")
    print(f"- Total PLW: {metrics['total_plw_enrolled']}")
    print(f"- Compliance Rate: {metrics['compliance_rate_pct']}%")
    print(f"- Total Approved Payroll: {metrics['total_payroll_mmk']:,} MMK ({len(payroll)} beneficiaries)")
