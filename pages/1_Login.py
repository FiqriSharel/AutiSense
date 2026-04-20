import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from auth import login_user, register_user

st.set_page_config(
    page_title="AutiSense - Login",
    page_icon="🌿",
    layout="centered"
)

# Custom styling
st.markdown("""
    <style>
    .main { background-color: #f0f7f4; }
    .stButton > button {
        background-color: #2D7D6F;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        width: 100%;
    }
    .stButton > button:hover { background-color: #1A5C52; }
    </style>
""", unsafe_allow_html=True)

# Redirect if already logged in
if "user" in st.session_state and st.session_state.user:
    st.switch_page("pages/2_Home.py")

st.markdown("<h1 style='text-align:center; color:#2D7D6F;'>AutiSense</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Personalised ASD Intervention Support</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.markdown("### Welcome back")
    email = st.text_input("Email address", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            success, result = login_user(email, password)
            if success:
                st.session_state.user = result
                st.success("Logged in successfully!")
                st.switch_page("pages/2_Home.py")
            else:
                st.error(result)

with tab2:
    st.markdown("### Create an account")
    reg_email = st.text_input("Email address", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    reg_confirm = st.text_input("Confirm password", type="password", key="reg_confirm")

    st.markdown("""
        <small style='color:#888;'>
        By registering, you agree that AutiSense is a <b>support tool only</b> 
        and not a diagnostic system. Your data will be stored securely and used 
        only to personalise your experience.
        </small>
    """, unsafe_allow_html=True)

    if st.button("Create Account", key="reg_btn"):
        if not reg_email or not reg_password or not reg_confirm:
            st.error("Please fill in all fields.")
        elif reg_password != reg_confirm:
            st.error("Passwords do not match.")
        elif len(reg_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            success, msg = register_user(reg_email, reg_password)
            if success:
                st.success(msg + " Please login.")
            else:
                st.error(msg)