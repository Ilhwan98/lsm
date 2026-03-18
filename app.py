import os
import streamlit as st
import subprocess

# st.markdown(
#     """
#     <style>
#     /* This targets the specific GitHub icon link container in the main menu */
#     [data-testid="stHeader"] .css-1jc7ptx, 
#     [data-testid="stHeader"] .css-1oe5kzh {
#         display: none !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )



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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_form()
    st.stop()

st.sidebar.success(f"✅ Logged in as {st.session_state.get('user','admin')}")
st.sidebar.button("Log out", on_click=logout)

st.title("👋 안녕하세요! LSM 웹입니다!")
st.caption("원하는 기능을 선택하세요.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 Create OS Tracker", use_container_width=True):
        st.session_state.page = "os"

with col2:
    if st.button("📊 View Reports", use_container_width=True):
        st.session_state.page = "reports"

with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.page = "settings"

if "page" not in st.session_state:
    st.session_state.page = "os"

st.divider()

# if st.session_state.page == "os":
#     st.subheader("📦 OS Tracker")
#     st.write("OS Tracker content here…")

# elif st.session_state.page == "reports":
#     st.subheader("📊 Reports")
#     st.write("Reports content here…")

# elif st.session_state.page == "settings":
#     st.subheader("⚙️ Settings")
#     st.write("Settings here…")

if st.button("Run Commercial Invoice"):
    result = subprocess.run(
        ["python", "TCC-commercial_invoice_cloud.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.success("Script ran successfully")
        st.text(result.stdout)
    else:
        st.error("Script failed")
        st.text(result.stderr)