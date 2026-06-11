import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from sidebar import render_sidebar
from database import get_interactions_collection, get_children_collection, get_users_collection
from session_manager import init_session
import pandas as pd

st.set_page_config(page_title="AutiSense - AI Logs", page_icon="🌿", layout="wide")

init_session()

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

if st.session_state.user.get("role") != "admin":
    st.switch_page("pages/2_Home.py")

user = st.session_state.user
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>Review AI Behaviour Logs</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Most recent 100 AI chat interactions across all users.</p>", unsafe_allow_html=True)
st.markdown("---")

logs = list(
    get_interactions_collection()
    .find({}, {"_id": 0})
    .sort("created_at", -1)
    .limit(100)
)

if not logs:
    st.info("No logs available.")
else:
    children_map = {
        c["child_id"]: c
        for c in get_children_collection().find({}, {"_id": 0})
    }
    users_map = {
        u["user_id"]: u["email"]
        for u in get_users_collection().find({}, {"_id": 0, "password_hash": 0})
    }

    rows = []
    for log in logs:
        child = children_map.get(log.get("child_id"), {})
        rows.append({
            "Timestamp": log["created_at"].strftime("%d %b %Y, %H:%M") if log.get("created_at") else "—",
            "User": users_map.get(child.get("user_id", ""), "Unknown"),
            "Child": child.get("name", "Unknown"),
            "Message Summary": log.get("user_message_summary", "—"),
            "Response Summary": log.get("response_summary", "—"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
