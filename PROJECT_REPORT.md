# ScamShield AI — Open Innovation Project Report

## 1. Abstract
ScamShield AI is an educational web prototype that screens user-submitted messages and visible URLs for common scam indicators. It combines a TF-IDF text representation and Logistic Regression classifier with transparent rule-based checks. It returns a risk band, score, observed signals and safety guidance.

## 2. Problem statement
Digital messages are frequently used to impersonate organizations, create urgency, request credentials or solicit unexpected payments. Users may struggle to identify warning signs quickly.

## 3. Proposed solution
A browser-based tool accepts pasted text, analyzes linguistic patterns and visible URL characteristics, and explains why caution may be appropriate. It does not open links or contact external services.

## 4. Methodology
1. Load labeled sample messages from CSV.
2. Convert text into TF-IDF unigram and bigram features.
3. Train a Logistic Regression classifier.
4. Independently check for explainable patterns such as urgency, OTP requests, prize claims and payment requests.
5. Apply simple lexical URL checks.
6. Blend model and rule indicators into a demonstration risk score.
7. Display the result and recommendations.

## 5. Technology
Python, Flask, scikit-learn, HTML, CSS, JavaScript, Docker and Google Cloud Run.

## 6. Innovation
The prototype emphasizes explainability: instead of returning only a label, it shows warning signals and practical next steps. It combines learned text patterns with explicit rules in one lightweight interface.

## 7. Limitations and responsible use
The training dataset is small and not representative of real-world traffic. Scores are not calibrated probabilities and the system can produce false positives and false negatives. URL checks are heuristic and do not inspect website content, certificates or reputation. Never use the result as the sole basis for financial or security decisions.

## 8. Future scope
Use a larger consented dataset, add Hindi-English code-mixed text, perform rigorous held-out evaluation, compare models, add privacy-preserving feedback, and integrate trusted threat-intelligence sources with appropriate safeguards.

## 9. Conclusion
ScamShield AI demonstrates how basic NLP and explainable rules can be combined into a useful educational cybersecurity interface. It provides a foundation for further experimentation and evaluation.
