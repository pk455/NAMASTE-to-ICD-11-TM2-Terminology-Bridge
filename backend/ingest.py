import csv
import json
import requests

# --- Configuration ---
# This is the address of the HAPI FHIR server running in Docker.
FHIR_SERVER_BASE_URL = "http://localhost:8080/fhir"
# Path to your NAMASTE data file. The '..' goes up one directory from 'backend'.
CSV_FILE_PATH = "../data/namaste.csv"

# Unique identifiers for our FHIR resources. These are important!
NAMASTE_CODESYSTEM_URL = "http://sih.gov.in/fhir/namaste-codes"
ICD11_TM2_CODESYSTEM_URL = "http://id.who.int/icd/entity"


def create_fhir_resources_from_csv():
    """
    Reads the NAMASTE CSV file and generates two FHIR resources:
    1. A CodeSystem for the NAMASTE terms.
    2. A ConceptMap to link NAMASTE codes to ICD-11 TM2 codes.
    """
    print("Reading data from CSV...")
    
    concepts = []
    map_elements = []

    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 1. Add a concept to our CodeSystem resource
                concepts.append({
                    "code": row["NAMASTE_CODE"],
                    "display": row["NAMASTE_TERM"]
                })

                # 2. Add an element to our ConceptMap resource
                map_elements.append({
                    "code": row["NAMASTE_CODE"],
                    "target": [{
                        "code": row["ICD11_TM2_CODE"],
                        "display": row["ICD11_TM2_TERM"],
                        "equivalence": "equivalent" # This indicates a direct mapping
                    }]
                })
    except FileNotFoundError:
        print(f"ERROR: The file was not found at {CSV_FILE_PATH}")
        print("Please make sure the 'data/namaste.csv' file exists.")
        return None, None

    # --- Build the CodeSystem Resource ---
    namaste_code_system = {
        "resourceType": "CodeSystem",
        "id": "namaste-cs", # A unique ID for the resource on the server
        "url": NAMASTE_CODESYSTEM_URL,
        "name": "NAMASTECodes",
        "title": "NAMASTE Terminology Code System",
        "status": "active",
        "content": "complete",
        "concept": concepts
    }

    # --- Build the ConceptMap Resource ---
    namaste_to_icd_concept_map = {
        "resourceType": "ConceptMap",
        "id": "namaste-to-icd11-tm2-cm", # A unique ID for the resource
        "url": "http://sih.gov.in/fhir/namaste-to-icd-conceptmap",
        "name": "NAMASTEToICD11TM2Map",
        "title": "NAMASTE to ICD-11 TM2 Concept Map",
        "status": "active",
        "sourceUri": NAMASTE_CODESYSTEM_URL,
        "targetUri": ICD11_TM2_CODESYSTEM_URL,
        "group": [{
            "source": NAMASTE_CODESYSTEM_URL,
            "target": ICD11_TM2_CODESYSTEM_URL,
            "element": map_elements
        }]
    }

    print("Successfully generated FHIR CodeSystem and ConceptMap resources.")
    return namaste_code_system, namaste_to_icd_concept_map


def post_resource_to_fhir_server(resource_type, resource_json):
    """
    Posts a given FHIR resource (as a Python dictionary) to the FHIR server.
    The server will assign a permanent ID if the resource is new.
    """
    url = f"{FHIR_SERVER_BASE_URL}/{resource_type}/{resource_json['id']}"
    headers = {"Content-Type": "application/fhir+json"}
    
    try:
        print(f"Uploading {resource_type} to {url}...")
        # We use a PUT request to ensure our resource has the specific ID we set.
        response = requests.put(url, data=json.dumps(resource_json), headers=headers)
        
        # Check if the request was successful
        if response.status_code in [200, 201]:
            print(f"✅ Success! {resource_type} uploaded/updated. Status: {response.status_code}")
        else:
            print(f"❌ Error uploading {resource_type}. Status: {response.status_code}")
            print("Response Body:", response.text)
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Could not connect to the FHIR server at {FHIR_SERVER_BASE_URL}")
        print("Please ensure the HAPI FHIR Docker container is running.")


if __name__ == "__main__":
    # This block runs when you execute "python ingest.py"
    code_system, concept_map = create_fhir_resources_from_csv()
    
    if code_system and concept_map:
        post_resource_to_fhir_server("CodeSystem", code_system)
        print("-" * 20)
        post_resource_to_fhir_server("ConceptMap", concept_map)
