import streamlit as st
from db import get_wedding, update_wedding, add_guest, get_all_guests, delete_guest, get_all_vendors
from utils import create_invitation, generate_invitation_code
import pandas as pd
import io

def host_dashboard():
    user = st.session_state.user
    wedding = get_wedding(user['id'])
    
    tab1, tab2, tab3, tab4 = st.tabs(["👰‍♀️ Wedding Info", "👥 Guest Manager", "✉️ Invitations", "🏪 Vendors"])
    
    with tab1:
        st.header("💍 Wedding Details")
        if wedding:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Couple", wedding['couple_names'])
                st.metric("Date", wedding['event_date'])
                st.metric("Venue", wedding['venue'])
            with col2:
                st.metric("Guests", wedding['guest_count'])
                st.metric("Address", wedding['venue_address'] or "TBD")
        else:
            st.info("Create your wedding details first!")
        
        # Update form
        with st.form("wedding_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                couple = st.text_input("Couple Names", value=wedding['couple_names'] if wedding else "")
            with col2:
                date = st.date_input("Event Date", value=pd.to_datetime(wedding['event_date'] if wedding else "2024-12-25"))
            with col3:
                venue = st.text_input("Venue", value=wedding['venue'] if wedding else "")
            with col4:
                address = st.text_input("Address", value=wedding['venue_address'] if wedding else "")
            
            if st.form_submit_button("💾 Update"):
                update_wedding(user['id'], (couple, str(date), venue, address))
                st.success("Updated!")
                st.rerun()
    
    with tab2:
        st.header("👥 Guest Management")
        
        # Add guest form
        with st.form("add_guest"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: name = st.text_input("Name")
            with col2: email = st.text_input("Email")
            with col3: phone = st.text_input("Phone")
            with col4: category = st.selectbox("Category", ["Family", "Friends", "Work", "Relatives"])
            if st.form_submit_button("➕ Add Guest"):
                code = add_guest(wedding['id'], name, email, phone, category)
                st.success(f"Guest added! Code: **{code}**")
        
        # Guest list
        guests = get_all_guests(wedding['id'])
        if guests:
            df = pd.DataFrame(guests)
            st.dataframe(df, use_container_width=True)
            
            # RSVP Stats
            stats = df['rsvp_status'].value_counts()
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("✅ Confirmed", stats.get('confirmed', 0))
            with col2: st.metric("⏳ Pending", stats.get('pending', 0))
            with col3: st.metric("❌ Declined", stats.get('declined', 0))
            
            # Delete guest
            st.caption("Select guest to delete:")
            selected = st.multiselect("Guests", df['name'].tolist())
            if st.button("🗑️ Delete Selected") and selected:
                for name in selected:
                    guest = df[df['name'] == name].iloc[0]
                    delete_guest(guest['id'])
                st.success("Deleted!")
                st.rerun()
    
    with tab3:
        st.header("✉️ Generate Invitations")
        guest_name = st.text_input("Guest Name")
        if st.button("🎨 Generate Invitation") and guest_name and wedding:
            code = generate_invitation_code()
            path = f"inv_{code}.png"
            create_invitation(guest_name, wedding['couple_names'], wedding['event_date'], wedding['venue'], path)
            st.image(path, caption=f"Invitation for {guest_name}")
            with open(path, "rb") as f:
                st.download_button("💾 Download", f.read(), file_name=path)
    
    with tab4:
        st.header("🏪 Vendor Marketplace")
        category = st.selectbox("Category", ["All", "Photography", "Catering", "Decoration", "DJ"])
        location = st.text_input("Location")
        
        filters = {}
        if category != "All": filters['category'] = category
        if location: filters['location'] = location
        
        vendors = get_all_vendors(filters)
        cols = st.columns(3)
        for i, vendor in enumerate(vendors):
            with cols[i % 3]:
                st.markdown(f"""
                ### {vendor['business_name']}
                **{vendor['category']}** | {vendor['location']}
                {vendor['description']}
                **₹{vendor['min_price']} - ₹{vendor['max_price']}**
                """)
                st.button(f"📞 Contact", key=f"contact_{vendor['id']}")
