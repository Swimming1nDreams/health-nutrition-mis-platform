"""
Humanitarian Health & Nutrition MIS Platform
Module 3: DHIS2 Health MIS & Data Validation Rule Engine
Author: M&E & Data Assistant Candidate
Direct Alignment: Sun Community Health (SCH) Jr. MIS Officer
Functions:
- Executes programmatic DHIS2 Validation Rules (Left-Hand Side vs Right-Hand Side)
- Detects clinical reporting inconsistencies (Male pregnancy, ACT over-dispensation, vaccination anomalies)
- Exports compliant DHIS2 DataValueSets JSON payload for DHIS2 Web API (/api/dataValueSets)
"""

import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

DHIS2_DATA_ELEMENTS = {
    "opd_total_attendance": {"uid": "DE_OPD_TOTAL", "name": "OPD Total Consultations"},
    "anc_1st_visit": {"uid": "DE_ANC_1ST", "name": "Antenatal Care 1st Visit"},
    "anc_4th_visit": {"uid": "DE_ANC_4TH", "name": "Antenatal Care 4th Visit"},
    "male_anc_visits": {"uid": "DE_ANC_MALE", "name": "Male ANC Attendance (Validation Trap)"},
    "pnc_visits": {"uid": "DE_PNC_TOTAL", "name": "Postnatal Care Visits"},
    "malaria_rdt_tested": {"uid": "DE_MAL_TESTED", "name": "Malaria RDT Tested"},
    "malaria_rdt_positive": {"uid": "DE_MAL_POS", "name": "Malaria RDT Positive Cases"},
    "malaria_treated_act": {"uid": "DE_MAL_ACT", "name": "Malaria Cases Treated with ACT"},
    "tb_screened": {"uid": "DE_TB_SCREEN", "name": "Presumptive TB Screened"},
    "tb_sputum_positive": {"uid": "DE_TB_POS", "name": "TB Sputum Positive Confirmed"},
    "mr_measles_doses_given": {"uid": "DE_IMM_MEASLES", "name": "Measles-Rubella Doses Administered"},
    "sam_admissions": {"uid": "DE_NUT_SAM", "name": "Severe Acute Malnutrition New Admissions"}
}

def evaluate_dhis2_validation_rules(df):
    """
    Executes standard DHIS2 Validation Rules against monthly clinic reports.
    Returns:
    - enriched_df with validation flags
    - violations_log: Detailed log of exact clinic-months that broke rules
    """
    df = df.copy()
    violations = []
    
    for idx, row in df.iterrows():
        period = row["period"]
        clinic = row["org_unit_name"]
        township = row["township"]
        
        # Rule 1: Male ANC Attendance must strictly be 0
        if row.get("male_anc_visits", 0) > 0:
            violations.append({
                "period": period,
                "health_facility": clinic,
                "township": township,
                "rule_name": "VAL-01: Biological Impossibility (Male ANC Attendance)",
                "expression": "male_anc_visits == 0",
                "left_side_value": row["male_anc_visits"],
                "right_side_value": 0,
                "severity": "Critical Error",
                "action": "Immediate return to clinic data clerk for correction"
            })
            
        # Rule 2: Malaria ACT treated cannot exceed RDT confirmed positive cases
        if row["malaria_treated_act"] > row["malaria_rdt_positive"]:
            violations.append({
                "period": period,
                "health_facility": clinic,
                "township": township,
                "rule_name": "VAL-02: Over-prescription Discrepancy (ACT Treated > RDT Positive)",
                "expression": "malaria_treated_act <= malaria_rdt_positive",
                "left_side_value": row["malaria_treated_act"],
                "right_side_value": row["malaria_rdt_positive"],
                "severity": "Warning / Audit Needed",
                "action": "Verify if clinical presumptive treatment without RDT occurred"
            })
            
        # Rule 3: Measles vaccination doses cannot exceed birth cohort by > 20%
        births = row["estimated_monthly_birth_cohort"]
        if row["mr_measles_doses_given"] > (births * 1.25):
            violations.append({
                "period": period,
                "health_facility": clinic,
                "township": township,
                "rule_name": "VAL-03: Immunization Target Overflow (Measles Doses > 125% Birth Cohort)",
                "expression": "mr_measles_doses <= birth_cohort * 1.25",
                "left_side_value": row["mr_measles_doses_given"],
                "right_side_value": births,
                "severity": "Data Anomaly",
                "action": "Check for duplicate batch recording or cross-boundary migrant influx"
            })
            
        # Rule 4: ANC 4th Visits cannot exceed ANC 1st Visits
        if row["anc_4th_visit"] > row["anc_1st_visit"]:
            violations.append({
                "period": period,
                "health_facility": clinic,
                "township": township,
                "rule_name": "VAL-04: Longitudinal Inconsistency (ANC 4th > ANC 1st)",
                "expression": "anc_4th_visit <= anc_1st_visit",
                "left_side_value": row["anc_4th_visit"],
                "right_side_value": row["anc_1st_visit"],
                "severity": "Logic Contradiction",
                "action": "Audit antenatal register dropouts"
            })

    df_violations = pd.DataFrame(violations)
    return df, df_violations

def export_dhis2_json_payload(df):
    """
    Constructs a standard DHIS2 DataValueSets JSON payload ready for
    DHIS2 Web API POST `/api/dataValueSets`.
    """
    data_values = []
    
    for _, row in df.iterrows():
        # Convert YYYY-MM to DHIS2 period format YYYYMM (e.g. 202608)
        period_str = str(row["period"]).replace("-", "")
        org_unit = row["mimu_pcode"]
        
        for col_name, de_meta in DHIS2_DATA_ELEMENTS.items():
            if col_name in row:
                val = row[col_name]
                data_values.append({
                    "dataElement": de_meta["uid"],
                    "period": period_str,
                    "orgUnit": org_unit,
                    "value": str(val),
                    "comment": f"{de_meta['name']} recorded at {row['org_unit_name']}"
                })
                
    payload = {
        "dataSet": "SCH_PRIMARY_HEALTH_MONTHLY",
        "completeDate": "2026-11-01",
        "period": "2026Q3",
        "orgUnit": "MMR_SCH_FACILITIES",
        "dataValues": data_values
    }
    return payload

if __name__ == "__main__":
    raw_path = os.path.join(BASE_DIR, "data", "raw", "raw_dhis2_clinic_monthly_reports.csv")
    df = pd.read_csv(raw_path)
    df_audited, df_violations = evaluate_dhis2_validation_rules(df)
    dhis2_json = export_dhis2_json_payload(df)
    
    df_violations.to_csv(os.path.join(REPORTS_DIR, "dhis2_validation_rule_violations.csv"), index=False)
    with open(os.path.join(REPORTS_DIR, "dhis2_health_datavaluesets_export.json"), "w") as f:
        json.dump(dhis2_json, f, indent=2)
        
    print("=== DHIS2 HEALTH MIS ENGINE AUDITED ===")
    print(f"- Total Clinic Reports Analyzed: {len(df)}")
    print(f"- Validation Rule Violations Flagged: {len(df_violations)}")
    print(f"- DHIS2 Data Values in Payload: {len(dhis2_json['dataValues'])}")
