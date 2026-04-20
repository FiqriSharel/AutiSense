import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from ai_chat import get_ai_response, analyse_style, save_interaction
from observations import get_child_observations
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AutiSense - AI Chat", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user

with st.sidebar:
    st.markdown("### AutiSense")
    st.markdown(f"<small>Logged in as <b>{user['email']}</b></small>", unsafe_allow_html=True)
    st.markdown("---")
    selected = option_menu(
        menu_title=None,
        options=["Home", "Child Profile", "Observations", "AI Chat", "Progress"],
        icons=["house", "person", "pencil", "chat-dots", "bar-chart"],
        default_index=3,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#A8D8CE", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px", "text-align": "left",
                "margin": "2px 0", "padding": "8px 12px",
                "border-radius": "8px", "color": "#C8E6E0",
            },
            "nav-link-selected": {
                "background-color": "#2D7D6F", "color": "white", "font-weight": "500",
            },
        }
    )
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.switch_page("pages/1_Login.py")

if selected == "Home":
    st.switch_page("pages/2_Home.py")
elif selected == "Child Profile":
    st.switch_page("pages/3_Child_Profile.py")
elif selected == "Observations":
    st.switch_page("pages/4_Observations.py")
elif selected == "Progress":
    st.switch_page("pages/6_Progress.py")

st.markdown("<h2 style='color:#2D7D6F;'>AI Chat</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Get personalised intervention guidance for your child.</p>", unsafe_allow_html=True)

st.warning("⚠️ AutiSense is a support tool only and does not provide medical diagnoses. Always consult a qualified professional for clinical advice.")
st.markdown("---")

selected_child = st.session_state.get("selected_child")
if not selected_child:
    st.warning("No child selected. Please select a child profile first.")
    if st.button("Go to Child Profile"):
        st.switch_page("pages/3_Child_Profile.py")
    st.stop()

st.markdown(f"### Chatting about: **{selected_child['name']}**")
st.markdown(f"**Age:** {selected_child['age']}  |  **Focus areas:** {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = None
if "starter_message" in st.session_state and st.session_state.starter_message:
    user_input = st.session_state.starter_message
    st.session_state.starter_message = None

prompt = st.chat_input("Ask AutiSense anything about your child...")
if prompt:
    user_input = prompt

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

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

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    save_interaction(selected_child["child_id"], user_input, response)

if st.session_state.chat_history:
    st.markdown("---")
    if st.button("Start New Session", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()
