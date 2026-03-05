import os
import streamlit as st

st.set_page_config(page_title="LSM App Log In", layout="centered")

APP_PASSWORD = os.getenv("admin", "Spigen4545")

def logout():
    st.session_state.logged_in = False

def login_form():
    st.title("🚚 슈피겐 LSM Website")
    st.write("Please log in")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if username == "admin" and  password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password")

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

st.markdown("""
<style>

/* Hide Streamlit footer */
footer {visibility: hidden;}

/* Hide Streamlit hamburger menu */
#MainMenu {visibility: hidden;}

/* Hide deploy / GitHub toolbar */
[data-testid="stDecoration"] {
    display: none;
}

/* Hide bottom-right floating buttons */
button[kind="secondary"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)