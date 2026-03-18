import os
import io
import json
from datetime import datetime
import pandas as pd
import pdfplumber
import openpyxl
from httplib2 import Http
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


# CONFIG
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service_account.json"

SOURCE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_SOURCE_FOLDER_ID")
TARGET_FOLDER_ID = os.getenv("GOOGLE_DRIVE_TARGET_FOLDER_ID")
ERROR_URL = os.getenv("ERROR_URL")

today = datetime.now().strftime("%m%d%y")

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# GOOGLE DRIVE
def get_drive():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def list_files(service, folder_id, query=""):
    q = f"'{folder_id}' in parents and trashed=false"
    if query:
        q += f" and {query}"

    results = service.files().list(
        q=q,
        fields="files(id, name, mimeType)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    return results.get("files", [])


def download_file(service, file_id, path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()


def upload_file(service, path, filename):
    media = MediaFileUpload(path, resumable=True)

    file = service.files().create(
        body={"name": filename, "parents": [TARGET_FOLDER_ID]},
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

    return file


# NOTIFICATIONS
def notify(msg):
    if not ERROR_URL:
        print(msg)
        return

    http = Http()
    body = {"text": f"*[{today}]*\n{msg}"}

    http.request(
        ERROR_URL,
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps(body)
    )


# MAIN LOGIC
def run():
    service = get_drive()

    print("Searching billing folder...")
    folders = list_files(
        service,
        SOURCE_FOLDER_ID,
        f"name contains '{today} Billing' and mimeType='application/vnd.google-apps.folder'"
    )

    if not folders:
        raise Exception("No billing folder found")

    billing_folder = folders[0]["id"]
    print("📂 Found billing folder")

    see_folders = list_files(
        service,
        billing_folder,
        "mimeType='application/vnd.google-apps.folder'"
    )

    all_data = []

    for folder in see_folders:
        if not folder["name"].startswith("SEE"):
            continue

        print(f"Processing {folder['name']}")

        pdfs = list_files(
            service,
            folder["id"],
            "mimeType='application/pdf'"
        )

        for pdf in pdfs:
            if not pdf["name"].endswith(".ENT.pdf"):
                continue

            local_pdf = os.path.join(DOWNLOAD_DIR, pdf["name"])
            download_file(service, pdf["id"], local_pdf)

            print(f"Extracting {pdf['name']}")

            with pdfplumber.open(local_pdf) as p:
                for page in p.pages:
                    table = page.extract_table()
                    if table:
                        all_data.extend(table)

    if not all_data:
        raise Exception("No data extracted")

    # SAVE EXCEL
    file_name = f"{today}_CommercialInvoice.xlsx"
    output_path = os.path.join(OUTPUT_DIR, file_name)
    df = pd.DataFrame(all_data)
    df.to_excel(output_path, index=False)
    print("📊 Excel created")

    # UPLOAD
    upload_file(service, output_path, file_name)

    print("☁️ Uploaded to Drive")

    notify("Billing 파일 생성 완료")

def test(url):
    try:
        msg = {
            'text': f'Testing',
        }
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        http = Http()
        response, content = http.request(
            url, method='POST', headers=headers, body=json.dumps(msg)
        )

        if response.status == 200:
            print("Message sent successfully.")
        else:
            print(f"Error: {response.status}\n{content}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# ENTRY
if __name__ == "__main__":
    try:
        url = "https://chat.googleapis.com/v1/spaces/AAAAdp2-7rc/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=BVhGARAAbgjqHRJVQz-NIoIPO_IgcIYcdATwu1v9bEw"
        test(url)
        # run()
    except Exception as e:
        print("❌ ERROR:", e)
        notify(f"에러 발생: {e}")
        raise





