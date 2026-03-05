import os
import streamlit as st

st.set_page_config(page_title="LSM App Log In", layout="centered")

APP_PASSWORD = os.getenv("admin", "Spigen4545")

def logout():
    st.session_state.logged_in = False

def login_form():

    st.markdown(
        """
        <style>
        .login-container {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("""
        <div class="login-container">
            <div class="login-title">🚚 슈파센 LSM Website</div>
            <div class="login-subtitle">로그인을 해주세요</div>
        """, unsafe_allow_html=True)

        with st.form("login"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Log in")

            if submitted:
                if username == "admin" and password == APP_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        st.markdown("</div>", unsafe_allow_html=True)

# Initialize session flag
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Gate ---
if not st.session_state.logged_in:
    login_form()
    st.stop()

# --- Your app content after login ---
st.sidebar.button("Log out", on_click=logout)

st.title("👋 안녕하세요! LSM 웹입니다!")
st.write("앱을 설치할 예정입니다!")

# Example protected content
st.button("Create OS Tracker")