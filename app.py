import streamlit as st
import sqlite3
from db import init_db, seed_demo_data
from auth import login_form, register_form, logout, get_current_user
from host import host_dashboard
from vendor import vendor_dashboard
from guest import guest_dashboard
import os

# Page config
st.set_page_config(
    page_title="Shaadi Manager",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
if not os.path.exists("wedding_app.db"):
    init_db()
    seed_demo_data()

st.title("💍 Shaadi Manager")
st.markdown("---")

# Sidebar Navigation
with st.sidebar:
    st.header("👤 User Panel")
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_form()
        with tab2:
            register_form()
    else:
        st.success(f"Welcome, {st.session_state.user['name']}!")
        st.info(f"Role: {st.session_state.user['role'].title()}")
        if st.button("🚪 Logout"):
            logout()
            st.rerun()

# Role-based dashboard
user = get_current_user()
if user:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📋 Navigation")
    
    if user['role'] == 'host':
        host_dashboard()
    elif user['role'] == 'vendor':
        vendor_dashboard()
    elif user['role'] == 'guest':
        guest_dashboard()
else:
    st.info("🔐 Please login to access your dashboard!")
    st.balloons()
