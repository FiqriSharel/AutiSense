import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from ai_chat import stream_ai_response, analyse_style, save_interaction
from observations import get_child_observations
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - AI Chat", page_icon=None, layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user

if user.get("role") == "admin":
    st.switch_page("pages/7_Admin_Home.py")

if not st.session_state.get("selected_child"):
    st.switch_page("pages/3_Child_Profile.py")
selected_child = st.session_state.selected_child
render_sidebar(user)

st.markdown("""
<style>
.loading-dots span {
    animation: ld-blink 1.2s infinite;
    animation-fill-mode: both;
    font-size: 1.4rem;
    color: #6b7280;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes ld-blink {
    0%   { opacity: 0.15; }
    30%  { opacity: 1; }
    100% { opacity: 0.15; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:#2D7D6F;'>AI Chat</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Get personalised intervention guidance for your child.</p>", unsafe_allow_html=True)

st.warning("⚠️ AutiSense is a support tool only and does not provide medical diagnoses. Always consult a qualified professional for clinical advice.")
st.markdown("---")

st.markdown(f"### Chatting about: **{selected_child['name']}**")
st.markdown(f"**Age:** {selected_child['age']}  |  **Focus areas:** {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

# Initialise chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Allow starter buttons to wrap text and grow in height naturally
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] .stButton > button {
    white-space: normal !important;
    height: auto !important;
    min-height: 3rem;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

def _trim_to_sentence(text, max_chars=120):
    """Return a clean summary: first sentence if short enough, else trim at word boundary."""
    first_sentence_end = text.find('. ')
    if 0 < first_sentence_end <= max_chars:
        return text[:first_sentence_end + 1]
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars]
    last_space = trimmed.rfind(' ')
    return (trimmed[:last_space] if last_space > 0 else trimmed) + '...'

# Starter suggestions — static if fewer than 4 observations, observation-based otherwise
if not st.session_state.chat_history:
    past_obs = get_child_observations(selected_child["child_id"], limit=50)

    st.markdown("#### Not sure where to start? Try one of these:")
    col1, col2, col3 = st.columns(3)

    if len(past_obs) > 3:
        recent_three = past_obs[:3]
        for col, obs in zip([col1, col2, col3], recent_three):
            area = obs.get("focus_area", "Observation")
            summary = _trim_to_sentence(obs["observation_text"])
            label = f"{area}: {summary}"
            full_prompt = (
                f"I recently observed that {selected_child['name']} "
                f"{obs['observation_text']} "
                f"What activities or strategies can I use at home to support them?"
            )
            with col:
                if st.button(label, use_container_width=True, key=f"starter_{obs['obs_id']}"):
                    st.session_state.starter_message = full_prompt
                    st.rerun()
    else:
        with col1:
            if st.button("How can I improve communication at home?", use_container_width=True):
                st.session_state.starter_message = "How can I improve communication at home?"
                st.rerun()
        with col2:
            if st.button("My child had a meltdown today. What should I do?", use_container_width=True):
                st.session_state.starter_message = "My child had a meltdown today. What should I do?"
                st.rerun()
        with col3:
            if st.button("What activities help with social skills?", use_container_width=True):
                st.session_state.starter_message = "What activities help with social skills?"
                st.rerun()

    st.markdown("---")

# Display existing chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle starter message
user_input = None
if "starter_message" in st.session_state and st.session_state.starter_message:
    user_input = st.session_state.starter_message
    st.session_state.starter_message = None

# Chat input box
prompt = st.chat_input("Ask AutiSense anything about your child...")
if prompt:
    user_input = prompt

# Process user input
if user_input:
    # Show user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    style_profile = analyse_style(st.session_state.chat_history)
    observations = get_child_observations(selected_child["child_id"])

    with st.chat_message("assistant"):
        loading = st.empty()
        loading.markdown(
            '<div class="loading-dots"><span>.</span><span>.</span><span>.</span></div>',
            unsafe_allow_html=True
        )

        def _stream_with_clear():
            first = True
            for chunk in stream_ai_response(
                selected_child, user_input,
                st.session_state.chat_history, style_profile
            ):
                if first:
                    loading.empty()
                    first = False
                yield chunk

        response = st.write_stream(_stream_with_clear())

    # Save to history and database
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    # save_interaction(selected_child["child_id"], user_input, response)

# Clear chat button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("Start New Session", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()