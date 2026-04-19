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

    if observations:
        obs_text = "\n".join([
            f"- [{o['submitted_at'].strftime('%d %b %Y')}]: {o['observation_text'][:300]}"
            for o in observations
        ])
    else:
        obs_text = "No observations recorded yet. Give general guidance based on focus areas."

    tone = style_profile.get("tone", "neutral")
    formality = style_profile.get("formality", "semi-formal")

    prompt = f"""{SYSTEM_PROMPT}

CHILD PROFILE:
- Name: {child_name}
- Age: {age}
- Focus Areas: {focus_areas}

RECENT CAREGIVER OBSERVATIONS (most recent first):
{obs_text}

COMMUNICATION STYLE DETECTED:
- Tone: {tone}
- Formality: {formality}
- Please match this style naturally in your response.

CAREGIVER MESSAGE:
{user_message}

Instructions:
- Reference specific details from the observations above to show you understand this child's situation
- Give practical, actionable suggestions tailored to {child_name}'s focus areas
- Match the caregiver's detected tone and formality
- Be warm, encouraging and non-judgmental
- Never provide diagnostic conclusions or replace professional advice
- Keep response concise and easy to read"""

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
        from observations import get_child_observations
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        # Fetch real observations
        observations = get_child_observations(child["child_id"], limit=5)

        # Fetch recent interaction summaries
        recent_interactions = list(get_interactions_collection().find(
            {"child_id": child["child_id"]},
            sort=[("created_at", -1)],
            limit=3
        ))

        # Build contextual prompt
        prompt = build_context_prompt(child, observations, style_profile, user_message)

        # Add recent interaction context
        if recent_interactions:
            interaction_context = "\n".join([
                f"- {i['user_message_summary']}"
                for i in recent_interactions
            ])
            prompt += f"\n\nRECENT CONVERSATION TOPICS:\n{interaction_context}\nUse this to maintain continuity and avoid repeating advice already given."

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Show a friendly error message instead of crashing
        return f"I'm sorry, I'm having trouble connecting right now. Please try again in a moment. If the issue persists, please refresh the page.\n\n*(Error: {str(e)})*"