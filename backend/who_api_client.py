import os
import requests

# --- WHO ICD-11 API Configuration ---
# It's best practice to use environment variables for secrets.
# You will need to get these from the WHO ICD-11 API website.
# IMPORTANT: Replace the placeholder values before running!
CLIENT_ID = os.getenv("WHO_API_CLIENT_ID", "8f4c2882-ca3f-4bf1-9b50-14e7cfcae246_48ea1966-bee3-49ca-932b-e2337b0a0f5a")
CLIENT_SECRET = os.getenv("WHO_API_CLIENT_SECRET", "/pEMz4YvncwCnKLLDwSp5G4063Glr8CY6yzIn7AmUzk=")

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
API_BASE_URL = "https://id.who.int"

# This variable will cache the token to avoid re-fetching it on every request.
_cached_token = None

def get_who_api_token():
    """
    Fetches an OAuth 2.0 access token from the WHO ICD-API.
    Caches the token in memory to speed up subsequent requests.
    """
    global _cached_token
    # For this simple example, we don't check for token expiration.
    # In a real app, you would store the expiration time and refresh if needed.
    if _cached_token:
        return _cached_token

    if CLIENT_ID == "YOUR_CLIENT_ID_HERE" or CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE":
        print("⚠️ WARNING: WHO API Client ID and Secret are not set.")
        return None

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'icdapi_access'
    }
    
    try:
        print("Fetching new WHO API token...")
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        
        token_data = response.json()
        _cached_token = token_data.get('access_token')
        print("✅ Successfully obtained WHO API token.")
        return _cached_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching WHO API token: {e}")
        return None

def search_who_api(search_term: str):
    """
    Searches the WHO ICD-11 API for a given term.
    """
    token = get_who_api_token()
    if not token:
        return {"error": "Could not authenticate with WHO API."}

    search_url = f"{API_BASE_URL}/icd/entity/search"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'en', # You can change this to other languages
        'API-Version': 'v2'
    }
    params = {'q': search_term}
    
    try:
        print(f"Searching WHO API for '{search_term}'...")
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching WHO API: {e}")
        return {"error": f"Failed to search WHO API: {e}"}
