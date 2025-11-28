from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import base64
import json
import os
from dotenv import load_dotenv
import logging
import pandas as pd
from openai import OpenAI
from pathlib import Path
from typing import Optional
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("⚠️ OPENAI_API_KEY environment variable not set")
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
    raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")

app = FastAPI(title="Insurance Policy Processing System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Formula Data
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

def extract_excel_data(file_bytes: bytes, filename: str) -> list:
    """Extract data from Excel file - hardcoded columns"""
    try:
        # Read Excel file
        df = pd.read_excel(BytesIO(file_bytes))
        
        # Log available columns for debugging
        logger.info(f"Available columns: {df.columns.tolist()}")
        
        # Normalize column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Map columns - handle different possible names
        column_mapping = {
            'state': ['state', 'State', 'STATE'],
            'cluster': ['cluster', 'Cluster', 'CLUSTER', 'location', 'Location'],
            'segment': ['segment', 'Segment', 'SEGMENT'],
            'status': ['status', 'Status', 'STATUS', 'policy_type', 'Policy Type'],
            'cd2': ['cd2', 'CD2', 'payin', 'Payin', 'PAYIN']
        }
        
        # Find actual column names
        actual_columns = {}
        for key, possible_names in column_mapping.items():
            for col in df.columns:
                if col in [name.lower() for name in possible_names]:
                    actual_columns[key] = col
                    break
        
        logger.info(f"Mapped columns: {actual_columns}")
        
        # Extract records
        records = []
        for idx, row in df.iterrows():
            try:
                record = {
                    'state': str(row.get(actual_columns.get('state', ''), 'N/A')),
                    'location': str(row.get(actual_columns.get('cluster', ''), 'N/A')),
                    'segment': str(row.get(actual_columns.get('segment', ''), 'Unknown')),
                    'policy_type': str(row.get(actual_columns.get('status', ''), 'Comp')),
                    'payin': row.get(actual_columns.get('cd2', ''), 0) * 100 if isinstance(row.get(actual_columns.get('cd2', ''), 0), (int, float)) and row.get(actual_columns.get('cd2', ''), 0) < 1 else row.get(actual_columns.get('cd2', ''), 0)
                }
                
                # Skip empty rows
                if record['segment'] != 'Unknown' and record['segment'] != 'nan':
                    records.append(record)
                    
            except Exception as e:
                logger.warning(f"Skipping row {idx}: {str(e)}")
                continue
        
        logger.info(f"✅ Extracted {len(records)} records from Excel")
        return records
        
    except Exception as e:
        logger.error(f"Error reading Excel: {str(e)}")
        raise ValueError(f"Failed to read Excel file: {str(e)}")

def map_segment_to_lob_and_standard(segment_name: str, policy_type: str) -> dict:
    """Use OpenAI to map segment to LOB and standardized segment"""
    
    prompt = f"""
You are mapping insurance segment names to standardized LOB (Line of Business) and Segment names.

Given segment: "{segment_name}"
Given policy type: "{policy_type}"

MAPPING RULES:

TWO WHEELER (LOB = "TW"):
- Keywords: 2W, MC, MCY, SC, Scooter, Two Wheeler, EV 2W
- If policy_type is "Comp" or "1+1" or contains "SAOD" → Segment = "TW SAOD + COMP"
- If policy_type is "TP" or "SATP" → Segment = "TW TP"
- If segment contains "1+5" or "New" or "Fresh" → Segment = "1+5"

PRIVATE CAR (LOB = "PVT CAR"):
- Keywords: Car, PVT CAR, PCI, 4W, Four Wheeler, Private Car
- If policy_type is "Comp" or "1+1" or contains "SAOD" → Segment = "PVT CAR COMP + SAOD"
- If policy_type is "TP" or "SATP" → Segment = "PVT CAR TP"

COMMERCIAL VEHICLE (LOB = "CV"):
- Keywords: CV, GVW, PCV, GCV, Commercial Vehicle, tonnage, 3W Auto
- ALWAYS → Segment = "All GVW & PCV 3W, GCV 3W"

BUS (LOB = "BUS"):
- Keywords: Bus, School Bus, Staff Bus
- If contains "School" → Segment = "SCHOOL BUS"
- Otherwise → Segment = "STAFF BUS"

TAXI (LOB = "TAXI"):
- Keywords: Taxi, Cab
- Segment = "TAXI"

MISCELLANEOUS (LOB = "MISD"):
- Keywords: Tractor, Ambulance, Misd, Miscellaneous
- Segment = "Misd, Tractor"

Return ONLY a JSON object:
{{
  "LOB": "...",
  "SEGMENT": "...",
  "confidence": "high/medium/low"
}}

No explanation, just JSON.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        # Remove markdown if present
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        result = json.loads(result_text)
        logger.info(f"Mapped '{segment_name}' → LOB: {result['LOB']}, Segment: {result['SEGMENT']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in segment mapping: {str(e)}")
        # Fallback to basic logic
        return {"LOB": "UNKNOWN", "SEGMENT": segment_name, "confidence": "low"}

def classify_payin(payin_value):
    """Classify payin into categories"""
    try:
        if isinstance(payin_value, (int, float)):
            payin_float = float(payin_value)
        else:
            payin_clean = str(payin_value).replace('%', '').replace(' ', '').replace('-', '').strip()
            if not payin_clean or payin_clean.upper() == 'N/A':
                return 0.0, "Payin Below 20%"
            payin_float = float(payin_clean)
        
        if payin_float <= 20:
            return payin_float, "Payin Below 20%"
        elif payin_float <= 30:
            return payin_float, "Payin 21% to 30%"
        elif payin_float <= 50:
            return payin_float, "Payin 31% to 50%"
        else:
            return payin_float, "Payin Above 50%"
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse payin: {payin_value}, error: {e}")
        return 0.0, "Payin Below 20%"

def apply_formula(policy_data):
    """Apply formula rules and calculate payouts"""
    if not policy_data:
        return []
    
    calculated_data = []
    
    for record in policy_data:
        try:
            # Get mapped LOB and Segment
            lob = record.get('LOB', 'UNKNOWN')
            segment = record.get('SEGMENT', record.get('segment', ''))
            payin_value = record.get('Payin_Value', 0)
            payin_category = record.get('Payin_Category', '')
            
            # Find matching rule
            matched_rule = None
            for rule in FORMULA_DATA:
                # Match LOB
                if rule["LOB"] != lob:
                    continue
                
                # Match Segment
                rule_segment = rule["SEGMENT"].upper()
                segment_upper = segment.upper()
                
                if rule_segment not in segment_upper and segment_upper not in rule_segment:
                    continue
                
                # Match Payin Category or NIL
                remarks = rule.get("REMARKS", "")
                if remarks == "NIL" or payin_category in remarks:
                    matched_rule = rule
                    break
            
            # Calculate payout
            if matched_rule:
                po_formula = matched_rule["PO"]
                calculated_payout = payin_value
                
                if "90% of Payin" in po_formula:
                    calculated_payout *= 0.9
                elif "88% of Payin" in po_formula:
                    calculated_payout *= 0.88
                elif "Less 2%" in po_formula or "-2%" in po_formula:
                    calculated_payout -= 2
                elif "-3%" in po_formula:
                    calculated_payout -= 3
                elif "-4%" in po_formula:
                    calculated_payout -= 4
                elif "-5%" in po_formula:
                    calculated_payout -= 5
                
                calculated_payout = max(0, calculated_payout)
                formula_used = po_formula
                rule_explanation = f"Match: LOB={lob}, Segment={matched_rule['SEGMENT']}, {remarks}"
            else:
                calculated_payout = payin_value
                formula_used = "No matching rule"
                rule_explanation = f"No rule for LOB={lob}, Segment={segment}"
            
            calculated_data.append({
                'State': record.get('state', 'N/A'),
                'Location/Cluster': record.get('location', 'N/A'),
                'Original Segment': record.get('segment', ''),
                'Mapped Segment': segment,
                'LOB': lob,
                'Policy Type': record.get('policy_type', 'Comp'),
                'Payin (CD2)': f"{payin_value:.2f}%",
                'Payin Category': payin_category,
                'Calculated Payout': f"{calculated_payout:.2f}%",
                'Formula Used': formula_used,
                'Rule Explanation': rule_explanation
            })
            
        except Exception as e:
            logger.error(f"Error processing record {record}: {str(e)}")
            calculated_data.append({
                'State': record.get('state', 'N/A'),
                'Location/Cluster': record.get('location', 'N/A'),
                'Original Segment': record.get('segment', 'Unknown'),
                'Mapped Segment': 'Error',
                'LOB': 'Error',
                'Policy Type': record.get('policy_type', 'Comp'),
                'Payin (CD2)': str(record.get('payin', '0%')),
                'Payin Category': 'Error',
                'Calculated Payout': "Error",
                'Formula Used': "Error",
                'Rule Explanation': f"Error: {str(e)}"
            })
    
    return calculated_data

def process_files(
    file_bytes: bytes, 
    filename: str, 
    company_name: str,
    override_enabled: bool = False,
    override_lob: Optional[str] = None,
    override_segment: Optional[str] = None,
    override_policy_type: Optional[str] = None
):
    """Main processing function"""
    try:
        logger.info(f"🚀 Processing {filename} for {company_name}")
        logger.info(f"Override enabled: {override_enabled}")
        
        # Extract Excel data (hardcoded)
        excel_records = extract_excel_data(file_bytes, filename)
        
        if not excel_records:
            raise ValueError("No data extracted from Excel")
        
        logger.info(f"✅ Extracted {len(excel_records)} records from Excel")
        
        # Map segments using OpenAI OR override
        for record in excel_records:
            if override_enabled and override_lob and override_segment:
                # OVERRIDE MODE
                logger.info(f"🔄 Overriding with LOB={override_lob}, Segment={override_segment}")
                record['LOB'] = override_lob
                record['SEGMENT'] = override_segment
                if override_policy_type:
                    record['policy_type'] = override_policy_type
            else:
                # NORMAL MODE - Use OpenAI mapping
                mapping = map_segment_to_lob_and_standard(
                    record['segment'], 
                    record['policy_type']
                )
                record['LOB'] = mapping['LOB']
                record['SEGMENT'] = mapping['SEGMENT']
            
            # Classify payin
            payin_val, payin_cat = classify_payin(record.get('payin', 0))
            record['Payin_Value'] = payin_val
            record['Payin_Category'] = payin_cat
        
       
        
        # Apply formulas
        calculated_data = apply_formula(excel_records)
        
        if not calculated_data:
            raise ValueError("No data after formula application")
        
        logger.info(f"✅ Calculated {len(calculated_data)} records")
        
        # Create Excel
        df = pd.DataFrame(calculated_data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Policy Data', startrow=2, index=False)
            worksheet = writer.sheets['Policy Data']
            
            # Format headers
            for col_num, value in enumerate(df.columns, 1):
                cell = worksheet.cell(row=3, column=col_num, value=value)
                cell.font = cell.font.copy(bold=True)
            
            # Add title
            title_cell = worksheet.cell(row=1, column=1, value=f"{company_name} - Policy Data Analysis")
            worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
            title_cell.font = title_cell.font.copy(bold=True, size=14)
            title_cell.alignment = title_cell.alignment.copy(horizontal='center')
        
        output.seek(0)
        excel_data_base64 = base64.b64encode(output.read()).decode('utf-8')
        
        # Calculate metrics
        avg_payin = sum([r['Payin_Value'] for r in excel_records]) / len(excel_records)
        formula_summary = {}
        for record in calculated_data:
            formula = record['Formula Used']
            formula_summary[formula] = formula_summary.get(formula, 0) + 1
        
        return {
            "extracted_data": excel_records,
            "calculated_data": calculated_data,
            "excel_data": excel_data_base64,
            "csv_data": df.to_csv(index=False),
            "json_data": json.dumps(calculated_data, indent=2),
            "metrics": {
                "total_records": len(calculated_data),
                "avg_payin": round(avg_payin, 1),
                "unique_segments": len(set([r['Mapped Segment'] for r in calculated_data])),
                "company_name": company_name,
                "formula_summary": formula_summary
            }
        }
    
    except Exception as e:
        logger.error(f"Error in process_files: {str(e)}", exc_info=True)
        raise

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML frontend"""
    return HTMLResponse(content="""
    <html>
        <head><title>Insurance Policy Processor</title></head>
        <body>
            <h1>Insurance Policy Processing System</h1>
            <p>Upload Excel file via POST /process</p>
            <p>Expected columns: STATE, Cluster, Segment, Status, CD1, CD2</p>
        </body>
    </html>
    """)

@app.post("/process")
async def process_policy(
    company_name: str = Form(...), 
    policy_file: UploadFile = File(...),
    override_enabled: str = Form(default="false"),
    override_lob: Optional[str] = Form(default=None),
    override_segment: Optional[str] = Form(default=None),
    override_policy_type: Optional[str] = Form(default=None)
):
    """Process Excel file"""
    try:
        file_bytes = await policy_file.read()
        if not file_bytes:
            return JSONResponse(status_code=400, content={"error": "Empty file"})
        
        # Pass override parameters
        results = process_files(
            file_bytes, 
            policy_file.filename, 
            company_name,
            override_enabled == "true",
            override_lob,
            override_segment,
            override_policy_type
        )
        return JSONResponse(content=results)
        
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Processing failed: {str(e)}"})
    
    
@app.get("/health")
async def health_check():
    """Health check"""
    return JSONResponse(content={"status": "healthy", "message": "Excel processor ready"})

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Excel processor at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
