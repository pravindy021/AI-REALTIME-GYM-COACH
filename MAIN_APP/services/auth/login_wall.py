import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    st.title("🏋️‍♂️ AI-GYM-TRAINER")
    st.markdown("### Welcome! Please enter your E-mail to start.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("E-mail", placeholder="E-mail id: e.g. pravind@domain.com")
        submit_button = st.form_submit_button("Start Session", width="stretch")

    if submit_button:
        if not username:
            st.error("E-mail cannot be empty.")
            return False
        
        user = get_or_create_user(username)
    
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False
    