import streamlit as st
from google import genai
from database import get_database

def test_mongo():
    try:
        db = get_database()
        db.command("ping")
        return True, "MongoDB Atlas connected successfully!"
    except Exception as e:
        return False, f"MongoDB connection failed: {e}"

def test_gemini():
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say hello in one word."
        )
        return True, f"Gemini API connected! Response: {response.text.strip()}"
    except Exception as e:
        return False, f"Gemini connection failed: {e}"