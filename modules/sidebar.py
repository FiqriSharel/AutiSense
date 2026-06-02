import streamlit as st

NAV_ITEMS = [
    ("🏠", "Home", "pages/2_Home.py"),
    ("👤", "Child Profile", "pages/3_Child_Profile.py"),
    ("📋", "Observations", "pages/4_Observations.py"),
    ("💬", "AI Chat", "pages/5_AI_Chat.py"),
    ("📈", "Progress", "pages/6_Progress.py"),
]

SIDEBAR_CSS = """
<style>
[data-testid="stSidebarNav"] { display: none; }

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    color: #374151;
    text-align: left;
    padding: 0.55rem 0.9rem;
    border-radius: 10px;
    font-size: 0.92rem;
    font-weight: 400;
    width: 100%;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
    margin-bottom: 2px;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8f4f2;
    border-color: #c0e4de;
    color: #2D7D6F;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    box-shadow: none !important;
    outline: none !important;
}

/* Logout button — targeted via adjacent sibling after the marker span */
div:has(#logout-marker) + div .stButton > button {
    color: #991b1b;
}

div:has(#logout-marker) + div .stButton > button:hover {
    background: #fef2f2 !important;
    border-color: #fecaca !important;
    color: #dc2626 !important;
}
</style>
"""


def render_sidebar(user):
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # Brand header
        st.markdown("""
            <div style="text-align:center; padding:1.6rem 0.5rem 1.3rem;">
                <div style="font-size:2.4rem; line-height:1.2;">🌿</div>
                <div style="font-size:1.3rem; font-weight:700; color:#2D7D6F;
                            margin-top:6px; letter-spacing:0.4px;">AutiSense</div>
                <div style="font-size:0.68rem; color:#9ca3af; margin-top:3px;
                            letter-spacing:1px; text-transform:uppercase;">Support & Guidance</div>
            </div>
        """, unsafe_allow_html=True)

        # User chip
        initial = user['email'][0].upper()
        display_name = user['email'].split('@')[0]
        st.markdown(f"""
            <div style="background:#f0faf8; border:1px solid #c9ece5; border-radius:12px;
                        padding:0.6rem 0.85rem; margin-bottom:1.3rem;
                        display:flex; align-items:center; gap:10px;">
                <div style="background:#2D7D6F; color:#fff; border-radius:50%;
                            min-width:34px; height:34px; display:flex;
                            align-items:center; justify-content:center;
                            font-size:0.9rem; font-weight:700; flex-shrink:0;">
                    {initial}
                </div>
                <div style="min-width:0;">
                    <div style="font-size:0.82rem; font-weight:600; color:#1f2937;
                                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {display_name}
                    </div>
                    <div style="font-size:0.7rem; color:#6b7280;">Caregiver</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Section label
        st.markdown("""
            <p style="font-size:0.67rem; font-weight:700; color:#9ca3af;
                      text-transform:uppercase; letter-spacing:1.3px;
                      margin:0 0 6px 4px;">Menu</p>
        """, unsafe_allow_html=True)

        # Nav items
        for icon, label, page in NAV_ITEMS:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{label}"):
                st.switch_page(page)

        # Divider before logout
        st.markdown("""
            <hr style="margin:1.2rem 0 0.8rem; border:none;
                       border-top:1px solid #e5e7eb;">
        """, unsafe_allow_html=True)

        # Logout (styled red via the marker trick)
        st.markdown('<span id="logout-marker"></span>', unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True, key="nav_logout"):
            st.session_state.user = None
            st.switch_page("pages/1_Login.py")
