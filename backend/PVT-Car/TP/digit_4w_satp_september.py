import pandas as pd
import io
import os
import base64
from typing import List, Optional

# ------------------- FORMULA DATA & LOGIC (same as your API) -------------------
FORMULA_DATA = [
    {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT" : "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
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

STATE_MAPPING = {
    "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
    "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
    "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
    "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
    "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
    "Himachal Pradesh": "HIMACHAL PRADESH", "Andaman": "ANDAMAN AND NICOBAR ISLANDS",
    "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
    "West Bengal": "WEST BENGAL", "North Bengal": "WEST BENGAL", "Orissa": "ODISHA",
    "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
    "ROM2": "REST OF MAHARASHTRA", "Good Vizag": "ANDHRA PRADESH", "Good TN": "TAMIL NADU",
    "Kerala": "KERALA", "Good MP": "MADHYA PRADESH", "Good CG": "CHHATTISGARH",
    "Good RJ": "RAJASTHAN", "Bad RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH",
    "Bad UP": "UTTAR PRADESH", "Good UK": "UTTARAKHAND", "Bad UK": "UTTARAKHAND",
    "Punjab": "PUNJAB", "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM",
    "NE EX ASSAM": "NORTH EAST", "Good NL": "NAGALAND", "GOOD KA": "KARNATAKA",
    "BAD KA": "KARNATAKA", "HR Ref": "HARYANA", "Dehradun, Haridwar": "UTTARAKHAND"
}

def safe_float(value):
    if pd.isna(value):
        return None
    val_str = str(value).strip().upper()
    if val_str in ["D", "NA", "", "NAN", "NONE"]:
        return None
    try:
        num = float(val_str.replace('%', '').strip())
        return num * 100 if 0 < num < 1 else num
    except:
        return None

def get_payin_category(payin: float):
    if payin <= 20: return "Payin Below 20%"
    elif payin <= 30: return "Payin 21% to 30%"
    elif payin <= 50: return "Payin 31% to 50%"
    else: return "Payin Above 50%"

def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
    segment_key = segment.upper()
    if lob == "TW":
        segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
    elif lob == "PVT CAR":
        segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
    elif lob in ["TAXI", "CV", "BUS", "MISD"]:
        segment_key = segment.upper()

    payin_cat = get_payin_category(payin)
    matching_rule = None
    for rule in FORMULA_DATA:
        if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
            if rule["REMARKS"] == payin_cat or rule["REMARKS"] == "NIL":
                matching_rule = rule
                break

    if not matching_rule and payin > 20:
        for rule in FORMULA_DATA:
            if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
                if (payin > 20 and rule["REMARKS"] == "Payin Above 20%") or \
                   (payin > 30 and rule["REMARKS"] == "Payin Above 30%") or \
                   (payin > 40 and rule["REMARKS"] == "Payin Above 40%") or \
                   (payin > 50 and rule["REMARKS"] == "Payin Above 50%"):
                    matching_rule = rule
                    break

    if not matching_rule:
        deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
        return f"-{deduction}%", round(payin - deduction, 2)

    formula = matching_rule["PO"]
    if "% of Payin" in formula:
        pct = float(formula.split("%")[0].replace("Less ", ""))
        return formula, round(payin * pct / 100, 2) if "Less" not in formula else round(payin - pct, 2)
    elif formula.startswith("-"):
        ded = float(formula.replace("%", "").replace("-", ""))
        return formula, round(payin - ded, 2)
    else:
        return formula, round(payin - 2, 2)

def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
    if payin == 0:
        return 0, "0% (No Payin)", "Payin is 0"
    formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
    return payout, formula, f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {get_payin_category(payin)}"

# ------------------- PROCESSORS (converted from API) -------------------
def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        for _, row in df.iterrows():
            cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not cluster: continue
            segmentation = str(row.iloc[1]).strip() if len(row) > 1 else ""
            comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
            satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None

            state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
            segment_desc = f"TW {segmentation}"

            lob = override_lob if override_enabled and override_lob else "TW"
            seg = override_segment if override_enabled and override_segment else "TW"

            if comp_cd2 is not None:
                pt = override_policy_type or "Comp"
                payout, formula, exp = calculate_payout_with_formula(lob, seg, pt, comp_cd2)
                records.append({"State": state.upper(), "Location/Cluster": cluster, "Original Segment": segment_desc,
                                "Mapped Segment": seg, "LOB": lob, "Policy Type": pt,
                                "Payin (CD2)": f"{comp_cd2:.2f}%", "Payin Category": get_payin_category(comp_cd2),
                                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": exp})

            if satp_cd2 is not None:
                payout, formula, exp = calculate_payout_with_formula(lob, seg, "TP", satp_cd2)
                records.append({"State": state.upper(), "Location/Cluster": cluster, "Original Segment": segment_desc,
                                "Mapped Segment": seg, "LOB": lob, "Policy Type": "TP",
                                "Payin (CD2)": f"{satp_cd2:.2f}%", "Payin Category": get_payin_category(satp_cd2),
                                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": exp})
        return records
    except Exception as e:
        print(f"Error in TW sheet: {e}")
        return []

def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        for _, row in df.iterrows():
            city_cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not city_cluster: continue
            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city_cluster.upper()), "UNKNOWN")
            cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
            cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None

            segment_desc = "Taxi Electric"
            lob = override_lob if override_enabled and override_lob else "TAXI"
            seg = override_segment if override_enabled and override_segment else "TAXI"

            if cvod_cd2 is not None:
                pt = override_policy_type or "Comp"
                payout, formula, exp = calculate_payout_with_formula(lob, seg, pt, cvod_cd2)
                records.append({"State": state.upper(), "Location/Cluster": city_cluster, "Original Segment": segment_desc,
                                "Mapped Segment": seg, "LOB": lob, "Policy Type": pt,
                                "Payin (CD2)": f"{cvod_cd2:.2f}%", "Payin Category": get_payin_category(cvod_cd2),
                                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": exp})

            if cvtp_cd2 is not None:
                payout, formula, exp = calculate_payout_with_formula(lob, seg, "TP", cvtp_cd2)
                records.append({"State": state.upper(), "Location/Cluster": city_cluster, "Original Segment": segment_desc,
                                "Mapped Segment": seg, "LOB": lob, "Policy Type": "TP",
                                "Payin (CD2)": f"{cvtp_cd2:.2f}%", "Payin Category": get_payin_category(cvtp_cd2),
                                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": exp})
        return records
    except Exception as e:
        print(f"Error in Electric sheet: {e}")
        return []

def process_regular_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        prev_location = ""
        for i in range(5, len(df)):
            row = df.iloc[i]
            location = str(row.iloc[0]).strip() or prev_location
            if location: prev_location = location
            if not location: continue

            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")
            lob = override_lob if override_enabled and override_lob else "TAXI"
            seg = override_segment if override_enabled and override_segment else "TAXI"

            combinations = [
                ("Without Add On Cover <=1000 CC", "SAOD", 10), ("Without Add On Cover >1000 CC", "SAOD", 12),
                ("With Add On Cover <=1000 CC", "SAOD", 14), ("With Add On Cover >1000 CC", "SAOD", 16),
                ("<=1000 CC TP", "TP", 13), (">1000 CC TP", "TP", 14)
            ]

            for desc, ptype, cd2_idx in combinations:
                if cd2_idx >= len(row): continue
                payin = safe_float(row.iloc[cd2_idx])
                if payin is None: continue
                pt = override_policy_type or ("TP" if ptype == "TP" else "Comp")
                payout, formula, exp = calculate_payout_with_formula(lob, seg, pt, payin)
                records.append({"State": state.upper(), "Location/Cluster": location, "Original Segment": f"Taxi {desc}",
                                "Mapped Segment": seg, "LOB": lob, "Policy Type": pt,
                                "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
                                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": exp})
        return records
    except Exception as e:
        print(f"Error in Regular sheet: {e}")
        return []

# def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
#         df = df.astype(str).applymap(lambda x: x.strip() if isinstance(x, str) else "")

#         header_row_idx = None
#         cluster_col = segment_col = age_col = cd2_col = None

#         for i in range(min(100, len(df))):
#             row_text = " ".join(df.iloc[i].astype(str).str.upper().values)
#             if "CLUSTER" in row_text and "CD2" in row_text:
#                 header_row_idx = i
#                 for j, cell in enumerate(df.iloc[i]):
#                     cell_up = str(cell).upper()
#                     if "CLUSTER" in cell_up:
#                         cluster_col = j
#                     elif any(k in cell_up for k in ["SEGMENT", "MAPPING"]):
#                         segment_col = j
#                     elif any(k in cell_up for k in ["AGE", "BAND"]):
#                         age_col = j
#                     elif "CD2" in cell_up:
#                         cd2_col = j
#                 break

#         if header_row_idx is None or cd2_col is None:
#             print(f"Could not find header row with 'Cluster' and 'CD2' in sheet '{sheet_name}'")
#             return []

#         print(f"Found SATP header at row {header_row_idx+1}")

#         lob = override_lob if override_enabled and override_lob else "PVT CAR"
#         seg = override_segment if override_enabled and override_segment else "PVT CAR TP"
#         pt = override_policy_type or "TP"

#         for i in range(header_row_idx + 1, len(df)):
#             cluster = str(df.iloc[i, cluster_col]).strip()
#             if not cluster or cluster.lower() in ["total", "grand total", ""]:
#                 continue

#             segment_val = str(df.iloc[i, segment_col]).strip() if segment_col is not None else ""
#             age_val = str(df.iloc[i, age_col]).strip() if age_col is not None else "All"

#             original_seg = f"PVT CAR TP {segment_val} Age Band: {age_val}".strip()

#             raw_cd2 = df.iloc[i, cd2_col]
#             payin = safe_float(raw_cd2)
#             if payin is None:
#                 continue

#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

#             payout, formula, exp = calculate_payout_with_formula(lob, seg, pt, payin)

#             records.append({
#                 "State": state.upper(),
#                 "Location/Cluster": cluster,
#                 "Original Segment": original_seg,
#                 "Mapped Segment": seg,
#                 "LOB": lob,
#                 "Policy Type": pt,
#                 "Payin (CD2)": f"{payin:.2f}%",
#                 "Payin Category": get_payin_category(payin),
#                 "Calculated Payout": f"{payout:.2f}%",
#                 "Formula Used": formula,
#                 "Rule Explanation": exp
#             })

#         print(f"Extracted {len(records)} records from '{sheet_name}'")
#         return records

#     except Exception as e:
#         print(f"Error in SATP sheet: {e}")
#         import traceback
#         traceback.print_exc()
#         return []

def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        # Read as raw cells - no header assumption
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        df = df.astype(str).applymap(lambda x: x.strip() if isinstance(x, str) else "")

        # Dynamic header detection
        header_row_idx = None
        cluster_col = segment_col = age_col = cd2_col = None

        for i in range(min(100, len(df))):  # Search first 100 rows
            row_upper = df.iloc[i].astype(str).str.upper()
            row_text = " ".join(row_upper.values)

            if "CLUSTER" in row_text and "CD2" in row_text:
                header_row_idx = i
                for j, cell in enumerate(df.iloc[i]):
                    cell_up = str(cell).upper()
                    if "CLUSTER" in cell_up:
                        cluster_col = j
                    elif any(k in cell_up for k in ["SEGMENT", "MAPPING"]):
                        segment_col = j
                    elif any(k in cell_up for k in ["AGE", "BAND"]):
                        age_col = j
                    elif "CD2" in cell_up:
                        cd2_col = j
                print(f"SATP Sheet '{sheet_name}': Header found at row {i+1} (Cluster col={cluster_col+1 if cluster_col is not None else 'N/A'}, CD2 col={cd2_col+1 if cd2_col is not None else 'N/A'})")
                break

        if header_row_idx is None or cluster_col is None or cd2_col is None:
            print(f"ERROR: Could not detect SATP header row (needs 'Cluster' and 'CD2') in sheet '{sheet_name}'")
            return []

        # Data starts after header
        data_start_row = header_row_idx + 1

        # Apply overrides or defaults
        lob = override_lob if override_enabled and override_lob else "PVT CAR"
        seg = override_segment if override_enabled and override_segment else "PVT CAR TP"
        pt = override_policy_type or "TP"

        for i in range(data_start_row, len(df)):
            row = df.iloc[i]

            # Get Cluster
            cluster = str(row.iloc[cluster_col]).strip() if cluster_col < len(row) else ""
            if not cluster or cluster.lower() in ["total", "grand total", "", "nan"]:
                continue

            # Get Segment and Age (optional)
            segment_val = str(row.iloc[segment_col]).strip() if segment_col is not None and segment_col < len(row) else ""
            age_val = str(row.iloc[age_col]).strip() if age_col is not None and age_col < len(row) else "All"

            original_segment = f"PVT CAR TP {segment_val} Age Band: {age_val}".strip()
            if not segment_val:
                original_segment = "PVT CAR TP"

            # Get CD2 value (raw)
            cd2_raw = row.iloc[cd2_col] if cd2_col < len(row) else None
            payin = safe_float(cd2_raw)
            if payin is None:
                continue  # Skip if no valid payin

            # State mapping
            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

            # Calculate payout
            payout, formula, exp = calculate_payout_with_formula(lob, seg, pt, payin)

            records.append({
                "State": state.upper(),
                "Location/Cluster": cluster,
                "Original Segment": original_segment,
                "Mapped Segment": seg,
                "LOB": lob,
                "Policy Type": pt,
                "Payin (CD2)": f"{payin:.2f}%",
                "Payin Category": get_payin_category(payin),
                "Calculated Payout": f"{payout:.2f}%",
                "Formula Used": formula,
                "Rule Explanation": exp
            })

        print(f"Successfully extracted {len(records)} records from SATP sheet '{sheet_name}'")
        return records

    except Exception as e:
        print(f"ERROR processing SATP sheet '{sheet_name}': {e}")
        import traceback
        traceback.print_exc()
        return []
# ------------------- MAIN CMD LOGIC -------------------
def get_sheet_names(file_path: str) -> List[str]:
    xls = pd.ExcelFile(file_path)
    return xls.sheet_names

def choose_sheets(sheets: List[str]):
    print("\n" + "="*70)
    print("Available Worksheets:")
    print("="*70)
    for i, s in enumerate(sheets, 1):
        print(f"  {i}. {s}")
    print("  A. Process ALL sheets")
    print("="*70)

    while True:
        choice = input("\nEnter number(s) separated by comma (e.g. 1,3) or 'A' for all: ").strip().upper()
        if choice == 'A':
            return sheets
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip()]
            selected = [sheets[i] for i in indices if 0 <= i < len(sheets)]
            if selected:
                return selected
            print("Invalid selection.")
        except:
            print("Please enter valid numbers or 'A'.")

def main():
    print("Insurance Policy Payout Processor - CMD Version")
    print("="*70)

    file_path = input("\nEnter full path to Excel file: ").strip().strip('"')
    if not os.path.exists(file_path):
        print("File not found!")
        return

    company_name = input("Enter Company Name: ").strip() or "Unknown"

    sheets = get_sheet_names(file_path)
    selected_sheets = choose_sheets(sheets)

    override = input("\nEnable override? (y/n): ").strip().lower() == 'y'
    override_lob = input("Override LOB (e.g. PVT CAR, TW): ").strip().upper() or None if override else None
    override_seg = input("Override Segment: ").strip().upper() or None if override else None
    override_pt = input("Override Policy Type (Comp/TP/SAOD): ").strip().upper() or None if override else None

    with open(file_path, "rb") as f:
        content = f.read()

    all_records = []
    for sheet in selected_sheets:
        print(f"\nProcessing sheet: {sheet}")
        sheet_lower = sheet.lower()
        if "electric" in sheet_lower or "ev" in sheet_lower:
            records = process_electric_sheet(content, sheet, override, override_lob, override_seg, override_pt)
        elif "tw" in sheet_lower or "2w" in sheet_lower:
            records = process_tw_sheet(content, sheet, override, override_lob, override_seg, override_pt)
        elif "satp" in sheet_lower:
            records = process_4w_satp_sheet(content, sheet, override, override_lob, override_seg, override_pt)
        else:
            records = process_regular_sheet(content, sheet, override, override_lob, override_seg, override_pt)
        all_records.extend(records)
        print(f"→ {len(records)} records from '{sheet}'")

    if not all_records:
        print("No data extracted from selected sheets.")
        return

    df_out = pd.DataFrame(all_records)
    base = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base}_PROCESSED_{company_name.replace(' ', '_')}.xlsx"
    df_out.to_excel(output_file, index=False)

    payins = df_out["Payin (CD2)"].str.replace('%', '').astype(float)
    avg_payin = payins.mean()

    print("\n" + "="*70)
    print(f"SUCCESS! Processed {len(all_records)} records")
    print(f"Average Payin: {avg_payin:.2f}%")
    print(f"Unique Segments: {df_out['Mapped Segment'].nunique()}")
    print(f"Output saved: {output_file}")
    print("="*70)

    print("\nSample Results:")
    print(df_out.head(10)[["Location/Cluster", "Policy Type", "Payin (CD2)", "Calculated Payout", "Formula Used"]])

if __name__ == "__main__":
    main()