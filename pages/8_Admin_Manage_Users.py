import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from sidebar import render_sidebar
from database import get_users_collection
from session_manager import init_session

st.set_page_config(page_title="AutiSense - Manage Users", page_icon="🌿", layout="wide")

init_session()

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

if st.session_state.user.get("role") != "admin":
    st.switch_page("pages/2_Home.py")

user = st.session_state.user
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>Manage User Accounts</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>View and manage registered caregiver accounts.</p>", unsafe_allow_html=True)
st.markdown("---")

users_col = get_users_collection()
caregivers = list(users_col.find({"role": "caregiver"}, {"password_hash": 0, "_id": 0}))

if not caregivers:
    st.info("No caregiver accounts registered yet.")
else:
    st.markdown(f"**{len(caregivers)} caregiver(s) registered**")
    st.markdown("")

    for u in caregivers:
        uid = u["user_id"]
        email = u.get("email", "—")
        created = u.get("created_at")
        created_str = created.strftime("%d %b %Y") if created else "—"
        is_active = u.get("is_active", True)

        status_color = "#16a34a" if is_active else "#dc2626"
        status_label = "Active" if is_active else "Deactivated"

        with st.expander(f"{email}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Email:** {email}")
                st.markdown(f"**Registered:** {created_str}")
                st.markdown(
                    f"**Status:** <span style='color:{status_color}; font-weight:600;'>{status_label}</span>",
                    unsafe_allow_html=True
                )

            with col2:
                toggle_label = "Reactivate" if not is_active else "Deactivate"
                if st.button(toggle_label, key=f"toggle_{uid}", use_container_width=True):
                    users_col.update_one(
                        {"user_id": uid},
                        {"$set": {"is_active": not is_active}}
                    )
                    action = "reactivated" if not is_active else "deactivated"
                    st.toast(f"{email} {action}.")
                    st.rerun()

                if st.button("Delete", key=f"delete_{uid}", use_container_width=True):
                    users_col.delete_one({"user_id": uid})
                    st.toast(f"{email} deleted.")
                    st.rerun()
