import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from observations import get_progress_record, get_child_observations
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

st.set_page_config(page_title="AutiSense - Progress", page_icon="🌿", layout="wide")

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
        default_index=4,
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
elif selected == "Observations":
    st.switch_page("pages/4_Observations.py")
elif selected == "AI Chat":
    st.switch_page("pages/5_AI_Chat.py")

st.markdown("<h2 style='color:#2D7D6F;'>Progress Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Track your child's engagement and progress over time.</p>", unsafe_allow_html=True)
st.markdown("---")

selected_child = st.session_state.get("selected_child")
if not selected_child:
    st.warning("No child selected. Please select a child profile first.")
    if st.button("Go to Child Profile"):
        st.switch_page("pages/3_Child_Profile.py")
    st.stop()

st.markdown(f"### Progress for: **{selected_child['name']}**")
st.markdown(f"**Age:** {selected_child['age']}  |  **Focus areas:** {', '.join(selected_child['focus_areas'])}")
st.markdown("---")

record = get_progress_record(selected_child["child_id"])

if not record:
    st.info("No progress data yet. Start by submitting observations!")
    if st.button("Go to Observations"):
        st.switch_page("pages/4_Observations.py")
    st.stop()

level = record.get("progress_level", "Low")
score = record.get("composite_score", 0)
valid_obs = record.get("valid_observations", 0)
active_weeks = record.get("active_weeks", 0)

level_interpretations = {
    "Low": "Limited engagement trend",
    "Medium": "Moderate and emerging consistency",
    "High": "Sustained and consistent engagement",
}
interpretation = level_interpretations.get(level, "")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Progress Level", value=level)
with col2:
    st.metric(label="Observations Recorded", value=valid_obs)
with col3:
    st.metric(label="Active Weeks", value=active_weeks)

style_metric_cards(
    background_color="#E8F5F2",
    border_left_color="#2D7D6F",
    border_color="#C2D8D4",
    box_shadow=False,
)

st.markdown(f"<p style='color:#555; margin-top:0.5rem;'>Interpretation: <b>{interpretation}</b></p>", unsafe_allow_html=True)
st.markdown("---")

score_history = record.get("score_history", [])

if len(score_history) < 2:
    st.info("Keep submitting observations to see your progress graph grow!")
else:
    st.markdown("### Progress Over Time")
    st.markdown("<small style='color:#888;'>The graph shows your child's engagement level over time based on observations submitted.</small>", unsafe_allow_html=True)

    dates = [entry["recorded_at"] for entry in score_history]
    scores = [entry["score"] for entry in score_history]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")

    ax.plot(dates, scores, color="#2D7D6F", linewidth=2.5, marker="o", markersize=6, zorder=3)

    ax.fill_between(dates, 0, 39, alpha=0.08, color="#FFC107", label="_nolegend_")
    ax.fill_between(dates, 40, 69, alpha=0.08, color="#17A2B8", label="_nolegend_")
    ax.fill_between(dates, 70, 100, alpha=0.08, color="#28A745", label="_nolegend_")

    ax.axhline(y=40, color="#FFC107", linestyle="--", linewidth=1, alpha=0.6, zorder=2)
    ax.axhline(y=70, color="#28A745", linestyle="--", linewidth=1, alpha=0.6, zorder=2)

    ax.set_yticks([20, 55, 85])
    ax.set_yticklabels(["Low", "Medium", "High"], color="white", fontsize=12)
    ax.set_ylim(0, 100)

    ax.tick_params(axis="x", colors="white", labelsize=9)
    ax.tick_params(axis="y", colors="white")

    ax.grid(axis="x", linestyle="--", alpha=0.2, color="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#444")
    ax.spines["bottom"].set_color("#444")

    low_patch = mpatches.Patch(color="#FFC107", alpha=0.4, label="Low (0-39)")
    med_patch = mpatches.Patch(color="#17A2B8", alpha=0.4, label="Medium (40-69)")
    high_patch = mpatches.Patch(color="#28A745", alpha=0.4, label="High (70-100)")
    ax.legend(handles=[low_patch, med_patch, high_patch], loc="upper left",
              facecolor="#1E2130", edgecolor="#444", labelcolor="white", fontsize=9)

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

st.markdown("### Get Personalised Activity Suggestions")
st.markdown("<p style='color:#555;'>Based on your child's current progress level, AutiSense can suggest personalised activities tailored to their focus areas.</p>", unsafe_allow_html=True)

focus_areas = selected_child.get("focus_areas", [])
child_name = selected_child.get("name", "your child")

suggestion_prompt = f"Based on {child_name}'s current progress level of {level} and their focus areas of {', '.join(focus_areas)}, what are some specific activities I can do at home this week to help them improve?"

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"""
        <div style='background:#E8F5F2; padding:1rem; border-radius:8px;'>
            <p style='color:#2D7D6F; margin:0; font-size:0.9rem;'>
            <b>Ready to ask:</b> "{suggestion_prompt[:120]}..."
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("Ask AutiSense for suggestions", use_container_width=True, type="primary"):
        st.session_state.starter_message = suggestion_prompt
        st.switch_page("pages/5_AI_Chat.py")

st.markdown("---")
st.markdown("<small style='color:#888;'>⚠️ These suggestions are for support purposes only and do not constitute clinical advice. Please consult a qualified professional for personalised therapy.</small>", unsafe_allow_html=True)
