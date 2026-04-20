import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from children import create_child_profile, get_user_children, update_child_profile, delete_child_profile, FOCUS_AREAS
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AutiSense - Child Profile", page_icon="🌿", layout="wide")

if "user" not in st.session_state or not st.session_state.user:
    st.switch_page("pages/1_Login.py")

user = st.session_state.user
user_id = user["user_id"]

with st.sidebar:
    st.markdown("### AutiSense")
    st.markdown(f"<small>Logged in as <b>{user['email']}</b></small>", unsafe_allow_html=True)
    st.markdown("---")
    selected = option_menu(
        menu_title=None,
        options=["Home", "Child Profile", "Observations", "AI Chat", "Progress"],
        icons=["house", "person", "pencil", "chat-dots", "bar-chart"],
        default_index=1,
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
elif selected == "Observations":
    st.switch_page("pages/4_Observations.py")
elif selected == "AI Chat":
    st.switch_page("pages/5_AI_Chat.py")
elif selected == "Progress":
    st.switch_page("pages/6_Progress.py")

st.markdown("<h2 style='color:#2D7D6F;'>Child Profile</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Manage your child's profile and focus areas.</p>", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.get("child_just_created"):
    child_name = st.session_state.get("child_just_created_name", "your child")
    st.toast(f"Profile for {child_name} created successfully!")
    st.session_state.child_just_created = False

children = get_user_children(user_id)

tab1, tab2 = st.tabs(["My Children", "Add New Child"])

with tab1:
    if not children:
        st.info("No child profiles yet. Go to 'Add New Child' to create one!")
    else:
        for child in children:
            with st.expander(f"{child['name']} — Age {child['age']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Focus Areas:** {', '.join(child['focus_areas'])}")
                    st.markdown(f"**Created:** {child['created_at'].strftime('%d %b %Y')}")
                with col2:
                    if st.button("Select", key=f"select_{child['child_id']}"):
                        st.session_state.selected_child = child
                        st.success(f"Selected: {child['name']}")

                st.markdown("##### Edit Profile")
                new_name = st.text_input("Name", value=child["name"], key=f"name_{child['child_id']}")
                new_age = st.text_input("Age", value=str(child["age"]), key=f"age_{child['child_id']}")
                new_focus = st.multiselect("Focus Areas", FOCUS_AREAS, default=child["focus_areas"], key=f"focus_{child['child_id']}")

                col3, col4 = st.columns(2)
                with col3:
                    if st.button("Save Changes", key=f"save_{child['child_id']}"):
                        if not new_name or not new_focus:
                            st.error("Name and at least one focus area are required.")
                        elif not new_age.isdigit() or not (1 <= int(new_age) <= 18):
                            st.error("Please enter a valid age between 1 and 18.")
                        else:
                            update_child_profile(child["child_id"], new_name, int(new_age), new_focus)
                            st.success("Profile updated!")
                            st.rerun()
                with col4:
                    if st.button("Delete Profile", key=f"delete_{child['child_id']}"):
                        delete_child_profile(child["child_id"])
                        st.success("Profile deleted.")
                        st.rerun()

with tab2:
    st.markdown("### Add a new child profile")

    name = st.text_input("Child's name")
    age = st.text_input("Child's age", placeholder="e.g. 7")
    focus_areas = st.multiselect(
        "Focus areas",
        FOCUS_AREAS,
        help="Select the areas you'd like AutiSense to focus on"
    )

    st.markdown("""
        <small style='color:#888;'>
        AutiSense uses this information to personalise guidance for your child.
        This is not a diagnostic tool — please consult a professional for clinical advice.
        </small>
    """, unsafe_allow_html=True)
    st.markdown("")

    if st.button("Create Profile", use_container_width=True, disabled=st.session_state.get("creating_profile", False)):
        if not name:
            st.error("Please enter your child's name.")
        elif not age or not age.isdigit() or not (1 <= int(age) <= 18):
            st.error("Please enter a valid age between 1 and 18.")
        elif not focus_areas:
            st.error("Please select at least one focus area.")
        else:
            st.session_state.creating_profile = True
            success, msg = create_child_profile(user_id, name, int(age), focus_areas)
            if success:
                children_updated = get_user_children(user_id)
                for c in children_updated:
                    if c["name"] == name:
                        st.session_state.selected_child = c
                        break
                st.session_state.child_just_created = True
                st.session_state.child_just_created_name = name
                st.session_state.creating_profile = False
                st.switch_page("pages/3_Child_Profile.py")
            else:
                st.session_state.creating_profile = False
                st.error(msg)
