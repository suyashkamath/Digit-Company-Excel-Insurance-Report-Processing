# # from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# # from fastapi.responses import JSONResponse, StreamingResponse
# # from fastapi.middleware.cors import CORSMiddleware
# # import pandas as pd
# # import io
# # import base64
# # from typing import Optional, List
# # import os

# # app = FastAPI(title="Insurance Policy Processor API")

# # # Allow frontend (localhost:5500 or any)
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # ------------------- FORMULA DATA -------------------
# # FORMULA_DATA = [
# #     {"LOB": "TW", "SEGMENT": "1+5", "PO": "90% of Payin", "REMARKS": "NIL"},
    
# #     # TW SAOD + COMP rules
# #     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
# #     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
# #     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
# #     {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
# #     # TW TP rules
# #     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
# #     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
# #     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin 31% to 50%"},
# #     {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
# #     # PVT CAR rules
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 30%"},
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 40%"},
# #     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 50%"},
    
# #     # CV rules
# #     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
# #     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
# #     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
# #     {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
# #     # BUS rules
# #     {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
# #     {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
    
# #     # TAXI rules
# #     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
# #     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
# #     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
# #     {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
# #     # MISD rules
# #     {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
# # ]

# # # ------------------- PAYOUT LOGIC -------------------
# # def get_payin_category(payin: float):
# #     if payin <= 20:
# #         return "Payin Below 20%"
# #     elif payin <= 30:
# #         return "Payin 21% to 30%"
# #     elif payin <= 50:
# #         return "Payin 31% to 50%"
# #     else:
# #         return "Payin Above 50%"

# # def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
# #     """
# #     Look up formula from FORMULA_DATA based on LOB, segment, policy type and payin
# #     Returns: (formula_string, payout_value)
# #     """
# #     segment_key = segment.upper()
    
# #     if lob == "TW":
# #         if policy_type == "TP":
# #             segment_key = "TW TP"
# #         else:
# #             segment_key = "TW SAOD + COMP"
# #     elif lob == "PVT CAR":
# #         if policy_type == "TP":
# #             segment_key = "PVT CAR TP"
# #         else:
# #             segment_key = "PVT CAR COMP + SAOD"
# #     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
# #         segment_key = segment.upper()
    
# #     payin_category = get_payin_category(payin)
# #     matching_rule = None
    
# #     for rule in FORMULA_DATA:
# #         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
# #             if rule["REMARKS"] == payin_category:
# #                 matching_rule = rule
# #                 break
# #             elif rule["REMARKS"] == "NIL":
# #                 matching_rule = rule
    
# #     if not matching_rule and payin > 20:
# #         for rule in FORMULA_DATA:
# #             if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
# #                 if rule["REMARKS"] == "Payin Above 20%":
# #                     matching_rule = rule
# #                     break
# #                 elif payin > 30 and rule["REMARKS"] == "Payin Above 30%":
# #                     matching_rule = rule
# #                     break
# #                 elif payin > 40 and rule["REMARKS"] == "Payin Above 40%":
# #                     matching_rule = rule
# #                     break
# #                 elif payin > 50 and rule["REMARKS"] == "Payin Above 50%":
# #                     matching_rule = rule
# #                     break
    
# #     if not matching_rule:
# #         deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
# #         return f"-{deduction}%", round(payin - deduction, 2)
    
# #     formula = matching_rule["PO"]
    
# #     if "%" in formula and "of Payin" in formula:
# #         percentage = float(formula.split("%")[0])
# #         payout = round(payin * percentage / 100, 2)
# #         return formula, payout
# #     elif formula.startswith("-") and "%" in formula:
# #         deduction = float(formula.replace("%", "").replace("-", ""))
# #         payout = round(payin - deduction, 2)
# #         return formula, payout
# #     elif formula.startswith("Less") and "%" in formula:
# #         deduction = float(formula.split()[1].replace("%", ""))
# #         payout = round(payin - deduction, 2)
# #         return formula, payout
# #     else:
# #         deduction = 2
# #         return f"-{deduction}%", round(payin - deduction, 2)

# # def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
# #     if payin == 0:
# #         return 0, "0% (No Payin)", f"Payin is 0, so Payout is 0"
    
# #     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
# #     payin_cat = get_payin_category(payin)
# #     rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
# #     return payout, formula, rule_explanation

# # # ------------------- STATE MAPPING -------------------
# # STATE_MAPPING = {
# #     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
# #     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
# #     "Surat": "GUJARAT", "Jaipur": "RAJASTHAN", "Lucknow": "UTTAR PRADESH",
# #     "Patna": "BIHAR", "Ranchi": "JHARKHAND", "Bhuvaneshwar": "ODISHA",
# #     "Srinagar": "JAMMU AND KASHMIR", "Dehradun": "UTTARAKHAND", "Haridwar": "UTTARAKHAND",
# #     "Himachal Pradesh": "HIMACHAL PRADESH", "Andaman": "ANDAMAN AND NICOBAR ISLANDS",
# #     "Bangalore": "KARNATAKA", "Jharkhand": "JHARKHAND", "Bihar": "BIHAR",
# #     "West Bengal": "WEST BENGAL", "North Bengal": "WEST BENGAL", "Orissa": "ODISHA",
# #     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
# #     "ROM2": "REST OF MAHARASHTRA", "Good Vizag": "ANDHRA PRADESH", "Good TN": "TAMIL NADU",
# #     "Kerala": "KERALA", "Good MP": "MADHYA PRADESH", "Good CG": "CHHATTISGARH",
# #     "Good RJ": "RAJASTHAN", "Bad RJ": "RAJASTHAN", "Good UP": "UTTAR PRADESH",
# #     "Bad UP": "UTTAR PRADESH", "Good UK": "UTTARAKHAND", "Bad UK": "UTTARAKHAND",
# #     "Punjab": "PUNJAB", "Jammu": "JAMMU AND KASHMIR", "Assam": "ASSAM",
# #     "NE EX ASSAM": "NORTH EAST", "Good NL": "NAGALAND", "GOOD KA": "KARNATAKA",
# #     "BAD KA": "KARNATAKA", "HR Ref": "HARYANA", "Dehradun, Haridwar": "UTTARAKHAND",
# #     "Tamil Nadu": "TAMIL NADU", "TN": "TAMIL NADU", "Chennai": "TAMIL NADU",
# #     "Coimbatore": "TAMIL NADU"
# # }

# # def safe_float(value):
# #     if pd.isna(value):
# #         return None
# #     val_str = str(value).strip().upper()
# #     if val_str in ["D", "NA", "", "NAN", "NONE"]:
# #         return None
# #     try:
# #         num = float(val_str.replace('%', '').strip())
# #         if 0 < num < 1:
# #             num = num * 100
# #         return num
# #     except:
# #         return None

# # # ------------------- SCHOOL BUS SHEET PROCESSOR -------------------
# # def process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
# #     records = []
    
# #     try:
# #         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
# #         print(f"Processing School Bus sheet: {sheet_name}")
        
# #         # Find the "School Bus" header to locate table start
# #         table_start_row = None
# #         for i in range(min(10, len(df))):
# #             for j in range(len(df.columns)):
# #                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
# #                 if "school bus" in cell:
# #                     table_start_row = i
# #                     print(f"Found 'School Bus' header at row {i}")
# #                     break
# #             if table_start_row is not None:
# #                 break
        
# #         if table_start_row is None:
# #             print("Could not find 'School Bus' header")
# #             return []
        
# #         # Headers are at table_start_row + 1
# #         header_row = table_start_row + 1
# #         data_start_row = table_start_row + 2
        
# #         # Find column indices dynamically
# #         state_col = 0
# #         rto_col = 1
# #         school_col = None
# #         transport_col = None
# #         individual_col = None
        
# #         # Search for column headers
# #         for col_idx in range(len(df.columns)):
# #             header = str(df.iloc[header_row, col_idx]).strip().lower() if pd.notna(df.iloc[header_row, col_idx]) else ""
# #             if "in the name of" in header or "school" in header:
# #                 school_col = col_idx
# #             elif "transporter" in header:
# #                 transport_col = col_idx
# #             elif "individual" in header:
# #                 individual_col = col_idx
        
# #         # Fallback to fixed positions if not found
# #         if school_col is None:
# #             school_col = 2
# #         if transport_col is None:
# #             transport_col = 3
# #         if individual_col is None:
# #             individual_col = 4
        
# #         # Process data rows
# #         current_state = ""
        
# #         for row_idx in range(data_start_row, len(df)):
# #             # Check if we've reached end of section
# #             first_cell = str(df.iloc[row_idx, 0]).strip().lower() if pd.notna(df.iloc[row_idx, 0]) else ""
# #             if "seating capacity" in first_cell or "staff bus" in first_cell or "note:" in first_cell:
# #                 break
            
# #             # Get state
# #             state_val = str(df.iloc[row_idx, state_col]).strip() if pd.notna(df.iloc[row_idx, state_col]) else ""
# #             if state_val and state_val.upper() not in ["", "NAN"]:
# #                 current_state = state_val
            
# #             # Get RTO cluster
# #             rto_cluster = str(df.iloc[row_idx, rto_col]).strip() if pd.notna(df.iloc[row_idx, rto_col]) else ""
            
# #             # Skip empty rows
# #             if not rto_cluster or rto_cluster.lower() in ["", "nan"]:
# #                 continue
            
# #             # Process three columns: School, Transporter, Individual
# #             contracts = [
# #                 (school_col, "In name of School"),
# #                 (transport_col, "On Contract (Transporter)"),
# #                 (individual_col, "On Contract (Individual)")
# #             ]
            
# #             for col_idx, contract_type in contracts:
# #                 payin_val = df.iloc[row_idx, col_idx] if col_idx < len(df.columns) else None
# #                 payin = safe_float(payin_val)
                
# #                 if payin is None:
# #                     continue
                
# #                 # Map state
# #                 state_mapped = current_state.upper()
# #                 for key, value in STATE_MAPPING.items():
# #                     if key.upper() in current_state.upper():
# #                         state_mapped = value
# #                         break
                
# #                 # Build segment description
# #                 segment_desc = f"School Bus - {contract_type} - Seating 8+"
# #                 if rto_cluster and rto_cluster != current_state:
# #                     segment_desc += f" ({rto_cluster})"
                
# #                 # Apply overrides
# #                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
# #                 segment_final = override_segment if override_enabled == "true" and override_segment else "SCHOOL BUS"
# #                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
# #                 # Calculate payout
# #                 payout, formula, rule_exp = calculate_payout_with_formula(
# #                     lob_final, segment_final, policy_type_final, payin
# #                 )
                
# #                 records.append({
# #                     "State": state_mapped.upper(),
# #                     "Location/Cluster": f"{current_state} - {rto_cluster}".strip(),
# #                     "Original Segment": segment_desc.strip(),
# #                     "Mapped Segment": segment_final,
# #                     "LOB": lob_final,
# #                     "Policy Type": policy_type_final,
# #                     "Payin (CD2)": f"{payin:.2f}%",
# #                     "Payin Category": get_payin_category(payin),
# #                     "Calculated Payout": f"{payout:.2f}%",
# #                     "Formula Used": formula,
# #                     "Rule Explanation": rule_exp
# #                 })
        
# #         print(f"Processed {len(records)} records from School Bus section")
# #         return records
        
# #     except Exception as e:
# #         print(f"Error processing school bus sheet: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         return []

# # # ------------------- STAFF BUS SHEET PROCESSOR -------------------
# # def process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
# #     records = []
    
# #     try:
# #         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
# #         print(f"Processing Staff Bus sheet: {sheet_name}")
        
# #         # Find the "STAFF BUS" header
# #         table_start_row = None
# #         for i in range(min(30, len(df))):
# #             for j in range(len(df.columns)):
# #                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
# #                 if "staff bus" in cell:
# #                     table_start_row = i
# #                     print(f"Found 'STAFF BUS' header at row {i}")
# #                     break
# #             if table_start_row is not None:
# #                 break
        
# #         if table_start_row is None:
# #             print("Could not find 'STAFF BUS' header")
# #             return []
        
# #         # Headers are at table_start_row + 1
# #         header_row = table_start_row + 1
# #         data_start_row = table_start_row + 2
        
# #         # Find column indices dynamically
# #         rto_col = 0
# #         company_col = None
# #         transport_col = None
# #         individual_col = None
# #         seating_col = None
        
# #         for col_idx in range(len(df.columns)):
# #             header = str(df.iloc[header_row, col_idx]).strip().lower() if pd.notna(df.iloc[header_row, col_idx]) else ""
# #             if "company" in header:
# #                 company_col = col_idx
# #             elif "transport" in header:
# #                 transport_col = col_idx
# #             elif "individual" in header:
# #                 individual_col = col_idx
# #             elif "seating" in header:
# #                 seating_col = col_idx
        
# #         # Fallback positions
# #         if company_col is None:
# #             company_col = 1
# #         if transport_col is None:
# #             transport_col = 2
# #         if individual_col is None:
# #             individual_col = 3
# #         if seating_col is None:
# #             seating_col = 4
        
# #         # Process data rows
# #         for row_idx in range(data_start_row, len(df)):
# #             rto_val = str(df.iloc[row_idx, rto_col]).strip() if pd.notna(df.iloc[row_idx, rto_col]) else ""
            
# #             # Skip empty rows and notes
# #             if not rto_val or rto_val.lower() in ["", "nan", "note:", "for new vehicles"]:
# #                 continue
            
# #             # Check if this is a notes/instruction row
# #             if any(keyword in rto_val.lower() for keyword in ["permit copy", "validation", "exception", "sport-term", "seating capacity", "above grid"]):
# #                 continue
            
# #             # Process contract type columns
# #             contracts = [
# #                 (company_col, "In name of Company"),
# #                 (transport_col, "Contract (Transport)"),
# #                 (individual_col, "Contract (Individual)")
# #             ]
            
# #             for col_idx, contract_type in contracts:
# #                 cell_value = str(df.iloc[row_idx, col_idx]).strip() if col_idx < len(df.columns) and pd.notna(df.iloc[row_idx, col_idx]) else ""
                
# #                 if not cell_value or cell_value.lower() in ["", "nan", "decline"]:
# #                     continue
                
# #                 # Extract CD2 value from format like "CD1 95% / CD2 42.5%"
# #                 payin = None
# #                 if "CD2" in cell_value.upper():
# #                     parts = cell_value.split("/")
# #                     for part in parts:
# #                         if "CD2" in part.upper():
# #                             cd2_part = part.strip()
# #                             cd2_cleaned = cd2_part.replace("CD2", "").replace("cd2", "").strip()
# #                             payin = safe_float(cd2_cleaned)
# #                             break
                
# #                 if payin is None:
# #                     continue
                
# #                 # Get seating capacity
# #                 seating = str(df.iloc[row_idx, seating_col]).strip() if seating_col < len(df.columns) and pd.notna(df.iloc[row_idx, seating_col]) else ""
                
# #                 # Map state from RTO
# #                 state_mapped = "UNKNOWN"
# #                 for key, value in STATE_MAPPING.items():
# #                     if key.upper() in rto_val.upper():
# #                         state_mapped = value
# #                         break
                
# #                 # Build segment description
# #                 segment_desc = f"Staff Bus - {contract_type}"
# #                 if seating:
# #                     segment_desc += f" - Seating: {seating}"
                
# #                 # Apply overrides
# #                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
# #                 segment_final = override_segment if override_enabled == "true" and override_segment else "STAFF BUS"
# #                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
# #                 # Calculate payout
# #                 payout, formula, rule_exp = calculate_payout_with_formula(
# #                     lob_final, segment_final, policy_type_final, payin
# #                 )
                
# #                 records.append({
# #                     "State": state_mapped.upper(),
# #                     "Location/Cluster": rto_val,
# #                     "Original Segment": segment_desc.strip(),
# #                     "Mapped Segment": segment_final,
# #                     "LOB": lob_final,
# #                     "Policy Type": policy_type_final,
# #                     "Payin (CD2)": f"{payin:.2f}%",
# #                     "Payin Category": get_payin_category(payin),
# #                     "Calculated Payout": f"{payout:.2f}%",
# #                     "Formula Used": formula,
# #                     "Rule Explanation": rule_exp
# #                 })
        
# #         print(f"Processed {len(records)} records from Staff Bus section")
# #         return records
        
# #     except Exception as e:
# #         print(f"Error processing staff bus sheet: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         return []

# # # ------------------- COMBINED BUS SHEET PROCESSOR -------------------
# # def process_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
# #     """
# #     Process a bus sheet that contains both School Bus and Staff Bus sections
# #     """
# #     records = []
    
# #     # Process School Bus section
# #     school_records = process_school_bus_sheet(
# #         content, sheet_name, override_enabled, 
# #         override_lob, override_segment, override_policy_type
# #     )
# #     records.extend(school_records)
    
# #     # Process Staff Bus section
# #     staff_records = process_staff_bus_sheet(
# #         content, sheet_name, override_enabled,
# #         override_lob, override_segment, override_policy_type
# #     )
# #     records.extend(staff_records)
    
# #     return records

# # # ------------------- LIST WORKSHEETS -------------------
# # @app.post("/list-worksheets")
# # async def list_worksheets(policy_file: UploadFile = File(...)):
# #     try:
# #         content = await policy_file.read()
# #         xls = pd.ExcelFile(io.BytesIO(content))
# #         worksheets = xls.sheet_names
# #         return {"worksheets": worksheets}
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))

# # # ------------------- EXISTING PROCESSORS (abbreviated for space) -------------------
# # # Include your existing processors: process_tw_sheet, process_electric_sheet, 
# # # process_regular_sheet, process_4w_satp_sheet, process_4w_comp_saod_sheet

# # # ------------------- MAIN PROCESS FUNCTION -------------------
# # def process_file_updated(
# #     company_name: str,
# #     policy_file_content: bytes,
# #     sheet_name: Optional[str] = None,
# #     override_enabled: str = "false",
# #     override_lob: Optional[str] = None,
# #     override_segment: Optional[str] = None,
# #     override_policy_type: Optional[str] = None,
# # ):
# #     try:
# #         xls = pd.ExcelFile(io.BytesIO(policy_file_content))
        
# #         if sheet_name and sheet_name in xls.sheet_names:
# #             sheets_to_process = [sheet_name]
# #         else:
# #             sheets_to_process = xls.sheet_names
        
# #         all_records = []
        
# #         for sheet in sheets_to_process:
# #             print(f"\n{'='*60}")
# #             print(f"Processing sheet: {sheet}")
# #             print(f"{'='*60}")
            
# #             sheet_lower = sheet.lower()
            
# #             # Determine sheet type and process accordingly
# #             if "bus" in sheet_lower and ("school" in sheet_lower or "staff" in sheet_lower or "seating" in sheet_lower):
# #                 # Bus sheet (School Bus and/or Staff Bus)
# #                 records = process_bus_sheet(
# #                     policy_file_content, sheet, override_enabled,
# #                     override_lob, override_segment, override_policy_type
# #                 )
# #             # ... other sheet types ...
            
# #             all_records.extend(records)
# #             print(f"Sheet '{sheet}' produced {len(records)} records")
        
# #         return all_records
        
# #     except Exception as e:
# #         print(f"Error in process_file_updated: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         raise

# # # ------------------- FASTAPI ENDPOINT -------------------
# # @app.post("/process")
# # async def process_file(
# #     company_name: str = Form(...),
# #     policy_file: UploadFile = File(...),
# #     sheet_name: Optional[str] = Form(None),
# #     override_enabled: str = Form("false"),
# #     override_lob: Optional[str] = Form(None),
# #     override_segment: Optional[str] = Form(None),
# #     override_policy_type: Optional[str] = Form(None),
# # ):
# #     try:
# #         content = await policy_file.read()
        
# #         all_records = process_file_updated(
# #             company_name=company_name,
# #             policy_file_content=content,
# #             sheet_name=sheet_name,
# #             override_enabled=override_enabled,
# #             override_lob=override_lob,
# #             override_segment=override_segment,
# #             override_policy_type=override_policy_type
# #         )
        
# #         if not all_records:
# #             raise HTTPException(status_code=400, detail="No valid data found in any sheet")
        
# #         result_df = pd.DataFrame(all_records)
        
# #         # Calculate metrics
# #         payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records]
# #         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        
# #         formula_summary = {}
# #         for r in all_records:
# #             f = r["Formula Used"]
# #             formula_summary[f] = formula_summary.get(f, 0) + 1
        
# #         # Generate outputs
# #         excel_buffer = io.BytesIO()
# #         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
# #             result_df.to_excel(writer, index=False, sheet_name='Processed')
# #         excel_buffer.seek(0)
# #         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
# #         csv_buffer = io.StringIO()
# #         result_df.to_csv(csv_buffer, index=False)
# #         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
# #         json_str = result_df.to_json(orient="records")
        
# #         return {
# #             "metrics": {
# #                 "company_name": company_name,
# #                 "total_records": len(all_records),
# #                 "avg_payin": f"{avg_payin:.2f}",
# #                 "unique_segments": len(result_df["Mapped Segment"].unique()),
# #                 "formula_summary": formula_summary
# #             },
# #             "calculated_data": all_records,
# #             "excel_data": excel_b64,
# #             "csv_data": csv_b64,
# #             "json_data": json_str
# #         }
    
# #     except Exception as e:
# #         print(f"Error: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         raise HTTPException(status_code=500, detail=str(e))

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import io
# import base64
# from typing import Optional, List
# import os

# app = FastAPI(title="Insurance Policy Processor API")

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

# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Tamil Nadu": "TAMIL NADU", "TN": "TAMIL NADU", "Chennai": "TAMIL NADU",
#     "Kerala": "KERALA", "Karnataka": "KARNATAKA", "Bangalore": "KARNATAKA",
#     "Gujarat": "GUJARAT", "Rajasthan": "RAJASTHAN", "Punjab": "PUNJAB",
#     "Uttar Pradesh": "UTTAR PRADESH", "Delhi NCR": "DELHI", "Rest of India": "REST OF INDIA"
# }

# def get_payin_category(payin: float):
#     if payin <= 20:
#         return "Payin Below 20%"
#     elif payin <= 30:
#         return "Payin 21% to 30%"
#     elif payin <= 50:
#         return "Payin 31% to 50%"
#     else:
#         return "Payin Above 50%"

# def safe_float(value):
#     if pd.isna(value):
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ["D", "NA", "", "NAN", "NONE", "DECLINE"]:
#         return None
#     try:
#         num = float(val_str.replace('%', '').strip())
#         if 0 < num < 1:
#             num = num * 100
#         return num
#     except:
#         return None

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     if payin == 0:
#         return 0, "0% (No Payin)", "Payin is 0, so Payout is 0"
    
#     # Find matching formula
#     matching_rule = None
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"].upper() == segment.upper():
#             if rule["REMARKS"] == "NIL" or rule["REMARKS"] == get_payin_category(payin):
#                 matching_rule = rule
#                 break
    
#     if not matching_rule:
#         deduction = 2
#         return round(payin - deduction, 2), f"-{deduction}%", f"Fallback: LOB={lob}"
    
#     formula = matching_rule["PO"]
    
#     if "%" in formula and "of Payin" in formula:
#         percentage = float(formula.split("%")[0].replace("Less ", ""))
#         if "Less" in formula:
#             payout = round(payin - percentage, 2)
#         else:
#             payout = round(payin * percentage / 100, 2)
#     elif formula.startswith("-"):
#         deduction = float(formula.replace("%", "").replace("-", ""))
#         payout = round(payin - deduction, 2)
#     else:
#         payout = round(payin - 2, 2)
    
#     return payout, formula, f"Match: LOB={lob}, Segment={segment}"

# # ------------------- SCHOOL BUS PROCESSOR -------------------
# def process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(10, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "school bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         data_start_row = table_start_row + 2
#         current_state = ""
        
#         for row_idx in range(data_start_row, len(df)):
#             first_cell = str(df.iloc[row_idx, 0]).strip().lower() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if "seating" in first_cell or "staff" in first_cell or "note" in first_cell:
#                 break
            
#             state_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if state_val and state_val.upper() not in ["", "NAN"]:
#                 current_state = state_val
            
#             rto_cluster = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ""
#             if not rto_cluster:
#                 continue
            
#             contracts = [(2, "In name of School"), (3, "On Contract (Transporter)"), (4, "On Contract (Individual)")]
            
#             for col_idx, contract_type in contracts:
#                 payin = safe_float(df.iloc[row_idx, col_idx])
#                 if payin is None:
#                     continue
                
#                 state_mapped = STATE_MAPPING.get(current_state, current_state.upper())
#                 segment_desc = f"School Bus - {contract_type} - Seating 8+ ({rto_cluster})"
                
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "SCHOOL BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(),
#                     "Location/Cluster": f"{current_state} - {rto_cluster}",
#                     "Original Segment": segment_desc,
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
#         print(f"Error processing school bus: {str(e)}")
#         return []

# # ------------------- STAFF BUS PROCESSOR -------------------
# def process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(30, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "staff bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         data_start_row = table_start_row + 2
        
#         for row_idx in range(data_start_row, len(df)):
#             rto_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if not rto_val or any(kw in rto_val.lower() for kw in ["note", "permit", "validation", "exception", "above grid"]):
#                 continue
            
#             contracts = [(1, "In name of Company"), (2, "Contract (Transport)"), (3, "Contract (Individual)")]
#             seating = str(df.iloc[row_idx, 4]).strip() if pd.notna(df.iloc[row_idx, 4]) else ""
            
#             for col_idx, contract_type in contracts:
#                 cell_value = str(df.iloc[row_idx, col_idx]).strip() if pd.notna(df.iloc[row_idx, col_idx]) else ""
#                 if not cell_value or "decline" in cell_value.lower():
#                     continue
                
#                 payin = None
#                 if "CD2" in cell_value.upper():
#                     for part in cell_value.split("/"):
#                         if "CD2" in part.upper():
#                             cd2_cleaned = part.replace("CD2", "").replace("cd2", "").strip()
#                             payin = safe_float(cd2_cleaned)
#                             break
                
#                 if payin is None:
#                     continue
                
#                 state_mapped = STATE_MAPPING.get(rto_val, "UNKNOWN")
#                 for key, value in STATE_MAPPING.items():
#                     if key.upper() in rto_val.upper():
#                         state_mapped = value
#                         break
                
#                 segment_desc = f"Staff Bus - {contract_type}"
#                 if seating:
#                     segment_desc += f" - Seating: {seating}"
                
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "STAFF BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(),
#                     "Location/Cluster": rto_val,
#                     "Original Segment": segment_desc,
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
#         print(f"Error processing staff bus: {str(e)}")
#         return []

# # ------------------- COMBINED BUS PROCESSOR -------------------
# def process_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     records.extend(process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     records.extend(process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     return records

# @app.post("/list-worksheets")
# async def list_worksheets(policy_file: UploadFile = File(...)):
#     try:
#         content = await policy_file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         return {"worksheets": xls.sheet_names}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

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
#         xls = pd.ExcelFile(io.BytesIO(content))
        
#         sheets_to_process = [sheet_name] if sheet_name and sheet_name in xls.sheet_names else xls.sheet_names
#         all_records = []
        
#         for sheet in sheets_to_process:
#             sheet_lower = sheet.lower()
            
#             if "bus" in sheet_lower:
#                 records = process_bus_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             else:
#                 records = []  # Add other sheet processors here
            
#             all_records.extend(records)
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found")
        
#         result_df = pd.DataFrame(all_records)
        
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "unique_segments": len(result_df["Mapped Segment"].unique())
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import io
# import base64
# from typing import Optional, List
# import os

# app = FastAPI(title="Insurance Policy Processor API")

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

# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Tamil Nadu": "TAMIL NADU", "TN": "TAMIL NADU", "Chennai": "TAMIL NADU",
#     "Kerala": "KERALA", "Karnataka": "KARNATAKA", "Bangalore": "KARNATAKA",
#     "Gujarat": "GUJARAT", "Rajasthan": "RAJASTHAN", "Punjab": "PUNJAB",
#     "Uttar Pradesh": "UTTAR PRADESH", "Delhi NCR": "DELHI", "Rest of India": "REST OF INDIA",
#     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
#     "ROM2": "REST OF MAHARASHTRA", "Good TN": "TAMIL NADU", "Good MP": "MADHYA PRADESH"
# }

# def get_payin_category(payin: float):
#     if payin <= 20:
#         return "Payin Below 20%"
#     elif payin <= 30:
#         return "Payin 21% to 30%"
#     elif payin <= 50:
#         return "Payin 31% to 50%"
#     else:
#         return "Payin Above 50%"

# def safe_float(value):
#     if pd.isna(value):
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ["D", "NA", "", "NAN", "NONE", "DECLINE"]:
#         return None
#     try:
#         num = float(val_str.replace('%', '').strip())
#         if 0 < num < 1:
#             num = num * 100
#         return num
#     except:
#         return None

# def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
#     segment_key = segment.upper()
    
#     if lob == "TW":
#         segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
#     elif lob == "PVT CAR":
#         segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
#     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
#         segment_key = segment.upper()
    
#     payin_category = get_payin_category(payin)
#     matching_rule = None
    
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#             if rule["REMARKS"] == payin_category or rule["REMARKS"] == "NIL":
#                 matching_rule = rule
#                 break
    
#     if not matching_rule and payin > 20:
#         for rule in FORMULA_DATA:
#             if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#                 if (rule["REMARKS"] == "Payin Above 20%" or
#                     (payin > 30 and rule["REMARKS"] == "Payin Above 30%") or
#                     (payin > 40 and rule["REMARKS"] == "Payin Above 40%") or
#                     (payin > 50 and rule["REMARKS"] == "Payin Above 50%")):
#                     matching_rule = rule
#                     break
    
#     if not matching_rule:
#         deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#         return f"-{deduction}%", round(payin - deduction, 2)
    
#     formula = matching_rule["PO"]
    
#     if "%" in formula and "of Payin" in formula:
#         percentage = float(formula.split("%")[0].replace("Less ", ""))
#         if "Less" in formula:
#             payout = round(payin - percentage, 2)
#         else:
#             payout = round(payin * percentage / 100, 2)
#     elif formula.startswith("-"):
#         deduction = float(formula.replace("%", "").replace("-", ""))
#         payout = round(payin - deduction, 2)
#     else:
#         payout = round(payin - 2, 2)
    
#     return formula, payout

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     if payin == 0:
#         return 0, "0% (No Payin)", "Payin is 0, so Payout is 0"
    
#     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
#     payin_cat = get_payin_category(payin)
#     rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
#     return payout, formula, rule_explanation

# # ------------------- TWO WHEELER PROCESSOR -------------------
# def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             cluster = str(row.iloc[0]).strip()
#             segmentation = str(row.iloc[1]).strip() if len(row) > 1 else ""
            
#             comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
#             satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None
            
#             state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TW"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TW"
            
#             if comp_cd2 is not None:
#                 policy_type = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, comp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{comp_cd2:.2f}%", "Payin Category": get_payin_category(comp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
            
#             if satp_cd2 is not None:
#                 policy_type = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, satp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{satp_cd2:.2f}%", "Payin Category": get_payin_category(satp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error processing TW: {str(e)}")
#         return []

# # ------------------- ELECTRIC/TAXI PROCESSOR -------------------
# def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]):
#                 continue
            
#             city = str(row.iloc[0]).strip()
#             fuel = str(row.iloc[2]).strip() if len(row) > 2 else "Electric"
            
#             cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
#             cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city.upper()), "UNKNOWN")
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
#             if cvod_cd2 is not None:
#                 policy_type = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvod_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{cvod_cd2:.2f}%", "Payin Category": get_payin_category(cvod_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
            
#             if cvtp_cd2 is not None:
#                 policy_type = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvtp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{cvtp_cd2:.2f}%", "Payin Category": get_payin_category(cvtp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error processing electric: {str(e)}")
#         return []

# # ------------------- 4W SATP PROCESSOR -------------------
# def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=0)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.get('Cluster')):
#                 continue
            
#             cluster = str(row['Cluster']).strip()
#             payin = safe_float(row.get('CD2'))
            
#             if payin is None:
#                 continue
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
#             lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR TP"
#             policy_type = override_policy_type if override_policy_type else "TP"
            
#             payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, payin)
            
#             records.append({
#                 "State": state, "Location/Cluster": cluster, "Original Segment": "PVT CAR TP",
#                 "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                 "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                 "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#             })
        
#         return records
#     except Exception as e:
#         print(f"Error processing 4W SATP: {str(e)}")
#         return []

# # ------------------- SCHOOL BUS PROCESSOR -------------------
# def process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(10, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "school bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         data_start_row = table_start_row + 2
#         current_state = ""
        
#         for row_idx in range(data_start_row, len(df)):
#             first_cell = str(df.iloc[row_idx, 0]).strip().lower() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if "seating" in first_cell or "staff" in first_cell or "note" in first_cell:
#                 break
            
#             state_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if state_val and state_val.upper() not in ["", "NAN"]:
#                 current_state = state_val
            
#             rto_cluster = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ""
#             if not rto_cluster:
#                 continue
            
#             contracts = [(2, "In name of School"), (3, "On Contract (Transporter)"), (4, "On Contract (Individual)")]
            
#             for col_idx, contract_type in contracts:
#                 payin = safe_float(df.iloc[row_idx, col_idx])
#                 if payin is None:
#                     continue
                
#                 state_mapped = STATE_MAPPING.get(current_state, current_state.upper())
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "SCHOOL BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(), "Location/Cluster": f"{current_state} - {rto_cluster}",
#                     "Original Segment": f"School Bus - {contract_type}", "Mapped Segment": segment_final,
#                     "LOB": lob_final, "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return []

# # ------------------- STAFF BUS PROCESSOR -------------------
# def process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(30, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "staff bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         data_start_row = table_start_row + 2
        
#         for row_idx in range(data_start_row, len(df)):
#             rto_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if not rto_val or any(kw in rto_val.lower() for kw in ["note", "permit", "validation", "exception", "above grid"]):
#                 continue
            
#             contracts = [(1, "In name of Company"), (2, "Contract (Transport)"), (3, "Contract (Individual)")]
            
#             for col_idx, contract_type in contracts:
#                 cell_value = str(df.iloc[row_idx, col_idx]).strip() if pd.notna(df.iloc[row_idx, col_idx]) else ""
#                 if not cell_value or "decline" in cell_value.lower():
#                     continue
                
#                 payin = None
#                 if "CD2" in cell_value.upper():
#                     for part in cell_value.split("/"):
#                         if "CD2" in part.upper():
#                             cd2_cleaned = part.replace("CD2", "").replace("cd2", "").strip()
#                             payin = safe_float(cd2_cleaned)
#                             break
                
#                 if payin is None:
#                     continue
                
#                 state_mapped = next((v for k, v in STATE_MAPPING.items() if k.upper() in rto_val.upper()), "UNKNOWN")
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "STAFF BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(), "Location/Cluster": rto_val,
#                     "Original Segment": f"Staff Bus - {contract_type}", "Mapped Segment": segment_final,
#                     "LOB": lob_final, "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return []

# # ------------------- COMBINED BUS PROCESSOR -------------------
# def process_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     records.extend(process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     records.extend(process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     return records

# @app.post("/list-worksheets")
# async def list_worksheets(policy_file: UploadFile = File(...)):
#     try:
#         content = await policy_file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         return {"worksheets": xls.sheet_names}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

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
#         xls = pd.ExcelFile(io.BytesIO(content))
        
#         sheets_to_process = [sheet_name] if sheet_name and sheet_name in xls.sheet_names else xls.sheet_names
#         all_records = []
        
#         for sheet in sheets_to_process:
#             sheet_lower = sheet.lower()
#             print(f"Processing: {sheet}")
            
#             if "bus" in sheet_lower:
#                 records = process_bus_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "tw" in sheet_lower or "2w" in sheet_lower:
#                 records = process_tw_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "electric" in sheet_lower or "taxi" in sheet_lower:
#                 records = process_electric_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "satp" in sheet_lower:
#                 records = process_4w_satp_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             else:
#                 records = []
#                 print(f"No processor for sheet: {sheet}")
            
#             all_records.extend(records)
#             print(f"Records from {sheet}: {len(records)}")
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found")
        
#         result_df = pd.DataFrame(all_records)
        
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "unique_segments": len(result_df["Mapped Segment"].unique())
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64
#         }
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)



# =========== Grok====================

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse, StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import io
# import base64
# from typing import Optional, List
# import os

# app = FastAPI(title="Insurance Policy Processor API")

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

# STATE_MAPPING = {
#     "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
#     "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
#     "Tamil Nadu": "TAMIL NADU", "TN": "TAMIL NADU", "Chennai": "TAMIL NADU",
#     "Kerala": "KERALA", "Karnataka": "KARNATAKA", "Bangalore": "KARNATAKA",
#     "Gujarat": "GUJARAT", "Rajasthan": "RAJASTHAN", "Punjab": "PUNJAB",
#     "Uttar Pradesh": "UTTAR PRADESH", "Delhi NCR": "DELHI", "Rest of India": "REST OF INDIA",
#     "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
#     "ROM2": "REST OF MAHARASHTRA", "Good TN": "TAMIL NADU", "Good MP": "MADHYA PRADESH"
# }

# def get_payin_category(payin: float):
#     if payin <= 20:
#         return "Payin Below 20%"
#     elif payin <= 30:
#         return "Payin 21% to 30%"
#     elif payin <= 50:
#         return "Payin 31% to 50%"
#     else:
#         return "Payin Above 50%"

# def safe_float(value):
#     if pd.isna(value):
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ["D", "NA", "", "NAN", "NONE", "DECLINE"]:
#         return None
#     try:
#         num = float(val_str.replace('%', '').strip())
#         if 0 < num < 1:
#             num = num * 100
#         return num
#     except:
#         return None

# def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
#     segment_key = segment.upper()
    
#     if lob == "TW":
#         segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
#     elif lob == "PVT CAR":
#         segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
#     elif lob in ["TAXI", "CV", "BUS", "MISD"]:
#         segment_key = segment.upper()
    
#     payin_category = get_payin_category(payin)
#     matching_rule = None
    
#     for rule in FORMULA_DATA:
#         if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#             if rule["REMARKS"] == payin_category or rule["REMARKS"] == "NIL":
#                 matching_rule = rule
#                 break
    
#     if not matching_rule and payin > 20:
#         for rule in FORMULA_DATA:
#             if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
#                 if (rule["REMARKS"] == "Payin Above 20%" or
#                     (payin > 30 and rule["REMARKS"] == "Payin Above 30%") or
#                     (payin > 40 and rule["REMARKS"] == "Payin Above 40%") or
#                     (payin > 50 and rule["REMARKS"] == "Payin Above 50%")):
#                     matching_rule = rule
#                     break
    
#     if not matching_rule:
#         deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#         return f"-{deduction}%", round(payin - deduction, 2)
    
#     formula = matching_rule["PO"]
    
#     if "%" in formula and "of Payin" in formula:
#         percentage = float(formula.split("%")[0].replace("Less ", ""))
#         if "Less" in formula:
#             payout = round(payin - percentage, 2)
#         else:
#             payout = round(payin * percentage / 100, 2)
#     elif formula.startswith("-"):
#         deduction = float(formula.replace("%", "").replace("-", ""))
#         payout = round(payin - deduction, 2)
#     else:
#         payout = round(payin - 2, 2)
    
#     return formula, payout

# def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
#     if payin == 0:
#         return 0, "0% (No Payin)", "Payin is 0, so Payout is 0"
    
#     formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
#     payin_cat = get_payin_category(payin)
#     rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
#     return payout, formula, rule_explanation

# # ------------------- TWO WHEELER PROCESSOR -------------------
# def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             cluster = str(row.iloc[0]).strip()
#             segmentation = str(row.iloc[1]).strip() if len(row) > 1 else ""
            
#             comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
#             satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None
            
#             state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TW"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TW"
            
#             if comp_cd2 is not None:
#                 policy_type = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, comp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{comp_cd2:.2f}%", "Payin Category": get_payin_category(comp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
            
#             if satp_cd2 is not None:
#                 policy_type = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, satp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{satp_cd2:.2f}%", "Payin Category": get_payin_category(satp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error processing TW: {str(e)}")
#         return []

# # ------------------- ELECTRIC/TAXI PROCESSOR -------------------
# def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.iloc[0]):
#                 continue
            
#             city = str(row.iloc[0]).strip()
#             fuel = str(row.iloc[2]).strip() if len(row) > 2 else "Electric"
            
#             cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
#             cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city.upper()), "UNKNOWN")
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
#             if cvod_cd2 is not None:
#                 policy_type = override_policy_type if override_policy_type else "Comp"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvod_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{cvod_cd2:.2f}%", "Payin Category": get_payin_category(cvod_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
            
#             if cvtp_cd2 is not None:
#                 policy_type = "TP"
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvtp_cd2)
#                 records.append({
#                     "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
#                     "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                     "Payin (CD2)": f"{cvtp_cd2:.2f}%", "Payin Category": get_payin_category(cvtp_cd2),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error processing electric: {str(e)}")
#         return []

# # ------------------- 4W SATP PROCESSOR -------------------
# def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=0)
#         df.columns = df.columns.str.strip()
        
#         for idx, row in df.iterrows():
#             if pd.isna(row.get('Cluster')):
#                 continue
            
#             cluster = str(row['Cluster']).strip()
#             payin = safe_float(row.get('CD2'))
            
#             if payin is None:
#                 continue
            
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
#             lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR TP"
#             policy_type = override_policy_type if override_policy_type else "TP"
            
#             payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, payin)
            
#             records.append({
#                 "State": state, "Location/Cluster": cluster, "Original Segment": "PVT CAR TP",
#                 "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
#                 "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                 "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#             })
        
#         return records
#     except Exception as e:
#         print(f"Error processing 4W SATP: {str(e)}")
#         return []

# # ------------------- SCHOOL BUS PROCESSOR -------------------
# def process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(10, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "school bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         # Find the seating capacity row to skip it
#         seating_row = None
#         for i in range(table_start_row + 1, min(table_start_row + 5, len(df))):
#             cell = str(df.iloc[i, 0]).strip().lower() if pd.notna(df.iloc[i, 0]) else ""
#             if "seating capacity" in cell:
#                 seating_row = i
#                 break
        
#         if seating_row is not None:
#             data_start_row = seating_row + 1
#         else:
#             data_start_row = table_start_row + 2
        
#         current_state = ""
        
#         for row_idx in range(data_start_row, len(df)):
#             first_cell = str(df.iloc[row_idx, 0]).strip().lower() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if "seating" in first_cell or "staff" in first_cell or "note" in first_cell:
#                 break
            
#             state_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if state_val and state_val.upper() not in ["", "NAN"]:
#                 current_state = state_val
            
#             rto_cluster = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ""
#             if not rto_cluster:
#                 continue
            
#             contracts = [(2, "In name of School"), (3, "On Contract (Transporter)"), (4, "On Contract (Individual)")]
            
#             for col_idx, contract_type in contracts:
#                 payin = safe_float(df.iloc[row_idx, col_idx])
#                 if payin is None:
#                     continue
                
#                 state_mapped = STATE_MAPPING.get(current_state, current_state.upper())
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "SCHOOL BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(), "Location/Cluster": f"{current_state} - {rto_cluster}",
#                     "Original Segment": f"School Bus - {contract_type}", "Mapped Segment": segment_final,
#                     "LOB": lob_final, "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return []

# # ------------------- STAFF BUS PROCESSOR -------------------
# def process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         table_start_row = None
#         for i in range(min(30, len(df))):
#             for j in range(len(df.columns)):
#                 cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
#                 if "staff bus" in cell:
#                     table_start_row = i
#                     break
#             if table_start_row is not None:
#                 break
        
#         if table_start_row is None:
#             return []
        
#         data_start_row = table_start_row + 2
        
#         for row_idx in range(data_start_row, len(df)):
#             rto_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
#             if not rto_val or any(kw in rto_val.lower() for kw in ["note", "permit", "validation", "exception", "above grid"]):
#                 continue
            
#             contracts = [(1, "In name of Company"), (2, "Contract (Transport)"), (3, "Contract (Individual)")]
            
#             for col_idx, contract_type in contracts:
#                 cell_value = str(df.iloc[row_idx, col_idx]).strip() if pd.notna(df.iloc[row_idx, col_idx]) else ""
#                 if not cell_value or "decline" in cell_value.lower():
#                     continue
                
#                 payin = None
#                 if "CD2" in cell_value.upper():
#                     for part in cell_value.split("/"):
#                         if "CD2" in part.upper():
#                             cd2_cleaned = part.replace("CD2", "").replace("cd2", "").strip()
#                             payin = safe_float(cd2_cleaned)
#                             break
                
#                 if payin is None:
#                     continue
                
#                 state_mapped = next((v for k, v in STATE_MAPPING.items() if k.upper() in rto_val.upper()), "UNKNOWN")
#                 lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
#                 segment_final = override_segment if override_enabled == "true" and override_segment else "STAFF BUS"
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
#                 records.append({
#                     "State": state_mapped.upper(), "Location/Cluster": rto_val,
#                     "Original Segment": f"Staff Bus - {contract_type}", "Mapped Segment": segment_final,
#                     "LOB": lob_final, "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
#                 })
        
#         return records
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return []

# # ------------------- COMBINED BUS PROCESSOR -------------------
# def process_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     records = []
#     records.extend(process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     records.extend(process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
#     return records

# @app.post("/list-worksheets")
# async def list_worksheets(policy_file: UploadFile = File(...)):
#     try:
#         content = await policy_file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         return {"worksheets": xls.sheet_names}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

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
#         xls = pd.ExcelFile(io.BytesIO(content))
        
#         sheets_to_process = [sheet_name] if sheet_name and sheet_name in xls.sheet_names else xls.sheet_names
#         all_records = []
        
#         for sheet in sheets_to_process:
#             sheet_lower = sheet.lower()
#             print(f"Processing: {sheet}")
            
#             if "bus" in sheet_lower:
#                 records = process_bus_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "tw" in sheet_lower or "2w" in sheet_lower:
#                 records = process_tw_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "electric" in sheet_lower or "taxi" in sheet_lower:
#                 records = process_electric_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             elif "satp" in sheet_lower:
#                 records = process_4w_satp_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
#             else:
#                 records = []
#                 print(f"No processor for sheet: {sheet}")
            
#             all_records.extend(records)
#             print(f"Records from {sheet}: {len(records)}")
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found")
        
#         result_df = pd.DataFrame(all_records)
        
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "unique_segments": len(result_df["Mapped Segment"].unique())
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64
#         }
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import base64
from typing import Optional, List
import os

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

STATE_MAPPING = {
    "DELHI": "DELHI", "Mumbai": "MAHARASHTRA", "Pune": "MAHARASHTRA", "Goa": "GOA",
    "Kolkata": "WEST BENGAL", "Hyderabad": "TELANGANA", "Ahmedabad": "GUJARAT",
    "Tamil Nadu": "TAMIL NADU", "TN": "TAMIL NADU", "Chennai": "TAMIL NADU",
    "Kerala": "KERALA", "Karnataka": "KARNATAKA", "Bangalore": "KARNATAKA",
    "Gujarat": "GUJARAT", "Rajasthan": "RAJASTHAN", "Punjab": "PUNJAB",
    "Uttar Pradesh": "UTTAR PRADESH", "Delhi NCR": "DELHI", "Rest of India": "REST OF INDIA",
    "Good GJ": "GUJARAT", "Bad GJ": "GUJARAT", "ROM1": "REST OF MAHARASHTRA",
    "ROM2": "REST OF MAHARASHTRA", "Good TN": "TAMIL NADU", "Good MP": "MADHYA PRADESH"
}

def get_payin_category(payin: float):
    if payin <= 20:
        return "Payin Below 20%"
    elif payin <= 30:
        return "Payin 21% to 30%"
    elif payin <= 50:
        return "Payin 31% to 50%"
    else:
        return "Payin Above 50%"

def safe_float(value):
    if pd.isna(value):
        return None
    val_str = str(value).strip().upper()
    if val_str in ["D", "NA", "", "NAN", "NONE", "DECLINE"]:
        return None
    try:
        num = float(val_str.replace('%', '').strip())
        if 0 < num < 1:
            num = num * 100
        return num
    except:
        return None

def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
    segment_key = segment.upper()
    
    if lob == "TW":
        segment_key = "TW TP" if policy_type == "TP" else "TW SAOD + COMP"
    elif lob == "PVT CAR":
        segment_key = "PVT CAR TP" if policy_type == "TP" else "PVT CAR COMP + SAOD"
    elif lob in ["TAXI", "CV", "BUS", "MISD"]:
        segment_key = segment.upper()
    
    payin_category = get_payin_category(payin)
    matching_rule = None
    
    for rule in FORMULA_DATA:
        if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
            if rule["REMARKS"] == payin_category or rule["REMARKS"] == "NIL":
                matching_rule = rule
                break
    
    if not matching_rule and payin > 20:
        for rule in FORMULA_DATA:
            if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
                if (rule["REMARKS"] == "Payin Above 20%" or
                    (payin > 30 and rule["REMARKS"] == "Payin Above 30%") or
                    (payin > 40 and rule["REMARKS"] == "Payin Above 40%") or
                    (payin > 50 and rule["REMARKS"] == "Payin Above 50%")):
                    matching_rule = rule
                    break
    
    if not matching_rule:
        deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
        return f"-{deduction}%", round(payin - deduction, 2)
    
    formula = matching_rule["PO"]
    
    if "%" in formula and "of Payin" in formula:
        percentage = float(formula.split("%")[0].replace("Less ", ""))
        if "Less" in formula:
            payout = round(payin - percentage, 2)
        else:
            payout = round(payin * percentage / 100, 2)
    elif formula.startswith("-"):
        deduction = float(formula.replace("%", "").replace("-", ""))
        payout = round(payin - deduction, 2)
    else:
        payout = round(payin - 2, 2)
    
    return formula, payout

def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
    if payin == 0:
        return 0, "0% (No Payin)", "Payin is 0, so Payout is 0"
    
    formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
    payin_cat = get_payin_category(payin)
    rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
    return payout, formula, rule_explanation

# ------------------- TWO WHEELER PROCESSOR -------------------
def process_tw_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        
        for idx, row in df.iterrows():
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
                continue
            
            cluster = str(row.iloc[0]).strip()
            segmentation = str(row.iloc[1]).strip() if len(row) > 1 else ""
            
            comp_cd2 = safe_float(row.iloc[3]) if len(row) > 3 else None
            satp_cd2 = safe_float(row.iloc[4]) if len(row) > 4 else None
            
            state = "MAHARASHTRA" if "MH" in cluster.upper() else "UNKNOWN"
            lob_final = override_lob if override_enabled == "true" and override_lob else "TW"
            segment_final = override_segment if override_enabled == "true" and override_segment else "TW"
            
            if comp_cd2 is not None:
                policy_type = override_policy_type if override_policy_type else "Comp"
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, comp_cd2)
                records.append({
                    "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
                    "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
                    "Payin (CD2)": f"{comp_cd2:.2f}%", "Payin Category": get_payin_category(comp_cd2),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                })
            
            if satp_cd2 is not None:
                policy_type = "TP"
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, satp_cd2)
                records.append({
                    "State": state, "Location/Cluster": cluster, "Original Segment": f"TW {segmentation}",
                    "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
                    "Payin (CD2)": f"{satp_cd2:.2f}%", "Payin Category": get_payin_category(satp_cd2),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                })
        
        return records
    except Exception as e:
        print(f"Error processing TW: {str(e)}")
        return []

# ------------------- ELECTRIC/TAXI PROCESSOR -------------------
def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        
        for idx, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue
            
            city = str(row.iloc[0]).strip()
            fuel = str(row.iloc[2]).strip() if len(row) > 2 else "Electric"
            
            cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
            cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city.upper()), "UNKNOWN")
            lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
            segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
            if cvod_cd2 is not None:
                policy_type = override_policy_type if override_policy_type else "Comp"
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvod_cd2)
                records.append({
                    "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
                    "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
                    "Payin (CD2)": f"{cvod_cd2:.2f}%", "Payin Category": get_payin_category(cvod_cd2),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                })
            
            if cvtp_cd2 is not None:
                policy_type = "TP"
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, cvtp_cd2)
                records.append({
                    "State": state, "Location/Cluster": city, "Original Segment": f"Taxi {fuel}",
                    "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
                    "Payin (CD2)": f"{cvtp_cd2:.2f}%", "Payin Category": get_payin_category(cvtp_cd2),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                })
        
        return records
    except Exception as e:
        print(f"Error processing electric: {str(e)}")
        return []

# ------------------- 4W SATP PROCESSOR -------------------
def process_4w_satp_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=0)
        df.columns = df.columns.str.strip()
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('Cluster')):
                continue
            
            cluster = str(row['Cluster']).strip()
            payin = safe_float(row.get('CD2'))
            
            if payin is None:
                continue
            
            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in cluster.upper()), "UNKNOWN")
            lob_final = override_lob if override_enabled == "true" and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled == "true" and override_segment else "PVT CAR TP"
            policy_type = override_policy_type if override_policy_type else "TP"
            
            payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type, payin)
            
            records.append({
                "State": state, "Location/Cluster": cluster, "Original Segment": "PVT CAR TP",
                "Mapped Segment": segment_final, "LOB": lob_final, "Policy Type": policy_type,
                "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
                "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
            })
        
        return records
    except Exception as e:
        print(f"Error processing 4W SATP: {str(e)}")
        return []

# ------------------- SCHOOL BUS PROCESSOR -------------------
def process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
        table_start_row = None
        for i in range(min(10, len(df))):
            for j in range(len(df.columns)):
                cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
                if "school bus" in cell:
                    table_start_row = i
                    break
            if table_start_row is not None:
                break
        
        if table_start_row is None:
            return []
        
        # Find the seating capacity row to skip it
        seating_row = None
        for i in range(table_start_row + 1, min(table_start_row + 5, len(df))):
            cell = str(df.iloc[i, 0]).strip().lower() if pd.notna(df.iloc[i, 0]) else ""
            if "seating capacity" in cell:
                seating_row = i
                break
        
        if seating_row is not None:
            data_start_row = seating_row + 1
            remarks = str(df.iloc[seating_row, 0]).strip()
        else:
            data_start_row = table_start_row + 2
            remarks = ""
        
        current_state = ""
        
        for row_idx in range(data_start_row, len(df)):
            first_cell = str(df.iloc[row_idx, 0]).strip().lower() if pd.notna(df.iloc[row_idx, 0]) else ""
            if "staff bus" in first_cell or "note" in first_cell:
                break
            if "seating capacity" in first_cell:
                # Handle the 7-seater section if needed
                # For now, since it's a note, we can skip or add with new remarks
                # But according to data, there is no payrate in that row, so continue
                continue
            
            state_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
            if state_val and state_val.upper() not in ["", "NAN"]:
                current_state = state_val
            
            rto_cluster = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ""
            if not rto_cluster:
                continue
            
            contracts = [(2, "In name of School"), (3, "On Contract (Transporter)"), (4, "On Contract (Individual)")]
            
            for col_idx, contract_type in contracts:
                payin = safe_float(df.iloc[row_idx, col_idx])
                if payin is None:
                    continue
                
                state_mapped = next((v for k, v in STATE_MAPPING.items() if k.upper() in current_state.upper()), current_state.upper())
                lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
                segment_final = override_segment if override_enabled == "true" and override_segment else "SCHOOL BUS"
                policy_type_final = override_policy_type if override_policy_type else "Comp"
                
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
                record = {
                    "State": state_mapped.upper(), "Location/Cluster": f"{current_state} - {rto_cluster}",
                    "Original Segment": f"School Bus - {contract_type}", "Mapped Segment": segment_final,
                    "LOB": lob_final, "Policy Type": policy_type_final,
                    "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                }
                if remarks:
                    record["Remarks"] = remarks
                
                records.append(record)
        
        return records
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# ------------------- STAFF BUS PROCESSOR -------------------
def process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
        table_start_row = None
        for i in range(min(30, len(df))):
            for j in range(len(df.columns)):
                cell = str(df.iloc[i, j]).strip().lower() if pd.notna(df.iloc[i, j]) else ""
                if "staff bus" in cell:
                    table_start_row = i
                    break
            if table_start_row is not None:
                break
        
        if table_start_row is None:
            return []
        
        data_start_row = table_start_row + 2
        
        for row_idx in range(data_start_row, len(df)):
            rto_val = str(df.iloc[row_idx, 0]).strip() if pd.notna(df.iloc[row_idx, 0]) else ""
            if not rto_val or any(kw in rto_val.lower() for kw in ["note", "permit", "validation", "exception", "above grid"]):
                continue
            
            contracts = [(1, "In name of Company"), (2, "Contract (Transport)"), (3, "Contract (Individual)")]
            
            for col_idx, contract_type in contracts:
                cell_value = str(df.iloc[row_idx, col_idx]).strip() if pd.notna(df.iloc[row_idx, col_idx]) else ""
                if not cell_value or "decline" in cell_value.lower():
                    continue
                
                payin = None
                if "CD2" in cell_value.upper():
                    for part in cell_value.split("/"):
                        if "CD2" in part.upper():
                            cd2_cleaned = part.replace("CD2", "").replace("cd2", "").strip()
                            payin = safe_float(cd2_cleaned)
                            break
                
                if payin is None:
                    continue
                
                state_mapped = next((v for k, v in STATE_MAPPING.items() if k.upper() in rto_val.upper()), "UNKNOWN")
                lob_final = override_lob if override_enabled == "true" and override_lob else "BUS"
                segment_final = override_segment if override_enabled == "true" and override_segment else "STAFF BUS"
                policy_type_final = override_policy_type if override_policy_type else "Comp"
                
                payout, formula, rule_exp = calculate_payout_with_formula(lob_final, segment_final, policy_type_final, payin)
                
                records.append({
                    "State": state_mapped.upper(), "Location/Cluster": rto_val,
                    "Original Segment": f"Staff Bus - {contract_type}", "Mapped Segment": segment_final,
                    "LOB": lob_final, "Policy Type": policy_type_final,
                    "Payin (CD2)": f"{payin:.2f}%", "Payin Category": get_payin_category(payin),
                    "Calculated Payout": f"{payout:.2f}%", "Formula Used": formula, "Rule Explanation": rule_exp
                })
        
        return records
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# ------------------- COMBINED BUS PROCESSOR -------------------
def process_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    records = []
    records.extend(process_school_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
    records.extend(process_staff_bus_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type))
    return records

@app.post("/list-worksheets")
async def list_worksheets(policy_file: UploadFile = File(...)):
    try:
        content = await policy_file.read()
        xls = pd.ExcelFile(io.BytesIO(content))
        return {"worksheets": xls.sheet_names}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    try:
        content = await policy_file.read()
        xls = pd.ExcelFile(io.BytesIO(content))
        
        sheets_to_process = [sheet_name] if sheet_name and sheet_name in xls.sheet_names else xls.sheet_names
        all_records = []
        
        for sheet in sheets_to_process:
            sheet_lower = sheet.lower()
            print(f"Processing: {sheet}")
            
            if "bus" in sheet_lower:
                records = process_bus_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
            elif "tw" in sheet_lower or "2w" in sheet_lower:
                records = process_tw_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
            elif "electric" in sheet_lower or "taxi" in sheet_lower:
                records = process_electric_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
            elif "satp" in sheet_lower:
                records = process_4w_satp_sheet(content, sheet, override_enabled, override_lob, override_segment, override_policy_type)
            else:
                records = []
                print(f"No processor for sheet: {sheet}")
            
            all_records.extend(records)
            print(f"Records from {sheet}: {len(records)}")
        
        if not all_records:
            raise HTTPException(status_code=400, detail="No valid data found")
        
        result_df = pd.DataFrame(all_records)
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name='Processed')
        excel_buffer.seek(0)
        excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)
        csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
        return {
            "metrics": {
                "company_name": company_name,
                "total_records": len(all_records),
                "unique_segments": len(result_df["Mapped Segment"].unique())
            },
            "calculated_data": all_records,
            "excel_data": excel_b64,
            "csv_data": csv_b64
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
