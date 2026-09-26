# AI-REALTIME-GYM-COACH
A real-time AI fitness assistant that tracks workouts, detects exercise posture, counts repetitions, and helps users improve form with live feedback.

## Run locally

Install the dependencies from `requirements.txt`, then start the landing page and
authentication server:

```bash
python backend_server.py
```

Open `http://127.0.0.1:8000` to view the landing page. Create an account or sign
in there to open the workout app. A successful sign-in creates a short-lived,
single-use ticket for the app session.

## Password reset delivery

The sign-in popup includes a password reset flow that sends a six-digit,
single-use code to the account's registered email or mobile number. Codes expire
after 10 minutes and are limited to five verification attempts.

Copy `.env.example` to `.env` and configure SMTP credentials for email, Twilio
credentials for SMS, or both. Restart `backend_server.py` after changing the
configuration. Mobile numbers used for Twilio delivery should be in E.164
format. Passwords are stored as salted PBKDF2 hashes; existing plaintext
passwords are upgraded to hashes the next time the account signs in.

## Deploy to Render

The `render.yaml` Blueprint deploys the landing page, login API, and Streamlit
dashboard together. In Render, create a new Blueprint and connect this GitHub
repository. The service root (`/`) serves the landing page; signing in opens the
dashboard at `/app/`.

The free Render service uses an ephemeral filesystem. Account data and uploads
can be lost when the service restarts or is redeployed; add persistent storage
before using this deployment for accounts you need to keep.

To enable password reset after deployment, add SMTP or Twilio credentials in the
service's Render environment settings. Keep provider credentials out of GitHub.
