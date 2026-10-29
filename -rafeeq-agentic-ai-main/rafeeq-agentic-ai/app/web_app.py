from collections import defaultdict, deque
from time import time
from threading import Lock

from flask import Flask, jsonify, render_template, request

from app.rag import MAX_UPLOAD_BYTES, add_pdf_document, list_uploaded_documents, retrieve_chunks
from app.openrouter_agent import run_openrouter_agent
from app.tools import REQUIRED_FIELDS, create_application_draft, validate_application

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES + (1024 * 1024)
MAX_MESSAGE_LENGTH = 4000
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60
_request_times = defaultdict(deque)
_rate_lock = Lock()


def _is_rate_limited(client_key: str) -> bool:
    now = time()
    with _rate_lock:
        recent = _request_times[client_key]
        while recent and now - recent[0] > RATE_LIMIT_WINDOW_SECONDS:
            recent.popleft()
        if len(recent) >= RATE_LIMIT_REQUESTS:
            return True
        recent.append(now)
        return False


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/rag")
def rag_page():
    """Show the document-grounded retrieval interface."""
    return render_template("rag.html")


@app.get("/application")
def application_page():
    """Show the structured application assistant."""
    return render_template("application.html")


def _application_payload():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "أرسل البيانات بصيغة JSON صحيحة."}), 400)
    if set(payload) - set(REQUIRED_FIELDS):
        return None, (jsonify({"error": "تحتوي البيانات على حقول غير مسموحة."}), 400)
    application = {field: payload.get(field, "") for field in REQUIRED_FIELDS}
    if any(not isinstance(value, str) for value in application.values()):
        return None, (jsonify({"error": "يجب أن تكون جميع الحقول نصية."}), 400)
    return application, None


@app.get("/api/rag/documents")
def rag_documents_api():
    return jsonify({"documents": list_uploaded_documents(), "storage": "in_memory"})


@app.post("/api/rag/upload")
def rag_upload_api():
    client_key = request.remote_addr or "unknown"
    if _is_rate_limited(client_key):
        return jsonify({"error": "طلبات كثيرة خلال وقت قصير. انتظر دقيقة ثم حاول مجددًا."}), 429
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Choose a PDF file to upload."}), 400
    content = uploaded.stream.read(MAX_UPLOAD_BYTES + 1)
    result = add_pdf_document(uploaded.filename, content)
    return jsonify(result), 200 if result.get("ok") else 400


@app.post("/api/rag/search")
def rag_search_api():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"query"}:
        return jsonify({"ok": False, "error": "Send a JSON object with only a query field."}), 400
    query = payload.get("query")
    if not isinstance(query, str):
        return jsonify({"ok": False, "error": "Query must be text."}), 400
    result = retrieve_chunks(query)
    return jsonify(result), 200 if result.get("ok") else 400


@app.post("/api/application/validate")
def validate_application_api():
    application, error_response = _application_payload()
    if error_response:
        return error_response
    return jsonify({"result": validate_application(application)}), 200


@app.post("/api/application/draft")
def create_application_draft_api():
    application, error_response = _application_payload()
    if error_response:
        return error_response
    result = create_application_draft(application)
    return jsonify({"result": result}), 200 if result.get("status") == "awaiting_approval" else 422


@app.post("/chat")
def chat():
    # This is a lightweight demo limiter; use a shared store for multi-worker deployment.
    client_key = request.remote_addr or "unknown"
    if _is_rate_limited(client_key):
        return jsonify({"error": "طلبات كثيرة خلال وقت قصير. انتظر دقيقة ثم حاول مجددًا."}), 429

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "أرسل الطلب بصيغة JSON صحيحة."}), 400
    message = payload.get("message", "")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "اكتب رسالة أولاً."}), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": "الرسالة طويلة جدًا. الحد الأقصى 4000 حرف."}), 413

    try:
        result = run_openrouter_agent(message.strip())
        status = 200 if result.get("ok") else 502
        return jsonify({"result": result}), status
    except Exception:
        app.logger.exception("Rafeeq agent request failed")
        return jsonify({"error": "تعذر تشغيل الوكيل. تحقق من إعدادات الخدمة ثم حاول مرة أخرى."}), 500


if __name__ == "__main__":
    # Local demo only. Do not expose publicly without authentication and safeguards.
    app.run(host="127.0.0.1", port=5000, debug=False)
