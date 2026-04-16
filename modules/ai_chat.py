import google.generativeai as genai
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_interactions_collection

SYSTEM_PROMPT = """You are AutiSense, a warm and supportive AI assistant helping parents 
and caregivers of children diagnosed with Autism Spectrum Disorder (ASD). 

Your role is to:
- Provide personalised, non-diagnostic intervention guidance
- Suggest practical activities based on the child's focus areas
- Be empathetic, supportive and encouraging
- Use simple, clear language
- Adapt your tone to match the caregiver's communication style over time

You must NEVER:
- Provide medical diagnoses or clinical assessments
- Replace professional therapy or medical advice
- Use technical jargon without explanation
- Make the caregiver feel judged or inadequate

Always remind caregivers that AutiSense is a support tool, not a replacement for 
professional intervention."""

def build_context_prompt(child, observations, style_profile, user_message):
    focus_areas = ", ".join(child.get("focus_areas", []))
    child_name = child.get("name", "your child")
    age = child.get("age", "unknown")

    obs_text = ""
    if observations:
        obs_text = "\n".join([f"- {o['observation_text'][:200]}" for o in observations[:3]])
    else:
        obs_text = "No observations recorded yet."

    tone = style_profile.get("tone", "neutral")
    formality = style_profile.get("formality", "semi-formal")

    prompt = f"""{SYSTEM_PROMPT}

CHILD PROFILE:
- Name: {child_name}
- Age: {age}
- Focus Areas: {focus_areas}

RECENT OBSERVATIONS FROM CAREGIVER:
{obs_text}

COMMUNICATION STYLE:
- Tone detected: {tone}
- Formality level: {formality}
- Please match this style in your response.

CAREGIVER MESSAGE:
{user_message}

Respond in a warm, supportive way that is personalised to {child_name}'s profile 
and focus areas. Keep your response concise and practical. 
Do not provide any diagnostic conclusions."""

    return prompt

def analyse_style(messages):
    if not messages:
        return {"tone": "neutral", "formality": "semi-formal"}

    all_text = " ".join([m["content"] for m in messages if m["role"] == "user"])

    casual_words = ["thanks", "hey", "ok", "yeah", "hi", "lol", "omg", "btw"]
    formal_words = ["however", "therefore", "regarding", "would", "could", "please"]

    casual_count = sum(1 for w in casual_words if w in all_text.lower())
    formal_count = sum(1 for w in formal_words if w in all_text.lower())

    formality = "casual" if casual_count > formal_count else "semi-formal"

    concern_words = ["worried", "struggle", "hard", "difficult", "help", "problem"]
    positive_words = ["great", "good", "happy", "progress", "better", "improved"]

    concern_count = sum(1 for w in concern_words if w in all_text.lower())
    positive_count = sum(1 for w in positive_words if w in all_text.lower())

    if concern_count > positive_count:
        tone = "concerned"
    elif positive_count > concern_count:
        tone = "positive"
    else:
        tone = "neutral"

    return {"tone": tone, "formality": formality}

def get_mock_response(child, user_message, style_profile):
    child_name = child.get("name", "your child")
    focus_areas = child.get("focus_areas", [])
    tone = style_profile.get("tone", "neutral")

    greeting = "I understand your concern." if tone == "concerned" else "That's wonderful to hear!"

    suggestions = {
        "Communication": f"Try using visual schedules or picture cards to help {child_name} express their needs more clearly.",
        "Social Interaction": f"Short, structured playdates with one familiar peer can help {child_name} practise social skills in a safe environment.",
        "Behaviour": f"Consistent routines and clear expectations can help {child_name} feel more secure and reduce challenging behaviours.",
        "Sensory": f"Consider creating a calm corner at home where {child_name} can retreat when feeling overwhelmed.",
        "Emotional Regulation": f"Emotion cards or a feelings chart can help {child_name} identify and communicate their emotions."
    }

    relevant = [suggestions[f] for f in focus_areas if f in suggestions]
    suggestion_text = relevant[0] if relevant else f"Keep engaging with {child_name} through play-based activities they enjoy."

    response = f"""{greeting}

Based on what you've shared about {child_name}, here's my suggestion:

{suggestion_text}

Remember, every child progresses at their own pace. You're doing a great job by staying engaged and observant.

*Please note: AutiSense is a support tool and does not replace professional therapy or medical advice.*"""

    return response

def save_interaction(child_id, user_message, ai_response):
    interactions = get_interactions_collection()
    interactions.insert_one({
        "child_id": child_id,
        "interaction_type": "guidance",
        "user_message_summary": user_message[:100],
        "response_summary": ai_response[:200],
        "created_at": datetime.utcnow()
    })

def get_ai_response(child, user_message, chat_history, style_profile):
    try:
        import streamlit as st
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        observations = []
        prompt = build_context_prompt(child, observations, style_profile, user_message)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"DEBUG ERROR: {str(e)}"