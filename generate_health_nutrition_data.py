"""
Humanitarian Health & Nutrition MIS Platform
Simulated Data Generator (DHIS2 & SMART Standards)
Generates:
1. Child Nutrition Anthropometric Screening (WHZ, HAZ, MUAC, Edema, OTP outcomes)
2. Maternal & Child Cash Transfer (MCCT) Beneficiary Compliance Cohorts
3. DHIS2 Clinic Monthly Aggregates with intentional Validation Rule violations
4. Medical Commodity & RUTF (Plumpy'Nut) Stock & Consumption Ledgers
Targeting: Sun Community Health (SCH Jr. MIS Officer) & Terre des hommes (Tdh MEAL Assistant)
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Deterministic seed for reproducible evaluation
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEALTH_FACILITIES = {
    "Mandalay Peri-Urban Clinic": {
        "township": "Mandalay",
        "region": "Mandalay Region",
        "mimu_pcode": "MMR004001",
        "partner": "Terre des hommes (Tdh)",
        "facility_type": "Primary Health Centre & Nutrition OTP",
        "catchment_population": 42000
    },
    "Hlaingtharyar Community Clinic": {
        "township": "Hlaingtharyar",
        "region": "Yangon Region",
        "mimu_pcode": "MMR013008",
        "partner": "Sun Community Health (SCH)",
        "facility_type": "Sun Quality Health Clinic",
        "catchment_population": 78000
    },
    "Lashio IDP Health Post": {
        "township": "Lashio",
        "region": "Shan State (North)",
        "mimu_pcode": "MMR014001",
        "partner": "Tdh & Best Shelter",
        "facility_type": "Emergency Mobile Clinic & OTP",
        "catchment_population": 28000
    },
    "Bogale Rural Sub-Center": {
        "township": "Bogale",
        "region": "Ayeyarwady Region",
        "mimu_pcode": "MMR017006",
        "partner": "Sun Community Health (SCH)",
        "facility_type": "Sub-Rural Health Centre",
        "catchment_population": 31000
    },
    "Dawei Coastal Clinic": {
        "township": "Dawei",
        "region": "Tanintharyi Region",
        "mimu_pcode": "MMR007001",
        "partner": "Shwe Kyun Thar & SCH",
        "facility_type": "Community Health Post",
        "catchment_population": 25000
    }
}

# -------------------------------------------------------------
# 1. CHILD NUTRITION ANTHROPOMETRY DATA (SMART & OTP)
# -------------------------------------------------------------
def generate_nutrition_anthropometry(n_records=420):
    records = []
    base_date = datetime(2026, 7, 1)
    
    fac_names = list(HEALTH_FACILITIES.keys())
    
    for i in range(1, n_records + 1):
        fac_name = random.choice(fac_names)
        fac_info = HEALTH_FACILITIES[fac_name]
        
        child_id = f"NUT-{fac_info['township'][:3].upper()}-{i:04d}"
        screen_date = base_date + timedelta(days=random.randint(0, 90))
        gender = random.choice(["Female", "Male"])
        age_months = random.randint(6, 59)
        
        # Anthropometry simulation based on WHO 2006 growth curves
        # Height typically 65cm to 110cm for 6-59 months
        base_height = 60.0 + (age_months * 0.85) + np.random.normal(0, 3.5)
        base_height = round(min(115.0, max(55.0, base_height)), 1)
        
        # Vulnerability weighting by hub (Lashio IDP and Mandalay have higher malnutrition)
        is_high_risk = fac_info["township"] in ["Lashio", "Mandalay"] or random.random() < 0.20
        
        # Weight based on height: WHZ distribution
        if is_high_risk and random.random() < 0.25:
            # SAM or MAM child
            target_whz = np.random.uniform(-3.8, -2.1)
        else:
            target_whz = np.random.normal(-0.8, 1.1)
            
        # WHO approximate median weight for height H: W_med ≈ 0.0016 * H^1.95
        w_med = 0.0016 * (base_height ** 1.95)
        w_sd = w_med * 0.10
        weight_kg = round(max(3.5, w_med + (target_whz * w_sd) + np.random.normal(0, 0.2)), 2)
        
        # MUAC (in mm): Normal >= 125, MAM 115-124, SAM < 115
        if target_whz < -3.0:
            muac_mm = random.randint(102, 114) # Red
        elif target_whz < -2.0:
            muac_mm = random.randint(115, 124) # Yellow
        else:
            muac_mm = random.randint(125, 158) # Green
            
        # Bilateral Pitting Edema (Rare, Pathognomonic for SAM / Kwashiorkor)
        has_edema = "Yes" if (target_whz < -2.8 and random.random() < 0.08) else "No"
        
        # Admission & OTP/TSFP Outcome
        if target_whz < -3.0 or has_edema == "Yes" or muac_mm < 115:
            nut_category = "SAM (Severe Acute Malnutrition)"
            program = "OTP (Outpatient Therapeutic Programme)"
            rutf_sachets = random.randint(14, 28)
            outcome = random.choices(["In Treatment", "Discharged Cured", "Defaulter", "Died", "Non-responder"], weights=[0.45, 0.42, 0.09, 0.02, 0.02])[0]
        elif target_whz < -2.0 or muac_mm < 125:
            nut_category = "MAM (Moderate Acute Malnutrition)"
            program = "TSFP (Targeted Supplementary Feeding)"
            rutf_sachets = random.randint(7, 14)
            outcome = random.choices(["In Treatment", "Discharged Cured", "Defaulter", "Non-responder"], weights=[0.50, 0.42, 0.06, 0.02])[0]
        else:
            nut_category = "Normal / Well Nourished"
            program = "Community Growth Monitoring"
            rutf_sachets = 0
            outcome = "Normal Screening"
            
        # Measurer ID
        measurer_id = f"CHW-{random.randint(101, 112)}"

        records.append({
            "child_id": child_id,
            "screening_date": screen_date.strftime("%Y-%m-%d"),
            "health_facility": fac_name,
            "township": fac_info["township"],
            "region": fac_info["region"],
            "mimu_pcode": fac_info["mimu_pcode"],
            "implementing_partner": fac_info["partner"],
            "measurer_id": measurer_id,
            "gender": gender,
            "age_months": age_months,
            "height_cm": base_height,
            "weight_kg": weight_kg,
            "muac_mm": muac_mm,
            "bilateral_edema": has_edema,
            "nutritional_status": nut_category,
            "program_enrolled": program,
            "rutf_sachets_prescribed": rutf_sachets,
            "program_outcome": outcome
        })
        
    df = pd.DataFrame(records)
    
    # Intentional Data Quality / SMART Plausibility checks:
    # 1. Terminal digit preference clustering on height/weight (CHW-104 prefers .0 and .5)
    for idx in df[df["measurer_id"] == "CHW-104"].index:
        df.loc[idx, "height_cm"] = round(df.loc[idx, "height_cm"])
        df.loc[idx, "weight_kg"] = round(df.loc[idx, "weight_kg"] * 2) / 2
        
    # 2. Extreme impossible outlier (measuring typo: 95kg instead of 9.5kg)
    df.loc[14, "weight_kg"] = 95.0
    df.loc[38, "height_cm"] = 19.5 # 19.5cm instead of 91.5cm
    
    return df

# -------------------------------------------------------------
# 2. MATERNAL & CHILD CASH TRANSFER (MCCT) COHORT
# -------------------------------------------------------------
def generate_mcct_plw_data(n_records=280):
    records = []
    base_date = datetime(2026, 6, 1)
    
    fac_names = list(HEALTH_FACILITIES.keys())
    
    for i in range(1, n_records + 1):
        fac_name = random.choice(fac_names)
        fac_info = HEALTH_FACILITIES[fac_name]
        
        reg_id = f"MCCT-{fac_info['township'][:3].upper()}-{i:04d}"
        mother_name = f"Daw {random.choice(['Hla Hla', 'Aye Aye', 'Khin Win', 'Su Su', 'Thin Thin', 'Nilar', 'May Thazin', 'Thida', 'Phyu Phyu'])} {random.choice(['Win', 'Moe', 'Khaing', 'San', 'Latt', 'New', 'Oo', 'Mon'])}"
        
        reg_date = base_date + timedelta(days=random.randint(0, 80))
        mother_age = random.randint(18, 42)
        beneficiary_type = random.choices(["Pregnant Woman", "Lactating Mother"], weights=[0.45, 0.55])[0]
        
        # MCCT conditionalities / co-responsibilities
        if beneficiary_type == "Pregnant Woman":
            gestational_weeks = random.randint(12, 38)
            child_age_m = 0
            # Target ANC is 4 visits across pregnancy
            anc_visits = min(4, max(1, int(gestational_weeks / 8)))
            facility_delivery = "Pending"
            child_immunized = "Not Applicable"
        else:
            gestational_weeks = 40
            child_age_m = random.randint(1, 18)
            anc_visits = random.choices([2, 3, 4], weights=[0.15, 0.35, 0.50])[0]
            facility_delivery = random.choices(["Yes (Hospital/Clinic)", "Yes (RHC Midwife)", "No (Home / Unskilled)"], weights=[0.55, 0.30, 0.15])[0]
            child_immunized = "Full for Age" if random.random() > 0.14 else "Delayed / Defaulter"
            
        iycf_sessions = random.randint(1, 6)
        
        # Compliance evaluation for monthly 50,000 MMK cash tranche
        # Condition: At least 3 ANC visits (or on schedule), attended IYCF session
        is_compliant = (anc_visits >= 2 and iycf_sessions >= 2)
        if beneficiary_type == "Lactating Mother" and child_immunized == "Delayed / Defaulter":
            is_compliant = False
            
        compliance_status = "Compliant (Eligible for Cash)" if is_compliant else "Non-Compliant (Hold Tranche)"
        payment_channel = random.choices(["Wave Money", "KBZPay", "Cash Delivery at Clinic"], weights=[0.50, 0.35, 0.15])[0]
        
        disbursement = "Disbursed" if (is_compliant and random.random() > 0.08) else ("Pending Approval" if is_compliant else "Withheld / Remedial Action")
        
        records.append({
            "beneficiary_id": reg_id,
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "mother_name": mother_name,
            "age": mother_age,
            "township": fac_info["township"],
            "health_facility": fac_name,
            "implementing_partner": fac_info["partner"],
            "beneficiary_type": beneficiary_type,
            "gestational_weeks": gestational_weeks,
            "child_age_months": child_age_m,
            "anc_visits_completed": anc_visits,
            "facility_delivery_status": facility_delivery,
            "child_immunization_status": child_immunized,
            "iycf_sessions_attended": iycf_sessions,
            "monthly_cash_entitlement_mmk": 50000,
            "compliance_status": compliance_status,
            "payment_channel": payment_channel,
            "disbursement_status": disbursement
        })
        
    return pd.DataFrame(records)

# -------------------------------------------------------------
# 3. DHIS2 CLINIC MONTHLY AGGREGATE REPORTS
# -------------------------------------------------------------
def generate_dhis2_monthly_reports():
    records = []
    months = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    
    for month in months:
        for fac_name, fac_info in HEALTH_FACILITIES.items():
            base_pop = fac_info["catchment_population"]
            
            # OPD Consultations
            opd_u5_f = int(base_pop * random.uniform(0.008, 0.015))
            opd_u5_m = int(base_pop * random.uniform(0.008, 0.015))
            opd_o5_f = int(base_pop * random.uniform(0.020, 0.035))
            opd_o5_m = int(base_pop * random.uniform(0.018, 0.030))
            opd_total = opd_u5_f + opd_u5_m + opd_o5_f + opd_o5_m
            
            # Maternal & Reproductive Health
            anc_1st = int(base_pop * random.uniform(0.0025, 0.0040))
            anc_4th = int(anc_1st * random.uniform(0.65, 0.88))
            pnc_visits = int(anc_4th * random.uniform(0.70, 0.90))
            fp_oral_cycles = random.randint(45, 180)
            fp_depo_injections = random.randint(60, 240)
            
            # Malaria Surveillance (RDT)
            malaria_tested = random.randint(80, 320)
            malaria_positive = int(malaria_tested * random.uniform(0.04, 0.14))
            malaria_treated_act = malaria_positive # standard clinical protocol
            
            # Tuberculosis
            tb_presumptive_screened = random.randint(25, 80)
            tb_confirmed_positive = int(tb_presumptive_screened * random.uniform(0.08, 0.18))
            tb_dots_enrolled = tb_confirmed_positive
            
            # Immunization (Birth cohort ≈ base_pop * 0.025 / 12)
            monthly_births = int(base_pop * 0.025 / 12)
            bcg_doses = int(monthly_births * random.uniform(0.85, 1.05))
            penta_3_doses = int(monthly_births * random.uniform(0.78, 0.96))
            mr_measles_doses = int(monthly_births * random.uniform(0.75, 0.94))
            
            # Nutrition (SAM/MAM admissions)
            sam_new_admissions = random.randint(4, 25)
            mam_new_admissions = random.randint(12, 45)
            
            records.append({
                "period": month,
                "org_unit_name": fac_name,
                "township": fac_info["township"],
                "mimu_pcode": fac_info["mimu_pcode"],
                "partner": fac_info["partner"],
                "opd_under5_female": opd_u5_f,
                "opd_under5_male": opd_u5_m,
                "opd_over5_female": opd_o5_f,
                "opd_over5_male": opd_o5_m,
                "opd_total_attendance": opd_total,
                "anc_1st_visit": anc_1st,
                "anc_4th_visit": anc_4th,
                "male_anc_visits": 0, # Should strictly be 0 (tested by DHIS2 rule)
                "pnc_visits": pnc_visits,
                "fp_oral_cycles_distributed": fp_oral_cycles,
                "fp_depo_injections_given": fp_depo_injections,
                "malaria_rdt_tested": malaria_tested,
                "malaria_rdt_positive": malaria_positive,
                "malaria_treated_act": malaria_treated_act,
                "tb_screened": tb_presumptive_screened,
                "tb_sputum_positive": tb_confirmed_positive,
                "tb_started_dots": tb_dots_enrolled,
                "estimated_monthly_birth_cohort": monthly_births,
                "bcg_doses_given": bcg_doses,
                "penta_3_doses_given": penta_3_doses,
                "mr_measles_doses_given": mr_measles_doses,
                "sam_admissions": sam_new_admissions,
                "mam_admissions": mam_new_admissions
            })
            
    df = pd.DataFrame(records)
    
    # Intentional DHIS2 Validation Rule Violations:
    # 1. Male ANC Attendance > 0 (Impossible logic error: 3 male ANC recorded at Bogale in 2026-08)
    bogale_idx = df[(df["township"] == "Bogale") & (df["period"] == "2026-08")].index
    if len(bogale_idx) > 0:
        df.loc[bogale_idx[0], "male_anc_visits"] = 3
        
    # 2. ACT Treatment > RDT Positives (Over-treatment / data discrepancy: treated 42 when only 18 positive)
    lashio_idx = df[(df["township"] == "Lashio") & (df["period"] == "2026-09")].index
    if len(lashio_idx) > 0:
        df.loc[lashio_idx[0], "malaria_treated_act"] = df.loc[lashio_idx[0], "malaria_rdt_positive"] + 24
        
    # 3. Measles MR Vaccinations > Total Birth Cohort (Surpassing 100% by 180% - duplicate tally)
    mandalay_idx = df[(df["township"] == "Mandalay") & (df["period"] == "2026-07")].index
    if len(mandalay_idx) > 0:
        df.loc[mandalay_idx[0], "mr_measles_doses_given"] = df.loc[mandalay_idx[0], "estimated_monthly_birth_cohort"] + 65

    return df

# -------------------------------------------------------------
# 4. MEDICAL COMMODITY & RUTF STOCK LEDGER
# -------------------------------------------------------------
def generate_commodity_stock_data():
    records = []
    months = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    
    commodities = [
        {"item": "RUTF (Plumpy'Nut 92g Sachets)", "unit": "Sachets", "pack_size": 150, "base_monthly_dispensed": 1200},
        {"item": "Iron Folic Acid (IFA 60mg/400mcg)", "unit": "Tablets", "pack_size": 1000, "base_monthly_dispensed": 4500},
        {"item": "Amoxicillin 125mg/5ml Dry Syrup", "unit": "Bottles", "pack_size": 50, "base_monthly_dispensed": 350},
        {"item": "Malaria Pf/Pv Rapid Test (RDT)", "unit": "Tests", "pack_size": 25, "base_monthly_dispensed": 200},
        {"item": "Artemether-Lumefantrine (ACT) 20/120mg", "unit": "Blisters", "pack_size": 30, "base_monthly_dispensed": 80},
        {"item": "Oral Rehydration Salts (ORS) + Zinc", "unit": "Co-packs", "pack_size": 100, "base_monthly_dispensed": 400},
        {"item": "Vitamin A 200,000 IU Capsules", "unit": "Capsules", "pack_size": 500, "base_monthly_dispensed": 600}
    ]
    
    for fac_name, fac_info in HEALTH_FACILITIES.items():
        for comm in commodities:
            current_balance = int(comm["base_monthly_dispensed"] * random.uniform(1.8, 3.2))
            
            for m in months:
                dispensed = int(comm["base_monthly_dispensed"] * random.uniform(0.85, 1.25))
                # Restocking every 2 months
                received = int(comm["base_monthly_dispensed"] * 2.5) if random.random() < 0.45 else 0
                losses = random.choice([0, 0, 0, 5, 12])
                
                # Intentional Stock-out scenario for RUTF at Lashio in 2026-09 & 2026-10
                if fac_info["township"] == "Lashio" and "RUTF" in comm["item"] and m in ["2026-09", "2026-10"]:
                    received = 0
                    dispensed = min(current_balance, dispensed)
                    closing_balance = max(0, current_balance - dispensed - losses)
                    days_stockout = random.randint(8, 16)
                else:
                    closing_balance = max(0, current_balance + received - dispensed - losses)
                    days_stockout = 0 if closing_balance > 50 else random.randint(1, 5)
                    
                records.append({
                    "month": m,
                    "health_facility": fac_name,
                    "township": fac_info["township"],
                    "commodity_name": comm["item"],
                    "unit": comm["unit"],
                    "opening_balance": current_balance,
                    "received_quantity": received,
                    "dispensed_quantity": dispensed,
                    "losses_and_expired": losses,
                    "closing_balance": closing_balance,
                    "stock_out_days": days_stockout
                })
                current_balance = closing_balance
                
    return pd.DataFrame(records)

if __name__ == "__main__":
    print("Generating Humanitarian Health & Nutrition MIS Datasets...")
    df_nut = generate_nutrition_anthropometry(420)
    df_mcct = generate_mcct_plw_data(280)
    df_dhis2 = generate_dhis2_monthly_reports()
    df_stock = generate_commodity_stock_data()
    
    df_nut.to_csv(os.path.join(RAW_DIR, "raw_child_nutrition_anthropometry.csv"), index=False)
    df_mcct.to_csv(os.path.join(RAW_DIR, "raw_mcct_plw_beneficiaries.csv"), index=False)
    df_dhis2.to_csv(os.path.join(RAW_DIR, "raw_dhis2_clinic_monthly_reports.csv"), index=False)
    df_stock.to_csv(os.path.join(RAW_DIR, "raw_medical_commodity_stock.csv"), index=False)
    
    print(f"[OK] Child Anthropometric records: {len(df_nut)}")
    print(f"[OK] MCCT PLW Beneficiaries: {len(df_mcct)}")
    print(f"[OK] DHIS2 Monthly Clinic Reports: {len(df_dhis2)}")
    print(f"[OK] Commodity Stock Ledgers: {len(df_stock)}")
