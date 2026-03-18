import os
import streamlit as st
import requests

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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("Ilhwan98/lsm")         
GITHUB_WORKFLOW = os.getenv("GITHUB_WORKFLOW", "run_invoice.yml")
GITHUB_REF = os.getenv("GITHUB_REF", "main")







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




def trigger_github_workflow():
    if not GITHUB_TOKEN:
        return False, "Missing GITHUB_TOKEN"
    if not GITHUB_REPO:
        return False, "Missing GITHUB_REPO"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{GITHUB_WORKFLOW}/dispatches"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    payload = {
        "ref": GITHUB_REF
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code == 204:
        return True, "GitHub Actions workflow triggered successfully."
    return False, f"{response.status_code}: {response.text}"


if st.session_state.page == "os":
    st.subheader("📦 OS Tracker")
    st.write("OS Tracker content here…")

    if st.button("🚀 Run Commercial Invoice", use_container_width=True):
        with st.spinner("Triggering cloud job..."):
            ok, message = trigger_github_workflow()

        if ok:
            st.success(message)
            st.info("The script is now running on GitHub Actions, even if your computer is off.")
        else:
            st.error("Failed to trigger workflow")
            st.code(message)