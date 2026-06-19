import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from observations import submit_observation, get_child_observations
from sidebar import render_sidebar

st.set_page_config(page_title="AutiSense - Observations", page_icon=None, layout="wide")

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

# Show submission feedback from the previous rerun
if st.session_state.pop("obs_just_submitted", False):
    obs_valid = st.session_state.pop("obs_submission_valid", True)
    obs_msg = st.session_state.pop("obs_msg", "Observation submitted.")

    if obs_valid:
        st.markdown(f"""
        <div style='background:#f0fdf4; border:1px solid #86efac; border-radius:8px;
                    padding:12px 18px; margin-bottom:8px; color:#166534; font-weight:500;'>
            {obs_msg}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background:#fff8e1; border:1px solid #ffd54f; border-radius:8px;
                    padding:12px 18px; margin-bottom:8px; color:#7d5a00; font-weight:500;'>
            {obs_msg}
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"### Recording observation for: **{selected_child['name']}**")
st.markdown(f"Focus areas: {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

focus_areas = selected_child.get("focus_areas", [])

st.markdown("#### What did you observe today?")
st.markdown(
    "<small style='color:#888;'>Select the relevant focus area, then describe your child's behaviour, "
    "interactions, or progress.</small>",
    unsafe_allow_html=True
)

with st.form("observation_form", clear_on_submit=True):
    focus_area = st.selectbox(
        "Focus Area",
        options=focus_areas,
        help="Select the area this observation relates to."
    )
    observation_text = st.text_area(
        "Observation",
        placeholder="e.g. Today, my child maintained eye contact during our conversation for longer than usual. They also initiated play with their sibling twice.",
        height=200,
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Submit Observation", use_container_width=True, type="primary")

if submitted:
    if not focus_areas:
        st.error("No focus areas are defined for this child. Please update the child profile first.")
    elif not observation_text.strip():
        st.error("Please write an observation before submitting.")
    elif len(observation_text.strip()) < 20:
        st.error("Please write a more detailed observation (at least 20 characters).")
    else:
        success, is_valid, msg = submit_observation(
            selected_child["child_id"], focus_area, observation_text
        )
        if success:
            st.session_state.obs_just_submitted = True
            st.session_state.obs_submission_valid = is_valid
            st.session_state.obs_msg = msg
            st.rerun()
        else:
            st.error(msg)

st.markdown("---")
st.markdown("#### Past Observations")

if "obs_display_limit" not in st.session_state:
    st.session_state.obs_display_limit = 10

observations = get_child_observations(selected_child["child_id"], limit=st.session_state.obs_display_limit + 1)

if not observations:
    st.info("No observations recorded yet.")
else:
    has_more = len(observations) > st.session_state.obs_display_limit
    visible = observations[:st.session_state.obs_display_limit]

    for obs in visible:
        with st.container():
            col_date, col_tag = st.columns([3, 1])
            with col_date:
                st.markdown(f"**{obs['submitted_at'].strftime('%d %b %Y, %H:%M')}**")
            with col_tag:
                area = obs.get("focus_area", "")
                if area:
                    st.markdown(
                        f"<span style='background:#E8F5F2; color:#2D7D6F; padding:2px 8px; "
                        f"border-radius:12px; font-size:0.8rem;'>{area}</span>",
                        unsafe_allow_html=True
                    )
            st.markdown(obs["observation_text"])
            st.markdown("---")

    if has_more:
        if st.button("Load more", use_container_width=False):
            st.session_state.obs_display_limit += 10
            st.rerun()
