import streamlit as st
import uuid
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_database

COOKIE_NAME = "autisense_session"
SESSION_DAYS = 7


def _sessions():
    return get_database()["sessions"]


def _cm():
    """Return the CookieManager for this script run, creating it at most once."""
    import extra_streamlit_components as stx
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        run_id = ctx.script_run_id if ctx else None
    except Exception:
        run_id = None

    if st.session_state.get("_cm_run_id") != run_id or "_cm_instance" not in st.session_state:
        st.session_state._cm_run_id = run_id
        st.session_state._cm_instance = stx.CookieManager(key="autisense_cm")

    return st.session_state._cm_instance


def init_session():
    """Restore user from a persistent cookie if session_state has no user."""
    if st.session_state.get("user"):
        return
    cm = _cm()
    token = cm.get(COOKIE_NAME)
    if not token:
        return
    session = _sessions().find_one({"token": token})
    if not session:
        return
    if datetime.utcnow() > session.get("expires_at", datetime.max):
        _sessions().delete_one({"token": token})
        return
    st.session_state.user = session["user"]
    st.session_state._autisense_token = token


def set_session(user):
    """Create a persistent session token, store in DB, and set the cookie."""
    cm = _cm()
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=SESSION_DAYS)
    _sessions().insert_one({
        "token": token,
        "user": {k: user.get(k) for k in ("user_id", "email", "role")},
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
    })
    cm.set(COOKIE_NAME, token, expires_at=expires_at)
    st.session_state._autisense_token = token


def clear_session():
    """Delete the session from DB and clear the cookie."""
    cm = _cm()
    token = st.session_state.pop("_autisense_token", None) or cm.get(COOKIE_NAME)
    if token:
        _sessions().delete_one({"token": token})
        cm.delete(COOKIE_NAME)
    st.session_state.user = None
