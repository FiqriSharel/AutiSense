import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from observations import submit_observation, get_child_observations
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - Observations", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user

if user.get("role") == "admin":
    st.switch_page("pages/7_Admin_Home.py")

if not st.session_state.get("selected_child"):
    st.switch_page("pages/3_Child_Profile.py")
selected_child = st.session_state.selected_child
render_sidebar(user)

st.markdown("<h2 style='color:#2D7D6F;'>Observations</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Record your child's daily behaviours and interactions.</p>", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.pop("obs_just_submitted", False):
    st.markdown("""
    <div style='background:#f0fdf4; border:1px solid #86efac; border-radius:8px;
                padding:12px 18px; margin-bottom:8px; color:#166534; font-weight:500;'>
        Observation submitted successfully.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"### Recording observation for: **{selected_child['name']}**")
st.markdown(f"Focus areas: {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

st.markdown("#### What did you observe today?")
st.markdown(
    "<small style='color:#888;'>Describe your child's behaviour, interactions, or progress. Be as detailed as you like.</small>",
    unsafe_allow_html=True
)

with st.form("observation_form", clear_on_submit=True):
    observation_text = st.text_area(
        "Observation",
        placeholder="e.g. Today, my child maintained eye contact during our conversation for longer than usual. They also initiated play with their sibling twice.",
        height=200,
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Submit Observation", use_container_width=True, type="primary")

if submitted:
    if not observation_text.strip():
        st.error("Please write an observation before submitting.")
    elif len(observation_text.strip()) < 20:
        st.error("Please write a more detailed observation (at least 20 characters).")
    else:
        success, msg = submit_observation(selected_child["child_id"], observation_text)
        if success:
            st.session_state.obs_just_submitted = True
            st.rerun()
        else:
            st.error(msg)

st.markdown("---")
st.markdown("#### Past Observations")

observations = get_child_observations(selected_child["child_id"])
if not observations:
    st.info("No observations recorded yet.")
else:
    for obs in observations:
        with st.container():
            st.markdown(f"**{obs['submitted_at'].strftime('%d %b %Y, %H:%M')}**")
            st.markdown(obs["observation_text"])
            st.markdown("---")
