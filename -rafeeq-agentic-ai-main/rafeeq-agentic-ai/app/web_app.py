from collections import defaultdict, deque
from time import time
from threading import Lock

from flask import Flask, jsonify, render_template, request

from app.openrouter_agent import run_openrouter_agent

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
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
