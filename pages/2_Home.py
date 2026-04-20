import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AutiSense - Home", page_icon="🌿", layout="wide")

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
        default_index=0,
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

if selected == "Child Profile":
    st.switch_page("pages/3_Child_Profile.py")
elif selected == "Observations":
    st.switch_page("pages/4_Observations.py")
elif selected == "AI Chat":
    st.switch_page("pages/5_AI_Chat.py")
elif selected == "Progress":
    st.switch_page("pages/6_Progress.py")

st.markdown("<h2 style='color:#2D7D6F;'>Welcome to AutiSense</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#555;'>Logged in as: <b>{user['email']}</b></p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
        <div style='background:#EAF4FE; padding:1.5rem; border-radius:12px; border-left:4px solid #2563EB; margin-bottom:0.5rem;'>
            <h4 style='color:#1E3A5F; margin:0 0 0.4rem 0;'>Child Profile</h4>
            <p style='color:#4A5568; margin:0; font-size:0.9rem;'>Set up and manage your child's profile</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Child Profile", use_container_width=True):
        st.switch_page("pages/3_Child_Profile.py")

with col2:
    st.markdown("""
        <div style='background:#EAF7F2; padding:1.5rem; border-radius:12px; border-left:4px solid #059669; margin-bottom:0.5rem;'>
            <h4 style='color:#1A3C2E; margin:0 0 0.4rem 0;'>Observations</h4>
            <p style='color:#4A5568; margin:0; font-size:0.9rem;'>Record your child's daily behaviours</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Observations", use_container_width=True):
        st.switch_page("pages/4_Observations.py")

with col3:
    st.markdown("""
        <div style='background:#F3EFFE; padding:1.5rem; border-radius:12px; border-left:4px solid #7C3AED; margin-bottom:0.5rem;'>
            <h4 style='color:#2D1B5C; margin:0 0 0.4rem 0;'>AI Chat</h4>
            <p style='color:#4A5568; margin:0; font-size:0.9rem;'>Get personalised intervention guidance</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to AI Chat", use_container_width=True):
        st.switch_page("pages/5_AI_Chat.py")

with col4:
    st.markdown("""
        <div style='background:#FEF9E8; padding:1.5rem; border-radius:12px; border-left:4px solid #D97706; margin-bottom:0.5rem;'>
            <h4 style='color:#4A2C07; margin:0 0 0.4rem 0;'>Progress</h4>
            <p style='color:#4A5568; margin:0; font-size:0.9rem;'>Track your child's progress over time</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Progress", use_container_width=True):
        st.switch_page("pages/6_Progress.py")

st.markdown("---")
selected_child = st.session_state.get("selected_child")
if selected_child:
    st.success(f"Currently viewing: **{selected_child['name']}** — Age {selected_child['age']}")
else:
    st.info("No child selected. Go to Child Profile to select or create one.")
