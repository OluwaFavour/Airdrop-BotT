from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Spreadsheet ID
sheet_id = 'GOOGLE_API_TOKEN'

try:
  service = build('sheets', 'v4', credentials=creds)
except:
  DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
  service = build('sheets', 'v4', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)

# Call the sheets API
sheet = service.spreadsheets()


# Requests here
def updateGSheet(row_num, *values_list):
    """
        Returns and execute the googlesheets update function

        Parameters:
        row_num (int): The row number of cell you wish to update
        *values_list (list): A tuple of lists of values you wish to add to cell

        Returns:
        UpdateValuesResponse: The response when updating a range of values in a spreadsheet
    """
    values = []
    # Append List parameter values_list into values, Each list signifies a row
    for val_list in values_list:
        values.append(val_list)
    return sheet.values().update(spreadsheetId=sheet_id, range=f"sheet1!A{row_num}", valueInputOption="USER_ENTERED", body={"values":values}).execute()
