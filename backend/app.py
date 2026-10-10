import os, uuid, hashlib, re, json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "15")) * 1024 * 1024
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "local-demo-only-change-me")
UPLOAD_DIR = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
allowed_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS(app, resources={r"/api/*": {"origins": [x.strip() for x in allowed_origins.split(",")]}})

SOURCE_LABEL = "SYNTHETIC DEMO REGISTRY DATA — GovTech Sandbox"
WEIGHTS = {
    "OCR_CHARACTER_CONFIDENCE": 15,
    "CROSS_FIELD_CONSISTENCY": 20,
    "IMAGE_FORENSICS": 20,
    "STAMP_SEAL_ANALYSIS": 15,
    "SIGNATURE_INTEGRITY": 10,
    "REGISTRY_RECONCILIATION": 10,
    "STRUCTURAL_METADATA": 10,
}
DEMO_CASES = {
 "indore": {
   "id":"indore","title":"Indore Sale Deed — Lower concern demo","district":"Indore",
   "fields":{"owner":"SYNTHETIC OWNER A","survey_number":"88/2","khata_number":"KH-IND-01","area_hectares":"0.750","village":"Demo Village A","registration_number":"DEMO-IND-001"},
   "pages":[{"page":1,"survey_number":"88/2","area_hectares":"0.750"},{"page":2,"survey_number":"88/2","area_hectares":"0.750"}],
   "registry":{"registration_number":"DEMO-IND-001","survey_number":"88/2","area_hectares":"0.750"},
   "indicators":{"image_forensics":8,"stamp_seal":12,"signature":10,"metadata":5},
   "expected":"Consistent synthetic example; not legal authentication."
 },
 "bhopal": {
   "id":"bhopal","title":"Bhopal Kolar Khasra — Manual verification demo","district":"Bhopal",
   "fields":{"owner":"SYNTHETIC OWNER B","survey_number":"142/1","khata_number":"KH-BPL-02","area_hectares":"1.200","village":"Demo Kolar Village","registration_number":"DEMO-BPL-002"},
   "pages":[{"page":1,"survey_number":"142/1","area_hectares":"1.200"},{"page":3,"survey_number":"142/9","area_hectares":"1.200"}],
   "registry":{"registration_number":"DEMO-BPL-002","survey_number":"142/1","area_hectares":"1.200"},
   "indicators":{"image_forensics":20,"stamp_seal":15,"signature":15,"metadata":15},
   "expected":"Cross-page survey number mismatch requires review."
 },
 "jabalpur": {
   "id":"jabalpur","title":"Jabalpur Registry — Elevated concern demo","district":"Jabalpur",
   "fields":{"owner":"SYNTHETIC OWNER C","survey_number":"51/4","khata_number":"KH-JBP-03","area_hectares":"3.400","village":"Demo Village C","registration_number":"DEMO-JBP-003"},
   "pages":[{"page":1,"survey_number":"51/4","area_hectares":"0.450"},{"page":2,"survey_number":"51/4","area_hectares":"3.400"}],
   "registry":{"registration_number":"DEMO-JBP-003","survey_number":"51/4","area_hectares":"0.450"},
   "indicators":{"image_forensics":78,"stamp_seal":70,"signature":45,"metadata":80},
   "expected":"Area inconsistency and synthetic anomaly indicators; no conclusive forgery claim."
 }
}
documents, verifications = {}, {}
DATASET_DIR = Path(__file__).resolve().parent / "reference_dataset"
CATALOG_PATH = DATASET_DIR / "catalog.json"
try:
    REFERENCE_CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["records"]
except Exception:
    REFERENCE_CATALOG = []


def err(code, message, status):
    return jsonify({"error":{"code":code,"message":message}}), status

def normalized(s):
    return re.sub(r"\s+", "", str(s or "")).lower().replace(",", ".")

def run_demo_analysis(case):
    findings = []
    pages = case["pages"]
    first = pages[0]
    for page in pages[1:]:
        for field in ("survey_number", "area_hectares"):
            a, b = first.get(field), page.get(field)
            if a is not None and b is not None and normalized(a) != normalized(b):
                label = "Survey number" if field == "survey_number" else "Land area"
                findings.append({
                    "finding_id": str(uuid.uuid4()), "category":"CROSS_FIELD_CONSISTENCY",
                    "title": f"{label} mismatch", "severity":"HIGH" if field=="survey_number" else "HIGH",
                    "description": f"{label} differs across document pages.",
                    "evidence": {f"page_{first['page']}_value":a, f"page_{page['page']}_value":b},
                    "page_numbers":[first["page"],page["page"]], "confidence":None,
                    "recommended_action":"Verify the values against the original record with the competent authority."
                })
    reg = case.get("registry", {})
    for field in ("survey_number", "area_hectares"):
        doc_val = case["fields"].get(field)
        reg_val = reg.get(field)
        if doc_val and reg_val and normalized(doc_val) != normalized(reg_val):
            findings.append({
                "finding_id":str(uuid.uuid4()),"category":"REGISTRY_RECONCILIATION",
                "title":f"{field.replace('_',' ').title()} differs from synthetic registry",
                "severity":"HIGH","description":"Extracted demo value differs from the matching synthetic fixture.",
                "evidence":{"document_value":doc_val,"synthetic_registry_value":reg_val,"source_label":SOURCE_LABEL},
                "page_numbers":[1],"confidence":None,
                "recommended_action":"Confirm the value with the official record; demo registry data is not authoritative."
            })
    category_results = []
    # OCR concern is derived from a demo extraction quality assumption, not a calibrated probability.
    ocr_concern = 12 if case["id"] == "indore" else 28 if case["id"] == "bhopal" else 35
    consistency = min(100, 15 + len([f for f in findings if f["category"]=="CROSS_FIELD_CONSISTENCY"]) * 65)
    registry_score = min(100, 10 + len([f for f in findings if f["category"]=="REGISTRY_RECONCILIATION"]) * 70)
    indicators = case["indicators"]
    values = {
      "OCR_CHARACTER_CONFIDENCE": ocr_concern,
      "CROSS_FIELD_CONSISTENCY": consistency,
      "IMAGE_FORENSICS": indicators["image_forensics"],
      "STAMP_SEAL_ANALYSIS": indicators["stamp_seal"],
      "SIGNATURE_INTEGRITY": indicators["signature"],
      "REGISTRY_RECONCILIATION": registry_score,
      "STRUCTURAL_METADATA": indicators["metadata"]
    }
    available_weight = sum(WEIGHTS.values())
    weighted = sum(WEIGHTS[k] * values[k] for k in WEIGHTS)
    score = round(weighted / available_weight)
    band = "LOWER_CONCERN" if score < 25 else "SOME_INDICATORS" if score < 50 else "ELEVATED_CONCERN" if score < 75 else "HIGH_CONCERN"
    for key, weight in WEIGHTS.items():
        category_results.append({"category":key,"weight":weight,"available":True,"concern_score":values[key],
                                 "reason_unavailable":None,"evidence_note":"Synthetic demo value for this guided case."})
    return {
      "verification_id":str(uuid.uuid4()),"status":"completed","mode":"SYNTHETIC_DEMO",
      "document_title":case["title"],"risk_score":score,"risk_level":band,
      "coverage_weight_percent":100,"findings":findings,"findings_count":len(findings),
      "categories":category_results,"unavailable_categories":[],
      "fields":case["fields"],"pages":case["pages"],"registry_match":case["registry"],
      "registry_source_label":SOURCE_LABEL,"sha256":None,
      "disclaimer":"AI-generated screening result. This assessment is not legal certification, proof of ownership, or a substitute for verification with the competent authority.",
      "disclaimer_hi":"एआई-जनरेटेड स्क्रीनिंग परिणाम। यह मूल्यांकन कानूनी प्रमाणन, स्वामित्व का प्रमाण या सक्षम प्राधिकारी के सत्यापन का विकल्प नहीं है。",
      "notes":["Guided scenario uses synthetic values; category scores are illustrative heuristics, not calibrated probabilities.",
               "Image, seal, signature and metadata indicators are not proof of tampering."]
    }

def extract_text_from_file(path, ext):
    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            chunks = []
            for i, page in enumerate(reader.pages[:20], start=1):
                chunks.append((i, page.extract_text() or ""))
            text = "\n".join(t for _, t in chunks)
            if text.strip():
                return text, "PDF_TEXT_LAYER", len(reader.pages), None
            # OCR scanned PDF is not automatically rendered here to keep MVP install light.
            return "", "UNAVAILABLE", len(reader.pages), "PDF has no extractable text layer; scanned-PDF OCR adapter is not configured."
        try:
            import pytesseract
            from PIL import Image
            # Prefer Hindi + English for Indian land-document scans. Tesseract must have hin.traineddata installed.
            try:
                text = pytesseract.image_to_string(Image.open(path), lang="hin+eng")
            except Exception:
                # Fall back to English OCR if the Hindi language pack is not installed.
                text = pytesseract.image_to_string(Image.open(path), lang="eng")
            return text, "TESSERACT_OCR", 1, None
        except Exception as exc:
            return "", "UNAVAILABLE", 1, f"OCR unavailable: {type(exc).__name__}. Install Tesseract and pytesseract."
    except Exception as exc:
        return "", "UNAVAILABLE", None, f"Text extraction failed: {type(exc).__name__}"

def analyze_uploaded(doc):
    path = Path(doc["path"])
    text, method, page_count, unavailable_reason = extract_text_from_file(path, doc["ext"])
    reference_match = match_reference_document(text) if text.strip() else {"status":"NO_IDENTIFIERS_EXTRACTED", "source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD", "message":"No text available for matching.", "extracted_fields":{}, "candidate":None, "field_comparison":[]}
    # This generic uploaded-file pipeline deliberately does not pretend to have expert forensic detectors.
    findings = []
    if not text.strip():
        findings.append({"finding_id":str(uuid.uuid4()),"category":"OCR_CHARACTER_CONFIDENCE","title":"Text extraction unavailable",
          "severity":"MEDIUM","description":unavailable_reason or "No readable text was extracted.",
          "evidence":{"extraction_method":method},"page_numbers":[],"confidence":None,
          "recommended_action":"Use a clear scan or run OCR with the required language packs; manually verify extracted fields."})
    else:
        # Only surface obvious labels/values if OCR or PDF text includes repeated survey/area values.
        survey_vals = re.findall(r"(?:survey(?:\s*(?:no|number))?|khasra(?:\s*(?:no|number))?)\s*[:#-]?\s*([0-9]+(?:/[0-9]+)?)", text, flags=re.I)
        area_vals = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*(?:ha|hectare|hectares|हेक्टेयर)", text, flags=re.I)
        if len(set(survey_vals)) > 1:
            findings.append({"finding_id":str(uuid.uuid4()),"category":"CROSS_FIELD_CONSISTENCY","title":"Possible survey-number inconsistency",
              "severity":"HIGH","description":"Multiple survey-number candidates were extracted; confirm context and page positions.",
              "evidence":{"candidate_values":list(dict.fromkeys(survey_vals))},"page_numbers":[],"confidence":None,
              "recommended_action":"Review the original pages and confirm the survey number with the competent authority."})
        if len(set(area_vals)) > 1:
            findings.append({"finding_id":str(uuid.uuid4()),"category":"CROSS_FIELD_CONSISTENCY","title":"Possible area inconsistency",
              "severity":"HIGH","description":"Multiple area values were extracted; these may refer to different parcels or contexts.",
              "evidence":{"candidate_values":list(dict.fromkeys(area_vals))},"page_numbers":[],"confidence":None,
              "recommended_action":"Check the field context and original record; OCR matches alone do not prove a discrepancy."})
    # Surface comparisons against the selected synthetic canonical record as explicit evidence.
    for comparison in reference_match.get("field_comparison", []):
        if comparison.get("status") == "MISMATCH":
            findings.append({"finding_id":str(uuid.uuid4()),"category":"REGISTRY_RECONCILIATION","title":f"{comparison['field'].replace('_',' ').title()} differs from synthetic reference",
              "severity":"HIGH","description":"An extracted value differs from the canonical value in the matched synthetic benchmark record.",
              "evidence":{"uploaded_value":comparison.get("uploaded_value"),"synthetic_reference_value":comparison.get("reference_value"),"reference_id":(reference_match.get("candidate") or {}).get("reference_id"),"source_label":reference_match.get("source_label")},
              "page_numbers":[],"confidence":None,"recommended_action":"Review the displayed pages and values. This is a synthetic benchmark comparison, not an official-record verification."})
    # Uploaded analysis has no calibrated forensic detectors; unavailable checks must not count as zero risk.
    available = {"OCR_CHARACTER_CONFIDENCE": bool(text.strip()), "CROSS_FIELD_CONSISTENCY": bool(text.strip())}
    scores = {"OCR_CHARACTER_CONFIDENCE": 45 if text.strip() else None,
              "CROSS_FIELD_CONSISTENCY": min(100, len(findings)*55) if text.strip() else None}
    category_results, weighted, denom = [], 0, 0
    unavailable = []
    for key, weight in WEIGHTS.items():
        ok = available.get(key, False)
        category_results.append({"category":key,"weight":weight,"available":ok,"concern_score":scores.get(key) if ok else None,
                                 "reason_unavailable":None if ok else "Detector not configured or no usable extraction evidence.",
                                 "evidence_note":"Heuristic extraction indicator only." if ok else "Not evaluated; not treated as zero risk."})
        if ok:
            weighted += weight * scores[key]; denom += weight
        else:
            unavailable.append(key)
    score = round(weighted / denom) if denom else None
    band = ("LOWER_CONCERN" if score < 25 else "SOME_INDICATORS" if score < 50 else "ELEVATED_CONCERN" if score < 75 else "HIGH_CONCERN") if score is not None else "INSUFFICIENT_DATA"
    return {"verification_id":str(uuid.uuid4()),"status":"completed","mode":"UPLOADED_DOCUMENT_SCREENING",
      "document_title":doc["filename"],"risk_score":score,"risk_level":band,
      "coverage_weight_percent":round(denom,1),"findings":findings,"findings_count":len(findings),
      "categories":category_results,"unavailable_categories":unavailable,
      "fields":{"extraction_method":method,"extracted_text_preview":text[:3000],"extracted_identifiers":reference_match.get("extracted_fields",{})},
      "pages":[],"registry_match":reference_match,"registry_source_label":SOURCE_LABEL,"sha256":doc["sha256"],
      "disclaimer":"AI-generated screening result. This assessment is not legal certification, proof of ownership, or a substitute for verification with the competent authority.",
      "disclaimer_hi":"एआई-जनरेटेड स्क्रीनिंग परिणाम। यह मूल्यांकन कानूनी प्रमाणन, स्वामित्व का प्रमाण या सक्षम प्राधिकारी के सत्यापन का विकल्प नहीं है。",
      "notes":["Uploaded-document analysis has limited text heuristics only; no expert image, stamp or signature detector is enabled.",
               "A missing check is unavailable, not a zero-risk result. Do not interpret this score as a probability of forgery."]}

def extract_document_fields(text):
    """Conservative field extraction for demo PDFs/text; OCR output may be imperfect."""
    patterns = {
      "registration_number": r"(?:Registration\s*/\s*Reference\s*ID|Registration\s*(?:No\.?|Number)|Reference\s*ID)\s*[:#-]?\s*(DEMO-MP-2026-\d{4})",
      "survey_number": r"(?:Survey\s*/\s*Khasra\s*number|Survey\s*(?:No\.?|Number)|Khasra\s*(?:No\.?|Number))\s*[:#-]?\s*([0-9]+\s*/\s*[0-9]+)",
      "area_hectares": r"(?:Land\s*area\s*\(hectares\)|Area\s*\(Ha\)|Area)\s*[:#-]?\s*([0-9]+(?:\.[0-9]+)?)",
      "district": r"District\s*[:#-]?\s*([A-Za-z ]+)",
      "village": r"Village\s*[:#-]?\s*(Demo Village\s*\d{2}|Demo Kolar Village|[A-Za-z ]+)",
      "khata_number": r"Khata\s*number\s*[:#-]?\s*(DEMO-KH-\d{3}|DEMO-KH-[A-Z0-9-]+|NOT PROVIDED)"
    }
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if match:
            value = re.sub(r"\s+", "", match.group(1)) if key == "survey_number" else match.group(1).strip()
            result[key] = value
    return result

def match_reference_document(text):
    """Match upload against bundled synthetic reference catalogue, never an official source."""
    extracted = extract_document_fields(text)
    if not extracted:
        return {"status":"NO_IDENTIFIERS_EXTRACTED", "source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD", "message":"No supported identifiers could be extracted. Enter details manually or upload a clearer document.", "extracted_fields":{}, "candidate":None, "field_comparison":[]}
    candidates = []
    for record in REFERENCE_CATALOG:
        canonical = record.get("canonical_fields", {})
        score, matched = 0, []
        for key, weight in (("registration_number", 60), ("survey_number", 25), ("district", 5), ("village", 5), ("khata_number", 5)):
            got, expected = extracted.get(key), canonical.get(key)
            if got and expected and normalized(got) == normalized(expected):
                score += weight; matched.append(key)
        if score:
            candidates.append((score, len(matched), record))
    if not candidates:
        return {"status":"NO_MATCH_FOUND", "source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD", "message":"No corresponding record was found in the 50-document synthetic benchmark. This does not imply the upload is fake.", "extracted_fields":extracted, "candidate":None, "field_comparison":[]}
    candidates.sort(key=lambda item:(item[0],item[1]), reverse=True)
    score, _, record = candidates[0]
    canonical = record["canonical_fields"]
    compare_keys = ["registration_number", "survey_number", "area_hectares", "district", "village", "khata_number", "owner_name", "document_type"]
    comparisons=[]
    for key in compare_keys:
        observed = extracted.get(key)
        expected = canonical.get(key)
        if observed is not None and expected is not None:
            same = normalized(observed) == normalized(expected)
            comparisons.append({"field":key,"uploaded_value":observed,"reference_value":expected,"status":"MATCH" if same else "MISMATCH"})
    return {"status":"MATCH_FOUND", "source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD", "match_score":score, "matched_identifiers": [k for k in extracted if k in canonical and normalized(extracted[k])==normalized(canonical[k])], "extracted_fields":extracted, "candidate":{"reference_id":record["reference_id"],"filename":record["filename"],"document_type":canonical.get("document_type"),"district":canonical.get("district"),"survey_number":canonical.get("survey_number"),"category":record.get("category"),"anomaly_labels":record.get("anomaly_labels",[])}, "field_comparison":comparisons, "interpretation":"This is a match against a fictional benchmark record only; it is not official verification or proof of authenticity."}

@app.errorhandler(413)
def too_large(_):
    return err("FILE_TOO_LARGE", "File exceeds the configured upload limit.", 413)

@app.get("/api/v1/health")
def health():
    return jsonify({"status":"ok","service":"bhusatya-api","version":"0.1.0"})

@app.get("/api/v1/demo-cases")
def demo_cases():
    return jsonify({"source_label":SOURCE_LABEL,"cases":[{"id":c["id"],"title":c["title"],"expected":c["expected"]} for c in DEMO_CASES.values()]})

@app.post("/api/v1/documents")
def upload_document():
    if "file" not in request.files:
        return err("MISSING_FILE", "Send the upload in multipart field named 'file'.", 400)
    f = request.files["file"]
    filename = secure_filename(f.filename or "")
    ext = Path(filename).suffix.lower()
    if not filename or ext not in {".pdf",".png",".jpg",".jpeg"}:
        return err("INVALID_FILE", "Only PDF, PNG, JPG and JPEG files are accepted.", 400)
    data = f.read()
    if not data:
        return err("EMPTY_FILE", "The uploaded file is empty.", 400)
    digest = hashlib.sha256(data).hexdigest()
    doc_id = str(uuid.uuid4())
    storage_name = f"{doc_id}{ext}"
    path = UPLOAD_DIR / storage_name
    path.write_bytes(data)
    doc = {"document_id":doc_id,"filename":filename,"path":str(path),"ext":ext,"sha256":digest,"size_bytes":len(data)}
    documents[doc_id] = doc
    return jsonify({"document_id":doc_id,"filename":filename,"size_bytes":len(data),"sha256":digest,"status":"uploaded"}), 201

@app.post("/api/v1/documents/<document_id>/analyze")
def analyze_document(document_id):
    doc = documents.get(document_id)
    if not doc:
        return err("DOCUMENT_NOT_FOUND", "No uploaded document found for this ID. The demo stores uploads in memory.", 404)
    result = analyze_uploaded(doc)
    verifications[result["verification_id"]] = result
    return jsonify(result)

@app.get("/api/v1/verifications/<verification_id>")
def get_verification(verification_id):
    result = verifications.get(verification_id)
    if not result:
        return err("VERIFICATION_NOT_FOUND", "Verification not found.", 404)
    return jsonify(result)

@app.get("/api/v1/verifications/<verification_id>/report")
def get_report(verification_id):
    result = verifications.get(verification_id)
    if not result:
        return err("REPORT_NOT_FOUND", "Report not found.", 404)
    return jsonify({"report":result,"registry_source_label":SOURCE_LABEL})

@app.get("/api/v1/registry/search")
def registry_search():
    q = request.args.get("q","").lower()
    rows = []
    for item in REFERENCE_CATALOG:
        f = item["canonical_fields"]
        rows.append({"reference_id":item["reference_id"],"registration_number":f["registration_number"],"owner_name":f["owner_name"],"survey_number":f["survey_number"],"district":f["district"],"tehsil":f["tehsil"],"village":f["village"],"area_hectares":float(f["area_hectares"]),"document_type":f["document_type"],"category":item["category"],"source_label":item["source_label"],"is_synthetic":True})
    return jsonify({"source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD","total":len(rows),"records":[r for r in rows if not q or q in json.dumps(r).lower()]})

@app.get("/api/v1/reference-documents")
def reference_documents():
    q = request.args.get("q", "").lower()
    rows = []
    for item in REFERENCE_CATALOG:
        f = item["canonical_fields"]
        row = {"reference_id":item["reference_id"],"filename":item["filename"],"document_type":f["document_type"],"district":f["district"],"tehsil":f["tehsil"],"village":f["village"],"survey_number":f["survey_number"],"category":item["category"],"source_label":item["source_label"],"is_synthetic":True}
        if not q or q in json.dumps(row).lower(): rows.append(row)
    return jsonify({"source_label":"SYNTHETIC DEMO DATA — NOT A GOVERNMENT RECORD","total":len(rows),"records":rows})

@app.get("/api/v1/reference-documents/<reference_id>/download")
def download_reference_document(reference_id):
    from flask import send_from_directory
    item = next((r for r in REFERENCE_CATALOG if r["reference_id"] == reference_id), None)
    if not item: return err("REFERENCE_NOT_FOUND", "Synthetic reference document not found.", 404)
    return send_from_directory(str(DATASET_DIR / "documents"), item["filename"], as_attachment=True, download_name=item["filename"])

@app.post("/api/v1/demo-cases/<case_id>/analyze")
def analyze_demo_case(case_id):
    case = DEMO_CASES.get(case_id)
    if not case:
        return err("DEMO_CASE_NOT_FOUND","Choose indore, bhopal or jabalpur.",404)
    result = run_demo_analysis(case)
    verifications[result["verification_id"]] = result
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")), debug=os.getenv("FLASK_DEBUG","false").lower()=="true")
