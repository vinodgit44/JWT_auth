import streamlit as st
import requests
from jose import jwt
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="JWT Demo", page_icon="🔐")
st.title("🔐 JWT Authentication Demo")

# ---------------- COOKIE MANAGER ----------------
cookies = EncryptedCookieManager(
    prefix="jwt_demo",
    password="CHANGE_THIS_COOKIE_SECRET"
)

if not cookies.ready():
    st.stop()

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    # Load token from cookie if exists
    st.session_state.token = cookies.get("token")

# ---------------- LOGIN ----------------
if not st.session_state.token:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
        )

        if res.status_code == 200:
            token = res.json()["access_token"]

            # Save token in session + cookie
            st.session_state.token = token
            cookies["token"] = token
            cookies.save()

            st.success("✅ Login successful")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

# ---------------- AUTHENTICATED VIEW ----------------
else:
    token = st.session_state.token

    st.subheader("🔑 JWT Token Info")

    # Show raw token
    st.text_area(
        "JWT Token",
        token,
        height=130
    )

    # Decode token WITHOUT verification (frontend-safe)
    decoded = jwt.get_unverified_claims(token)

    exp_timestamp = decoded.get("exp")
    exp_time = datetime.fromtimestamp(exp_timestamp)
    now = datetime.now()
    remaining = exp_time - now

    st.markdown(f"""
**Token Details**
- 👤 User: `{decoded.get("sub")}`
- ⏰ Expires at: `{exp_time}`
- ⏳ Time remaining: `{remaining}`
""")

    if remaining.total_seconds() <= 0:
        st.error("⚠️ Token expired")
    else:
        st.success("✅ Token is valid")

    st.divider()

    # ---------------- CALCULATOR ----------------
    st.subheader("🧮 Protected Calculator")

    a = st.number_input("Number A", value=0)
    b = st.number_input("Number B", value=0)

    if st.button("Calculate"):
        headers = {
            "Authorization": f"Bearer {token}"
        }

        res = requests.get(
            f"{API_URL}/calculate",
            params={"a": a, "b": b},
            headers=headers
        )

        if res.status_code == 200:
            st.success(f"Result: {res.json()['result']}")
        else:
            st.error("❌ Authentication failed (token expired or invalid)")

    st.divider()

    # ---------------- LOGOUT ----------------
    if st.button("Logout"):
        st.session_state.token = None
        cookies["token"] = ""
        cookies.save()
        st.rerun()

