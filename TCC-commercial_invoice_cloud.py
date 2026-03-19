import os
import io
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import pdfplumber
import openpyxl
from httplib2 import Http
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import streamlit as st


SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service_account.json"

SOURCE_FOLDER_ID = os.getenv("1PvY8NIMx_zblcDHFS_lJxtmJfvO-WThi")
TARGET_FOLDER_ID = os.getenv("1GzldiMuVpez2yJnU9yAFs-p1fUhH__Vu")
ERROR_URL = os.getenv("https://chat.googleapis.com/v1/spaces/AAAAdp2-7rc/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=BVhGARAAbgjqHRJVQz-NIoIPO_IgcIYcdATwu1v9bEw")

today = datetime.now()
today_date = today.strftime("%m%d%y")
current_date = today

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_drive_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def list_drive_files(service, query):
    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return files

def find_today_billing_folder(service, parent_folder_id, today_date):
    query = (
        f"'{parent_folder_id}' in parents and trashed=false and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"name contains '{today_date} Billing'"
    )

    folders = list_drive_files(service, query)

    if not folders:
        return None

    for folder in folders:
        if folder["name"].startswith(f"{today_date} Billing"):
            return folder

    return folders[0]

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    return list_drive_files(service, query)

if st.button("Test Billing Folder"):
    try:
        today_date = datetime.now().strftime("%m%d%y")

        st.write("Today date:", today_date)

        service = get_drive_service()
        billing_folder = find_today_billing_folder(service, SOURCE_FOLDER_ID, today_date)

        if not billing_folder:
            st.error(f"No folder found starting with '{today_date} Billing'")
        else:
            st.success(f"Found folder: {billing_folder['name']}")
            st.write("Folder ID:", billing_folder["id"])

            files = list_files_in_folder(service, billing_folder["id"])

            if not files:
                st.warning("Folder is empty")
            else:
                st.subheader("Files inside billing folder")
                for f in files:
                    st.write(f"- {f['name']} ({f['mimeType']})")

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Test Billing Folder"):
    try:
        today_date = datetime.now().strftime("%m%d%y")

        st.write("Today date:", today_date)

        service = get_drive_service()
        billing_folder = find_today_billing_folder(service, SOURCE_FOLDER_ID, today_date)

        if not billing_folder:
            st.error(f"No folder found starting with '{today_date} Billing'")
        else:
            st.success(f"Found folder: {billing_folder['name']}")
            st.write("Folder ID:", billing_folder["id"])

            files = list_files_in_folder(service, billing_folder["id"])

            if not files:
                st.warning("Folder is empty")
            else:
                st.subheader("Files inside billing folder")
                for f in files:
                    st.write(f"- {f['name']} ({f['mimeType']})")

    except Exception as e:
        st.error(f"Error: {e}")


