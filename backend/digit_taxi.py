# # main.py
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

# def get_formula(payin: float):
#     if payin <= 20:
#         return "-2%"
#     elif payin <= 30:
#         return "-3%"
#     elif payin <= 50:
#         return "-4%"
#     else:
#         return "-5%"

# def calculate_payout(payin: float):
#     deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#     return round(payin - deduction, 2)

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
#     "BAD KA": "KARNATAKA", "HR Ref": "HARYANA"
# }

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

# # ------------------- MAIN PROCESS ENDPOINT -------------------
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

#         # Determine sheet to process
#         if sheet_name and sheet_name in xls.sheet_names:
#             sheets_to_process = [sheet_name]
#         else:
#             sheets_to_process = xls.sheet_names[:1]  # default first sheet

#         all_records = []

#         for sheet in sheets_to_process:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=None)

#             records = []
#             prev_location = ""

#             for idx, row in df.iterrows():
#                 if idx < 5:
#                     continue

#                 location = str(row.iloc[0]) if pd.notna(row.iloc[0]) else prev_location
#                 prev_location = location

#                 fuel = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#                 make = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else ""
#                 remarks = str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else ""
#                 seating = str(row.iloc[4]) if len(row) > 4 and pd.notna(row.iloc[4]) else ""

#                 cols = row.values

#                 combinations = [
#                     ("Without Add On Cover", "<=1000 CC", "SAOD", 5, 6),
#                     ("Without Add On Cover", ">1000 CC",  "SAOD", 7, 8),
#                     ("With Add On Cover",    "<=1000 CC", "SAOD", 9, 10),
#                     ("With Add On Cover",    ">1000 CC",  "SAOD", 11, 12),
#                     ("", "<=1000 CC", "TP", None, 13),
#                     ("", ">1000 CC",  "TP", None, 14),
#                 ]

#                 for addon, cc, ptype, cd1_idx, cd2_idx in combinations:
#                     if len(cols) <= max(cd1_idx or 0, cd2_idx or 0):
#                         continue
#                     cd2_val = cols[cd2_idx] if cd2_idx < len(cols) else None
#                     try:
#                         payin = float(str(cd2_val).replace('%', '').strip()) if str(cd2_val).strip() not in ["D", "NA", "", "nan"] else None
#                     except:
#                         payin = None

#                     if payin is None:
#                         continue

#                     segment_desc = f"Taxi {fuel} {make} {remarks}".strip()
#                     if seating:
#                         segment_desc += f" Seating:{seating}"
#                     if cc and ptype == "SAOD":
#                         segment_desc += f" {cc}"
#                     if addon:
#                         segment_desc += f" {addon}"

#                     state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")

#                     lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#                     segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
#                     policy_type_final = override_policy_type if override_policy_type else (ptype if ptype == "TP" else "Comp")

#                     records.append({
#                         "State": state.upper(),
#                         "Location/Cluster": location,
#                         "Original Segment": segment_desc.strip(),
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": policy_type_final,
#                         "Payin (CD2)": f"{payin:.2f}%",
#                         "Payin Category": get_payin_category(payin),
#                         "Calculated Payout": f"{calculate_payout(payin):.2f}%",
#                         "Formula Used": get_formula(payin),
#                         "Rule Explanation": f"Match: LOB={lob_final}, Segment={segment_final}, {get_payin_category(payin)}"
#                     })

#             # Electric sheet special handling
#             if "Electric" in sheet:
#                 df_e = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=2)
#                 for _, row in df_e.iterrows():
#                     location = str(row.get('City/Cluster', ''))
#                     cd2 = row.get('CD2')
#                     try:
#                         payin = float(str(cd2).replace('%', '')) if str(cd2).strip() not in ["D", "NA", ""] else None
#                     except:
#                         payin = None
#                     if payin is None:
#                         continue

#                     state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")
#                     lob_final = override_lob if override_enabled == "true" else "TAXI"
#                     segment_final = override_segment if override_enabled == "true" else "TAXI"

#                     for ptype in ["Comp", "TP"]:
#                         records.append({
#                             "State": state.upper(),
#                             "Location/Cluster": location,
#                             "Original Segment": "Taxi Electric All Seating:5",
#                             "Mapped Segment": segment_final,
#                             "LOB": lob_final,
#                             "Policy Type": ptype,
#                             "Payin (CD2)": f"{payin:.2f}%",
#                             "Payin Category": get_payin_category(payin),
#                             "Calculated Payout": f"{calculate_payout(payin):.2f}%",
#                             "Formula Used": get_formula(payin),
#                             "Rule Explanation": f"Match: LOB={lob_final}, Segment={segment_final}, {get_payin_category(payin)}"
#                         })

#             all_records.extend(records)

#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found in the sheet")

#         result_df = pd.DataFrame(all_records)

#         # Metrics
#         payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records]
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0

#         formula_summary = {}
#         for r in all_records:
#             f = r["Formula Used"]
#             formula_summary[f] = formula_summary.get(f, 0) + 1

#         # Generate downloads
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()

#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()

#         json_str = result_df.to_json(orient="records")

#         return {
#             "metrics": {
#                 "company_name": company_name,
#                 "total_records": len(all_records),
#                 "avg_payin": f"{avg_payin:.2f}",
#                 "unique_segments": len(result_df["Mapped Segment"].unique()),
#                 "formula_summary": formula_summary
#             },
#             "calculated_data": all_records,
#             "excel_data": excel_b64,
#             "csv_data": csv_b64,
#             "json_data": json_str
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ------------------- RUN -------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# # main.py
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

# def get_formula(payin: float):
#     if payin <= 20:
#         return "-2%"
#     elif payin <= 30:
#         return "-3%"
#     elif payin <= 50:
#         return "-4%"
#     else:
#         return "-5%"

# def calculate_payout(payin: float):
#     deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
#     return round(payin - deduction, 2)

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
#         return float(val_str.replace('%', '').strip())
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

# # ------------------- ELECTRIC SHEET PROCESSOR -------------------
# def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     """
#     Process Electric vehicle sheet with structure:
#     City/Cluster | RTO Remarks | Fuel | Make | Seating Capacity | CVOD CD1 | CVOD CD2 | CVTP CD2
#     """
#     records = []
    
#     try:
#         # Read the sheet - header is in row 1 (index 0)
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        
#         # Clean column names
#         df.columns = df.columns.str.strip()
        
#         print(f"Electric sheet columns: {df.columns.tolist()}")
        
#         for idx, row in df.iterrows():
#             # Skip empty rows
#             if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
#                 continue
            
#             # Extract basic info
#             city_cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
#             rto_remarks = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
#             fuel = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Electric"
#             make = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else "All"
#             seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "5"
            
#             # Map state
#             state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city_cluster.upper()), "UNKNOWN")
             
#             # CVOD section (columns 5, 6)
#             cvod_cd1 = safe_float(row.iloc[5]) if len(row) > 5 else None
#             cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
            
#             # CVTP section (column 7)
#             cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
#             # Build segment description
#             segment_desc = f"Taxi {fuel} {make}"
#             if rto_remarks:
#                 segment_desc += f" {rto_remarks}"
#             segment_desc += f" Seating:{seating}"
            
#             lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
#             segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
#             # Process CVOD (Comprehensive)
#             if cvod_cd2 is not None:
#                 policy_type_final = override_policy_type if override_policy_type else "Comp"
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvod_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvod_cd2),
#                     "Calculated Payout": f"{calculate_payout(cvod_cd2):.2f}%",
#                     "Formula Used": get_formula(cvod_cd2),
#                     "Rule Explanation": f"Match: LOB={lob_final}, Segment={segment_final}, {get_payin_category(cvod_cd2)}"
#                 })
            
#             # Process CVTP (Third Party)
#             if cvtp_cd2 is not None:
#                 policy_type_final = "TP"
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": city_cluster,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{cvtp_cd2:.2f}%",
#                     "Payin Category": get_payin_category(cvtp_cd2),
#                     "Calculated Payout": f"{calculate_payout(cvtp_cd2):.2f}%",
#                     "Formula Used": get_formula(cvtp_cd2),
#                     "Rule Explanation": f"Match: LOB={lob_final}, Segment={segment_final}, {get_payin_category(cvtp_cd2)}"
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing electric sheet: {str(e)}")
#         return []

# # ------------------- REGULAR SHEET PROCESSOR -------------------
# def process_regular_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
#     """
#     Process regular sheets with CVOD/CVTP structure with sub-headers
#     """
#     records = []
    
#     try:
#         df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
#         prev_location = ""
        
#         for idx, row in df.iterrows():
#             # Skip header rows
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
            
#             # Define all combinations for CVOD and CVTP
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
                
#                 # Build segment description
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
                
#                 records.append({
#                     "State": state.upper(),
#                     "Location/Cluster": location,
#                     "Original Segment": segment_desc.strip(),
#                     "Mapped Segment": segment_final,
#                     "LOB": lob_final,
#                     "Policy Type": policy_type_final,
#                     "Payin (CD2)": f"{payin:.2f}%",
#                     "Payin Category": get_payin_category(payin),
#                     "Calculated Payout": f"{calculate_payout(payin):.2f}%",
#                     "Formula Used": get_formula(payin),
#                     "Rule Explanation": f"Match: LOB={lob_final}, Segment={segment_final}, {get_payin_category(payin)}"
#                 })
        
#         return records
        
#     except Exception as e:
#         print(f"Error processing regular sheet: {str(e)}")
#         return []

# # ------------------- MAIN PROCESS ENDPOINT -------------------
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
        
#         # Determine sheets to process
#         if sheet_name and sheet_name in xls.sheet_names:
#             sheets_to_process = [sheet_name]
#         else:
#             sheets_to_process = xls.sheet_names  # Process all sheets
        
#         all_records = []
        
#         for sheet in sheets_to_process:
#             print(f"Processing sheet: {sheet}")
            
#             # Detect if it's an Electric sheet
#             if "electric" in sheet.lower():
#                 records = process_electric_sheet(
#                     content, sheet, override_enabled, 
#                     override_lob, override_segment, override_policy_type
#                 )
#             else:
#                 records = process_regular_sheet(
#                     content, sheet, override_enabled,
#                     override_lob, override_segment, override_policy_type
#                 )
            
#             all_records.extend(records)
#             print(f"Sheet '{sheet}' produced {len(records)} records")
        
#         if not all_records:
#             raise HTTPException(status_code=400, detail="No valid data found in any sheet")
        
#         result_df = pd.DataFrame(all_records)
        
#         # Metrics
#         payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records]
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        
#         formula_summary = {}
#         for r in all_records:
#             f = r["Formula Used"]
#             formula_summary[f] = formula_summary.get(f, 0) + 1
        
#         # Generate downloads
#         excel_buffer = io.BytesIO()
#         with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
#             result_df.to_excel(writer, index=False, sheet_name='Processed')
#         excel_buffer.seek(0)
#         excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
#         csv_buffer = io.StringIO()
#         result_df.to_csv(csv_buffer, index=False)
#         csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
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


# # ------------------- RUN -------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import base64
from typing import Optional, List
import os

app = FastAPI(title="Insurance Policy Processor API")

# Allow frontend (localhost:5500 or any)
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
    
    # TW SAOD + COMP rules
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TW", "SEGMENT": "TW SAOD + COMP", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
    # TW TP rules
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TW", "SEGMENT": "TW TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
    
    # PVT CAR rules
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "-3%", "REMARKS": "Payin Above 20%"},
    
    # CV rules
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "CV", "SEGMENT": "All GVW & PCV 3W, GCV 3W", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
    # BUS rules
    {"LOB": "BUS", "SEGMENT": "SCHOOL BUS", "PO": "Less 2% of Payin", "REMARKS": "NIL"},
    {"LOB": "BUS", "SEGMENT": "STAFF BUS", "PO": "88% of Payin", "REMARKS": "NIL"},
    
    # TAXI rules
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-2%", "REMARKS": "Payin Below 20%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-3%", "REMARKS": "Payin 21% to 30%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-4%", "REMARKS": "Payin 31% to 50%"},
    {"LOB": "TAXI", "SEGMENT": "TAXI", "PO": "-5%", "REMARKS": "Payin Above 50%"},
    
    # MISD rules
    {"LOB": "MISD", "SEGMENT": "Misd, Tractor", "PO": "88% of Payin", "REMARKS": "NIL"}
]

# ------------------- PAYOUT LOGIC -------------------
def get_payin_category(payin: float):
    if payin <= 20:
        return "Payin Below 20%"
    elif payin <= 30:
        return "Payin 21% to 30%"
    elif payin <= 50:
        return "Payin 31% to 50%"
    else:
        return "Payin Above 50%"

def get_formula_from_data(lob: str, segment: str, policy_type: str, payin: float):
    """
    Look up formula from FORMULA_DATA based on LOB, segment, policy type and payin
    Returns: (formula_string, payout_value)
    """
    # Determine the segment key to look up
    segment_key = segment.upper()
    
    # For TW, map policy type to segment
    if lob == "TW":
        if policy_type == "TP":
            segment_key = "TW TP"
        else:  # Comp/SAOD
            segment_key = "TW SAOD + COMP"
    
    # For PVT CAR
    elif lob == "PVT CAR":
        if policy_type == "TP":
            segment_key = "PVT CAR TP"
        else:
            segment_key = "PVT CAR COMP + SAOD"
    
    # For TAXI, CV - use the segment as is
    elif lob in ["TAXI", "CV", "BUS", "MISD"]:
        segment_key = segment.upper()
    
    # Get payin category
    payin_category = get_payin_category(payin)
    
    # Find matching rule - try exact match first, then fallback to broader categories
    matching_rule = None
    for rule in FORMULA_DATA:
        if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
            # Exact match
            if rule["REMARKS"] == payin_category:
                matching_rule = rule
                break
            # For rules without payin conditions (NIL)
            elif rule["REMARKS"] == "NIL":
                matching_rule = rule
    
    # If no exact match found, try broader categories
    if not matching_rule and payin > 20:
        for rule in FORMULA_DATA:
            if rule["LOB"] == lob and rule["SEGMENT"] == segment_key:
                # Check for "Payin Above 20%" which covers 21% and above
                if rule["REMARKS"] == "Payin Above 20%":
                    matching_rule = rule
                    break
                # Check for "Payin Above 30%" 
                elif payin > 30 and rule["REMARKS"] == "Payin Above 30%":
                    matching_rule = rule
                    break
                # Check for "Payin Above 40%"
                elif payin > 40 and rule["REMARKS"] == "Payin Above 40%":
                    matching_rule = rule
                    break
                # Check for "Payin Above 50%"
                elif payin > 50 and rule["REMARKS"] == "Payin Above 50%":
                    matching_rule = rule
                    break
    
    if not matching_rule:
        # Fallback to old logic
        print(f"No matching rule found for LOB={lob}, Segment={segment_key}, Payin={payin}")
        deduction = 2 if payin <= 20 else 3 if payin <= 30 else 4 if payin <= 50 else 5
        return f"-{deduction}%", round(payin - deduction, 2)
    
    # Parse the formula
    formula = matching_rule["PO"]
    
    if "%" in formula and "of Payin" in formula:
        # Format: "90% of Payin" or "88% of Payin"
        percentage = float(formula.split("%")[0])
        payout = round(payin * percentage / 100, 2)
        return formula, payout
    elif formula.startswith("-") and "%" in formula:
        # Format: "-2%", "-3%", etc.
        deduction = float(formula.replace("%", "").replace("-", ""))
        payout = round(payin - deduction, 2)
        return formula, payout
    elif formula.startswith("Less") and "%" in formula:
        # Format: "Less 2% of Payin"
        deduction = float(formula.split()[1].replace("%", ""))
        payout = round(payin - deduction, 2)
        return formula, payout
    else:
        # Unknown format, use fallback
        deduction = 2
        return f"-{deduction}%", round(payin - deduction, 2)

def calculate_payout_with_formula(lob: str, segment: str, policy_type: str, payin: float):
    """
    Calculate payout using formula data
    Returns: (payout, formula_used, rule_explanation)
    """
    # If payin is 0, payout is also 0
    if payin == 0:
        return 0, "0% (No Payin)", f"Payin is 0, so Payout is 0"
    
    formula, payout = get_formula_from_data(lob, segment, policy_type, payin)
    payin_cat = get_payin_category(payin)
    
    rule_explanation = f"Match: LOB={lob}, Segment={segment}, Policy={policy_type}, {payin_cat}"
    
    return payout, formula, rule_explanation

# ------------------- STATE MAPPING -------------------
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
    """Safely convert value to float, handling 'D', 'NA', empty strings, etc."""
    if pd.isna(value):
        return None
    val_str = str(value).strip().upper()
    if val_str in ["D", "NA", "", "NAN", "NONE"]:
        return None
    try:
        num = float(val_str.replace('%', '').strip())
        if 0 < num < 1:
            num = num * 100
        return num
    except:
        return None

# ------------------- LIST WORKSHEETS -------------------
@app.post("/list-worksheets")
async def list_worksheets(policy_file: UploadFile = File(...)):
    try:
        content = await policy_file.read()
        xls = pd.ExcelFile(io.BytesIO(content))
        worksheets = xls.sheet_names
        return {"worksheets": worksheets}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------- ELECTRIC SHEET PROCESSOR -------------------
def process_electric_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    """
    Process Electric vehicle sheet with structure:
    City/Cluster | RTO Remarks | Fuel | Make | Seating Capacity | CVOD CD1 | CVOD CD2 | CVTP CD2
    """
    records = []
    
    try:
        # Read the sheet - header is in row 1 (index 0)
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"Electric sheet columns: {df.columns.tolist()}")
        
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
                continue
            
            # Extract basic info
            city_cluster = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            rto_remarks = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            fuel = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Electric"
            make = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else "All"
            seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "5"
            
            # Map state
            state = next((v for k, v in STATE_MAPPING.items() if k.upper() in city_cluster.upper()), "UNKNOWN")
             
            # CVOD section (columns 5, 6)
            cvod_cd1 = safe_float(row.iloc[5]) if len(row) > 5 else None
            cvod_cd2 = safe_float(row.iloc[6]) if len(row) > 6 else None
            
            # CVTP section (column 7)
            cvtp_cd2 = safe_float(row.iloc[7]) if len(row) > 7 else None
            
            # Build segment description
            segment_desc = f"Taxi {fuel} {make}"
            if rto_remarks:
                segment_desc += f" {rto_remarks}"
            segment_desc += f" Seating:{seating}"
            
            lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
            segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
            
            # Process CVOD (Comprehensive)
            if cvod_cd2 is not None:
                policy_type_final = override_policy_type if override_policy_type else "Comp"
                payout, formula, rule_exp = calculate_payout_with_formula(
                    lob_final, segment_final, policy_type_final, cvod_cd2
                )
                
                records.append({
                    "State": state.upper(),
                    "Location/Cluster": city_cluster,
                    "Original Segment": segment_desc.strip(),
                    "Mapped Segment": segment_final,
                    "LOB": lob_final,
                    "Policy Type": policy_type_final,
                    "Payin (CD2)": f"{cvod_cd2:.2f}%",
                    "Payin Category": get_payin_category(cvod_cd2),
                    "Calculated Payout": f"{payout:.2f}%",
                    "Formula Used": formula,
                    "Rule Explanation": rule_exp
                })
            
            # Process CVTP (Third Party)
            if cvtp_cd2 is not None:
                policy_type_final = "TP"
                payout, formula, rule_exp = calculate_payout_with_formula(
                    lob_final, segment_final, policy_type_final, cvtp_cd2
                )
                
                records.append({
                    "State": state.upper(),
                    "Location/Cluster": city_cluster,
                    "Original Segment": segment_desc.strip(),
                    "Mapped Segment": segment_final,
                    "LOB": lob_final,
                    "Policy Type": policy_type_final,
                    "Payin (CD2)": f"{cvtp_cd2:.2f}%",
                    "Payin Category": get_payin_category(cvtp_cd2),
                    "Calculated Payout": f"{payout:.2f}%",
                    "Formula Used": formula,
                    "Rule Explanation": rule_exp
                })
        
        return records
        
    except Exception as e:
        print(f"Error processing electric sheet: {str(e)}")
        return []

# ------------------- REGULAR SHEET PROCESSOR -------------------
def process_regular_sheet(content, sheet_name, override_enabled, override_lob, override_segment, override_policy_type):
    """
    Process regular sheets with CVOD/CVTP structure with sub-headers
    """
    records = []
    
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        
        prev_location = ""
        
        for idx, row in df.iterrows():
            # Skip header rows
            if idx < 5:
                continue
            
            location = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() else prev_location
            if location:
                prev_location = location
            
            fuel = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            make = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
            remarks = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
            seating = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            
            cols = row.values
            
            # Define all combinations for CVOD and CVTP
            combinations = [
                ("Without Add On Cover", "<=1000 CC", "SAOD", 5, 6),
                ("Without Add On Cover", ">1000 CC",  "SAOD", 7, 8),
                ("With Add On Cover",    "<=1000 CC", "SAOD", 9, 10),
                ("With Add On Cover",    ">1000 CC",  "SAOD", 11, 12),
                ("", "<=1000 CC", "TP", None, 13),
                ("", ">1000 CC",  "TP", None, 14),
            ]
            
            for addon, cc, ptype, cd1_idx, cd2_idx in combinations:
                if len(cols) <= cd2_idx:
                    continue
                
                cd2_val = cols[cd2_idx] if cd2_idx < len(cols) else None
                payin = safe_float(cd2_val)
                
                if payin is None:
                    continue
                
                # Build segment description
                segment_desc = f"Taxi {fuel} {make} {remarks}".strip()
                if seating:
                    segment_desc += f" Seating:{seating}"
                if cc and ptype == "SAOD":
                    segment_desc += f" {cc}"
                if addon:
                    segment_desc += f" {addon}"
                
                state = next((v for k, v in STATE_MAPPING.items() if k.upper() in location.upper()), "UNKNOWN")
                
                lob_final = override_lob if override_enabled == "true" and override_lob else "TAXI"
                segment_final = override_segment if override_enabled == "true" and override_segment else "TAXI"
                policy_type_final = override_policy_type if override_policy_type else ("TP" if ptype == "TP" else "Comp")
                
                payout, formula, rule_exp = calculate_payout_with_formula(
                    lob_final, segment_final, policy_type_final, payin
                )
                
                records.append({
                    "State": state.upper(),
                    "Location/Cluster": location,
                    "Original Segment": segment_desc.strip(),
                    "Mapped Segment": segment_final,
                    "LOB": lob_final,
                    "Policy Type": policy_type_final,
                    "Payin (CD2)": f"{payin:.2f}%",
                    "Payin Category": get_payin_category(payin),
                    "Calculated Payout": f"{payout:.2f}%",
                    "Formula Used": formula,
                    "Rule Explanation": rule_exp
                })
        
        return records
        
    except Exception as e:
        print(f"Error processing regular sheet: {str(e)}")
        return []

# ------------------- MAIN PROCESS ENDPOINT -------------------
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
        
        # Determine sheets to process
        if sheet_name and sheet_name in xls.sheet_names:
            sheets_to_process = [sheet_name]
        else:
            sheets_to_process = xls.sheet_names  # Process all sheets
        
        all_records = []
        
        for sheet in sheets_to_process:
            print(f"Processing sheet: {sheet}")
            
            # Detect if it's an Electric sheet
            if "electric" in sheet.lower():
                records = process_electric_sheet(
                    content, sheet, override_enabled, 
                    override_lob, override_segment, override_policy_type
                )
            else:
                records = process_regular_sheet(
                    content, sheet, override_enabled,
                    override_lob, override_segment, override_policy_type
                )
            
            all_records.extend(records)
            print(f"Sheet '{sheet}' produced {len(records)} records")
        
        if not all_records:
            raise HTTPException(status_code=400, detail="No valid data found in any sheet")
        
        result_df = pd.DataFrame(all_records)
        
        # Metrics
        payins = [float(r["Payin (CD2)"].replace('%', '')) for r in all_records]
        avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        
        formula_summary = {}
        for r in all_records:
            f = r["Formula Used"]
            formula_summary[f] = formula_summary.get(f, 0) + 1
        
        # Generate downloads
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name='Processed')
        excel_buffer.seek(0)
        excel_b64 = base64.b64encode(excel_buffer.read()).decode()
        
        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)
        csv_b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        
        json_str = result_df.to_json(orient="records")
        
        return {
            "metrics": {
                "company_name": company_name,
                "total_records": len(all_records),
                "avg_payin": f"{avg_payin:.2f}",
                "unique_segments": len(result_df["Mapped Segment"].unique()),
                "formula_summary": formula_summary,
                "sheets_processed": len(sheets_to_process)
            },
            "calculated_data": all_records,
            "excel_data": excel_b64,
            "csv_data": csv_b64,
            "json_data": json_str
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- RUN -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)