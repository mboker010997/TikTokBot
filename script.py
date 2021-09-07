from googleapiclient.discovery import *
from google.oauth2 import service_account
from functions import *


def main():
    credentials = service_account.Credentials.from_service_account_file(
        config.SERVICE_ACCOUNT_FILE, scopes=config.SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    file_id = '1otVA8nMNf76M3JD1W0lA86rT1lZHZC9k'
    filename = 'temp/1.mp4'
    download_surprise(service, file_id, filename)


if __name__ == '__main__':
    main()
