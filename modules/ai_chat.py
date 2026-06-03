import google.generativeai as genai
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_interactions_collection

SYSTEM_PROMPT = """You are AutiSense, a concise and supportive AI assistant helping parents
and caregivers of children diagnosed with Autism Spectrum Disorder (ASD).

Your role is to:
- Provide personalised, non-diagnostic intervention guidance
- Suggest practical activities based on the child's focus areas
- Be direct, warm, and encouraging
- Use simple, clear language

You must NEVER:
- Provide medical diagnoses or clinical assessments
- Replace professional therapy or medical advice
- Use technical jargon without explanation
- Make the caregiver feel judged or inadequate

LANGUAGE RULE (strictly enforced):
- Detect the language of the caregiver's message and reply in that exact same language
- If the message is in Bahasa Melayu, respond fully in Bahasa Melayu
- If the message is in English, respond fully in English
- Never mix languages in a single response unless the caregiver themselves mixed them

RESPONSE FORMAT (strictly enforced — always use this exact structure, never put every bullet point under the same section):

1. Opening (1–2 sentences): A brief, warm greeting that acknowledges what the caregiver shared and names the core concern.

2. Try to understand the issue better by double-checking symptoms or behaviours. This shows empathy and helps ensure your guidance is on target.
   - 2–4 short bullets listing signs or behaviours to watch for that relate to the concern

3. Actions: Based on the child's focus areas and the concern, suggest specific, practical things the caregiver can try at home. Tailor these to the child's profile and the issue at hand.
   - 2–4 short bullets with specific, practical things the caregiver can try

4. A brief, encouraging follow-up — invite them to share how it goes or offer further help.

5. Always end with a reminder that you're a support tool and not a replacement for professional advice, especially for medical concerns.

Rules:
- Never skip any of the four sections
- Keep each bullet to 1 sentence
- No extra prose, headers, or sections beyond this structure
- Only add a clinical disclaimer inside the Actions section when the question is medical in nature"""

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
- Respond in the same language as the CAREGIVER MESSAGE above — Bahasa Melayu if they wrote in Malay, English if they wrote in English
- If the caregiver's message contains a mix of languages, respond in the same mixed style
- Follow the four-section format exactly: Opening → Double check symptoms → Actions → Closing
- In the "Double check symptoms" bullets, reference specific details from {child_name}'s observations where possible
- In the "Actions" bullets, tailor suggestions to {child_name}'s focus areas: {focus_areas}
- Match the caregiver's detected tone ({tone}) and formality ({formality})
- Never provide diagnostic conclusions or replace professional advice"""

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

def _summarise_interaction(user_message, ai_response):
    """
    Calls Gemini once to produce separate 1-sentence summaries for the
    caregiver's message and the AI's response.
    Returns a dict: {"user_message_summary": ..., "response_summary": ...}
    """
    try:
        summary_prompt = f"""Summarise the caregiver's message and the AI response separately, each in 1 sentence.
Write in English regardless of the original language.
Do NOT include diagnostic language, clinical opinions, or personal details.
Return exactly two lines in this format (no extra text):
USER: <1-sentence summary of what the caregiver asked or described>
AI: <1-sentence summary of the guidance or suggestion the AI gave>

Caregiver message: {user_message}
AI response: {ai_response}"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(summary_prompt)
        text = result.text.strip()

        user_summary = ""
        ai_summary = ""
        for line in text.splitlines():
            if line.startswith("USER:"):
                user_summary = line[len("USER:"):].strip()
            elif line.startswith("AI:"):
                ai_summary = line[len("AI:"):].strip()

        return {
            "user_message_summary": user_summary or user_message[:120],
            "response_summary": ai_summary or ai_response[:120],
        }
    except Exception:
        return {
            "user_message_summary": user_message[:120],
            "response_summary": ai_response[:120],
        }

def save_interaction(child_id, user_message, ai_response):
    summaries = _summarise_interaction(user_message, ai_response)
    interactions = get_interactions_collection()
    interactions.insert_one({
        "child_id": child_id,
        "interaction_type": "guidance",
        "user_message_summary": summaries["user_message_summary"],
        "response_summary": summaries["response_summary"],
        "created_at": datetime.utcnow()
    })

def _build_prompt(child, user_message, style_profile):
    import streamlit as st
    from observations import get_child_observations
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    observations = get_child_observations(child["child_id"], limit=20)
    recent_interactions = list(get_interactions_collection().find(
        {"child_id": child["child_id"]},
        sort=[("created_at", -1)],
        limit=10
    ))

    prompt = build_context_prompt(child, observations, style_profile, user_message)

    if recent_interactions:
        interaction_context = "\n".join([
            f"- Caregiver asked: {i.get('user_message_summary', '—')} | Guidance given: {i.get('response_summary', '—')}"
            for i in recent_interactions
        ])
        prompt += f"\n\nRECENT CONVERSATION TOPICS:\n{interaction_context}\nUse this to maintain continuity and avoid repeating advice already given."

    return prompt

def stream_ai_response(child, user_message, chat_history, style_profile):
    try:
        prompt = _build_prompt(child, user_message, style_profile)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=True)
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
        save_interaction(child["child_id"], user_message, full_response)
    except Exception as e:
        yield f"I'm sorry, I'm having trouble connecting right now. Please try again in a moment. If the issue persists, please refresh the page.\n\n*(Error: {str(e)})*"

def get_ai_response(child, user_message, chat_history, style_profile):
    try:
        prompt = _build_prompt(child, user_message, style_profile)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        save_interaction(child["child_id"], user_message, response.text)
        return response.text
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting right now. Please try again in a moment. If the issue persists, please refresh the page.\n\n*(Error: {str(e)})*"