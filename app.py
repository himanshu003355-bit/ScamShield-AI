import csv
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "training_messages.csv"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024  # 20 KB request limit

vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)
classifier = LogisticRegression(max_iter=1000, class_weight="balanced")
MODEL_READY = False

def train_model():
    global MODEL_READY
    texts, labels = [], []
    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            texts.append(row["message"])
            labels.append(int(row["label"]))
    if len(set(labels)) < 2 or len(texts) < 10:
        raise RuntimeError("Training data must contain at least 10 examples from both classes.")
    matrix = vectorizer.fit_transform(texts)
    classifier.fit(matrix, labels)
    MODEL_READY = True

train_model()

SCAM_PATTERNS = [
    ("Urgent or threatening language", r"\b(urgent|immediately|within \d+ hours|account suspended|will be blocked|final warning|act now)\b", 18),
    ("Requests for credentials or OTP", r"\b(otp|one.time.password|password|pin|cvv|login details|verification code)\b", 25),
    ("Prize, lottery or unexpected reward", r"\b(won|winner|lottery|prize|reward|gift card|claim your)\b", 16),
    ("Payment or fee requested", r"\b(pay|payment|processing fee|transfer|upi|bank details|deposit)\b", 18),
    ("Suspicious shortened or unusual link", r"\b(bit\.ly|tinyurl\.com|t\.co|cutt\.ly|is\.gd)\b", 16),
    ("Impersonation or authority pressure", r"\b(police|customs|income tax|bank officer|government|courier|support team)\b", 10),
    ("Too-good-to-be-true offer", r"\b(guaranteed job|easy money|double your money|work from home.*earn|100% return)\b", 18),
]
URL_RE = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>()]+|(?:[a-z0-9-]+\.)+(?:com|net|org|in|co|io|info|xyz|top|site|online)(?:/[^\s<>()]*)?)")

def analyze_url(raw_url):
    value = raw_url.strip().rstrip(".,;!?)\"]}")
    if not value:
        return None
    candidate = value if "://" in value else "https://" + value
    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower()
    except ValueError:
        host = ""
    flags = []
    score = 0
    if not host or "." not in host:
        flags.append("URL could not be parsed normally")
        score += 20
    if re.search(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        flags.append("URL uses an IP address instead of a familiar domain")
        score += 25
    if host.startswith("xn--") or ".xn--" in host:
        flags.append("Internationalized/punycode domain; verify carefully")
        score += 20
    if len(host) > 35:
        flags.append("Unusually long domain name")
        score += 10
    if host.count("-") >= 3:
        flags.append("Several hyphens in the domain")
        score += 10
    if any(x in host for x in ["login", "verify", "secure", "account", "update", "gift", "claim"]):
        flags.append("Domain contains a commonly abused lure word")
        score += 10
    if host.endswith((".xyz", ".top", ".click", ".work", ".buzz")):
        flags.append("Uses a domain ending that deserves extra verification")
        score += 8
    if parsed.scheme != "https":
        flags.append("Link does not use HTTPS")
        score += 8
    return {"url": value, "host": host or "Unknown", "score": min(score, 60), "flags": flags}

def analyze_text(message):
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Please enter a message to analyze.")
    if len(cleaned) > 5000:
        raise ValueError("Please keep the message under 5,000 characters.")

    found = []
    rule_score = 0
    for title, pattern, weight in SCAM_PATTERNS:
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            found.append(title)
            rule_score += weight

    urls = URL_RE.findall(cleaned)
    url_results = [analyze_url(u) for u in urls[:5]]
    url_results = [u for u in url_results if u]
    url_score = max([u["score"] for u in url_results], default=0)

    model_probability = float(classifier.predict_proba(vectorizer.transform([cleaned]))[0][1])
    model_score = round(model_probability * 100)
    # Blend a learned text model with transparent rules. This is a demo score, not a calibrated probability.
    risk_score = round(min(100, max(0, 0.55 * model_score + 0.35 * min(rule_score, 100) + 0.10 * url_score)))
    if risk_score >= 65:
        verdict, level = "Likely suspicious", "high"
    elif risk_score >= 35:
        verdict, level = "Needs caution", "medium"
    else:
        verdict, level = "No strong scam signals found", "low"

    if not found and not url_results:
        found.append("No obvious keyword-based warning signs detected")
    recommendations = []
    if any("credentials" in x.lower() for x in found):
        recommendations.append("Never share an OTP, password, PIN or CVV with someone who contacted you.")
    if any("link" in x.lower() or "domain" in f.lower() for u in url_results for f in u["flags"]):
        recommendations.append("Do not open the link from the message; visit the organisation's official website independently.")
    if any("payment" in x.lower() or "prize" in x.lower() for x in found):
        recommendations.append("Do not pay an unexpected fee to receive a prize, job or refund.")
    if not recommendations:
        recommendations.append("Verify the sender through an independently found official contact channel.")
    recommendations.append("Treat this result as guidance, not proof. When uncertain, do not click or reply.")

    return {
        "verdict": verdict, "level": level, "risk_score": risk_score,
        "model_score": model_score, "signals": found,
        "urls": url_results, "recommendations": recommendations,
        "disclaimer": "Prototype assessment only. It does not verify sender identity, visit links, or guarantee safety."
    }

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "Message must be plain text."}), 400
    try:
        return jsonify(analyze_text(message))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_ready": MODEL_READY})

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Input is too large. Maximum request size is 20 KB."}), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False)
