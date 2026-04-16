import streamlit as st

st.set_page_config(page_title="AutiSense - AI Chat", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

st.markdown("<h2 style='color:#2D7D6F;'>💬 AI Chat</h2>", unsafe_allow_html=True)
st.info("Coming soon — Week 5!")