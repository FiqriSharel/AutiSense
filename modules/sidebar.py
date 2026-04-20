import streamlit as st

def render_sidebar(user):
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### AutiSense")
        st.markdown(f"Logged in as **{user['email']}**")
        st.markdown("---")
        if st.button("Home", use_container_width=True):
            st.switch_page("pages/2_Home.py")
        if st.button("Child Profile", use_container_width=True):
            st.switch_page("pages/3_Child_Profile.py")
        if st.button("Observations", use_container_width=True):
            st.switch_page("pages/4_Observations.py")
        if st.button("AI Chat", use_container_width=True):
            st.switch_page("pages/5_AI_Chat.py")
        if st.button("Progress", use_container_width=True):
            st.switch_page("pages/6_Progress.py")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.switch_page("pages/1_Login.py")
