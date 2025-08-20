from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from invoices import extract_text_from_image, parse_invoice_data, save_to_json

app = Flask(__name__)
UPLOAD_DIR = "uploaded_invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_invoice():
    if "invoice" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["invoice"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)

    # OCR + parsing
    text = extract_text_from_image(filepath)
    data = parse_invoice_data(text)
    json_path = save_to_json(data, filepath)

    # Redirect to result page with data
    return render_template("result.html", data=data, json_file=json_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port, debug=True)
