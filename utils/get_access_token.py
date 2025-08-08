import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_SECRET_KEY")
OAUTH_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

def get_new_paypal_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET not found in .env file.")
        return None
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(
            OAUTH_URL,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token: {e}")
        return None

def update_env_file(file_path, key, value):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    updated = False
    new_lines = []

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"\n{key}={value}\n")

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

    print(f"Successfully updated {key} in {file_path}")

if __name__ == "__main__":
    access_token = get_new_paypal_token()

    if access_token:
        update_env_file(".env", "PAYPAL_ACCESS_TOKEN", access_token)
    else:
        print("Failed to get a new access token. .env file was not updated.")