import google.generativeai as genai
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_interactions_collection

SYSTEM_PROMPT = """You are AutiSense, a warm and empathetic AI companion supporting parents and caregivers of children with Autism Spectrum Disorder (ASD).

Your personality:
- Speak like a knowledgeable, caring friend — not a clinical report
- Be empathetic, validating, and encouraging without being patronising
- Adapt naturally to the caregiver's emotional state
- Keep responses concise and conversational

Your role:
- Provide personalised, practical intervention guidance
- Suggest home activities tailored to the child's focus areas
- Help caregivers feel heard, supported, and capable

You must NEVER:
- Provide medical diagnoses or clinical assessments
- Replace professional therapy or medical advice
- Use technical jargon without explanation
- Make the caregiver feel judged or inadequate

LANGUAGE RULE:
- Detect the language of the caregiver's message and reply in that exact same language
- If the message is in Bahasa Melayu, respond fully in Bahasa Melayu
- If the message is in English, respond fully in English
- Never mix languages unless the caregiver does

RESPONSE STYLE — read the context and adapt dynamically:

If this is the FIRST message in the conversation:
- A brief, warm acknowledgement is fine to open (1 sentence max)
- Then ask 1–2 clarifying questions or note relevant behaviours to look out for
- Suggest 2–4 specific, practical home activities tailored to the child's profile
- Close with encouragement and an open invitation to continue

If the caregiver is ANSWERING a question you previously asked:
- Do NOT greet them again — pick up naturally from their answer
- Reflect their answer back briefly (1 sentence) to show you understood
- Build directly on what they told you — adjust your guidance accordingly
- Offer 2–4 refined suggestions based on the new information
- Close warmly, keep the conversation going if appropriate

If the caregiver is sharing a NEW concern mid-conversation:
- Do NOT greet — transition naturally
- Acknowledge the new concern with empathy (1 sentence)
- Provide relevant guidance tailored to the concern and child's profile
- Invite them to share more if needed

If the caregiver is expressing FRUSTRATION, EXHAUSTION, or DISTRESS:
- Lead with empathy — validate their feelings before any advice
- Keep suggestions light and manageable — do not overwhelm
- Remind them that small, consistent steps matter
- Offer to help further without pressure

Rules:
- NEVER open with "Hi", "Hello", "Great to hear from you!", or any greeting after the first message
- Write naturally — no visible numbered sections or rigid headers
- Keep responses focused and appropriately brief
- Always end with a short, unobtrusive reminder that AutiSense is a support tool, not a clinical service"""


def build_context_prompt(child, observations, style_profile, user_message, chat_history=None):
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

    # Determine if this is the first exchange so the AI knows whether to greet
    prior_turns = [m for m in (chat_history or []) if m["role"] == "user"]
    is_first_message = len(prior_turns) <= 1

    # Build a readable conversation history (exclude the current message which is user_message)
    history_text = ""
    if chat_history and len(chat_history) > 1:
        prior = chat_history[:-1]  # everything before the current user message
        recent = prior[-8:]        # cap at last 4 exchanges for brevity
        lines = []
        for m in recent:
            role = "Caregiver" if m["role"] == "user" else "AutiSense"
            lines.append(f"{role}: {m['content']}")
        history_text = "\n\n".join(lines)

    conversation_status = (
        "FIRST MESSAGE — a brief warm acknowledgement is appropriate."
        if is_first_message
        else "ONGOING CONVERSATION — do NOT greet. Continue naturally from where the conversation left off."
    )

    prompt = f"""{SYSTEM_PROMPT}

---

CHILD PROFILE:
- Name: {child_name}
- Age: {age}
- Focus Areas: {focus_areas}

RECENT CAREGIVER OBSERVATIONS (most recent first):
{obs_text}

COMMUNICATION STYLE DETECTED:
- Tone: {tone}
- Formality: {formality}
- Match this style naturally in your response.

CONVERSATION STATUS: {conversation_status}

{f"CONVERSATION SO FAR:{chr(10)}{history_text}" if history_text else ""}

CURRENT CAREGIVER MESSAGE:
{user_message}

---

Instructions:
- Respond in the same language as the CAREGIVER MESSAGE
- Determine the message type (first message / answering a question / new concern / distress) and adapt your structure and tone accordingly
- Reference {child_name}'s observations and focus areas ({focus_areas}) where relevant
- Match the caregiver's tone ({tone}) and formality ({formality})
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


def _build_prompt(child, user_message, chat_history, style_profile):
    import streamlit as st
    from observations import get_child_observations
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    observations = get_child_observations(child["child_id"], limit=20)
    recent_interactions = list(get_interactions_collection().find(
        {"child_id": child["child_id"]},
        sort=[("created_at", -1)],
        limit=10
    ))

    prompt = build_context_prompt(child, observations, style_profile, user_message, chat_history)

    if recent_interactions:
        interaction_context = "\n".join([
            f"- Caregiver asked: {i.get('user_message_summary', '—')} | Guidance given: {i.get('response_summary', '—')}"
            for i in recent_interactions
        ])
        prompt += f"\n\nPAST SESSION TOPICS (avoid repeating this advice):\n{interaction_context}"

    return prompt


def stream_ai_response(child, user_message, chat_history, style_profile):
    try:
        prompt = _build_prompt(child, user_message, chat_history, style_profile)
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
        prompt = _build_prompt(child, user_message, chat_history, style_profile)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        save_interaction(child["child_id"], user_message, response.text)
        return response.text
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting right now. Please try again in a moment. If the issue persists, please refresh the page.\n\n*(Error: {str(e)})*"
