import streamlit as st
from db import get_vendor_by_id, add_team_member, get_team_members, add_photo
import streamlit as st

def vendor_dashboard():
    user = st.session_state.user
    vendor = get_vendor_by_id(user['id'])
    
    tab1, tab2, tab3, tab4 = st.tabs(["👨‍💼 Profile", "👥 Team", "📅 Bookings", "📸 Photos"])
    
    with tab1:
        st.header("👨‍💼 Vendor Profile")
        st.metric("Business", vendor['business_name'])
        st.metric("Category", vendor['category'])
        st.metric("Rating", f"{vendor['rating']} ⭐")
        st.info(vendor['description'])
    
    with tab2:
        st.header("👥 Team Management")
        
        with st.form("add_team"):
            col1, col2, col3 = st.columns(3)
            with col1: name = st.text_input("Name")
            with col2: email = st.text_input("Email")
            with col3: role = st.selectbox("Role", ["Photographer", "Assistant", "Manager"])
            permissions = st.multiselect("Permissions", ["Upload Photos", "Manage Bookings", "Edit Profile"])
            if st.form_submit_button("➕ Add Member"):
                add_team_member(vendor['id'], name, email, role, permissions)
                st.success("Added!")
        
        members = get_team_members(vendor['id'])
        if members:
            st.dataframe(pd.DataFrame(members))
    
    with tab3:
        st.header("📅 Bookings")
        st.info("📋 No bookings yet. Check back later!")
        col1, col2 = st.columns(2)
        col1.metric("Pending", 0)
        col2.metric("Confirmed", 0)
    
    with tab4:
        st.header("📸 Upload Photos")
        wedding_id = st.number_input("Wedding ID", min_value=1)
        uploaded_files = st.file_uploader("Choose photos", accept_multiple_files=True)
        
        col1, col2 = st.columns(2)
        with col1:
            sneak_peek = st.checkbox("Mark as Sneak Peek")
        with col2:
            uploaded_by = st.text_input("Uploaded By", value=user['name'])
        
        if st.button("📤 Upload") and uploaded_files:
            for file in uploaded_files:
                # Simulate upload
                st.success(f"Uploaded: {file.name}")
                add_photo(wedding_id, f"/photos/{file.name}", sneak_peek, uploaded_by)
            st.success("All photos uploaded!")
