import os
import io
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import pdfplumber
from httplib2 import Http
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
import openpyxl


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
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
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
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
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

def download_drive_file(service, file_id, destination):
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

    with open(destination, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


def download_ent_pdfs(service, billing_folder_id):
    print("📥 Downloading PDFs...")

    sheet_names = []

    items = list_drive_files(service, f"'{billing_folder_id}' in parents")

    for item in items:
        if item["mimeType"] == "application/vnd.google-apps.folder" and item["name"].startswith("SEE"):
            print("📂 SEE folder:", item["name"])
            sheet_names.append(item["name"])

            files = list_drive_files(service, f"'{item['id']}' in parents")

            for f in files:
                if f["name"].endswith(".ENT.pdf"):
                    path = os.path.join(DOWNLOAD_DIR, f"{item['name']}_{f['name']}")
                    print("⬇️ Downloading:", f["name"])
                    download_drive_file(service, f["id"], path)

    return sheet_names


def extract_pdf_to_csv(pdf_path, csv_path):
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.extend(table)

    if not tables:
        print("⚠️ No tables found:", pdf_path)
        return False

    max_cols = max(len(row) for row in tables)
    rows = [row + [""] * (max_cols - len(row)) for row in tables]

    df = pd.DataFrame(rows[1:], columns=rows[0])
    df.to_csv(csv_path, index=False)

    return True

def process_csv_to_excel(sheet, csv_path):
    df = pd.read_csv(csv_path)

    for r, row in df.iterrows():
        for c, value in enumerate(row, start=1):
            sheet.cell(row=r+1, column=c, value=str(value))


def upload_drive_file(service, file_path, filename):
    print("📤 Uploading file...")

    media = MediaFileUpload(file_path, resumable=True)

    file_metadata = {
        "name": filename,
        "parents": [TARGET_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name",
        supportsAllDrives=True
    ).execute()

    print("✅ Uploaded:", file["name"])
    return file

def run():
    print("🚀 SCRIPT STARTED")

    service = get_drive_service()

    billing_folder = find_today_billing_folder(service)
    if not billing_folder:
        raise Exception("Billing folder not found")

    sheet_names = download_ent_pdfs(service, billing_folder["id"])

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    for name in sheet_names:
        sheet = wb.create_sheet(name)

        for file in os.listdir(DOWNLOAD_DIR):
            if file.startswith(name) and file.endswith(".pdf"):
                pdf_path = os.path.join(DOWNLOAD_DIR, file)
                csv_path = pdf_path.replace(".pdf", ".csv")

                if extract_pdf_to_csv(pdf_path, csv_path):
                    process_csv_to_excel(sheet, csv_path)

    output_file = os.path.join(OUTPUT_DIR, f"{today_date}_invoice.xlsx")
    wb.save(output_file)

    upload_drive_file(service, output_file, os.path.basename(output_file))

    print("🎉 DONE")


if __name__ == "__main__":
    run()