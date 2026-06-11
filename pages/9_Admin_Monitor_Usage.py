import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from sidebar import render_sidebar
from database import (
    get_users_collection, get_children_collection,
    get_observations_collection, get_interactions_collection
)
from session_manager import init_session

st.set_page_config(page_title="AutiSense - System Usage", page_icon="🌿", layout="wide")

init_session()

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

if st.session_state.user.get("role") != "admin":
    st.switch_page("pages/2_Home.py")

user = st.session_state.user
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>Monitor System Usage</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Platform-wide activity and statistics.</p>", unsafe_allow_html=True)
st.markdown("---")

total_users = get_users_collection().count_documents({"role": "caregiver"})
total_children = get_children_collection().count_documents({})
total_observations = get_observations_collection().count_documents({})
total_interactions = get_interactions_collection().count_documents({})

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", total_users)
col2.metric("Total Child Profiles", total_children)
col3.metric("Total Observations", total_observations)
col4.metric("Total AI Interactions", total_interactions)
