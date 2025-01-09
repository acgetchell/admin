# /// script
# dependencies = [
#   "pypdf",
#   "boxsdk"
# ]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///

"""Receipt organization and Box upload automation tool.

This module provides functionality to:
    - Extract company names and dates from PDF receipts
    - Organize receipts into directories
    - Upload receipts to Box cloud storage

Dependencies:
    - pypdf: PDF parsing
    - boxsdk: Box API integration
    - Python 3.6+: f-strings, Path objects

Key Functions:
    extract_company_and_date: Extracts metadata from PDF receipts
    upload_to_box: Handles Box cloud storage uploads

Example:
    >>> from organize_and_upload_receipts import extract_company_and_date
    >>> company, date = extract_company_and_date("receipt.pdf")
    >>> print(f"Company: {company}, Date: {date}")
"""

# pylint: disable=W0718, W0621  # Catch-all 'except' warnings, Redefining name from outer scope

__version__ = "0.1.0"
__author__ = "Adam Getchell"

import os
import re
from datetime import datetime
from pathlib import Path

from boxsdk import Client, OAuth2
from pypdf import PdfReader

# Box API credentials
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
DEVELOPER_TOKEN = "your_developer_token"

# Box folder ID for root directory (default root folder ID is '0')
BOX_ROOT_FOLDER_ID = "your_folder_id"

# Get current working directory and create a 'receipts' directory
# to store the receipts
RECEIPTS_DIRECTORY: Path = Path(os.getcwd()) / "receipts"

# Create the 'receipts' directory if it does not exist
if not RECEIPTS_DIRECTORY.exists():
    RECEIPTS_DIRECTORY.mkdir(parents=True)
    print(f"Created receipts directory: {RECEIPTS_DIRECTORY}")


def extract_company_and_date(pdf_path):
    """Extract the company name and date from the receipt PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() for page in reader.pages)
        # text = ""
        # for page in reader.pages:
        #     text += page.extract_text()

        # Example patterns for company name and date (adjust as needed)
        company_match = re.search(r"(?i)(company|vendor):\s*(\w+)", text)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)  # YYYY-MM-DD format

        company_name = company_match[2] if company_match else "Unknown_Company"
        date = date_match[1] if date_match else datetime.now().strftime("%Y-%m-%d")

        return company_name.strip(), date.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return "Unknown_Company", datetime.now().strftime("%Y-%m-%d")


def upload_to_box(file_path, company_name, new_file_name):
    """Upload the receipt to a Box folder corresponding to the company name."""
    oauth2 = OAuth2(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=DEVELOPER_TOKEN
    )
    client = Client(oauth2)

    # Ensure the company folder exists (create it if not)
    root_folder = client.folder(folder_id=BOX_ROOT_FOLDER_ID).get()
    company_folder = next(
        (
            item
            for item in root_folder.get_items()
            if item.name == company_name and item.type == "folder"
        ),
        None,
    )
    if not company_folder:
        print(f"Creating folder for company: {company_name}")
        company_folder = root_folder.create_subfolder(company_name)

    # Upload the file
    try:
        print(f"Uploading {new_file_name} to folder: {company_name}")
        with open(file_path, "rb") as file_stream:
            company_folder.upload_stream(file_stream, new_file_name)
        print(f"Successfully uploaded: {new_file_name}")
    except Exception as e:
        print(f"Error uploading file {new_file_name}: {e}")


def process_receipts():
    """Process all receipts in the RECEIPTS_DIRECTORY."""
    for file_name in os.listdir(RECEIPTS_DIRECTORY):
        file_path = os.path.join(RECEIPTS_DIRECTORY, file_name)

        # Skip non-PDF files
        if not file_name.lower().endswith(".pdf") or not os.path.isfile(file_path):
            continue

        # Extract company name and date
        company_name, date = extract_company_and_date(file_path)

        # Create a new file name with the date
        new_file_name = f"{date}_{file_name}"

        # Upload the file to the corresponding Box folder
        upload_to_box(file_path, company_name, new_file_name)


if __name__ == "__main__":
    process_receipts()
