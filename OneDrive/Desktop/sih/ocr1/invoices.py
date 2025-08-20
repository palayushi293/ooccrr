import pytesseract
from PIL import Image
import re
from datetime import datetime
import os
import json

# Path to Tesseract (Windows users only — comment this out if on Linux/macOS)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Folder to save uploaded images
UPLOAD_DIR = "uploaded_invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extract text from image
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Helper for regex extraction
def extract(pattern, text, group=1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(group).strip() if match else None

# Parse structured invoice data
def parse_invoice_data(text):
    invoice_number = extract(r'Invoice\s*(No\.?|Number)?[:\s]*([A-Z0-9\-]{4,})', text, group=2)
    invoice_date = extract(r'Invoice\s*Date[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})', text)
    due_date = extract(r'Due\s*Date[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})', text)
    total_amount = extract(r'(Invoice\s*Total|Total\s*Amount)[:\s₹$]*([\d,]+\.\d{2})', text, group=2)
    gst = extract(r'GST\s*[0-9]{1,2}\%?\s*[:₹\s]*([\d,]+\.\d{2})', text)
    account_number = extract(r'Account\s*Number[:\s]*([0-9]+)', text)
    routing_number = extract(r'Routing\s*Number[:\s]*([0-9]+)', text)
    terms = extract(r'Terms\s*&\s*Conditions[\s\S]*?(Payment is due.*?)\n', text)

    bill_to_match = re.search(r'Bill\s*To[:\s]*([\s\S]+?)\n(?:Ship\s*To|Invoice\s*#)', text, re.IGNORECASE)
    ship_to_match = re.search(r'Ship\s*To[:\s]*([\s\S]+?)\n(?:Invoice\s*Date|Due\s*Date)', text, re.IGNORECASE)

    bill_to = bill_to_match.group(1).strip() if bill_to_match else None
    ship_to = ship_to_match.group(1).strip() if ship_to_match else None

    return {
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "total_amount": float(total_amount.replace(",", "")) if total_amount else None,
        "gst": float(gst.replace(",", "")) if gst else None,
        "account_number": account_number,
        "routing_number": routing_number,
        "bill_to": bill_to,
        "ship_to": ship_to,
        "terms_conditions": terms,
        "raw_text": text
    }

# Save parsed JSON file
def save_to_json(data, image_path, output_dir="uploaded_invoices"):
    filename = f"invoice_{data['invoice_number'] or datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    output_path = os.path.join(output_dir, filename)
    data["image_path"] = image_path
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    return output_path
