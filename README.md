# Humanitarian Health & Nutrition MIS Platform
### Professional Portfolio Project for Health MIS & Nutrition MEAL Assistant Positions

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Portal-FF4B4B.svg)](https://streamlit.io/)
[![DHIS2 Standard](https://img.shields.io/badge/Standard-DHIS2%20Validation%20Rules-2B88D8.svg)](https://dhis2.org/)
[![WHO Standards](https://img.shields.io/badge/Standards-WHO%20Growth%202006-0093D5.svg)](https://www.who.int/)
[![SPHERE Standards](https://img.shields.io/badge/Charter-SPHERE%20Humanitarian%20OTP-10B981.svg)](https://www.spherestandards.org/)

---

## 📌 Executive Summary

This enterprise-grade **Humanitarian Health & Nutrition Management Information System (MIS)** was specifically engineered to demonstrate **100% technical competency alignment** with the hiring requirements of:
1. **Sun Community Health (SCH)** — *Junior MIS Officer* (DHIS2, Primary Health Care, Clinic Reporting, Medical Commodity Tracking, Data Quality Assurance).
2. **Terre des hommes (Tdh)** — *MEAL Assistant - Nutrition & Maternal Child Cash Transfer (MCCT)* (Mandalay Project, SMART Anthropometric Screening, OTP/TSFP Performance, Beneficiary Compliance Verification).

The platform models primary healthcare clinics and emergency nutrition sites across **5 Myanmar operational hubs** (*Mandalay Peri-Urban, Hlaingtharyar/Yangon Peri-Urban, Lashio IDP Sites, Bogale Delta, and Dawei Coastal*). It covers the full lifecycle of humanitarian health data: from clinical consultations and child anthropometric growth monitoring to DHIS2 validation rule evaluation, MCCT mobile money payroll processing, and essential commodity stock-out early warnings.

---

## 🎯 Key Health & Nutrition Competencies Demonstrated

| Technical Domain | Standard / Humanitarian Framework | Implementation in this Platform |
| :--- | :--- | :--- |
| **DHIS2 Health MIS & Validation Rules** | DHIS2 Web API Standard & MoHS Myanmar | Programmatic evaluation of Left-Hand Side vs Right-Hand Side expressions to catch reporting contradictions (Male ANC attendance, ACT over-dispensation vs RDT positives, Measles vaccination overflow). Exports valid `dataValueSets` JSON payloads. |
| **SMART Nutrition Surveillance** | WHO Child Growth Standards (2006) | Calculates Weight-for-Height Z-score (WHZ), Height-for-Age Z-score (HAZ), and Weight-for-Age Z-score (WAZ) for children 6-59 months. Classifies Global Acute Malnutrition (GAM), Severe Acute Malnutrition (SAM), and Moderate Acute Malnutrition (MAM). |
| **SPHERE Humanitarian Charter** | SPHERE Standards for Nutrition (OTP / TSFP) | Evaluates therapeutic feeding programme performance: Cure Rate (Target: $> 75\%$), Defaulter Rate (Target: $< 15\%$), and Death Rate (Target: $< 3\%$). |
| **SMART Plausibility Quality Audit** | SMART Survey Data Quality Methodology | Calculates Digit Preference Score (DPS) for height and weight terminal decimals (0-9) to detect surveyor rounding bias. Assesses WHZ Standard Deviation (normal: $0.80 - 1.20$), skewness, and kurtosis. |
| **Maternal & Child Cash Transfer (MCCT)** | National MCCT & Tdh Social Protection Guidelines | Tracks Pregnant & Lactating Women (PLW) cohorts against co-responsibilities (ANC visits, facility delivery, infant immunization, IYCF counseling attendance). Automatically verifies compliance and generates bulk mobile money payroll batches (Wave Money / KBZPay). |
| **Essential Medical Buffer Stock (MoS)** | Humanitarian Logistics & MoHS Supply Chain | Monitors Average Monthly Consumption (AMC) and Months of Stock (MoS = Balance / AMC) for essential commodities (RUTF Plumpy'Nut, Iron Folic Acid, Amoxicillin, Malaria RDTs). Triggers early warning alerts for stock-outs (< 1.0 MoS) and expiration risks (> 3.0 MoS). |
| **Primary Health Care & SADD** | IASC Health Cluster & Gender Disaggregation | Monthly morbidity tracking for OPD consultations disaggregated by age (Under 5 vs Over 5) and gender, Antenatal Care retention cascade (ANC 1st $\to$ ANC 4th $\to$ PNC), Family Planning, and TB/Malaria communicable disease surveillance. |

---

## 📂 Project Architecture

```
health_nutrition_mis_portfolio/
├── app.py                             # Executive Health & Nutrition MIS Portal (6 Tabs)
├── generate_health_nutrition_data.py  # Realistic Multi-Hub Clinical & Nutrition Data Generator
├── run_portal.bat                     # One-click Windows desktop launcher (Port 8502)
├── requirements.txt                   # Python dependencies
│
├── src/                               # Modular Clinical & Nutrition Engines
│   ├── nutrition_anthropometry.py     # WHO Growth Z-scores, GAM/SAM/MAM, SPHERE OTP, SMART DPS
│   ├── mcct_compliance.py             # PLW milestone verification & mobile money payroll generator
│   ├── dhis2_mis_engine.py            # DHIS2 Validation Rules & DataValueSets JSON exporter
│   └── commodity_stock_tracker.py     # Average Monthly Consumption (AMC) & Months of Stock (MoS)
│
├── data/
│   ├── raw/                           # Raw clinic and field screening registers
│   │   ├── raw_child_nutrition_anthropometry.csv
│   │   ├── raw_mcct_plw_beneficiaries.csv
│   │   ├── raw_dhis2_clinic_monthly_reports.csv
│   │   └── raw_medical_commodity_stock.csv
│   │
│   └── processed/                     # Analytical tables with Z-scores and compliance flags
│       ├── child_nutrition_with_zscores.csv
│       ├── mcct_plw_with_compliance.csv
│       └── commodity_stock_analyzed.csv
│
└── reports/                           # Humanitarian Export Deliverables
    ├── dhis2_health_datavaluesets_export.json
    ├── dhis2_validation_rule_violations.csv
    └── mcct_mobile_money_payroll_batch.csv
```

---

## 🚀 How to Run the Platform Locally

### Option 1: One-Click Desktop Launcher (Windows)
Double-click `run_portal.bat`. It will activate the virtual environment and open the interactive Health & Nutrition Operations Portal on `http://localhost:8502`.

### Option 2: Command Line Execution
```bash
# 1. Navigate to project directory
cd health_nutrition_mis_portfolio

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. (Optional) Re-run data generation and processing pipelines
python generate_health_nutrition_data.py
python src/nutrition_anthropometry.py
python src/mcct_compliance.py
python src/dhis2_mis_engine.py
python src/commodity_stock_tracker.py

# 4. Launch the Streamlit Portal
streamlit run app.py --server.port 8502
```

---

## 📊 Technical Methodology & Formulas

### 1. WHO 2006 Child Growth Standards (Z-Score Computation)
- **Weight-for-Height Z-score (WHZ):**
  $$\text{WHZ} = \frac{\text{Weight} - \text{Median Weight}(H)}{\text{SD}(H)}$$
  Categorization:
  - **SAM (Severe Acute Malnutrition):** $\text{WHZ} < -3.0$ OR $\text{MUAC} < 115\text{ mm}$ OR $\text{Bilateral Edema} == \text{"Yes"}$
  - **MAM (Moderate Acute Malnutrition):** $-3.0 \le \text{WHZ} < -2.0$ OR $115 \le \text{MUAC} < 125\text{ mm}$
  - **GAM (Global Acute Malnutrition):** $\text{GAM Rate} = \text{SAM \%} + \text{MAM \%}$

### 2. SMART Plausibility Audit (Digit Preference Score)
- Calculates terminal decimal distribution ($d \in \{0, 1, \dots, 9\}$) for heights and weights:
  $$\text{DPS} = \sqrt{\frac{1}{9} \sum_{d=0}^{9} \frac{(O_d - E)^2}{E}}$$
  where $E = N / 10$. Rating: $< 10$ Excellent, $10-15$ Good, $> 15$ Problematic rounding bias.

### 3. DHIS2 Validation Rules (Clinical Inconsistency Traps)
- **VAL-01:** Biological rule: `male_anc_visits == 0`.
- **VAL-02:** Over-treatment rule: `malaria_treated_act <= malaria_rdt_positive`.
- **VAL-03:** Target rule: `mr_measles_doses <= birth_cohort * 1.25`.
- **VAL-04:** Retention rule: `anc_4th_visit <= anc_1st_visit`.

### 4. Essential Commodity Supply & Months of Stock (MoS)
- **Average Monthly Consumption (AMC):** Mean units dispensed over historical period.
- **Months of Stock (MoS):** $\text{MoS} = \frac{\text{Closing Balance}}{\text{AMC}}$.
- **Recommended Order Quantity (ROQ):** $\text{ROQ} = (3.0 \times \text{AMC}) - \text{Closing Balance}$.

---

## 👤 Target Recruitment Alignment
Built specifically as a showcase portfolio for:
- **Sun Community Health (SCH)** — *Junior MIS Officer*
- **Terre des hommes (Tdh)** — *MEAL Assistant (Nutrition & MCCT Mandalay)*
- **UNICEF / Global Fund / LIFT** — Health & Nutrition Implementing Partner M&E teams
