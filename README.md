# 🚨 HELP

**Humanitarian Emergency Liaison Platform**

HELP is an AI-powered emergency incident reporting and response assistance platform built using Streamlit, Gemini AI, Supabase, and Twilio.

The platform allows users to report incidents using text, voice, images, and location data, receive AI-generated assessments, and communicate with relevant responders through email, SMS, and voice calls.

---

## Features

* 🔐 User Authentication
* 📍 Interactive Location Selection
* 📝 Incident Reporting
* 🎤 Voice Report Transcription
* 🖼️ Image Analysis (Gemini Vision)
* 🤖 AI Incident Assessment
* 🚑 Responder Recommendations
* 📧 Email Alerts
* 📱 SMS Notifications
* 📞 Voice Call Notifications
* 📊 Incident Dashboard
* 🔑 Bring Your Own Key (BYOK)

---

## Technology Stack

* Streamlit
* Google Gemini AI
* Supabase
* Twilio
* Folium
* Python

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd help
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure:

```env
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

Run the application:

```bash
streamlit run Home.py
```

---

## Disclaimer

HELP is an educational and demonstration project.

The platform assists with emergency reporting, incident analysis, and communication support. It does not replace emergency services, medical professionals, law enforcement, or other qualified responders.

Always contact official emergency services during real emergencies.
