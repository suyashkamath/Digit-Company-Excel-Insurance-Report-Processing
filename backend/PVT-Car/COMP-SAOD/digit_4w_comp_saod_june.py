# import pandas as pd
# import io
# import os
# import re
# from typing import List, Dict

# # ------------------- FORMULA DATA -------------------
# FORMULA_DATA = [
#     {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 30%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 40%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
#     {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
#     {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
#     {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
# ]

# # ------------------- STATE MAPPING -------------------
# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
#     "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
#     "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
#     "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
#     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
#     "Good TN": "TAMIL NADU", "Kerala": "KERALA", "Good MP": "MADHYA PRADESH",
#     "Good RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH", "Punjab": "PUNJAB",
#     "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM", "HR Ref": "HARYANA"
# }

# def safe_float(value):
#     if pd.isna(value):
#         return None
#     s = str(value).strip().upper()
#     if s in ["D", "NA", "", "NAN", "NONE"]:
#         return None
#     try:
#         num = float(s.replace("%", ""))
#         return num * 100 if 0 < num < 1 else num
#     except:
#         return None

# def get_payin_category(payin: float):
#     if payin <= 20:  return "Payin Below 20%"
#     elif payin <= 30: return "Payin 21% to 30%"
#     elif payin <= 50: return "Payin 31% to 50%"
#     else:            return "Payin Above 50%"

# def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
#     segment_key = segment.upper()
#     if lob == "TW":
#         segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
#     elif lob == "PVT CAR":
#         segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
#     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
#         segment_key = segment.upper()

#     payin_cat = get_payin_category(payin)
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#             if rule["REMARKS"] == payin_cat or rule["REMARKS"] == "NIL":
#                 formula = rule["PO"]
#                 if "of Payin" in formula:
#                     pct = float(formula.split("%")[0].replace("Less ", ""))
#                     payout = round(payin * pct / 100, 2) if "Less" not in formula else round(payin - pct, 2)
#                 elif formula.startswith("-"):
#                     ded = float(formula.replace("%", "").replace("-", ""))
#                     payout = round(payin - ded, 2)
#                 else:
#                     payout = round(payin - 2, 2)
#                 return formula, payout
#     # Default fallback
#     ded = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#     return f"-{ded}%", round(payin - ded, 2)

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     if payin == 0:
#         return 0, "0% (No Payin)", "Payin is 0"
#     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
#     return payout, formula, f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {get_payin_category(payin)}"

# # ------------------- 4W COMP+SAOD PROCESSING -------------------
# def process_4w_comp_saod_sheet(content: bytes, sheet_name: str,
#                                override_enabled: bool = False,
#                                override_lob: str = None,
#                                override_segment: str = None,
#                                override_policy_type: str = None) -> List[Dict]:

#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
#         df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

#         # Find Cluster column
#         cluster_col = None
#         for j in range(df.shape[1]):
#             if df.iloc[:, j].astype(str).str.contains("Cluster", case=False, na=False).any():
#                 cluster_col = j
#                 break

#         if cluster_col is None:
#             print("ERROR: Could not find 'Cluster' column.")
#             return []

#         # Find CD2 columns (any column to the right with "CD2" anywhere in the column)
#         cd2_cols = []
#         for j in range(cluster_col + 1, df.shape[1]):
#             col_str = df.iloc[:, j].astype(str).str.cat(sep=' ')
#             if "CD2" in col_str.upper():
#                 cd2_cols.append(j)

#         if not cd2_cols:
#             print("WARNING: No CD2 columns detected.")
#             return []

#         # Build full header text for each CD2 column (from rows 0 to cluster_row)
#         headers = {}
#         cluster_header_row = None
#         for i in range(df.shape[0]):
#             if pd.notna(df.iloc[i, cluster_col]) and "cluster" in str(df.iloc[i, cluster_col]).lower():
#                 cluster_header_row = i
#                 break

#         header_rows_range = range(0, cluster_header_row + 3 if cluster_header_row else 10)

#         for j in cd2_cols:
#             header_parts = []
#             for i in header_rows_range:
#                 val = df.iloc[i, j]
#                 if pd.notna(val):
#                     s = str(val).strip()
#                     if "CD2" not in s.upper():  # Exclude the CD2 label itself
#                         header_parts.append(s)
#             headers[j] = " ".join(header_parts).strip()

#         # === ROBUST DATA START ROW DETECTION ===
#         if cluster_header_row is not None:
#             data_start_row = cluster_header_row + 1
#             # Skip any fully empty rows after header
#             while data_start_row < df.shape[0] and pd.isna(df.iloc[data_start_row, cluster_col]):
#                 data_start_row += 1
#         else:
#             data_start_row = 10  # safe fallback

#         print(f"Processing sheet '{sheet_name}': Cluster col={cluster_col}, CD2 cols={cd2_cols}, data starts at row {data_start_row + 1}")

#         # Process data rows
#         for i in range(data_start_row, df.shape[0]):
#             cluster_cell = df.iloc[i, cluster_col]
#             if pd.isna(cluster_cell):
#                 continue
#             cluster = str(cluster_cell).strip()
#             if not cluster or "total" in cluster.lower() or cluster.lower() in ["grand total", "average"]:
#                 continue

#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

#             for j in cd2_cols:
#                 payin = safe_float(df.iloc[i, j])
#                 if payin is None:
#                     continue

#                 header_text = headers.get(j, "").upper()

#                 # Policy Type
#                 if "SAOD" in header_text and "COMP" not in header_text:
#                     policy_type = "SAOD"
#                 elif "COMP" in header_text:
#                     policy_type = "COMP"
#                 else:
#                     policy_type = "COMP"  # default

#                 # Fuel
#                 fuel = "Petrol" if "PETROL" in header_text and "NON" not in header_text and "CNG" not in header_text else "Non-Petrol (incl. CNG)"

#                 # HEV vs Non-HEV
#                 segment = "Non-HEV" if "NON HEV" in header_text or "NON-HEV" in header_text else "HEV"

#                 # Renewal?
#                 renewal = " (Renewals)" if "RENEWAL" in header_text or "RENEW" in header_text else ""

#                 orig_seg = f"PVT CAR {segment} - {fuel}{renewal}".strip()

#                 lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#                 segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
#                 policy_final = override_policy_type if override_policy_type else policy_type

#                 payout, formula, exp = calculate_payout_with_formula(lob_final, segment_final, policy_final, payin)

#                 records.append({
#                     "State": state,
#                     "Location/Cluster": cluster,
#                     "Original Segment": orig_seg,
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": exp
#                 })

#         print(f"Successfully extracted {len(records)} records from '{sheet_name}'")
#         return records

#     except Exception as e:
#         print(f"ERROR processing sheet '{sheet_name}': {e}")
#         import traceback
#         traceback.print_exc()
#         return []
# # ------------------- SHEET SELECTION & MAIN -------------------
# def get_sheet_names(file_path: str) -> List[str]:
#     try:
#         xls = pd.ExcelFile(file_path)
#         return xls.sheet_names
#     except Exception as e:
#         print(f"Error reading file: {e}")
#         return []

# def choose_sheet(sheets: List[str]) -> str:
#     print("\n" + "="*60)
#     print("Available Worksheets:")
#     print("="*60)
#     for i, sheet in enumerate(sheets, 1):
#         print(f"{i}. {sheet}")
#     print("="*60)

#     while True:
#         choice = input(f"\nEnter sheet number (1-{len(sheets)}): ").strip()
#         try:
#             num = int(choice)
#             if 1 <= num <= len(sheets):
#                 return sheets[num - 1]
#         except:
#             pass
#         print("Invalid choice. Try again.")

# def main():
#     print("Insurance Policy Payout Calculator (4W COMP+SAOD)")
#     print("="*60)

#     file_path = input("\nEnter the full path to your Excel file: ").strip().strip('"\'')
#     if not os.path.exists(file_path):
#         print("File not found!")
#         return

#     sheets = get_sheet_names(file_path)
#     if not sheets:
#         print("No worksheets found or file is invalid.")
#         return

#     selected_sheet = choose_sheet(sheets)
#     print(f"\nProcessing sheet: '{selected_sheet}'")

#     # Optional overrides
#     print("\nDo you want to override LOB/Segment/Policy Type? (usually 'n')")
#     override_choice = input("Override? (y/n): ").strip().lower()
#     override_enabled = override_choice == 'y'

#     override_lob = override_segment = override_policy_type = None
#     if override_enabled:
#         override_lob = input("Enter LOB (e.g. PVT CAR, TW): ").strip().upper() or None
#         override_segment = input("Enter Segment (e.g. PVT CAR COMP + SAOD): ").strip().upper() or None
#         override_policy_type = input("Enter Policy Type (COMP/SAOD/TP): ").strip().upper() or None

#     # Read file once
#     with open(file_path, "rb") as f:
#         content = f.read()

#     records = process_4w_comp_saod_sheet(
#         content=content,
#         sheet_name=selected_sheet,
#         override_enabled=override_enabled,
#         override_lob=override_lob,
#         override_segment=override_segment,
#         override_policy_type=override_policy_type
#     )

#     if not records:
#         print("No data extracted. Check if the sheet has the expected format (Cluster + CD2 columns).")
#         return

#     df_out = pd.DataFrame(records)

#     # Export
#     base_name = os.path.splitext(os.path.basename(file_path))[0]
#     output_file = f"{base_name}_Processed_{selected_sheet.replace(' ', '_')}.xlsx"
#     df_out.to_excel(output_file, index=False)
#     print(f"\nSuccess! {len(records)} records processed.")
#     print(f"Exported to: {output_file}")

#     # Show sample
#     print("\nSample Results (first 10):")
#     print(df_out.head(10)[["Location/Cluster", "Original Segment", "Policy Type", "Payin (CD2)", "Calculated Payout", "Formula Used"]])

# if __name__ == "__main__":
#     main()


import pandas as pd
import io
import os
from typing import List, Dict

# ------------------- FORMULA DATA -------------------
FORMULA_DATA = [
    {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 30%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 40%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
    {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
]

# ------------------- STATE MAPPING -------------------
STATE_MAPPING = {
    "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
    "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
    "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
    "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
    "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
    "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
    "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
    "Good TN": "TAMIL NADU", "Kerala": "KERALA", "Good MP": "MADHYA PRADESH",
    "Good RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH", "Punjab": "PUNJAB",
    "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM", "HR Ref": "HARYANA"
}

def safe_float(value):
    if pd.isna(value):
        return None
    s = str(value).strip().upper()
    if s in ["D", "NA", "", "NAN", "NONE"]:
        return None
    try:
        num = float(s.replace("%", ""))
        return num * 100 if 0 < num < 1 else num
    except:
        return None

def get_payin_category(payin: float):
    if payin <= 20:  return "Payin Below 20%"
    elif payin <= 30: return "Payin 21% to 30%"
    elif payin <= 50: return "Payin 31% to 50%"
    else:            return "Payin Above 50%"

def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
    segment_key = segment.upper()
    if lob == "TW":
        segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
    elif lob == "PVT CAR":
        segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
    elif lob in ["TAXI", "CV", "BUS", "MISD"]:
        segment_key = segment.upper()

    payin_cat = get_payin_category(payin)
    for rule in FORMULA_DATA:
        if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
            if rule["REMARKS"] == payin_cat or rule["REMARKS"] == "NIL":
                formula = rule["PO"]
                if "of Payin" in formula:
                    pct = float(formula.split("%")[0].replace("Less ", ""))
                    payout = round(payin * pct / 100, 2) if "Less" not in formula else round(payin - pct, 2)
                elif formula.startswith("-"):
                    ded = float(formula.replace("%", "").replace("-", ""))
                    payout = round(payin - ded, 2)
                else:
                    payout = round(payin - 2, 2)
                return formula, payout
    ded = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
    return f"-{ded}%", round(payin - ded, 2)

def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
    if payin == 0:
        return 0, "0% (No Payin)", "Payin is 0"
    formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
    return payout, formula, f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {get_payin_category(payin)}"

# ------------------- 4W COMP+SAOD PROCESSING (UPDATED FOR NEW PATTERN) -------------------
def process_4w_comp_saod_sheet(content: bytes, sheet_name: str,
                               override_enabled: bool = False,
                               override_lob: str = None,
                               override_segment: str = None,
                               override_policy_type: str = None) -> List[Dict]:

    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Find Cluster column
        cluster_col = None
        for j in range(df.shape[1]):
            if df.iloc[:, j].astype(str).str.contains("Cluster", case=False, na=False).any():
                cluster_col = j
                break

        if cluster_col is None:
            print("ERROR: Could not find 'Cluster' column.")
            return []

        # Find CD2 columns (look for common indicators like Net, OD, CD2, etc.)
        cd2_cols = []
        for j in range(cluster_col + 1, df.shape[1]):
            col_text = " ".join([str(df.iloc[i, j]) for i in range(min(20, df.shape[0])) if pd.notna(df.iloc[i, j])])
            if any(keyword in col_text.upper() for keyword in ["CD2", "NET", "OD", "ADD ON", "SAOD", "COMP"]):
                cd2_cols.append(j)

        if not cd2_cols:
            print("WARNING: No data columns detected.")
            return []

        # Find row where "Cluster" header appears
        cluster_header_row = None
        for i in range(df.shape[0]):
            if pd.notna(df.iloc[i, cluster_col]) and "cluster" in str(df.iloc[i, cluster_col]).lower():
                cluster_header_row = i
                break

        # Build headers from rows above and below cluster row
        header_rows_range = range(0, (cluster_header_row or 10) + 5)

        headers = {}
        for j in cd2_cols:
            parts = []
            for i in header_rows_range:
                val = df.iloc[i, j]
                if pd.notna(val):
                    s = str(val).strip()
                    if s.upper() not in ["CD2", "NET"]:  # exclude generic labels
                        parts.append(s)
            headers[j] = " ".join(parts).strip()

        # Data starts right after cluster header row
        data_start_row = (cluster_header_row + 1) if cluster_header_row is not None else 10
        while data_start_row < df.shape[0] and pd.isna(df.iloc[data_start_row, cluster_col]):
            data_start_row += 1

        print(f"Processing '{sheet_name}': Cluster col={cluster_col+1}, Data columns={len(cd2_cols)}, Start row={data_start_row+1}")

        for i in range(data_start_row, df.shape[0]):
            cluster_cell = df.iloc[i, cluster_col]
            if pd.isna(cluster_cell):
                continue
            cluster = str(cluster_cell).strip()
            if not cluster or "total" in cluster.lower() or cluster.lower() in ["grand total", "average"]:
                continue

            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

            for j in cd2_cols:
                payin = safe_float(df.iloc[i, j])
                if payin is None:
                    continue

                header_text = headers.get(j, "").upper()
                header_clean = header_text.replace("OD+ADD ON", "OD + ADD ON").replace("OD+ ADDON", "OD + ADD ON")

                # === POLICY TYPE LOGIC (NEW PATTERN) ===
                if "OD + ADD ON" in header_clean:
                    policy_type = "SAOD"
                elif "NET" in header_clean and "OD + ADD ON" not in header_clean:
                    policy_type = "COMP"
                elif "SAOD" in header_clean:
                    policy_type = "SAOD"
                elif "COMP" in header_clean or "COMPREHENSIVE" in header_clean:
                    policy_type = "COMP"
                else:
                    policy_type = "COMP"

                # === FUEL (if mentioned) ===
                fuel = "Petrol" if "PETROL" in header_clean and "NON" not in header_clean else "Non-Petrol (incl. CNG)"

                # === HEV vs Non-HEV ===
                if "NON HEV" in header_clean or "NON-HEV" in header_clean:
                    segment = "Non-HEV"
                elif "HEV" in header_clean:
                    segment = "HEV"
                else:
                    segment = "Non-HEV"

                # === RENEWALS ===
                renewal = " (Renewals)" if any(x in header_clean for x in ["REN+ROLL", "RENEWAL", "RENEW", "ROLL"]) else ""

                orig_seg = f"PVT CAR {segment} - {fuel}{renewal}".strip()

                lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
                segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
                policy_final = override_policy_type if override_policy_type else policy_type

                payout, formula, exp = calculate_payout_with_formula(lob_final, segment_final, policy_final, payin)

                records.append({
                    "State": state,
                    "Location/Cluster": cluster,
                    "Original Segment": orig_seg,
                    "Mapped Segment": segment_final,
                    "LOB": lob_final,
                    "Policy Type": policy_final,
                    "Payin (CD2)": f"{payin:.2f}%",
                    "Payin Category": get_payin_category(payin),
                    "Calculated Payout": f"{payout:.2f}%",
                    "Formula Used": formula,
                    "Rule Explanation": exp
                })

        print(f"Successfully extracted {len(records)} records from '{sheet_name}'")
        return records

    except Exception as e:
        print(f"ERROR processing sheet '{sheet_name}': {e}")
        import traceback
        traceback.print_exc()
        return []

# ------------------- SHEET SELECTION & MAIN -------------------
def get_sheet_names(file_path: str) -> List[str]:
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def choose_sheet(sheets: List[str]) -> str:
    print("\n" + "="*60)
    print("Available Worksheets:")
    print("="*60)
    for i, sheet in enumerate(sheets, 1):
        print(f"{i}. {sheet}")
    print("="*60)

    while True:
        choice = input(f"\nEnter sheet number (1-{len(sheets)}): ").strip()
        try:
            num = int(choice)
            if 1 <= num <= len(sheets):
                return sheets[num - 1]
        except:
            pass
        print("Invalid choice. Try again.")

def main():
    print("Insurance Policy Payout Calculator - Updated for New Patterns (OD+Add on = SAOD, Net = COMP)")
    print("="*80)

    file_path = input("\nEnter the full path to your Excel file: ").strip().strip('"\'')
    if not os.path.exists(file_path):
        print("File not found! Please check the path.")
        return

    sheets = get_sheet_names(file_path)
    if not sheets:
        print("No worksheets found or invalid file.")
        return

    selected_sheet = choose_sheet(sheets)
    print(f"\nProcessing sheet: '{selected_sheet}'")

    print("\nDo you want to override LOB/Segment/Policy Type? (usually 'n')")
    override_choice = input("Override? (y/n): ").strip().lower()
    override_enabled = override_choice == 'y'

    override_lob = override_segment = override_policy_type = None
    if override_enabled:
        override_lob = input("Enter LOB (e.g. PVT CAR): ").strip().upper() or None
        override_segment = input("Enter Segment: ").strip().upper() or None
        override_policy_type = input("Enter Policy Type (COMP/SAOD): ").strip().upper() or None

    with open(file_path, "rb") as f:
        content = f.read()

    records = process_4w_comp_saod_sheet(
        content=content,
        sheet_name=selected_sheet,
        override_enabled=override_enabled,
        override_lob=override_lob,
        override_segment=override_segment,
        override_policy_type=override_policy_type
    )

    if not records:
        print("No data extracted. The sheet may not match the expected format.")
        return

    df_out = pd.DataFrame(records)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}_Processed_{selected_sheet.replace(' ', '_')}.xlsx"
    df_out.to_excel(output_file, index=False)

    print(f"\nSUCCESS! {len(records)} records processed.")
    print(f"Exported to: {output_file}")

    print("\nSample Results (first 10 rows):")
    print(df_out.head(10)[["Location/Cluster", "Original Segment", "Policy Type", "Payin (CD2)", "Calculated Payout"]])

if __name__ == "__main__":
    main()