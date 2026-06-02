import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - Admin", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

if st.session_state.user.get("role") != "admin":
    st.switch_page("pages/2_Home.py")

user = st.session_state.user
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>Admin Panel</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#555;'>Logged in as <b>{user['email']}</b></p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='background:#EAF4FE; padding:1.5rem; border-radius:12px;
                    text-align:center; border-bottom:3px solid #2563EB;'>
            <h3 style='color:#1E3A5F; margin:0 0 0.4rem 0;'>Manage Users</h3>
            <p style='color:#4A5568; margin:0;'>View, edit, and manage caregiver accounts</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Manage Users", use_container_width=True):
        st.switch_page("pages/8_Admin_Manage_Users.py")

with col2:
    st.markdown("""
        <div style='background:#EAF7F2; padding:1.5rem; border-radius:12px;
                    text-align:center; border-bottom:3px solid #059669;'>
            <h3 style='color:#1A3C2E; margin:0 0 0.4rem 0;'>System Usage</h3>
            <p style='color:#4A5568; margin:0;'>Monitor platform activity and statistics</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to System Usage", use_container_width=True):
        st.switch_page("pages/9_Admin_Monitor_Usage.py")

with col3:
    st.markdown("""
        <div style='background:#F3EFFE; padding:1.5rem; border-radius:12px;
                    text-align:center; border-bottom:3px solid #7C3AED;'>
            <h3 style='color:#2D1B5C; margin:0 0 0.4rem 0;'>AI Behaviour Logs</h3>
            <p style='color:#4A5568; margin:0;'>Review AI chat interactions across all users</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to AI Logs", use_container_width=True):
        st.switch_page("pages/10_Admin_AI_Logs.py")
