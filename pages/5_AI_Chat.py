import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from ai_chat import get_ai_response, analyse_style, save_interaction
from observations import get_child_observations
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - AI Chat", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>AI Chat</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Get personalised intervention guidance for your child.</p>", unsafe_allow_html=True)

st.warning("⚠️ AutiSense is a support tool only and does not provide medical diagnoses. Always consult a qualified professional for clinical advice.")
st.markdown("---")

# Check child is selected
selected_child = st.session_state.get("selected_child")
if not selected_child:
    st.warning("No child selected. Please select a child profile first.")
    if st.button("Go to Child Profile"):
        st.switch_page("pages/3_Child_Profile.py")
    st.stop()

st.markdown(f"### Chatting about: **{selected_child['name']}**")
st.markdown(f"**Age:** {selected_child['age']}  |  **Focus areas:** {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

# Initialise chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Starter suggestions for new users
if not st.session_state.chat_history:
    st.markdown("#### Not sure where to start? Try one of these:")
    col1, col2, col3 = st.columns(3)
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
        with st.spinner("AutiSense is thinking..."):
            response = get_ai_response(
                selected_child,
                user_input,
                st.session_state.chat_history,
                style_profile
            )
        st.markdown(response)

    # Save to history and database
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    save_interaction(selected_child["child_id"], user_input, response)

# Clear chat button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("Start New Session", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()