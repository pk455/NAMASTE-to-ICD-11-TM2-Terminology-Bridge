import json
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime, timezone
import requests
from who_api_client import search_who_api

app = FastAPI(
    title="NAMASTE-ICD11 Integration API",
    description="An API to bridge NAMASTE codes with the ICD-11 module.",
    version="1.0.0"
)

# This line tells FastAPI that a "Bearer" token security system is available.
security_scheme = HTTPBearer()

# --- CORS Middleware ---
# This allows a frontend running on a different address to talk to this backend.
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
FHIR_SERVER_BASE_URL = "http://localhost:8080/fhir"
NAMASTE_CODESYSTEM_URL = "http://sih.gov.in/fhir/namaste-codes"


# --- THIS IS THE MISSING SECURITY FUNCTION ---
# This function acts as the "security guard" for our protected endpoints.
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if credentials.scheme != "Bearer" or credentials.credentials != "SIH2025_DUMMY_ABHA_TOKEN":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing ABHA token",
        )
    # If the token is valid, we return some user info for the audit log.
    return {"userId": "dr_arun_sharma"}


# --- API Endpoints ---

# PASTE THIS NEW, CORRECTED BLOCK IN ITS PLACE

# PASTE THIS ENTIRE BLOCK INTO YOUR main.py FILE

@app.get("/api/search", tags=["Terminology"])
async def search_terms(query: str = Query(..., min_length=3, description="Term to search for")):
    
    # --- THIS IS OUR SPECIAL DIAGNOSTIC MESSAGE ---
    # We added this to prove that the server is running this new code.
    print("\n\n--- RUNNING THE NEW FOOLPROOF SEARCH LOGIC ---\n\n")
    
    namaste_results = []
    
    # This is the foolproof logic that gets the entire CodeSystem
    # and searches it in Python, which is more reliable.
    fhir_get_url = f"{FHIR_SERVER_BASE_URL}/CodeSystem/namaste-cs"
    
    try:
        response = requests.get(fhir_get_url)
        response.raise_for_status()
        
        code_system = response.json()
        
        if code_system and "concept" in code_system:
            for concept in code_system.get("concept", []):
                if query.lower() in concept.get("display", "").lower():
                    namaste_results.append({
                        "source": "NAMASTE",
                        "code": concept.get("code"),
                        "display": concept.get("display")
                    })
    except requests.exceptions.RequestException as e:
        print(f"Could not retrieve CodeSystem from FHIR server: {e}")

    # This part for the WHO API remains the same.
    who_results_raw = search_who_api(query)
    biomedical_results = []
    if who_results_raw and "destinationEntities" in who_results_raw:
        for entity in who_results_raw["destinationEntities"]:
            biomedical_results.append({
                "source": "ICD-11",
                "code": entity.get("id", "").split('/')[-1],
                "display": entity.get("title")
            })
    else:
        print(f"Unexpected response from WHO API: {who_results_raw}")

    return {
        "namaste_ayush_results": namaste_results,
        "icd11_biomedical_results": biomedical_results
    }


@app.get("/api/translate", tags=["Terminology"])
async def translate_code(code: str = Query(..., description="A NAMASTE code, e.g., 'ASU001'")):
    # (This function is correct and remains unchanged)
    translate_url = (
        f"{FHIR_SERVER_BASE_URL}/ConceptMap/namaste-to-icd11-tm2-cm/$translate"
        f"?system={NAMASTE_CODESYSTEM_URL}"
        f"&code={code}"
    )
    try:
        response = requests.get(translate_url)
        response.raise_for_status()
        translation_result = response.json()
        parameters = translation_result.get("parameter", [])
        for param in parameters:
            if param.get("name") == "match":
                for part in param.get("part", []):
                    if part.get("name") == "concept":
                        concept = part.get("valueCoding", {})
                        if concept.get("code"):
                            return {
                                "source_code": code,
                                "target_code": concept.get("code"),
                                "target_display": concept.get("display"),
                                "target_system": concept.get("system")
                            }
        raise HTTPException(status_code=404, detail="Translation found, but no 'concept' part in the FHIR server response.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="ConceptMap or translation not found on the FHIR server.")
        else:
            raise HTTPException(status_code=500, detail=f"FHIR server communication error: {e}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to FHIR server: {e}")


# --- THIS ENDPOINT IS NOW SECURED AND HAS AUDITING ---
@app.post("/api/bundle", tags=["Data Exchange"])
async def upload_encounter_bundle(bundle: Dict[Any, Any], token_payload: dict = Depends(verify_token)):
    if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
        raise HTTPException(status_code=400, detail="Invalid input. Body must be a valid FHIR Bundle.")
    
    # This is the simulated audit log
    user_id = token_payload.get("userId")
    log_timestamp = datetime.now(timezone.utc).isoformat()
    
    print("\n--- AUDIT LOG ---")
    print(f"Timestamp: {log_timestamp}")
    print(f"User:      {user_id}")
    print(f"Action:    Received and validated FHIR Bundle")
    # A safe way to get the Patient ID from the bundle for the log
    patient_entry = next((e for e in bundle.get('entry', []) if e.get('resource', {}).get('resourceType') == 'Patient'), {})
    patient_id = patient_entry.get('resource', {}).get('id', 'Unknown')
    print(f"PatientID: {patient_id}")
    print("-----------------\n")
    
    return {"status": "success", "message": "FHIR Bundle received successfully."}

