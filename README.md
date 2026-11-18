# ScamShield AI

An educational Open Innovation project: an explainable scam-message and suspicious-URL screening prototype.

## Features
- TF-IDF + Logistic Regression text classifier trained from the included small sample dataset.
- Transparent pattern rules for urgency, OTP/credential requests, prize lures, payment requests and impersonation.
- Basic lexical URL checks. The application does **not** visit or fetch submitted links.
- Combined 0–100 demo risk score, explanation and safety recommendations.
- Responsive browser UI, JSON API and health endpoint.

## Important limitations
This is a student prototype, not a production anti-phishing product. The included dataset is small and partly synthetic; model scores are not calibrated probabilities and must not be presented as measured real-world accuracy. Attackers can change wording and domains. A low score does not prove safety. Do not enter real passwords, OTPs, bank details or private personal data. Do not click suspicious links to test them.

## Run locally (Python 3.10+)
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py
```
Open http://localhost:8080

## API example
```bash
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"URGENT: share your OTP to prevent account suspension"}'
```

## Deploy to Google Cloud Run
1. Install Google Cloud CLI and sign in:
   ```bash
   gcloud auth login
   gcloud init
   ```
2. In Google Cloud Console, create/select a project and ensure billing is enabled. Copy the Project ID.
3. From this project folder, run:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
   gcloud run deploy scamshield-ai \
     --source . \
     --region asia-south1 \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --timeout 60 \
     --max-instances 3
   ```
4. Confirm the prompts. When deployment completes, copy the **Service URL** printed by the command and open it. The URL is created by Google Cloud; it cannot be known before deployment.
5. Verify health at `YOUR_SERVICE_URL/health`.

If the deployment account lacks permission, ask the project administrator for the roles required by Cloud Run source deployment (Cloud Run Source Developer, Service Usage Consumer and Service Account User, as applicable).

## Update a deployment
After editing source files, run the same `gcloud run deploy ...` command again from this folder. Cloud Run creates a new revision.

## Suggested hackathon improvements
- Collect consented, anonymized, properly labeled examples.
- Evaluate on a held-out dataset and report precision, recall, F1 and confusion matrix.
- Add multilingual Hindi/English examples and compare performance.
- Add user feedback and analyst review before making strong claims.

## Project structure
```
ScamShield_AI/
├── app.py
├── data/training_messages.csv
├── templates/index.html
├── static/style.css
├── static/app.js
├── requirements.txt
├── Dockerfile
└── README.md
```
