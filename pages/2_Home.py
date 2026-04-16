import streamlit as st

st.set_page_config(page_title="AutiSense - Home", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user

with st.sidebar:
    st.markdown("### 🌿 AutiSense")
    st.markdown(f"Logged in as **{user['email']}**")
    st.markdown("---")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/2_Home.py")
    if st.button("👶 Child Profile", use_container_width=True):
        st.switch_page("pages/3_Child_Profile.py")
    if st.button("💬 AI Chat", use_container_width=True):
        st.switch_page("pages/4_AI_Chat.py")
    if st.button("📊 Progress", use_container_width=True):
        st.switch_page("pages/5_Progress.py")
    st.markdown("---")
    if st.button("📝 Observations", use_container_width=True):
        st.switch_page("pages/3b_Observations.py")
    if st.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.switch_page("pages/1_Login.py")

st.markdown(f"<h2 style='color:#2D7D6F;'>Welcome to AutiSense 🌿</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#555;'>Logged in as: <b>{user['email']}</b></p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='background:#E8F5F2; padding:1.5rem; border-radius:12px; text-align:center;'>
            <h3>👶 Child Profile</h3>
            <p>Set up and manage your child's profile</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Child Profile", use_container_width=True):
        st.switch_page("pages/3_Child_Profile.py")

with col2:
    st.markdown("""
        <div style='background:#E8F5F2; padding:1.5rem; border-radius:12px; text-align:center;'>
            <h3>💬 AI Chat</h3>
            <p>Get personalised intervention guidance</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to AI Chat", use_container_width=True):
        st.switch_page("pages/4_AI_Chat.py")

with col3:
    st.markdown("""
        <div style='background:#E8F5F2; padding:1.5rem; border-radius:12px; text-align:center;'>
            <h3>📊 Progress</h3>
            <p>Track your child's progress over time</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Progress", use_container_width=True):
        st.switch_page("pages/5_Progress.py")

st.markdown("---")
selected = st.session_state.get("selected_child")
if selected:
    st.success(f"Currently viewing: **{selected['name']}** — Age {selected['age']}")
else:
    st.info("No child selected. Go to Child Profile to select or create one.")