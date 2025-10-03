import os, json, glob, re
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Config / Inputs ---
ROOT = os.getcwd()
DATA_DIR = ROOT  # place daily files here
OUT_JSON = os.path.join(ROOT, "dashboard_payload.json")
Q4_TARGETS_FILE = os.path.join(ROOT, "Q4_Targets.csv")

# File roots (suffixes like (3).xlsx vary)
LOAN_ROOT = "Abaco - Loan Tape_Loan Data_Table"
PAY_SCH_ROOT = "Abaco - Loan Tape_Payment Schedule_Table"
HIST_PAY_ROOT = "Abaco - Loan Tape_Historic Real Payment_Table"

# Google Sheets
CREDS_PATH = os.getenv("GOOGLE_SHEETS_CREDS_PATH")
AUX_SHEET_ID = os.getenv("AUX_SHEET_ID")
DESEMBOLSOS_RANGE = os.getenv("DESEMBOLSOS_RANGE", "DESEMBOLSOS!A1:AV5000")
DATA_SHEET_NAME = os.getenv("DATA_SHEET_NAME", "Data")

# --- Helper Functions ---
def newest_by_root(root):
    """Find the newest file matching the given root pattern."""
    paths = glob.glob(os.path.join(DATA_DIR, f"{root}*"))
    if not paths: return None
    return max(paths, key=os.path.getmtime)

def to_month(d):
    """Convert date to first day of month."""
    return pd.to_datetime(d, errors="coerce").to_period("M").to_timestamp()

def safe_num(x):
    """Convert to float, return 0.0 on error."""
    try:
        return float(x)
    except:
        return 0.0

def within_tolerance(value: float, target: float, tol: float = 0.01) -> bool:
    """Check if value is within tolerance of target."""
    if pd.isna(value) or pd.isna(target) or target == 0:
        return False
    return abs(value - target) <= tol * target

def calculate_percentage_vs_target(current: float, target: float) -> float:
    """Calculate percentage achievement vs target (e.g., 7.61M / 7.80M = 97.5%)."""
    if pd.isna(target) or target == 0:
        return None
    return (current / target) * 100

# --- Load Q4 Targets ---
def load_q4_targets():
    """Load quarterly targets from CSV file."""
    if not os.path.exists(Q4_TARGETS_FILE):
        print(f"Warning: {Q4_TARGETS_FILE} not found, using empty targets")
        return pd.DataFrame()
    
    targets = pd.read_csv(Q4_TARGETS_FILE)
    targets["Month"] = pd.to_datetime(targets["Month"])
    return targets

# --- Load CSV/XLSX (latest) ---
loan_path = newest_by_root(LOAN_ROOT)
ps_path   = newest_by_root(PAY_SCH_ROOT)
hist_path = newest_by_root(HIST_PAY_ROOT)

if not all([loan_path, ps_path, hist_path]):
    raise SystemExit("Missing one or more input files. Ensure the three loan-tape files are in this folder.")

def read_any(path):
    """Read CSV or Excel file."""
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)

df_loans = read_any(loan_path)
df_ps    = read_any(ps_path)
df_hist  = read_any(hist_path)

# --- Normalize core columns (rename if needed) ---
# Expected columns (typical from your tapes):
# Loan Data: ["Loan ID","Customer ID","Disbursement Date","Disbursement Amount","Outstanding Loan Value","Interest Rate APR","Term","Term Unit","KAM"(optional)]
# Payment Schedule: ["Loan ID","Customer ID","Payment Date","Interest Payment","Fee Payment","DPD"(optional)]
# Historic Real Payment: ["Loan ID","Customer ID","True Payment Date","True Interest Payment","True Fee Payment","Payment Date"(scheduled date if present)]

for c in ["Disbursement Date"]:
    if c in df_loans.columns:
        df_loans[c] = pd.to_datetime(df_loans[c], errors="coerce")

for c in ["Payment Date"]:
    if c in df_ps.columns:
        df_ps[c] = pd.to_datetime(df_ps[c], errors="coerce")

for c in ["True Payment Date","Payment Date"]:
    if c in df_hist.columns:
        df_hist[c] = pd.to_datetime(df_hist[c], errors="coerce")

# --- Google Sheets: pull KAM + LineaCredito mappings ---
import gspread
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.readonly"]
creds = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
gc = gspread.authorize(creds)

# 1) From "DESEMBOLSOS" range: use columns to find Customer / KAM
ws = gc.open_by_key(AUX_SHEET_ID)
values = ws.values_get(DESEMBOLSOS_RANGE).get("values", [])
hdr = [h.strip() for h in values[0]] if values else []
rows = values[1:] if len(values)>1 else []

def idx(name):
    return hdr.index(name) if name in hdr else None

# try multiple candidate header names commonly used
cid_idx   = next((idx(n) for n in ["Customer ID","ClienteID","CustomerID","customer_id"] if idx(n) is not None), None)
name_idx  = next((idx(n) for n in ["Client Name","Nombre Cliente","client_name"] if idx(n) is not None), None)
kam_idx   = next((idx(n) for n in ["KAM","Ejecutivo","Account Manager"] if idx(n) is not None), None)

map_kam = {}
for r in rows:
    cid = r[cid_idx] if cid_idx is not None and len(r)>cid_idx else None
    kam = r[kam_idx] if kam_idx is not None and len(r)>kam_idx else None
    if cid and kam:
        map_kam[str(cid)] = kam

# 2) From sheet "Data": LineaCredito by Customer
try:
    ws_data = ws.worksheet(DATA_SHEET_NAME)
    data_vals = ws_data.get_all_records()
except:
    data_vals = []

map_linea = {}
for rec in data_vals:
    # Accept multiple key variants
    cid = rec.get("Customer ID") or rec.get("CustomerID") or rec.get("customer_id")
    lc  = rec.get("LineaCredito") or rec.get("Line of Credit") or rec.get("LineaCreditoUSD")
    if cid:
        map_linea[str(cid)] = lc

# Attach KAM/LineaCredito onto loans by Customer ID
df_loans["Customer ID"] = df_loans["Customer ID"].astype(str)
df_loans["KAM"] = df_loans["Customer ID"].map(map_kam)
df_loans["LineaCredito"] = df_loans["Customer ID"].map(map_linea)

# --- Load Q4 Targets ---
q4_targets = load_q4_targets()

# --- Executive KPIs ---
asof = pd.Timestamp.today().normalize()

# Outstanding portfolio (use latest EOM from Payment Schedule if it's a schedule table)
outstanding_total = safe_num(df_loans.get("Outstanding Loan Value", pd.Series(dtype=float))).sum()
if "Outstanding Loan Value" in df_ps.columns:  # sometimes PS has the current outstanding column
    outstanding_total = safe_num(df_ps["Outstanding Loan Value"]).sum() or outstanding_total

# Active clients (Outstanding > 0)
if "Outstanding Loan Value" in df_loans.columns:
    active_clients = df_loans.groupby("Customer ID")["Outstanding Loan Value"].sum()
    active_clients = int((active_clients > 0).sum())
else:
    active_clients = df_loans["Customer ID"].nunique()

# Weighted APR
if {"Interest Rate APR","Outstanding Loan Value"}.issubset(df_loans.columns):
    w_apr = (df_loans["Interest Rate APR"]*df_loans["Outstanding Loan Value"]).sum() / max(1.0, df_loans["Outstanding Loan Value"].sum())
else:
    w_apr = np.nan

# NPL ≥180 DPD (if you keep DPD in PS or can infer)
npl_180 = 0.0
if "DPD" in df_ps.columns and "Outstanding Loan Value" in df_ps.columns:
    npl_180 = df_ps.loc[df_ps["DPD"].fillna(0).astype(float) >= 180, "Outstanding Loan Value"].sum()

# Top-10 Concentration
if "Outstanding Loan Value" in df_loans.columns:
    by_cust = df_loans.groupby("Customer ID")["Outstanding Loan Value"].sum().sort_values(ascending=False)
    top10 = by_cust.head(10).sum()
    top10_share = float(top10 / max(1.0, by_cust.sum()) * 100)
else:
    top10_share = np.nan

# --- Target Comparisons with Dynamic Percentage ---
current_month = asof.replace(day=1)
current_targets = q4_targets[q4_targets["Month"] == current_month]

target_comparisons = {}
if not current_targets.empty:
    target_row = current_targets.iloc[0]
    
    # Outstanding vs Target
    if "Outstanding_Target" in target_row:
        outstanding_target = target_row["Outstanding_Target"]
        outstanding_pct = calculate_percentage_vs_target(outstanding_total, outstanding_target)
        target_comparisons["outstanding"] = {
            "current": round(outstanding_total, 2),
            "target": round(outstanding_target, 2),
            "percentage": round(outstanding_pct, 2) if outstanding_pct else None,
            "within_tolerance": within_tolerance(outstanding_total, outstanding_target)
        }
    
    # APR vs Target
    if "APR_Target" in target_row and not pd.isna(w_apr):
        apr_target = target_row["APR_Target"]
        apr_pct = w_apr * 100  # convert to percentage
        target_comparisons["apr"] = {
            "current": round(apr_pct, 2),
            "target": round(apr_target, 2),
            "percentage": round(calculate_percentage_vs_target(apr_pct, apr_target), 2) if not pd.isna(apr_target) else None,
            "within_tolerance": within_tolerance(apr_pct, apr_target, tol=0.01)
        }
    
    # NPL vs Target
    if "NPL_Target" in target_row:
        npl_target = target_row["NPL_Target"]
        npl_pct = (npl_180 / max(1.0, outstanding_total)) * 100
        target_comparisons["npl"] = {
            "current": round(npl_pct, 2),
            "target": round(npl_target, 2),
            "percentage": round(calculate_percentage_vs_target(npl_pct, npl_target), 2) if not pd.isna(npl_target) else None,
            "within_tolerance": within_tolerance(npl_pct, npl_target, tol=0.01)
        }

# Disbursements by month / client types
df_loans["Month"] = to_month(df_loans["Disbursement Date"])
disb_m = df_loans.groupby("Month")["Disbursement Amount"].sum().reset_index()

# New / Recurrent / Recovered
first_seen = df_loans.groupby("Customer ID")["Disbursement Date"].min()
span = df_loans.groupby("Customer ID").agg(first=("Disbursement Date","min"), last=("Disbursement Date","max"))
recurrent_ids = span.index[(span["last"] - span["first"]).dt.days > 90]

recovered_ids = []
for cid, g in df_loans.sort_values(["Customer ID", "Disbursement Date"]).groupby("Customer ID"):
    s = g["Disbursement Date"]  # already sorted within group
    if (s.diff().dt.days > 90).fillna(False).any():
        recovered_ids.append(cid)
recovered_ids = set(map(str, recovered_ids))

df_loans["is_new_2025"] = df_loans["Customer ID"].map(lambda c: first_seen.loc[c].year == 2025 if pd.notna(first_seen.loc[c]) else False)
new_m = df_loans[df_loans["is_new_2025"]].groupby("Month")["Customer ID"].nunique().reset_index(name="New Clients")
rec_m = df_loans[df_loans["Customer ID"].isin(recurrent_ids)].groupby("Month")["Customer ID"].nunique().reset_index(name="Recurrent Clients")
rev_m = df_loans[df_loans["Customer ID"].isin(recovered_ids)].groupby("Month")["Customer ID"].nunique().reset_index(name="Recovered Clients")
active_m = df_loans.groupby("Month")["Customer ID"].nunique().reset_index(name="Active Clients")

# Tenor buckets (by disbursement)
def tenor_bucket(row):
    t = row.get("Term")
    u = (row.get("Term Unit") or "").lower()
    if pd.isna(t): return "Unknown"
    days = float(t)
    if "day" in u:
        pass
    elif "month" in u:
        days = days*30
    elif "year" in u:
        days = days*365
    if days <= 30: return "≤30"
    if days <= 60: return "31–60"
    if days <= 90: return "61–90"
    return ">90"

if {"Term","Term Unit"}.issubset(df_loans.columns):
    df_loans["Tenor Bucket"] = df_loans.apply(tenor_bucket, axis=1)
    tenor_mix = (df_loans.groupby("Tenor Bucket")["Disbursement Amount"].sum() / max(1.0, df_loans["Disbursement Amount"].sum()) * 100).round(2).to_dict()
else:
    tenor_mix = {}

# Tenor Mix vs Targets with tolerance
tenor_target_comparisons = {}
if not current_targets.empty and tenor_mix:
    target_row = current_targets.iloc[0]
    tenor_mapping = {
        "≤30": "Tenor_30_Target",
        "31–60": "Tenor_60_Target",
        "61–90": "Tenor_90_Target",
        ">90": "Tenor_90plus_Target"
    }
    
    for bucket, target_col in tenor_mapping.items():
        if target_col in target_row and bucket in tenor_mix:
            current_val = tenor_mix[bucket]
            target_val = target_row[target_col]
            tenor_target_comparisons[bucket] = {
                "current": round(current_val, 2),
                "target": round(target_val, 2),
                "within_tolerance": within_tolerance(current_val, target_val, tol=0.01)
            }

# Revenue: Scheduled (PS) vs Received (Hist)
sched = df_ps.groupby(df_ps["Payment Date"].dt.to_period("M"))[["Interest Payment","Fee Payment"]].sum().rename(columns={"Interest Payment":"Sched Interest","Fee Payment":"Sched Fee"})
sched["Sched Revenue"] = sched.sum(axis=1)
sched.index = sched.index.to_timestamp()

# Attribute received to scheduled month if PS "Payment Date" exists in Historic
if "Payment Date" in df_hist.columns:
    recv_due = df_hist.groupby(df_hist["Payment Date"].dt.to_period("M"))[["True Interest Payment","True Fee Payment"]].sum()
else:
    # fallback: by calendar paid month
    recv_due = df_hist.groupby(df_hist["True Payment Date"].dt.to_period("M"))[["True Interest Payment","True Fee Payment"]].sum()
recv_due.columns = ["Recv Interest for Month","Recv Fee for Month"]
recv_due["Recv Revenue for Month"] = recv_due.sum(axis=1)
recv_due.index = recv_due.index.to_timestamp()

rev_tbl = pd.concat([sched, recv_due], axis=1).fillna(0)
rev_tbl["Collection Rate (for Due Month)"] = (rev_tbl["Recv Revenue for Month"] / rev_tbl["Sched Revenue"].replace(0, np.nan))*100

# KAM & Industry (if industry/sector column exists)
kam_pivot = df_loans.groupby("KAM")["Outstanding Loan Value"].sum().sort_values(ascending=False).reset_index()
sector_col = next((c for c in df_loans.columns if re.search(r"(industry|sector|categoria|rubro)", c, re.I)), None)
sector_pivot = (df_loans.groupby(sector_col)["Outstanding Loan Value"].sum().sort_values(ascending=False).reset_index()
                if sector_col else pd.DataFrame(columns=["Sector","Outstanding Loan Value"]))

# Capital plan from Q4 Targets (convert to capital plan format)
cap_plan = []
if not q4_targets.empty:
    for _, row in q4_targets.iterrows():
        if "Disbursement_Target" in row:
            cap_plan.append({
                "month": row["Month"].strftime("%Y-%m-%d"),
                "planned_disbursement": float(row["Disbursement_Target"])
            })

# --- Build JSON payload ---
payload = {
    "as_of": datetime.now().strftime("%Y-%m-%d"),
    "files_used": {
        "loan_data": os.path.basename(loan_path),
        "payment_schedule": os.path.basename(ps_path),
        "historic_real_payment": os.path.basename(hist_path)
    },
    "executive_kpis": {
        "outstanding_portfolio": round(outstanding_total, 2),
        "active_clients": active_clients,
        "weighted_apr": None if pd.isna(w_apr) else round(float(w_apr)*100, 2),
        "npl_180_amount": round(float(npl_180), 2),
        "top10_concentration_pct": None if pd.isna(top10_share) else round(float(top10_share), 2)
    },
    "target_comparisons": target_comparisons,
    "tenor_mix_pct": tenor_mix,
    "tenor_target_comparisons": tenor_target_comparisons,
    "monthly_series": {
        "disbursements": disb_m.rename(columns={"Month":"month","Disbursement Amount":"amount"}).to_dict(orient="records"),
        "active_clients": active_m.rename(columns={"Month":"month"}).to_dict(orient="records"),
        "new_clients": new_m.rename(columns={"Month":"month"}).to_dict(orient="records"),
        "recurrent_clients": rec_m.rename(columns={"Month":"month"}).to_dict(orient="records"),
        "recovered_clients": rev_m.rename(columns={"Month":"month"}).to_dict(orient="records"),
    },
    "revenue": {
        "by_month": (
            rev_tbl
            .reset_index()
            .rename(columns={"Payment Date": "month", "index": "month"})
            .to_dict(orient="records")
        )
    },
    "kam_breakdown": kam_pivot.rename(columns={"Outstanding Loan Value":"outstanding"}).to_dict(orient="records"),
    "sector_breakdown": [] if sector_pivot.empty else sector_pivot.rename(columns={sector_col:"sector","Outstanding Loan Value":"outstanding"}).to_dict(orient="records"),
    "mappings": {
        "kam_from_sheet": True,
        "linea_credito_from_sheet": True,
        "sheet_id": AUX_SHEET_ID,
        "desembolsos_range": DESEMBOLSOS_RANGE,
        "data_sheet": DATA_SHEET_NAME
    },
    "capital_plan_q4": cap_plan
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"OK → {OUT_JSON}")
print(f"\nKPI Summary:")
print(f"  Outstanding Portfolio: ${outstanding_total:,.2f}")
print(f"  Active Clients: {active_clients}")
if target_comparisons.get("outstanding"):
    tc = target_comparisons["outstanding"]
    print(f"  Outstanding vs Target: {tc['percentage']}% ({tc['current']:,.2f} / {tc['target']:,.2f})")
    print(f"  Within Tolerance: {tc['within_tolerance']}")
