import streamlit as st
import hashlib
from db import get_user_by_email, create_user
from utils import validate_email

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def login_form():
    with st.form("login_form"):
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            submitted = st.form_submit_button("Login")
        with col2:
            if st.form_submit_button("Demo Login"):
                st.session_state.user = {
                    'id': 1, 'name': 'Priya Sharma', 'email': 'priya@example.com', 'role': 'host'
                }
                st.success("Demo login successful!")
                st.rerun()
        
        if submitted:
            if email and password:
                user = get_user_by_email(email)
                if user and hash_password(password) == user['password']:
                    st.session_state.user = dict(user)
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
            else:
                st.warning("Please fill all fields!")

def register_form():
    with st.form("register_form"):
        st.subheader("📝 Register")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["host", "vendor", "guest"])
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if all([name, email, password]) and validate_email(email):
                user_id = create_user(name, email, password, role)
                if user_id:
                    st.session_state.user = {'id': user_id, 'name': name, 'email': email, 'role': role}
                    st.success("Registration successful!")
                    st.rerun()
                else:
                    st.error("Email already exists!")
            else:
                st.error("Please fill all fields correctly!")

def logout():
    st.session_state.user = None
    st.success("Logged out successfully!")
    st.rerun()

def get_current_user():
    return st.session_state.get('user')
