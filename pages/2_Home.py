import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - Home", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user
render_sidebar(user)

st.markdown(f"<h2 style='color:#2D7D6F;'>Welcome to AutiSense</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#555;'>Logged in as: <b>{user['email']}</b></p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
        <div style='background:#EAF4FE; padding:1.5rem; border-radius:12px; text-align:center; border-bottom:3px solid #2563EB;'>
            <h3 style='color:#1E3A5F; margin:0 0 0.4rem 0;'>Child Profile</h3>
            <p style='color:#4A5568; margin:0;'>Set up and manage your child's profile</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Child Profile", use_container_width=True):
        st.switch_page("pages/3_Child_Profile.py")

with col2:
    st.markdown("""
        <div style='background:#EAF7F2; padding:1.5rem; border-radius:12px; text-align:center; border-bottom:3px solid #059669;'>
            <h3 style='color:#1A3C2E; margin:0 0 0.4rem 0;'>Observations</h3>
            <p style='color:#4A5568; margin:0;'>Record your child's daily behaviours</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Observations", use_container_width=True):
        st.switch_page("pages/4_Observations.py")

with col3:
    st.markdown("""
        <div style='background:#F3EFFE; padding:1.5rem; border-radius:12px; text-align:center; border-bottom:3px solid #7C3AED;'>
            <h3 style='color:#2D1B5C; margin:0 0 0.4rem 0;'>AI Chat</h3>
            <p style='color:#4A5568; margin:0;'>Get personalised intervention guidance</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to AI Chat", use_container_width=True):
        st.switch_page("pages/5_AI_Chat.py")

with col4:
    st.markdown("""
        <div style='background:#FEF9E8; padding:1.5rem; border-radius:12px; text-align:center; border-bottom:3px solid #D97706;'>
            <h3 style='color:#4A2C07; margin:0 0 0.4rem 0;'>Progress</h3>
            <p style='color:#4A5568; margin:0;'>Track your child's progress over time</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Progress", use_container_width=True):
        st.switch_page("pages/6_Progress.py")

st.markdown("---")
selected = st.session_state.get("selected_child")
if selected:
    st.success(f"Currently viewing: **{selected['name']}** — Age {selected['age']}")
else:
    st.info("No child selected. Go to Child Profile to select or create one.")
