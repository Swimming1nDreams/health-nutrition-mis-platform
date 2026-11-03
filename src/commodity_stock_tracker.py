"""
Humanitarian Health & Nutrition MIS Platform
Module 4: Medical Commodity & RUTF Nutrition Supply Tracker
Author: M&E & Data Assistant Candidate
Direct Alignment: Sun Community Health & Tdh Logistics/MIS Coordination
Functions:
- Tracks consumption of essential lifesaving commodities (RUTF, IFA, Amoxicillin, RDTs)
- Computes Average Monthly Consumption (AMC) and Months of Stock (MoS)
- Early Warning Alerts for Stock-Outs and Overstock / Expiration Risks
- Calculates Recommended Re-Order Quantities (ROQ)
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Standard Humanitarian Buffer Stock Thresholds (in Months of Stock)
MIN_MONTHS_STOCK = 1.0  # Buffer minimum
MAX_MONTHS_STOCK = 3.0  # Upper ceiling to prevent shelf-life expiration

def analyze_commodity_stock(df):
    """
    Computes consumption dynamics and stock security metrics per facility & commodity:
    - Average Monthly Consumption (AMC)
    - Months of Stock (MoS = closing_balance / AMC)
    - Risk Categorization & Reorder Quantities
    """
    df = df.copy()
    
    # 1. Compute Average Monthly Consumption (AMC) per facility and commodity
    amc_table = df.groupby(["health_facility", "commodity_name"])["dispensed_quantity"].mean().reset_index()
    amc_table = amc_table.rename(columns={"dispensed_quantity": "amc"})
    amc_table["amc"] = amc_table["amc"].round(1)
    
    # Merge AMC back into dataframe
    df = df.merge(amc_table, on=["health_facility", "commodity_name"], how="left")
    
    # Avoid zero division
    df["amc"] = np.where(df["amc"] <= 0, 1.0, df["amc"])
    
    # 2. Months of Stock (MoS)
    df["months_of_stock"] = np.round(df["closing_balance"] / df["amc"], 2)
    
    # 3. Stock Security Status
    status_list = []
    reorder_list = []
    
    for _, row in df.iterrows():
        bal = row["closing_balance"]
        mos = row["months_of_stock"]
        amc = row["amc"]
        out_days = row.get("stock_out_days", 0)
        
        if bal == 0 or out_days > 0:
            status = "Stocked Out / Emergency Order"
            reorder = int((MAX_MONTHS_STOCK * amc) - bal)
        elif mos < MIN_MONTHS_STOCK:
            status = "Understocked / High Risk (< 1.0 MoS)"
            reorder = int((MAX_MONTHS_STOCK * amc) - bal)
        elif mos > MAX_MONTHS_STOCK:
            status = "Overstocked / Expiration Risk (> 3.0 MoS)"
            reorder = 0
        else:
            status = "Adequate Stock (1.0 - 3.0 MoS)"
            reorder = max(0, int((MAX_MONTHS_STOCK * amc) - bal))
            
        status_list.append(status)
        reorder_list.append(max(0, reorder))
        
    df["stock_security_status"] = status_list
    df["recommended_reorder_qty"] = reorder_list
    
    return df

def get_latest_stock_status_summary(df):
    """
    Filters to the latest reporting month (e.g. 2026-10) to generate executive alerts.
    """
    latest_month = df["month"].max()
    latest_df = df[df["month"] == latest_month].copy()
    
    critical_alerts = latest_df[latest_df["stock_security_status"].str.contains("Stocked Out|Understocked", na=False)]
    
    summary = {
        "latest_reporting_month": latest_month,
        "total_commodity_lines": len(latest_df),
        "stocked_out_lines": (latest_df["stock_security_status"] == "Stocked Out / Emergency Order").sum(),
        "understocked_lines": (latest_df["stock_security_status"] == "Understocked / High Risk (< 1.0 MoS)").sum(),
        "adequate_lines": (latest_df["stock_security_status"] == "Adequate Stock (1.0 - 3.0 MoS)").sum(),
        "overstocked_lines": (latest_df["stock_security_status"] == "Overstocked / Expiration Risk (> 3.0 MoS)").sum(),
        "critical_items_list": critical_alerts[["health_facility", "commodity_name", "closing_balance", "months_of_stock", "stock_security_status", "recommended_reorder_qty"]].to_dict(orient="records")
    }
    return latest_df, summary

if __name__ == "__main__":
    raw_path = os.path.join(BASE_DIR, "data", "raw", "raw_medical_commodity_stock.csv")
    df = pd.read_csv(raw_path)
    df_analyzed = analyze_commodity_stock(df)
    latest_df, summary = get_latest_stock_status_summary(df_analyzed)
    
    df_analyzed.to_csv(os.path.join(PROCESSED_DIR, "commodity_stock_analyzed.csv"), index=False)
    print("=== MEDICAL & NUTRITION COMMODITY STOCK ANALYZED ===")
    print(f"- Latest Month: {summary['latest_reporting_month']}")
    print(f"- Stocked Out Lines: {summary['stocked_out_lines']}")
    print(f"- Understocked Lines: {summary['understocked_lines']}")
    print(f"- Adequate Stock Lines: {summary['adequate_lines']}")
