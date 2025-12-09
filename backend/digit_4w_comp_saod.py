# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import io
# import base64
# from typing import Optional, List
# import os

# app = FastAPI(title="Insurance Policy Processor API")

# # Allow frontend (localhost:5500 or any)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------- FORMULA DATA -------------------
# FORMULA_DATA = [
#     {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
    
#     # TW SAOD + COMP rules
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # TW TP rules
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
#     # PVT CAR rules
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 30%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 40%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
#     # CV rules
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # BUS rules
#     {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
#     {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
    
#     # TAXI rules
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # MISD rules
#     {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
# ]

# # ------------------- PAYOUT LOGIC -------------------
# def get_payin_category(payin: float):
#     if payin <= 20:
#         return "Payin Below 20%"
#     elif payin <= 30:
#         return "Payin 21% to 30%"
#     elif payin <= 50:
#         return "Payin 31% to 50%"
#     else:
#         return "Payin Above 50%"

# def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
#     """
#     Look up formula from FORMULA_DATA based on LOB, segment, policy type and payin
#     Returns: (formula_string, payout_value)
#     """
#     # Determine the segment key to look up
#     segment_key = segment.upper()
    
#     # For TW, map policy type to segment
#     if lob == "TW":
#         if policy_type == "TP":
#             segment_key = "TW TP"
#         else:  # Comp/SAOD
#             segment_key = "TW SAOD + COMP"
    
#     # For PVT CAR
#     elif lob == "PVT CAR":
#         if policy_type == "TP":
#             segment_key = "PVT CAR TP"
#         else:
#             segment_key = "PVT CAR COMP + SAOD"
    
#     # For TAXI, CV - use the segment as is
#     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
#         segment_key = segment.upper()
    
#     # Get payin category
#     payin_category = get_payin_category(payin)
    
#     # Find matching rule - try exact match first, then fallback to broader categories
#     matching_rule = None
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#             # Exact match
#             if rule["REMARKS"] == payin_category:
#                 matching_rule = rule
#                 break
#             # For rules without payin conditions (NIL)
#             elif rule["REMARKS"] == "NIL":
#                 matching_rule = rule
    
#     # If no exact match found, try broader categories
#     if not matching_rule and payin > 20:
#         for rule in FORMULA_DATA:
#             if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#                 # Check for "Payin Above 20%" which covers 21% and above
#                 if rule["REMARKS"] == "Payin Above 20%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 30%" 
#                 elif payin > 30 and rule["REMARKS"] == "Payin Above 30%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 40%"
#                 elif payin > 40 and rule["REMARKS"] == "Payin Above 40%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 50%"
#                 elif payin > 50 and rule["REMARKS"] == "Payin Above 50%":
#                     matching_rule = rule
#                     break
    
#     if not matching_rule:
#         # Fallback to old logic
#         print(f"No matching rule found for LOB={lob}, Segment={segment_key}, Payin={payin}")
#         deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#         return f"-{deduction}%", round(payin - deduction, 2)
    
#     # Parse the formula
#     formula = matching_rule["PO"]
    
#     if "%" in formula and "of Payin" in formula:
#         # Format: "90% of Payin" or "88% of Payin"
#         percentage = float(formula.split("%")[0])
#         payout = round(payin * percentage / 100, 2)
#         return formula, payout
#     elif formula.startswith("-") and "%" in formula:
#         # Format: "-2%", "-3%", etc.
#         deduction = float(formula.replace("%", "").replace("-", ""))
#         payout = round(payin - deduction, 2)
#         return formula, payout
#     elif formula.startswith("Less") and "%" in formula:
#         # Format: "Less 2% of Payin"
#         deduction = float(formula.split()[1].replace("%", ""))
#         payout = round(payin - deduction, 2)
#         return formula, payout
#     else:
#         # Unknown format, use fallback
#         deduction = 2
#         return f"-{deduction}%", round(payin - deduction, 2)

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     """
#     Calculate payout using formula data
#     Returns: (payout, formula_used, rule_explanation)
#     """
#     # If payin is 0, payout is also 0
#     if payin == 0:
#         return 0, "0% (No Payin)", f"Payin is 0, so Payout is 0"
    
#     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
#     payin_cat = get_payin_category(payin)
    
#     rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
#     return payout, formula, rule_explanation

# # ------------------- STATE MAPPING -------------------
# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
#     "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
#     "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
#     "Himachal Pradesh": "HIMACHAL PRADESH", "Andaman": "ANDAMAN AND NICOBAR ISLANDS",
#     "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
#     "West Bengal": "WEST BENGAL", "North Bengal": "WEST BENGAL", "Orissa": "ODISHA",
#     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
#     "ROM2": "REST OF MAHARASHTRA", "Good Vizag": "ANDHRA PRADESH", "Good TN": "TAMIL NADU",
#     "Kerala": "KERALA", "Good MP": "MADHYA PRADESH", "Good CG": "CHHATTISGARH",
#     "Good RJ": "RAJASTHAN", "Bad RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH",
#     "Bad UP": "UTTAR PRADESH", "Good UK": "UTTARAKHAND", "Bad UK": "UTTARAKHAND",
#     "Punjab": "PUNJAB", "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM",
#     "NE EX ASSAM": "NORTH EAST", "Good NL": "NAGALAND", "GOOD KA": "KARNATAKA",
#     "BAD KA": "KARNATAKA", "HR Ref": "HARYANA", "Dehradun, Haridwar": "UTTARAKHAND"
# }

# def safe_float(value):
#     """Safely convert value to float, handling 'D', 'NA', empty strings, etc."""
#     if pd.isna(value):
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ["D", "NA", "", "NAN", "NONE"]:
#         return None
#     try:
#         num = float(val_str.replace('%', '').strip())
#         if 0 < num < 1:
#             num = num * 100
#         return num
#     except:
#         return None

# # ------------------- LIST WORKSHEETS -------------------
# @app.post("/list-worksheets")
# async def list_worksheets(policy_file: UploadFile = File(...)):
#     try:
#         content = await policy_file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         worksheets = xls.sheet_names
#         return {"worksheets": worksheets}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # ------------------- TWO WHEELER SHEET PROCESSOR -------------------
# def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         print(f"TW sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
#             segmentation = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            
#             comp_cd1 = safe_float(row.iloc[2]) if len(row) > 2 else None
#             comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
#             satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None
            
#             state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
#             segment_desc = f"TW {segmentation}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TW"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TW"
            
#             # Process Comp
#             if comp_cd2 is not None:
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, comp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{comp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(comp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
            
#             # Process TP
#             if satp_cd2 is not None:
#                 policy_type_final = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, satp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{satp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(satp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing TW sheet: {str(e)}")
#         return []

# # ------------------- ELECTRIC SHEET PROCESSOR -------------------
# def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         print(f"Electric sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             city_cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
#             rto_remarks = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#             fuel = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Electric"
#             make = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else "All"
#             seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "5"
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city_cluster.upper()), "UNKNOWN")
            
#             cvod_cd1 = safe_float(row.iloc[5]) if len(row) > 5 else None
#             cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
#             cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
#             segment_desc = f"Taxi {fuel} {make}"
#             if rto_remarks:
#                 segment_desc += f" {rto_remarks}"
#             segment_desc += f" Seating:{seating}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
#             # Process CVOD (Comp)
#             if cvod_cd2 is not None:
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, cvod_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvod_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvod_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
            
#             # Process CVTP (TP)
#             if cvtp_cd2 is not None:
#                 policy_type_final = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, cvtp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvtp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvtp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing electric sheet: {str(e)}")
#         return []

# # ------------------- REGULAR SHEET PROCESSOR -------------------
# def process_regular_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         prev_location = ""
        
#         for idx, row in df.iterrows():
#             if idx < 5:
#                 continue
            
#             location = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() else prev_location
#             if location:
#                 prev_location = location
            
#             fuel = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#             make = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
#             remarks = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
#             seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            
#             cols = row.values
            
#             combinations = [
#                 ("Without Add On Cover", "<=1000 CC", "SAOD", 5, 6),
#                 ("Without Add On Cover", ">1000 CC",  "SAOD", 7, 8),
#                 ("With Add On Cover",    "<=1000 CC", "SAOD", 9, 10),
#                 ("With Add On Cover",    ">1000 CC",  "SAOD", 11, 12),
#                 ("", "<=1000 CC", "TP", None, 13),
#                 ("", ">1000 CC",  "TP", None, 14),
#             ]
            
#             for addon, cc, ptype, cd1_idx, cd2_idx in combinations:
#                 if len(cols) <= cd2_idx:
#                     continue
                
#                 cd2_val = cols[cd2_idx] if cd2_idx < len(cols) else None
#                 payin = safe_float(cd2_val)
                
#                 if payin is None:
#                     continue
                
#                 segment_desc = f"Taxi {fuel} {make} {remarks}".strip()
#                 if seating:
#                     segment_desc += f" Seating:{seating}"
#                 if cc and ptype == "SAOD":
#                     segment_desc += f" {cc}"
#                 if addon:
#                     segment_desc += f" {addon}"
                
#                 state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")
                
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
#                 policy_type_final = override_policy_type if override_policy_type else ("TP" if ptype == "TP" else "Comp")
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, payin
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": location,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing regular sheet: {str(e)}")
#         return []

# # ------------------- 4W SATP SHEET PROCESSOR -------------------
# def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=0)
#         df.columns = df.columns.str.strip()
        
#         print(f"4W SATP sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row['Cluster']) or str(row['Cluster']).strip() == "":
#                 continue
            
#             cluster = str(row['Cluster']).strip()
#             new_segment_mapping = str(row['New Segment Mapping']).strip()
#             new_age_band = str(row['New Age Band']).strip()
            
#             cd2_val = row['CD2'] if 'CD2' in df.columns else None
#             payin = safe_float(cd2_val)
            
#             if payin is None:
#                 continue
            
#             # State mapping using fuzzy match
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
            
#             # Original segment description includes age band in remarks
#             segment_desc = f"PVT CAR TP {new_segment_mapping} Age Band: {new_age_band}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR TP"
#             policy_type_final = override_policy_type if override_policy_type else "TP"
            
#             payout, formula, rule_exp = calculate_payout_with_formula(
#                 lob_final, segment_final, policy_type_final, payin
#             )
            
#             records.append({
#                 "State": state.upper(),
#                 "Location/Cluster": cluster,
#                 "Original Segment": segment_desc.strip(),
#                 "Mapped Segment": segment_final,
#                 "LOB": lob_final,
#                 "Policy Type": policy_type_final,
#                 "Payin (CD2)": f"{payin:.2f}%",
#                 "Payin Category": get_payin_category(payin),
#                 "Calculated Payout": f"{payout:.2f}%",
#                 "Formula Used": formula,
#                 "Rule Explanation": rule_exp
#             })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing 4W SATP sheet: {str(e)}")
#         return []

# def process_4w_comp_saod_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     """
#     Process 4W COMP+SAOD sheet with dynamic table positioning.
#     Handles tables that can start from any (x,y) position.
#     """
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         print(f"Processing 4W COMP+SAOD sheet: {sheet_name}")
#         print(f"Sheet shape: {df.shape}")
        
#         # Step 1: Find the table start position by looking for "Cluster" header
#         table_start_row = None
#         table_start_col = None
        
#         for i in range(min(20, len(df))):  # Search first 20 rows
#             for j in range(min(10, len(df.columns))):  # Search first 10 columns
#                 cell_value = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "cluster" in cell_value:
#                     table_start_row = i
#                     table_start_col = j
#                     print(f"Found 'Cluster' at row {i}, col {j}")
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             print("Could not find 'Cluster' header in sheet")
#             return []
        
#         # Step 2: Parse the header structure
#         # Row 1 (relative): Policy Type indicators (SAOD/COMP with fuel type)
#         # Row 2 (relative): Segment (Non HEV, HEV, etc.)
#         # Row 3 (relative): Rate type (CD2_OD+Addon, etc.)
        
#         header_row1 = table_start_row  # Cluster row
#         header_row2 = table_start_row + 1  # Segment row (Non HEV)
#         header_row3 = table_start_row + 2  # Rate type row (CD2_OD+Addon)
#         data_start_row = table_start_row + 3  # Where actual data starts
        
#         # Step 3: Map column indices to their attributes
#         column_mappings = []
        
#         # Start from column after "Cluster"
#         for col_idx in range(table_start_col + 1, len(df.columns)):
#             # Get header values
#             policy_fuel = str(df.iloc[header_row1, col_idx]).strip() if pd.notna(df.iloc[header_row1, col_idx]) else ""
#             segment = str(df.iloc[header_row2, col_idx]).strip() if pd.notna(df.iloc[header_row2, col_idx]) else ""
#             rate_type = str(df.iloc[header_row3, col_idx]).strip() if pd.notna(df.iloc[header_row3, col_idx]) else ""
            
#             # Skip if all headers are empty
#             if not policy_fuel and not segment and not rate_type:
#                 continue
            
#             # Parse policy type and fuel/remarks from header
#             policy_type = None
#             remarks = ""
            
#             if "SAOD" in policy_fuel.upper():
#                 policy_type = "SAOD"
#                 if "Petrol" in policy_fuel and "Non-Petrol" not in policy_fuel:
#                     remarks = "Petrol"
#                 elif "Non-Petrol" in policy_fuel or "CNG" in policy_fuel:
#                     remarks = "Non-Petrol (incl. CNG)"
#             elif "COMP" in policy_fuel.upper():
#                 policy_type = "COMP"
#                 if "Petrol" in policy_fuel and "Non-Petrol" not in policy_fuel:
#                     remarks = "Petrol"
#                 elif "Non-Petrol" in policy_fuel or "CNG" in policy_fuel:
#                     remarks = "Non-Petrol (incl. CNG)"
            
#             # Clean segment
#             segment_clean = segment.replace("Non HEV", "Non-HEV").replace("HEV", "HEV").strip()
            
#             # Only process CD2 columns
#             if "CD2" in rate_type.upper():
#                 column_mappings.append({
#                     "col_idx": col_idx,
#                     "policy_type": policy_type,
#                     "segment": segment_clean,
#                     "remarks": remarks,
#                     "rate_type": rate_type
#                 })
                
#                 print(f"Column {col_idx}: Policy={policy_type}, Segment={segment_clean}, Remarks={remarks}")
        
#         # Step 4: Process data rows
#         for row_idx in range(data_start_row, len(df)):
#             cluster = str(df.iloc[row_idx, table_start_col]).strip() if pd.notna(df.iloc[row_idx, table_start_col]) else ""
            
#             # Skip empty rows
#             if not cluster or cluster == "" or cluster.lower() == "nan":
#                 continue
            
#             # Map cluster to state
#             state = "UNKNOWN"
#             for key, value in STATE_MAPPING.items():
#                 if key.upper() in cluster.upper():
#                     state = value
#                     break
            
#             # Process each column mapping
#             for col_map in column_mappings:
#                 col_idx = col_map["col_idx"]
                
#                 # Get the payin value
#                 payin_value = df.iloc[row_idx, col_idx] if col_idx < len(df.columns) else None
#                 payin = safe_float(payin_value)
                
#                 # Skip if no valid payin or if it's 'D' (declined)
#                 if payin is None:
#                     continue
                
#                 # Build segment description
#                 segment_desc = f"PVT CAR {col_map['segment']}"
#                 if col_map['remarks']:
#                     segment_desc += f" - {col_map['remarks']}"
                
#                 # Determine final LOB, segment, and policy type
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
                
#                 # For segment mapping, use the base segment (Non-HEV, HEV, etc.)
#                 if override_enabled == "true" and override_segment:
#                     segment_final = override_segment
#                 else:
#                     # Map to standard segments
#                     if col_map['policy_type'] == "COMP":
#                         segment_final = "PVT CAR COMP + SAOD"
#                     else:
#                         segment_final = "PVT CAR COMP + SAOD"
                
#                 # Policy type
#                 if override_enabled == "true" and override_policy_type:
#                     policy_type_final = override_policy_type
#                 else:
#                     # Map SAOD to Comp for formula lookup
#                     policy_type_final = "Comp" if col_map['policy_type'] in ["SAOD", "COMP"] else col_map['policy_type']
                
#                 # Calculate payout
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, 
#                     segment_final, 
#                     policy_type_final, 
#                     payin
#                 )
                
#                 # Create record
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         print(f"Processed {len(records)} records from 4W COMP+SAOD sheet")
#         return records
        
#     except Exception as e:
#         print(f"Error processing 4W COMP+SAOD sheet: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return []


# # Update the main process function to use this new processor
# def process_file_updated(
#     company_name: str,
#     policy_file_content: bytes,
#     sheet_name: Optional[str] = None,
#     override_enabled: str = "false",
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
#     override_policy_type: Optional[str] = None,
# ):
#     """
#     Updated process function with 4W COMP+SAOD support
#     """
#     try:
#         xls = pd.ExcelFile(io.BytesIO(policy_file_content))
        
#         if sheet_name and sheet_name in xls.sheet_names:
#             sheets_to_process = [sheet_name]
#         else:
#             sheets_to_process = xls.sheet_names
        
#         all_records = []
        
#         for sheet in sheets_to_process:
#             print(f"\n{'='*60}")
#             print(f"Processing sheet: {sheet}")
#             print(f"{'='*60}")
            
#             sheet_lower = sheet.lower()
            
#             # Determine sheet type and process accordingly
#             if "comp" in sheet_lower and "saod" in sheet_lower and "4w" in sheet_lower:
#                 # 4W COMP+SAOD sheet
#                 records = process_4w_comp_saod_sheet(
#                     policy_file_content, sheet, override_enabled, 
#                     override_lob, override_segment, override_policy_type
#                 )
#             elif "electric" in sheet_lower or "ev" in sheet_lower:
#                 records = process_electric_sheet(
#                     policy_file_content, sheet, override_enabled, 
#                     override_lob, override_segment, override_policy_type
#                 )
#             elif "tw" in sheet_lower or "2w" in sheet_lower or "two wheeler" in sheet_lower:
#                 records = process_tw_sheet(
#                     policy_file_content, sheet, override_enabled,
#                     override_lob, override_segment, override_policy_type
#                 )
#             elif "satp" in sheet_lower:
#                 records = process_4w_satp_sheet(
#                     policy_file_content, sheet, override_enabled,
#                     override_lob, override_segment, override_policy_type
#                 )
#             else:
#                 records = process_regular_sheet(
#                     policy_file_content, sheet, override_enabled,
#                     override_lob, override_segment, override_policy_type
#                 )
            
#             all_records.extend(records)
#             print(f"Sheet '{sheet}' produced {len(records)} records")
        
#         return all_records
        
#     except Exception as e:
#         print(f"Error in process_file_updated: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         raise


# # FastAPI endpoint update
# @app.post("/process")
# async def process_file(
#     company_name: str = Form(...),
#     policy_file: UploadFile = File(...),
#     sheet_name: Optional[str] = Form(None),
#     override_enabled: str = Form("false"),
#     override_lob: Optional[str] = Form(None),
#     override_segment: Optional[str] = Form(None),
#     override_policy_type: Optional[str] = Form(None),
# ):
#     try:
#         content = await policy_file.read()
        
#         # Use updated processor
#         all_records = process_file_updated(
#             company_name=company_name,
#             policy_file_content=content,
#             sheet_name=sheet_name,
#             override_enabled=override_enabled,
#             override_lob=override_lob,
#             override_segment=override_segment,
#             override_policy_type=override_policy_type
#         )
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found in any sheet")
        
#         result_df = pd.DataFrame(all_records)
        
#         # Calculate metrics
#         payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records]
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        
#         formula_summary = {}
#         for r in all_records:
#             f = r["Formula Used"]
#             formula_summary[f] = formula_summary.get(f, 0) + 1
        
#         # Generate Excel
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         # Generate CSV
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
#         # Generate JSON
#         json_str = result_df.to_json(orient="records")
        
#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "avg_payin": f"{avg_payin:.2f}",
#                 "unique_segments": len(result_df["Mapped Segment"].unique()),
#                 "formula_summary": formula_summary,
#                 "sheets_processed": len(all_records) // max(1, len(all_records))
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64,
#             "json_data": json_str
#         }
    
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))
# # ------------------- MAIN PROCESS ENDPOINT -------------------

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import io
# import base64
# from typing import Optional, List
# import os

# app = FastAPI(title="Insurance Policy Processor API")

# # Allow frontend (localhost:5500 or any)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------- FORMULA DATA -------------------
# FORMULA_DATA = [
#     {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
    
#     # TW SAOD + COMP rules
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # TW TP rules
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
#     # PVT CAR rules
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 30%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 40%"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
#     # CV rules
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # BUS rules
#     {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
#     {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
    
#     # TAXI rules
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
#     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
#     # MISD rules
#     {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
# ]

# # ------------------- PAYOUT LOGIC -------------------
# def get_payin_category(payin: float):
#     if payin <= 20:
#         return "Payin Below 20%"
#     elif payin <= 30:
#         return "Payin 21% to 30%"
#     elif payin <= 50:
#         return "Payin 31% to 50%"
#     else:
#         return "Payin Above 50%"

# def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
#     """
#     Look up formula from FORMULA_DATA based on LOB, segment, policy type and payin
#     Returns: (formula_string, payout_value)
#     """
#     # Determine the segment key to look up
#     segment_key = segment.upper()
    
#     # For TW, map policy type to segment
#     if lob == "TW":
#         if policy_type == "TP":
#             segment_key = "TW TP"
#         else:  # Comp/SAOD
#             segment_key = "TW SAOD + COMP"
    
#     # For PVT CAR
#     elif lob == "PVT CAR":
#         if policy_type == "TP":
#             segment_key = "PVT CAR TP"
#         else:
#             segment_key = "PVT CAR COMP + SAOD"
    
#     # For TAXI, CV - use the segment as is
#     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
#         segment_key = segment.upper()
    
#     # Get payin category
#     payin_category = get_payin_category(payin)
    
#     # Find matching rule - try exact match first, then fallback to broader categories
#     matching_rule = None
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#             # Exact match
#             if rule["REMARKS"] == payin_category:
#                 matching_rule = rule
#                 break
#             # For rules without payin conditions (NIL)
#             elif rule["REMARKS"] == "NIL":
#                 matching_rule = rule
    
#     # If no exact match found, try broader categories
#     if not matching_rule and payin > 20:
#         for rule in FORMULA_DATA:
#             if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#                 # Check for "Payin Above 20%" which covers 21% and above
#                 if rule["REMARKS"] == "Payin Above 20%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 30%" 
#                 elif payin > 30 and rule["REMARKS"] == "Payin Above 30%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 40%"
#                 elif payin > 40 and rule["REMARKS"] == "Payin Above 40%":
#                     matching_rule = rule
#                     break
#                 # Check for "Payin Above 50%"
#                 elif payin > 50 and rule["REMARKS"] == "Payin Above 50%":
#                     matching_rule = rule
#                     break
    
#     if not matching_rule:
#         # Fallback to old logic
#         print(f"No matching rule found for LOB={lob}, Segment={segment_key}, Payin={payin}")
#         deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#         return f"-{deduction}%", round(payin - deduction, 2)
    
#     # Parse the formula
#     formula = matching_rule["PO"]
    
#     if "%" in formula and "of Payin" in formula:
#         # Format: "90% of Payin" or "88% of Payin"
#         percentage = float(formula.split("%")[0])
#         payout = round(payin * percentage / 100, 2)
#         return formula, payout
#     elif formula.startswith("-") and "%" in formula:
#         # Format: "-2%", "-3%", etc.
#         deduction = float(formula.replace("%", "").replace("-", ""))
#         payout = round(payin - deduction, 2)
#         return formula, payout
#     elif formula.startswith("Less") and "%" in formula:
#         # Format: "Less 2% of Payin"
#         deduction = float(formula.split()[1].replace("%", ""))
#         payout = round(payin - deduction, 2)
#         return formula, payout
#     else:
#         # Unknown format, use fallback
#         deduction = 2
#         return f"-{deduction}%", round(payin - deduction, 2)

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     """
#     Calculate payout using formula data
#     Returns: (payout, formula_used, rule_explanation)
#     """
#     # If payin is 0, payout is also 0
#     if payin == 0:
#         return 0, "0% (No Payin)", f"Payin is 0, so Payout is 0"
    
#     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
#     payin_cat = get_payin_category(payin)
    
#     rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
#     return payout, formula, rule_explanation

# # ------------------- STATE MAPPING -------------------
# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
#     "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
#     "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
#     "Himachal Pradesh": "HIMACHAL PRADESH", "Andaman": "ANDAMAN AND NICOBAR ISLANDS",
#     "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
#     "West Bengal": "WEST BENGAL", "North Bengal": "WEST BENGAL", "Orissa": "ODISHA",
#     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
#     "ROM2": "REST OF MAHARASHTRA", "Good Vizag": "ANDHRA PRADESH", "Good TN": "TAMIL NADU",
#     "Kerala": "KERALA", "Good MP": "MADHYA PRADESH", "Good CG": "CHHATTISGARH",
#     "Good RJ": "RAJASTHAN", "Bad RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH",
#     "Bad UP": "UTTAR PRADESH", "Good UK": "UTTARAKHAND", "Bad UK": "UTTARAKHAND",
#     "Punjab": "PUNJAB", "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM",
#     "NE EX ASSAM": "NORTH EAST", "Good NL": "NAGALAND", "GOOD KA": "KARNATAKA",
#     "BAD KA": "KARNATAKA", "HR Ref": "HARYANA", "Dehradun, Haridwar": "UTTARAKHAND"
# }

# def safe_float(value):
#     """Safely convert value to float, handling 'D', 'NA', empty strings, etc."""
#     if pd.isna(value):
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ["D", "NA", "", "NAN", "NONE"]:
#         return None
#     try:
#         num = float(val_str.replace('%', '').strip())
#         if 0 < num < 1:
#             num = num * 100
#         return num
#     except:
#         return None

# # ------------------- LIST WORKSHEETS -------------------
# @app.post("/list-worksheets")
# async def list_worksheets(policy_file: UploadFile = File(...)):
#     try:
#         content = await policy_file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         worksheets = xls.sheet_names
#         return {"worksheets": worksheets
# }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # ------------------- TWO WHEELER SHEET PROCESSOR -------------------
# def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         print(f"TW sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
#             segmentation = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            
#             comp_cd1 = safe_float(row.iloc[2]) if len(row) > 2 else None
#             comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
#             satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None
            
#             state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
#             segment_desc = f"TW {segmentation}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TW"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TW"
            
#             # Process Comp
#             if comp_cd2 is not None:
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, comp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{comp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(comp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
            
#             # Process TP
#             if satp_cd2 is not None:
#                 policy_type_final = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, satp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{satp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(satp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing TW sheet: {str(e)}")
#         return []

# # ------------------- ELECTRIC SHEET PROCESSOR -------------------
# def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         print(f"Electric sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             city_cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
#             rto_remarks = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#             fuel = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Electric"
#             make = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else "All"
#             seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "5"
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city_cluster.upper()), "UNKNOWN")
            
#             cvod_cd1 = safe_float(row.iloc[5]) if len(row) > 5 else None
#             cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
#             cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
#             segment_desc = f"Taxi {fuel} {make}"
#             if rto_remarks:
#                 segment_desc += f" {rto_remarks}"
#             segment_desc += f" Seating:{seating}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
#             # Process CVOD (Comp)
#             if cvod_cd2 is not None:
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, cvod_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvod_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvod_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
            
#             # Process CVTP (TP)
#             if cvtp_cd2 is not None:
#                 policy_type_final = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, cvtp_cd2
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvtp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvtp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing electric sheet: {str(e)}")
#         return []

# # ------------------- REGULAR SHEET PROCESSOR -------------------
# def process_regular_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         prev_location = ""
        
#         for idx, row in df.iterrows():
#             if idx < 5:
#                 continue
            
#             location = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() else prev_location
#             if location:
#                 prev_location = location
            
#             fuel = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#             make = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
#             remarks = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
#             seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            
#             cols = row.values
            
#             combinations = [
#                 ("Without Add On Cover", "<=1000 CC", "SAOD", 5, 6),
#                 ("Without Add On Cover", ">1000 CC",  "SAOD", 7, 8),
#                 ("With Add On Cover",    "<=1000 CC", "SAOD", 9, 10),
#                 ("With Add On Cover",    ">1000 CC",  "SAOD", 11, 12),
#                 ("", "<=1000 CC", "TP", None, 13),
#                 ("", ">1000 CC",  "TP", None, 14),
#             ]
            
#             for addon, cc, ptype, cd1_idx, cd2_idx in combinations:
#                 if len(cols) <= cd2_idx:
#                     continue
                
#                 cd2_val = cols[cd2_idx] if cd2_idx < len(cols) else None
#                 payin = safe_float(cd2_val)
                
#                 if payin is None:
#                     continue
                
#                 segment_desc = f"Taxi {fuel} {make} {remarks}".strip()
#                 if seating:
#                     segment_desc += f" Seating:{seating}"
#                 if cc and ptype == "SAOD":
#                     segment_desc += f" {cc}"
#                 if addon:
#                     segment_desc += f" {addon}"
                
#                 state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")
                
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
#                 policy_type_final = override_policy_type if override_policy_type else ("TP" if ptype == "TP" else "Comp")
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, payin
#                 )
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": location,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing regular sheet: {str(e)}")
#         return []

# # ------------------- 4W SATP SHEET PROCESSOR -------------------
# def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=0)
#         df.columns = df.columns.str.strip()
        
#         print(f"4W SATP sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             if pd.isna(row['Cluster']) or str(row['Cluster']).strip() == "":
#                 continue
            
#             cluster = str(row['Cluster']).strip()
#             new_segment_mapping = str(row['New Segment Mapping']).strip()
#             new_age_band = str(row['New Age Band']).strip()
            
#             cd2_val = row['CD2'] if 'CD2' in df.columns else None
#             payin = safe_float(cd2_val)
            
#             if payin is None:
#                 continue
            
#             # State mapping using fuzzy match
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
            
#             # Original segment description includes age band in remarks
#             segment_desc = f"PVT CAR TP {new_segment_mapping} Age Band: {new_age_band}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR TP"
#             policy_type_final = override_policy_type if override_policy_type else "TP"
            
#             payout, formula, rule_exp = calculate_payout_with_formula(
#                 lob_final, segment_final, policy_type_final, payin
#             )
            
#             records.append({
#                 "State": state.upper(),
#                 "Location/Cluster": cluster,
#                 "Original Segment": segment_desc.strip(),
#                 "Mapped Segment": segment_final,
#                 "LOB": lob_final,
#                 "Policy Type": policy_type_final,
#                 "Payin (CD2)": f"{payin:.2f}%",
#                 "Payin Category": get_payin_category(payin),
#                 "Calculated Payout": f"{payout:.2f}%",
#                 "Formula Used": formula,
#                 "Rule Explanation": rule_exp
#             })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing 4W SATP sheet: {str(e)}")
#         return []

# # ------------------- NEW 4W COMP SAOD SHEET PROCESSOR (MY OWN LOGIC) -------------------
# def process_4w_comp_saod_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         # Trim all strings in DF
#         df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
#         # Find cluster column - assume first column with 'Cluster'
#         cluster_col = None
#         for j in range(df.shape[1]):
#             if 'Cluster' in df.iloc[:, j].values:
#                 cluster_col = j
#                 break
        
#         if cluster_col is None:
#             return []
        
#         # Find header rows - look for rows with policy types like SAOD, COMP
#         header_rows = []
#         for i in range(df.shape[0]):
#             if any(word in str(df.iloc[i, j]) for j in range(cluster_col + 1, df.shape[1]) for word in ['SAOD', 'COMP', 'Renewals', 'Non HEV', 'CD2_OD+Addon']):
#                 header_rows.append(i)
        
#         # The data starts after the last header row
#         data_start = max(header_rows) + 1
        
#         # Collect all header info by column
#         headers = {}
#         for j in range(cluster_col + 1, df.shape[1]):
#             col_header = ''
#             for i in header_rows:
#                 val = str(df.iloc[i, j])
#                 if val:
#                     col_header += val + ' '
#             headers[j] = col_header.strip()
        
#         # Process data rows
#         for i in range(data_start, df.shape[0]):
#             cluster = str(df.iloc[i, cluster_col])
#             if not cluster or pd.isna(cluster):
#                 continue
            
#             state = next((v.upper() for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
            
#             for j in range(cluster_col + 1, df.shape[1]):
#                 payin_val = df.iloc[i, j]
#                 payin = safe_float(payin_val)
#                 if payin is None:
#                     continue
                
#                 # Parse original segment from header
#                 header = headers[j]
#                 policy_type = 'SAOD' if 'SAOD' in header else 'COMP' if 'COMP' in header else ''
#                 fuel = 'Petrol' if 'Petrol' in header and 'Non' not in header else 'Non-Petrol (incl. CNG)' if 'Non' in header or 'CNG' in header else ''
#                 segment = 'Non-HEV' if 'Non HEV' in header or 'Non-HEV' in header else 'HEV' if 'HEV' in header else ''
#                 renewal = ' (Renewals)' if 'Renewals' in header else ''
                
#                 original_segment = f"PVT CAR {segment} - {fuel}{renewal}"
                
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR COMP + SAOD"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(
#                     lob_final, segment_final, policy_type_final, payin
#                 )
                
#                 records.append({
#                     "State": state,
#                     "Location/Cluster": cluster,
#                     "Original Segment": original_segment.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%",
#                     "Formula Used": formula,
#                     "Rule Explanation": rule_exp
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing 4W COMP+SAOD sheet: {str(e)}")
#         return []

# # ------------------- MAIN PROCESS FUNCTION -------------------
# def process_file_updated(
#     company_name: str,
#     policy_file_content: bytes,
#     sheet_name: Optional[str] = None,
#     override_enabled: str = "false",
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
#     override_policy_type: Optional[str] = None,
# ):
#     try:
#         xls = pd.ExcelFile(io.BytesIO(policy_file_content))
        
#         if sheet_name and sheet_name in xls.sheet_names:
#             sheets_to_process = [sheet_name]
#         else:
#             sheets_to_process = xls.sheet_names
        
#         all_records = []
        
#         for sheet in sheets_to_process:
#             sheet_lower = sheet.lower()
            
#             # Improved routing logic
#             if any(keyword in sheet_lower for keyword in ["comp", "saod", "od+addon", "private car", "pvt car", "4w", "four wheeler"]):
#                 # Extra check
#                 temp_df = pd.read_excel(io.BytesIO(policy_file_content), sheet_name=sheet, nrows=20, header=None)
#                 text = " ".join(temp_df.astype(str).values.flatten()).lower()
#                 if "cluster" in text and "cd2" in text:
#                     records = process_4w_comp_saod_sheet(
#                         policy_file_content, sheet, override_enabled, 
#                         override_lob, override_segment, override_policy_type
#                     )
#                 else:
#                     records = process_regular_sheet(policy_file_content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif any(keyword in sheet_lower for keyword in ["electric", "ev", "taxi", "cng", "lpg"]):
#                 records = process_electric_sheet(policy_file_content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif any(keyword in sheet_lower for keyword in ["tw", "2w", "two wheeler"]):
#                 records = process_tw_sheet(policy_file_content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "satp" in sheet_lower or "tp only" in sheet_lower:
#                 records = process_4w_satp_sheet(policy_file_content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             else:
#                 records = process_regular_sheet(policy_file_content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
            
#             all_records.extend(records)
        
#         return all_records
        
#     except Exception as e:
#         print(f"Error in process_file_updated: {str(e)}")
#         raise

# # FastAPI endpoint
# @app.post("/process")
# async def process_file(
#     company_name: str = Form(...),
#     policy_file: UploadFile = File(...),
#     sheet_name: Optional[str] = Form(None),
#     override_enabled: str = Form("false"),
#     override_lob: Optional[str] = Form(None),
#     override_segment: Optional[str] = Form(None),
#     override_policy_type: Optional[str] = Form(None),
# ):
#     try:
#         content = await policy_file.read()
        
#         all_records = process_file_updated(
#             company_name=company_name,
#             policy_file_content=content,
#             sheet_name=sheet_name,
#             override_enabled=override_enabled,
#             override_lob=override_lob,
#             override_segment=override_segment,
#             override_policy_type=override_policy_type
#         )
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found in any sheet")
        
#         result_df = pd.DataFrame(all_records)
        
#         # Calculate metrics
#         payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records if r["Payin (CD2)"]]
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        
#         formula_summary = {}
#         for r in all_records:
#             f = r["Formula Used"]
#             formula_summary[f] = formula_summary.get(f, 0) + 1
        
#         # Generate Excel
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         # Generate CSV
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
#         # Generate JSON
#         json_str = result_df.to_json(orient="records")
        
#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "avg_payin": f"{avg_payin:.2f}",
#                 "unique_segments": len(result_df["Mapped Segment"].unique()),
#                 "formula_summary": formula_summary,
#                 "sheets_processed": len(sheets_to_process)
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64,
#             "json_data": json_str
#         }
    
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import base64
from typing import Optional

app = FastAPI(title="Insurance Policy Processor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ------------------- PAYOUT LOGIC -------------------
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
    if pd.isna(value): return None
    s = str(value).strip().upper()
    if s in ["D", "NA", "", "NAN", "NONE"]: return None
    try:
        num = float(s.replace("%", ""))
        return num * 100 if 0 < num < 1 else num
    except:
        return None

# ------------------- LIST WORKSHEETS -------------------
@app.post("/list-worksheets")
async def list_worksheets(policy_file: UploadFile = File(...)):
    content = await policy_file.read()
    xls = pd.ExcelFile(io.BytesIO(content))
    return {"worksheets": xls.sheet_names}


# ------------------- 4W COMP+SAOD – MY BULLETPROOF LOGIC -------------------
# def process_4w_comp_saod_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None).applymap(lambda x: x.strip() if isinstance(x, str) else x)

#         # Find "Cluster" column
#         cluster_col = next((j for j in range(df.shape[1]) if df.iloc[:, j].astype(str).str.contains("Cluster", case=False, na=False).any()), None)
#         if cluster_col is None: return []

#         # Find all columns that contain "CD2"
#         cd2_cols = [j for j in range(cluster_col + 1, df.shape[1]) if df.iloc[:, j].astype(str).str.contains("CD2", case=False, na=False).any()]

#         # Build header text for each CD2 column
#         headers = {}
#         for j in cd2_cols:
#             header = " ".join([str(df.iloc[i, j]) for i in range(df.shape[0]) if pd.notna(df.iloc[i, j]) and "CD2" not in str(df.iloc[i, j])])
#             headers[j] = header

#         # Find first data row (after last header row)
#         data_start_row = max((i for i in range(df.shape[0]) for j in cd2_cols if pd.notna(df.iloc[i, j]) and "CD2" in str(df.iloc[i, j])), default=0) + 1

#         for i in range(data_start_row, df.shape[0]):
#             cluster = str(df.iloc[i, cluster_col])
#             if not cluster or pd.isna(cluster) or "total" in cluster.lower(): continue

#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

#             for j in cd2_cols:
#                 payin = safe_float(df.iloc[i, j])
#                 if payin is None: continue

#                 header = headers[j]
#                 policy = "SAOD" if "SAOD" in header else "COMP" if "COMP" in header else "COMP"
#                 fuel = "Petrol" if "Petrol" in header and "Non" not in header else "Non-Petrol (incl. CNG)"
#                 segment = "Non-HEV" if "Non HEV" in header or "Non-HEV" in header else "HEV"
#                 renewal = " (Renewals)" if "Renewal" in header else ""

#                 orig_seg = f"PVT CAR {segment} - {fuel}{renewal}"

#                 lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR COMP + SAOD"
#                 policy_final = override_policy_type if override_policy_type else "Comp"

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
#         return records
#     except Exception as e:
#         print(f"Error in 4W COMP+SAOD: {e}")
#         return []
def process_4w_comp_saod_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Find Cluster column
        cluster_col = next((j for j in range(df.shape[1]) 
                          if df.iloc[:, j].astype(str).str.contains("Cluster", case=False, na=False).any()), None)
        if cluster_col is None: 
            return []

        # Find all CD2 columns
        cd2_cols = [j for j in range(cluster_col + 1, df.shape[1]) 
                   if df.iloc[:, j].astype(str).str.contains("CD2", case=False, na=False).any()]

        # Build full header text for each CD2 column
        headers = {}
        for j in cd2_cols:
            header_parts = []
            for i in range(df.shape[0]):
                val = str(df.iloc[i, j])
                if pd.notna(df.iloc[i, j]) and "CD2" not in val.upper():
                    header_parts.append(val)
            headers[j] = " ".join(header_parts)

        # Find data start row
        data_start_row = max((i for i in range(df.shape[0]) for j in cd2_cols 
                            if pd.notna(df.iloc[i, j]) and "CD2" in str(df.iloc[i, j]).upper()), default=0) + 1

        for i in range(data_start_row, df.shape[0]):
            cluster = str(df.iloc[i, cluster_col])
            if not cluster or pd.isna(cluster) or "total" in cluster.lower():
                continue

            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")

            for j in cd2_cols:
                payin = safe_float(df.iloc[i, j])
                if payin is None: 
                    continue

                header = headers[j].upper()

                # FIXED: Proper SAOD vs COMP detection
                if "SAOD" in header and "COMP" not in header:
                    policy_type = "SAOD"
                elif "COMP" in header:
                    policy_type = "COMP"
                else:
                    policy_type = "SAOD"  # fallback

                # Fuel
                fuel = "Petrol" if "PETROL" in header and "NON" not in header else "Non-Petrol (incl. CNG)"

                # Segment
                segment = "Non-HEV" if any(x in header for x in ["NON HEV", "NON-HEV"]) else "HEV"

                # Renewal
                renewal = " (Renewals)" if "RENEWAL" in header else ""

                orig_seg = f"PVT CAR {segment} - {fuel}{renewal}".strip()

                lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
                segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR COMP + SAOD"
                policy_final = override_policy_type if override_policy_type else policy_type  # ← NOW SHOWS SAOD or COMP correctly!

                payout, formula, exp = calculate_payout_with_formula(lob_final, segment_final, policy_final, payin)

                records.append({
                    "State": state,
                    "Location/Cluster": cluster,
                    "Original Segment": orig_seg,
                    "Mapped Segment": segment_final,
                    "LOB": lob_final,
                    "Policy Type": policy_final,           # ← NOW SHOWS "SAOD" or "COMP"
                    "Payin (CD2)": f"{payin:.2f}%",
                    "Payin Category": get_payin_category(payin),
                    "Calculated Payout": f"{payout:.2f}%",
                    "Formula Used": formula,
                    "Rule Explanation": exp
                })
        return records

    except Exception as e:
        print(f"Error in 4W COMP+SAOD: {e}")
        import traceback
        traceback.print_exc()
        return []
# ------------------- MAIN PROCESSING -------------------
@app.post("/process")
async def process_file(
    company_name: str = Form(...),
    policy_file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    override_enabled: str = Form("false"),
    override_lob: Optional[str] = Form(None),
    override_segment: Optional[str] = Form(None),
    override_policy_type: Optional[str] = Form(None),
):
    content = await policy_file.read()
    xls = pd.ExcelFile(io.BytesIO(content))
    sheets_to_process = [sheet_name] if sheet_name and sheet_name in xls.sheet_names else xls.sheet_names

    all_records = []

    for sheet in sheets_to_process:
        sheet_lower = sheet.lower()

        # Smart routing
        try:
            temp_df = pd.read_excel(io.BytesIO(content), sheet_name=sheet, nrows=30, header=None)
            sample_text = " ".join(temp_df.astype(str).values.flatten()).lower()
        except:
            sample_text = ""

        if ("cluster" in sample_text and "cd2" in sample_text and any(x in sample_text for x in ["saod", "comp", "od+addon"])):
            records = process_4w_comp_saod_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
       

        all_records.extend(records)

    if not all_records:
        raise HTTPException(status_code=400, detail="No data extracted")

    df_out = pd.DataFrame(all_records)
    excel_io = io.BytesIO()
    df_out.to_excel(excel_io, index=False, sheet_name="Processed")
    excel_io.seek(0)
    excel_b64 = base64.b64encode(excel_io.read()).decode()

    csv_io = io.StringIO()
    df_out.to_csv(csv_io, index=False)
    csv_b64 = base64.b64encode(csv_io.getvalue().encode()).decode()

    return {
        "metrics": {"company_name": company_name, "total_records": len(all_records)},
        "calculated_data": all_records,
        "excel_data": excel_b64,
        "csv_data": csv_b64
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
