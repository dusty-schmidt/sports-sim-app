import requests
import sys
from urllib.parse import urljoin

# Config
API_URL = "http://127.0.0.1:8000"
TOKEN_URL = f"{API_URL}/api/v1/login/access-token"
OPENAPI_URL = f"{API_URL}/api/v1/openapi.json"
USERNAME = "admin@example.com"
PASSWORD = "admin12345"

def get_access_token():
    print(f"Authenticating as {USERNAME}...")
    try:
        response = requests.post(
            TOKEN_URL,
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        if response:
            print(f"Response: {response.text}")
        sys.exit(1)

def get_openapi_schema(token):
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Fetching OpenAPI schema from {OPENAPI_URL}...")
    try:
        response = requests.get(OPENAPI_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch OpenAPI schema: {e}")
        sys.exit(1)

def check_endpoints():
    token = get_access_token()
    schema = get_openapi_schema(token)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    success_count = 0
    fail_count = 0
    skip_count = 0

    print("\n--- Starting Endpoint Checks ---\n")

    paths = schema.get("paths", {})
    for path, methods in paths.items():
        if "get" not in methods:
            continue
            
        # Skip paths with parameters for this simple check
        if "{" in path:
            print(f"[SKIP] {path} (Requires parameters)")
            skip_count += 1
            continue

        full_url = f"{API_URL}/api/v1{path}" # Assuming /api/v1 prefix based on schema usually relative to root or base
        # Correction: OpenAPI paths usually include the full route relative to server. 
        # The schema path starts with /, e.g., /users/. 
        # API_V1 is /api/v1. 
        # Let's check if the schema paths include the prefix or not.  
        # In FastAPI with root_path or prefix, it can vary. 
        # Safer to assume path is as listed in 'paths' keys, which usually includes the prefix if included in the router.
        # But wait, in app/main.py: app.include_router(api_router, prefix=settings.API_V1_STR)
        # So the paths in openapi.json will likely NOT have the prefix if the openapi definition is on the app object? 
        # Actually, FastAPI openapi usually includes the full path from the root of the app.
        # Let's try constructing with just API_URL + path first (checking if path starts with /api/v1)
        
        target_url = urljoin(API_URL, path) # path usually starts with /
        if not path.startswith("/api/v1"):
             target_url = f"{API_URL}/api/v1{path}"

        try:
            r = requests.get(target_url, headers=headers, timeout=5)
            if r.status_code < 400:
                print(f"[PASS] {r.status_code} {path}")
                success_count += 1
            else:
                print(f"[FAIL] {r.status_code} {path}")
                print(f"Response: {r.text}")
                fail_count += 1
        except Exception as e:
            print(f"[ERR ] {path} - {str(e)}")
            fail_count += 1

    print("\n--- Summary ---")
    print(f"Total: {success_count + fail_count + skip_count}")
    print(f"Pass:  {success_count}")
    print(f"Fail:  {fail_count}")
    print(f"Skip:  {skip_count}")

    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    check_endpoints()
