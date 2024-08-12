import os
import requests
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1ALLSe0BUI-dQXUwrhu5u6wlWJNCgzxS2qYmi4fwD9bU'  # Replace with your spreadsheet ID
RANGE_NAME = 'Sheet1!D4:D'  # Adjust the range name as necessary
UPDATE_RANGE_NAME = 'Sheet1!O4:O'  # Adjust the range name as necessary

# Google Sheets API setup
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# ORCID API credentials
client_id = 'APP-KAFJG5JRLIOZMAWX'
client_secret = '438a93cb-3013-4d46-91df-6abf26ca541b'
token_url = 'https://orcid.org/oauth/token'

# Function to get access token
def get_access_token():
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': '/read-public'
    }
    response = requests.post(token_url, data=payload)
    response_data = response.json()
    return response_data['access_token']

# Function to get works count from ORCID ID
def get_works_count(orcid_id, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    api_url = f'https://pub.orcid.org/v3.0/{orcid_id}/works'
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        works_data = response.json()
        return len(works_data['group'])
    else:
        return None

# Function to get ORCID IDs from Google Sheet
def get_orcid_ids(service, spreadsheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return [row[0] for row in values if row]

# Function to update Google Sheet with works count
def update_sheet_with_counts(service, spreadsheet_id, range_name, counts):
    values = [[count] for count in counts]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    return result

# Main script
def main():
    access_token = get_access_token()
    orcid_ids = get_orcid_ids(service, SPREADSHEET_ID, RANGE_NAME)
    
    works_counts = []
    for orcid_url in orcid_ids:
        orcid_id = orcid_url.split('/')[-1]  # Extract ORCID ID from URL
        works_count = get_works_count(orcid_id, access_token)
        works_counts.append(works_count if works_count is not None else 'Error')
    
    update_result = update_sheet_with_counts(service, SPREADSHEET_ID, UPDATE_RANGE_NAME, works_counts)
    print('Update result:', update_result)

if __name__ == '__main__':
    main()
