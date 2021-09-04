import googleapiclient
from googleapiclient import *
from googleapiclient.discovery import *
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from config import *
import os
import functions
from work import *


def main():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    file_id = '1otVA8nMNf76M3JD1W0lA86rT1lZHZC9k'
    filename = 'temp/1.mp4'
    functions.download_surprise(service, file_id, filename)


if __name__ == '__main__':
    main()
