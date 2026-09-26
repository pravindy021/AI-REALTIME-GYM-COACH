import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.title("🏋️‍♂️ AI-GYM-TRAINER")
    st.markdown("### Welcome! Please sign in to access the full coaching experience.")
    st.info("Only registered users can view the app dashboard, weekly plan builder, and live coaching tools.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Email", placeholder="e.g. abcd@gmail.com")
        submit_button = st.form_submit_button("Enter Dashboard", width="stretch")

    if submit_button:
        if not username:
            st.error("Email cannot be empty.")
            return False

        user = get_or_create_user(username)

        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]
        st.session_state["auth_ready"] = True

        st.rerun()

    return False
    
