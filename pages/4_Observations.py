import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from observations import submit_observation, get_child_observations, get_progress_record
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AutiSense - Observations", page_icon="🌿", layout="wide")

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
        default_index=2,
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

if selected == "Home":
    st.switch_page("pages/2_Home.py")
elif selected == "Child Profile":
    st.switch_page("pages/3_Child_Profile.py")
elif selected == "AI Chat":
    st.switch_page("pages/5_AI_Chat.py")
elif selected == "Progress":
    st.switch_page("pages/6_Progress.py")

st.markdown("<h2 style='color:#2D7D6F;'>Observations</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Record your child's daily behaviours and interactions.</p>", unsafe_allow_html=True)
st.markdown("---")

selected_child = st.session_state.get("selected_child")
if not selected_child:
    st.warning("No child selected. Please select a child profile first.")
    if st.button("Go to Child Profile"):
        st.switch_page("pages/3_Child_Profile.py")
    st.stop()

st.markdown(f"### Recording observation for: **{selected_child['name']}**")
st.markdown(f"Focus areas: {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

tab1, tab2 = st.tabs(["New Observation", "Past Observations"])

with tab1:
    st.markdown("#### What did you observe today?")
    st.markdown("<small style='color:#888;'>Describe your child's behaviour, interactions, or progress today. Be as detailed as you like.</small>", unsafe_allow_html=True)

    observation_text = st.text_area(
        "Observation",
        placeholder="e.g. Today, my child maintained eye contact during our conversation for longer than usual. They also initiated play with their sibling twice.",
        height=200,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        char_count = len(observation_text)
        st.caption(f"{char_count} characters")

    if st.button("Submit Observation", use_container_width=True, type="primary"):
        if not observation_text.strip():
            st.error("Please write an observation before submitting.")
        elif len(observation_text.strip()) < 20:
            st.error("Please write a more detailed observation (at least 20 characters).")
        else:
            success, msg = submit_observation(selected_child["child_id"], observation_text)
            if success:
                st.toast("Observation saved!")
                st.success(msg)
                record = get_progress_record(selected_child["child_id"])
                if record:
                    st.info(f"Progress level updated: **{record['progress_level']}** (Score: {record['composite_score']}/100)")
                st.rerun()
            else:
                st.error(msg)

with tab2:
    observations = get_child_observations(selected_child["child_id"])
    if not observations:
        st.info("No observations recorded yet.")
    else:
        for obs in observations:
            with st.container():
                st.markdown(f"**{obs['submitted_at'].strftime('%d %b %Y, %H:%M')}**")
                st.markdown(obs["observation_text"])
                st.markdown("---")
