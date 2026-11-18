# Demo test cases

Use only these sample strings in the demo; do not test by clicking suspicious links.

| Case | Input | Expected demonstration |
|---|---|---|
| Urgent credential request | `URGENT: Your account will be blocked. Share your OTP and password now.` | Elevated risk; urgency and credential signals |
| Prize fee lure | `You won a prize. Pay a processing fee to claim your reward.` | Elevated risk; prize and payment signals |
| Ordinary college update | `The project meeting is tomorrow at 10 AM in the seminar hall.` | Usually lower risk |
| Shortened URL | `Please verify your account at https://bit.ly/example` | URL shortening indicator |

Outputs can vary because the final score blends a trained model with heuristic rules.
