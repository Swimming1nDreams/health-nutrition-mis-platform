"""
Humanitarian Health & Nutrition MIS Platform
Module 1: SMART Nutrition Anthropometry & Child Growth Standards
Author: M&E & Data Assistant Candidate
Methodology:
- WHO Child Growth Standards (2006) Z-score Calculations (WHZ, HAZ, WAZ)
- Acute Malnutrition Classification (GAM, SAM, MAM, Bilateral Edema)
- SPHERE Humanitarian Charter Standards for OTP/TSFP Performance (Cure, Default, Death Rates)
- SMART Methodology Plausibility Audit (Digit Preference Score & WHZ Normality Check)
"""

import os
import math
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def calculate_who_zscores(df):
    """
    Computes WHO 2006 Child Growth Standards Z-scores for children 6-59 months.
    - WHZ: Weight-for-Height (Wasting / Acute Malnutrition)
    - HAZ: Height-for-Age (Stunting / Chronic Malnutrition)
    - WAZ: Weight-for-Age (Underweight)
    """
    df = df.copy()
    
    # Clean extreme impossible data entry errors before z-score math
    # Flag impossible weights (> 40kg for under 5) or heights (< 45cm or > 130cm)
    valid_mask = (df["weight_kg"] >= 3.0) & (df["weight_kg"] <= 35.0) & (df["height_cm"] >= 50.0) & (df["height_cm"] <= 125.0)
    
    # WHO Median approximations based on 2006 Multicentre Growth Reference Study (MGRS)
    h = df["height_cm"]
    w = df["weight_kg"]
    age = df["age_months"]
    
    # 1. WHZ: Weight-for-Height Z-score
    # Median weight for height: W_med ≈ 0.0016 * H^1.95, SD ≈ 0.10 * W_med
    w_med_h = 0.0016 * (h ** 1.95)
    w_sd_h = 0.102 * w_med_h
    whz = (w - w_med_h) / w_sd_h
    
    # 2. HAZ: Height-for-Age Z-score
    # Median height for age: H_med ≈ 60.5 + 0.84 * age, SD ≈ 3.8 cm
    h_med_age = 60.5 + (0.84 * age)
    haz = (h - h_med_age) / 3.85
    
    # 3. WAZ: Weight-for-Age Z-score
    # Median weight for age: W_med ≈ 6.2 + 0.22 * age, SD ≈ 1.25 kg
    w_med_age = 6.2 + (0.22 * age)
    waz = (w - w_med_age) / 1.28
    
    # Set impossible outliers to NaN
    whz = np.where(valid_mask, whz, np.nan)
    haz = np.where(valid_mask, haz, np.nan)
    waz = np.where(valid_mask, waz, np.nan)
    
    df["whz_score"] = np.round(whz, 2)
    df["haz_score"] = np.round(haz, 2)
    df["waz_score"] = np.round(waz, 2)
    df["is_anthropometry_valid"] = valid_mask
    
    # Categorization based on WHO & SPHERE guidelines
    # SAM: WHZ < -3.0 OR MUAC < 115mm OR Bilateral Edema == 'Yes'
    # MAM: (-3.0 <= WHZ < -2.0) OR (115 <= MUAC < 125mm) (without edema)
    # Normal: WHZ >= -2.0 and MUAC >= 125mm
    is_sam = (df["whz_score"] < -3.0) | (df["muac_mm"] < 115) | (df["bilateral_edema"] == "Yes")
    is_mam = (~is_sam) & ((df["whz_score"] < -2.0) | (df["muac_mm"] < 125))
    is_normal = (~is_sam) & (~is_mam)
    
    conditions = [is_sam, is_mam, is_normal]
    choices = ["SAM (Severe Acute Malnutrition)", "MAM (Moderate Acute Malnutrition)", "Normal / Well-Nourished"]
    df["acute_malnutrition_class"] = np.select(conditions, choices, default="Normal / Well-Nourished")
    
    # Stunting classification (HAZ)
    is_severe_stunted = df["haz_score"] < -3.0
    is_mod_stunted = (df["haz_score"] >= -3.0) & (df["haz_score"] < -2.0)
    df["stunting_class"] = np.select(
        [is_severe_stunted, is_mod_stunted],
        ["Severely Stunted", "Moderately Stunted"],
        default="Normal Height-for-Age"
    )
    
    # MUAC Color Band
    muac_cond = [
        df["muac_mm"] < 115,
        (df["muac_mm"] >= 115) & (df["muac_mm"] < 125),
        df["muac_mm"] >= 125
    ]
    df["muac_color_band"] = np.select(muac_cond, ["Red (<115mm SAM)", "Yellow (115-124mm MAM)", "Green (>=125mm Normal)"], default="Green (>=125mm Normal)")
    
    return df

def calculate_sphere_otp_indicators(df):
    """
    Calculates international SPHERE Standards performance indicators for OTP/TSFP:
    - Cure Rate: Target > 75%
    - Defaulter Rate: Target < 15%
    - Death Rate: Target < 3%
    """
    discharges = df[df["program_outcome"].isin(["Discharged Cured", "Defaulter", "Died", "Non-responder"])]
    total_discharged = len(discharges)
    if total_discharged == 0:
        return {}
        
    cured = (discharges["program_outcome"] == "Discharged Cured").sum()
    defaulters = (discharges["program_outcome"] == "Defaulter").sum()
    deaths = (discharges["program_outcome"] == "Died").sum()
    non_resp = (discharges["program_outcome"] == "Non-responder").sum()
    
    cure_rate = round((cured / total_discharged) * 100, 1)
    defaulter_rate = round((defaulters / total_discharged) * 100, 1)
    death_rate = round((deaths / total_discharged) * 100, 1)
    non_resp_rate = round((non_resp / total_discharged) * 100, 1)
    
    return {
        "total_discharges_evaluated": total_discharged,
        "cured_count": cured,
        "cure_rate_pct": cure_rate,
        "cure_sphere_met": cure_rate >= 75.0,
        "defaulter_count": defaulters,
        "defaulter_rate_pct": defaulter_rate,
        "defaulter_sphere_met": defaulter_rate < 15.0,
        "death_count": deaths,
        "death_rate_pct": death_rate,
        "death_sphere_met": death_rate < 3.0,
        "non_responder_pct": non_resp_rate
    }

def audit_smart_plausibility(df):
    """
    SMART Methodology Survey Quality Audit:
    1. Digit Preference Score (DPS) for height and weight terminal digits (0-9).
    2. WHZ Standard Deviation (normal range: 0.80 to 1.20).
    3. WHZ Skewness and Kurtosis (normality test).
    """
    valid_df = df[df["is_anthropometry_valid"] == True].copy()
    
    # 1. Terminal Digit Preference for Height
    # Multiply by 10 to get the first decimal digit: e.g. 78.4 -> 4
    h_decimals = (valid_df["height_cm"] * 10).round().astype(int) % 10
    w_decimals = (valid_df["weight_kg"] * 10).round().astype(int) % 10
    
    # Compute Digit Preference Score: Chi-square of terminal digits
    n_h = len(h_decimals)
    h_counts = h_decimals.value_counts().to_dict()
    expected_d = n_h / 10.0
    dps_h = sum([((h_counts.get(d, 0) - expected_d) ** 2) / expected_d for d in range(10)])
    dps_h = round(math.sqrt(dps_h / 9.0) if dps_h >= 0 else 0.0, 1)
    
    dps_rating = "Excellent (<10)" if dps_h < 10 else ("Good (10-15)" if dps_h < 15 else "Problematic / Rounding Bias (>15)")
    
    # 2. WHZ Distribution Metrics
    whz_series = valid_df["whz_score"].dropna()
    whz_mean = round(float(whz_series.mean()), 2)
    whz_std = round(float(whz_series.std()), 2)
    whz_skew = round(float(whz_series.skew()), 2)
    whz_kurt = round(float(whz_series.kurtosis()), 2)
    
    # Standard deviation assessment (SMART Guideline)
    if 0.80 <= whz_std <= 1.20:
        sd_status = "Excellent (0.80 - 1.20)"
    elif 1.20 < whz_std <= 1.30:
        sd_status = "Acceptable (1.20 - 1.30)"
    else:
        sd_status = "Alert: High Dispersion (>1.30) - Possible measurement errors"
        
    return {
        "sample_size": len(valid_df),
        "digit_preference_score_height": dps_h,
        "dps_rating": dps_rating,
        "whz_mean": whz_mean,
        "whz_standard_deviation": whz_std,
        "whz_sd_status": sd_status,
        "whz_skewness": whz_skew,
        "whz_kurtosis": whz_kurt
    }

if __name__ == "__main__":
    raw_path = os.path.join(BASE_DIR, "data", "raw", "raw_child_nutrition_anthropometry.csv")
    df = pd.read_csv(raw_path)
    df_analyzed = calculate_who_zscores(df)
    sphere = calculate_sphere_otp_indicators(df_analyzed)
    plausibility = audit_smart_plausibility(df_analyzed)
    
    df_analyzed.to_csv(os.path.join(PROCESSED_DIR, "child_nutrition_with_zscores.csv"), index=False)
    print("=== SMART NUTRITION & ANTHROPOMETRY PROCESSED ===")
    print(f"- Total Screened: {len(df_analyzed)}")
    print(f"- GAM Prevalence: {round((df_analyzed['acute_malnutrition_class'].isin(['SAM (Severe Acute Malnutrition)', 'MAM (Moderate Acute Malnutrition)']).sum() / len(df_analyzed))*100, 1)}%")
    print(f"- OTP Cure Rate: {sphere.get('cure_rate_pct')}% (Target > 75%)")
    print(f"- SMART DPS Score: {plausibility.get('digit_preference_score_height')} ({plausibility.get('dps_rating')})")
    print(f"- WHZ Standard Deviation: {plausibility.get('whz_standard_deviation')} ({plausibility.get('whz_sd_status')})")
