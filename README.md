# AutiSense

A Streamlit web application that supports caregivers of children with Autism Spectrum Disorder (ASD) through observation tracking, engagement monitoring, and AI-powered guidance.

---

## Prerequisites

- Python 3.10 or higher
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account with a cluster set up
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd autisense
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

Create the file `.streamlit/secrets.toml` (this file is gitignored and will never be committed):

```toml
MONGO_URI = "your-mongodb-connection-string"
GEMINI_API_KEY = "your-gemini-api-key"
```

Replace the values with your own credentials.

### 5. Seed the admin account

Before running the app for the first time, create the admin account by running the seed script. You will be prompted for the admin email and password — nothing is stored in plain text.

```bash
python seed_admin.py
```

> `seed_admin.py` is gitignored and stays local only.

### 6. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Project Structure

```
autisense/
├── app.py                  # Entry point
├── requirements.txt
├── seed_admin.py           # One-time admin account setup (gitignored)
├── .streamlit/
│   └── secrets.toml        # API keys and DB URI (gitignored)
├── modules/                # Core logic
│   ├── auth.py             # Login and registration
│   ├── database.py         # MongoDB connection
│   ├── observations.py     # Observation submission and scoring
│   ├── ai_chat.py          # Gemini AI integration
│   ├── children.py         # Child profile management
│   └── sidebar.py          # Navigation sidebar
└── pages/                  # Streamlit pages
    ├── 1_Login.py
    ├── 2_Home.py
    ├── 3_Child_Profile.py
    ├── 4_Observations.py
    ├── 5_AI_Chat.py
    ├── 6_Progress.py
    └── 7_Admin_Home.py     # and other admin pages
```

---

## Notes

- The AI chat feature requires a valid Gemini API key. Without it, the chat page will return a connection error.
- The MongoDB cluster must be accessible from your machine. Check that your IP address is whitelisted in Atlas under **Network Access**.
- The engagement scoring system updates automatically each time a valid observation is submitted. No manual action is needed.
- AutiSense is a support tool only and does not provide medical diagnoses or replace professional clinical advice.
