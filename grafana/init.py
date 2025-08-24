import os
import json
import requests
from datetime import datetime

from dotenv import load_dotenv

from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent

load_dotenv()

GRAFANA_URL = "http://localhost:3000"
 
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD")

PG_HOST = os.getenv("POSTGRES_HOST")
PG_DB = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT")


def create_service_account_token():
    """Get existing token or create service account with token"""
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    headers = {"Content-Type": "application/json"}
    account_name = "api-account"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    token_name = f"api-token-{timestamp}"
    
    # Get existing service accounts
    sa_response = requests.get(f"{GRAFANA_URL}/api/serviceaccounts/search?perpage=10&page=1&query={account_name}", auth=auth, headers=headers)

    if sa_response.status_code == 200:
        for sa in sa_response.json().get("serviceAccounts", []):
            if sa["name"] == account_name:
                sa_id = sa["id"]
                print(f"✓ Found existing service account (ID: {sa_id})")
                
                # Get existing tokens
                tokens_response = requests.get(f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens", auth=auth, headers=headers)
                
                if tokens_response.status_code == 200 and tokens_response.json():
                    existing_token = tokens_response.json()[0]
                    print(f"✓ Using existing token: {existing_token['name']}")
                   
                token_data = {"name": token_name}
                token_response = requests.post(f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens", json=token_data, auth=auth, headers=headers)
            
                if token_response.status_code == 200:
                    print("✓ New token created for existing service account")
                    return token_response.json()["key"]
    
    # Create new service account
    sa_data = {"name": account_name, "role": "Admin"}
    sa_create_response = requests.post(f"{GRAFANA_URL}/api/serviceaccounts", json=sa_data, auth=auth, headers=headers)
    
    if sa_create_response.status_code != 201:
        raise Exception(f"Failed to create service account: {sa_create_response.text}")
    
    sa_id = sa_create_response.json()["id"]
    print(f"✓ Created new service account (ID: {sa_id})")
    
    # Create token for new service account
    token_data = {"name": token_name}
    token_response = requests.post(f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens", json=token_data, auth=auth, headers=headers)
    
    if token_response.status_code == 200:
        print("✓ Token created for new service account")
        return token_response.json()["key"]
    
    raise Exception(f"Failed to create token: {token_response.text}")
   


def create_datasource(api_token):
    """Create PostgreSQL datasource"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    datasource = {
        "name": "PostgreSQL",
        "type": "postgres",
        "url": PG_HOST,
        "access": "proxy",
        "user": PG_USER,
        "database": PG_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {"sslmode": "disable"},
        "secureJsonData": {"password": PG_PASSWORD}
    }
    
    response = requests.post(f"{GRAFANA_URL}/api/datasources", json=datasource, headers=headers)
    
    if response.status_code in [200, 201]:
        print("✓ Datasource created")
        return response.json().get("uid")
    else:
        raise Exception(f"Failed to create datasource: {response.text}")


def create_dashboard(token, datasource_uid):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    dashboard_file = BASE_PATH / "dashboard.json"

    try:
        with open(dashboard_file, "r") as f:
            dashboard_json = json.load(f)
    except FileNotFoundError:
        print(f"Error: {dashboard_file} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding {dashboard_file}: {str(e)}")
        return

    print("Dashboard JSON loaded successfully.")

    # Update datasource UID in the dashboard JSON
    panels_updated = 0
    for panel in dashboard_json.get("panels", []):
        if isinstance(panel.get("datasource"), dict):
            panel["datasource"]["uid"] = datasource_uid
            panels_updated += 1
        elif isinstance(panel.get("targets"), list):
            for target in panel["targets"]:
                if isinstance(target.get("datasource"), dict):
                    target["datasource"]["uid"] = datasource_uid
                    panels_updated += 1

    print(f"Updated datasource UID for {panels_updated} panels/targets.")

    # Remove keys that shouldn't be included when creating a new dashboard
    dashboard_json.pop("id", None)
    dashboard_json.pop("uid", None)
    dashboard_json.pop("version", None)

    # Prepare the payload
    dashboard_payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": "Updated by Python script",
    }

    print("Sending dashboard creation request...")

    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=dashboard_payload
    )

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        print("Dashboard created successfully")
        return response.json().get("uid")
    else:
        print(f"Failed to create dashboard: {response.text}")
        return None


def main():
    token = create_service_account_token()
    if not token:
        print("API key creation failed")
        return

    datasource_uid = create_datasource(token)
    if not datasource_uid:
        print("Datasource creation failed")

    create_dashboard(token, datasource_uid)


if __name__ == "__main__":
    main()
