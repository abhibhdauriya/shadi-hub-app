import streamlit as st
import sqlite3
from db import initialize_app, get_user_by_email, verify_login, create_user
import os

# Page config
st.set_page_config(
    page_title="Shadi-Hub - Wedding Manager",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Wedding Theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #FFF5E6 0%, #FFFFFF 100%);
    }
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Georgia', serif;
    }
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37, #C5A028);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 8px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #D4AF37;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid #D4AF37;
    }
    div[data-testid="stMetricValue"] {
        color: #D4AF37;
        font-size: 28px;
    }
    .css-1r6slb0 {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
initialize_app()

# Session state setup
if 'user' not in st.session_state:
    st.session_state.user = None

# ==================== AUTHENTICATION FUNCTIONS ====================

def login_form():
    """Login form for users"""
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        submitted = st.form_submit_button("🔐 Login", use_container_width=True)
        
        if submitted:
            if email and password:
                user = verify_login(email, password)
                if user:
                    st.session_state.user = dict(user)
                    st.success(f"Welcome {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password!")
            else:
                st.warning("Please fill all fields")

def register_form():
    """Registration form for new users"""
    with st.form("register_form"):
        name = st.text_input("Full Name", placeholder="Enter your name")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Create password")
        role = st.selectbox("I am a", ["host", "vendor", "guest"], 
                           format_func=lambda x: {"host": "💒 Wedding Host", 
                                                   "vendor": "📸 Service Provider", 
                                                   "guest": "💝 Guest"}[x])
        
        submitted = st.form_submit_button("📝 Register", use_container_width=True)
        
        if submitted:
            if name and email and password:
                user_id = create_user(name, email, password, role)
                if user_id:
                    st.success("Registration successful! Please login.")
                    st.balloons()
                else:
                    st.error("Email already exists!")
            else:
                st.warning("Please fill all fields")

def logout():
    """Logout user"""
    st.session_state.user = None
    st.rerun()

def get_current_user():
    """Get current logged in user"""
    return st.session_state.user

# ==================== HOST DASHBOARD ====================

def host_dashboard():
    """Host dashboard with wedding management"""
    user = get_current_user()
    st.markdown(f"<h1>🌟 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #D4AF37;'>Manage your wedding from here</p>", unsafe_allow_html=True)
    
    from db import (get_wedding_by_host, create_or_update_wedding, get_all_guests, 
                   add_guest, update_guest_rsvp, delete_guest, get_guest_rsvp_stats,
                   get_all_vendors, get_wedding_id_by_host)
    from utils import generate_invitation
    import pandas as pd
    import os
    
    # Get wedding details
    wedding = get_wedding_by_host(user['id'])
    wedding_id = wedding['id'] if wedding else None
    
    # Stats
    if wedding_id:
        stats = get_guest_rsvp_stats(wedding_id)
    else:
        stats = {'confirmed': 0, 'pending': 0, 'declined': 0, 'total': 0}
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Guests", stats['total'])
    with col2:
        st.metric("✅ Confirmed", stats['confirmed'])
    with col3:
        st.metric("⏳ Pending", stats['pending'])
    with col4:
        st.metric("❌ Declined", stats['declined'])
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Wedding Info", "👥 Guest Manager", "🎨 Invitations", "🛍️ Vendors"])
    
    # TAB 1: Wedding Info
    with tab1:
        st.subheader("Wedding Details")
        
        if wedding:
            couple = st.text_input("Couple Names", wedding['couple_names'])
            event_date = st.date_input("Wedding Date", 
                                       pd.to_datetime(wedding['event_date']).date() if wedding['event_date'] else None)
            venue = st.text_input("Venue Name", wedding['venue'])
            venue_address = st.text_area("Venue Address", wedding['venue_address'] if wedding['venue_address'] else "")
            guest_count = st.number_input("Expected Guests", 50, 2000, wedding['guest_count'] or 150)
        else:
            couple = st.text_input("Couple Names", "Rahul & Priya")
            event_date = st.date_input("Wedding Date")
            venue = st.text_input("Venue Name", "Grand Palace")
            venue_address = st.text_area("Venue Address", "")
            guest_count = st.number_input("Expected Guests", 50, 2000, 150)
        
        if st.button("💾 Save Wedding Details", use_container_width=True):
            create_or_update_wedding(user['id'], couple, str(event_date), venue, venue_address, guest_count)
            st.success("✅ Wedding details saved!")
            st.rerun()
    
    # TAB 2: Guest Manager
    with tab2:
        st.subheader("Guest Management")
        
        # Add guest form
        with st.expander("➕ Add New Guest", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                guest_name = st.text_input("Full Name", key="gname")
                guest_email = st.text_input("Email", key="gemail")
            with col2:
                guest_phone = st.text_input("Phone", key="gphone")
                guest_category = st.selectbox("Category", ["Family", "Friend", "Colleague", "Other"], key="gcat")
            
            if st.button("Add Guest", key="add_btn"):
                if guest_name and wedding_id:
                    guest_id, code = add_guest(wedding_id, guest_name, guest_email, guest_phone, guest_category)
                    st.success(f"✅ {guest_name} added! Invitation code: {code}")
                    st.rerun()
                elif not wedding_id:
                    st.warning("Please setup wedding details first in 'Wedding Info' tab")
                else:
                    st.warning("Please enter guest name")
        
        # Guest list
        if wedding_id:
            guests = get_all_guests(wedding_id)
            
            if guests:
                # Convert to list of dicts for display
                guest_data = []
                for guest in guests:
                    guest_data.append({
                        "Name": guest['name'],
                        "Email": guest['email'] or "-",
                        "Phone": guest['phone'] or "-",
                        "Category": guest['category'] or "-",
                        "RSVP": guest['rsvp_status'].title(),
                        "ID": guest['id']
                    })
                
                df = pd.DataFrame(guest_data)
                st.dataframe(df.drop(columns=['ID']), use_container_width=True)
                
                # Delete guest option
                with st.expander("🗑️ Delete Guest"):
                    guest_names = {g['name']: g['id'] for g in guests}
                    selected_guest = st.selectbox("Select guest to delete", list(guest_names.keys()))
                    if st.button("Delete Guest", key="del_btn"):
                        delete_guest(guest_names[selected_guest])
                        st.success(f"Deleted {selected_guest}")
                        st.rerun()
            else:
                st.info("No guests added yet. Use the form above to add guests.")
        else:
            st.warning("Please setup wedding details first in 'Wedding Info' tab")
    
    # TAB 3: Invitations
    with tab3:
        st.subheader("Digital Invitation Generator")
        
        if wedding and wedding_id:
            guests = get_all_guests(wedding_id)
            
            if guests:
                st.markdown("### 🎨 Generate Invitations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Generate for Single Guest", use_container_width=True):
                        guest_options = {g['name']: g['id'] for g in guests}
                        selected_guest = st.selectbox("Select Guest", list(guest_options.keys()))
                        if selected_guest:
                            os.makedirs("invitations", exist_ok=True)
                            path = f"invitations/{selected_guest}.jpg"
                            generate_invitation(selected_guest, wedding['couple_names'], 
                                               wedding['event_date'], wedding['venue'], path)
                            if os.path.exists(path):
                                st.image(path, use_container_width=True)
                                st.success(f"✅ Invitation generated for {selected_guest}")
                
                with col2:
                    if st.button("🎨 Generate for ALL Guests", use_container_width=True):
                        os.makedirs("invitations", exist_ok=True)
                        progress_bar = st.progress(0)
                        for i, guest in enumerate(guests):
                            path = f"invitations/{guest['name']}.jpg"
                            generate_invitation(guest['name'], wedding['couple_names'], 
                                               wedding['event_date'], wedding['venue'], path)
                            progress_bar.progress((i + 1) / len(guests))
                        st.success(f"✅ Generated {len(guests)} invitations!")
                        st.balloons()
            else:
                st.warning("Please add guests first in Guest Manager tab!")
        else:
            st.warning("Please setup wedding details first in 'Wedding Info' tab")
    
    # TAB 4: Vendors
    with tab4:
        st.subheader("Find Wedding Vendors")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Category", ["All", "photographer", "mehndi", "catering", "venue", "decor"])
        with col2:
            price_filter = st.selectbox("Budget", ["All", "budget", "mid-range", "premium", "luxury"])
        with col3:
            location_filter = st.text_input("Location", placeholder="City name")
        
        vendors = get_all_vendors(
            category=None if category_filter == "All" else category_filter,
            price_range=None if price_filter == "All" else price_filter,
            location=location_filter if location_filter else None
        )
        
        if vendors:
            for vendor in vendors:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**{vendor['business_name']}**")
                        st.caption(f"⭐ {vendor['rating']}/5.0 • {vendor['category'].title()}")
                    with col2:
                        st.write(f"💰 {vendor['price_range'].title()}")
                        st.write(f"📍 {vendor['location']}")
                    with col3:
                        if st.button("💝 Contact", key=f"contact_{vendor['id']}"):
                            st.success(f"Inquiry sent to {vendor['business_name']}!")
                    st.divider()
        else:
            st.info("No vendors found with selected filters.")

# ==================== VENDOR DASHBOARD ====================

def vendor_dashboard():
    """Vendor dashboard with team management"""
    user = get_current_user()
    st.markdown(f"<h1>📸 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #D4AF37;'>Manage your business</p>", unsafe_allow_html=True)
    
    from db import get_vendor_by_user_id, add_team_member, get_team_members, delete_team_member
    
    vendor = get_vendor_by_user_id(user['id'])
    
    tab1, tab2 = st.tabs(["👥 Team Management", "📅 Bookings"])
    
    with tab1:
        st.subheader("Add Team Member")
        
        with st.form("add_team_form"):
            col1, col2 = st.columns(2)
            with col1:
                member_name = st.text_input("Full Name")
                member_email = st.text_input("Email Address")
            with col2:
                member_role = st.selectbox("Role", ["photographer", "editor", "assistant", "videographer"])
                permissions = st.multiselect("Permissions", ["upload_photos", "edit_schedule", "view_clients"])
            
            if st.form_submit_button("➕ Add Team Member"):
                if member_name and member_email and vendor:
                    add_team_member(vendor['id'], member_name, member_email, member_role, permissions)
                    st.success(f"✅ {member_name} added as {member_role}!")
                    st.balloons()
                    st.rerun()
                elif not vendor:
                    st.warning("Please complete your vendor profile first!")
                else:
                    st.warning("Please fill all fields")
        
        # Display team
        st.markdown("### 👥 Current Team Members")
        
        if vendor:
            team = get_team_members(vendor['id'])
            
            if team:
                team_data = []
                for member in team:
                    team_data.append({
                        "Name": member['member_name'],
                        "Email": member['member_email'],
                        "Role": member['role'].title(),
                        "Permissions": member['permissions'] or "-",
                        "ID": member['id']
                    })
                
                import pandas as pd
                df = pd.DataFrame(team_data)
                st.dataframe(df.drop(columns=['ID']), use_container_width=True)
                
                # Delete member
                with st.expander("🗑️ Remove Team Member"):
                    member_names = {m['member_name']: m['id'] for m in team}
                    selected_member = st.selectbox("Select member to remove", list(member_names.keys()))
                    if st.button("Remove Member"):
                        delete_team_member(member_names[selected_member])
                        st.success(f"Removed {selected_member}")
                        st.rerun()
            else:
                st.info("No team members yet. Add your first team member above!")
        else:
            st.info("Please complete your vendor profile to add team members.")
    
    with tab2:
        st.subheader("Booking Requests")
        st.info("📌 New booking inquiries will appear here")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Pending", "0")
        with col2:
            st.metric("✅ Confirmed", "0")
        with col3:
            st.metric("🎉 Completed", "0")

# ==================== GUEST DASHBOARD ====================

def guest_dashboard():
    """Guest view dashboard"""
    user = get_current_user()
    st.markdown(f"<h1>💌 Hello {user['name']}!</h1>", unsafe_allow_html=True)
    
    from db import get_wedding_by_id, get_guest_by_email, update_guest_rsvp, update_guest_well_wish
    
    # Get guest details
    guest = get_guest_by_email(user['email'])
    
    if guest and guest['wedding_id']:
        wedding = get_wedding_by_id(guest['wedding_id'])
        
        if wedding:
            st.markdown(f"""
            <div style="background: white; border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0;">
                <h2 style="color: #D4AF37;">✨ You're Invited! ✨</h2>
                <h3 style="color: #8B6914;">{wedding['couple_names']}</h3>
                <p style="font-size: 18px; margin: 20px 0;">Request the pleasure of your company at their wedding celebration</p>
                <div style="height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 30px 0;"></div>
                <p><b>📅 Date:</b> {wedding['event_date']}</p>
                <p><b>📍 Venue:</b> {wedding['venue']}</p>
                <p><b>📌 Address:</b> {wedding['venue_address'] or wedding['venue']}</p>
                <p><b>⏰ Time:</b> 7:00 PM onwards</p>
                <div style="height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 30px 0;"></div>
                <p style="color: #D4AF37;">🎉 Reception to follow 🎉</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if guest['rsvp_status'] != 'confirmed':
                    if st.button("✅ Will Attend", use_container_width=True):
                        update_guest_rsvp(guest['id'], 'confirmed')
                        st.success("🎉 Thank you! We can't wait to celebrate with you!")
                        st.balloons()
                        st.rerun()
                else:
                    st.success("✅ You are attending! We're excited to see you!")
            
            with col2:
                if guest['rsvp_status'] != 'declined':
                    if st.button("❌ Cannot Attend", use_container_width=True):
                        update_guest_rsvp(guest['id'], 'declined')
                        st.info("💝 We'll miss you! Photos will be shared after the event.")
                        st.rerun()
                else:
                    st.info("❌ You've declined the invitation")
            
            st.markdown("---")
            st.markdown("### 💝 Leave Your Blessings")
            
            current_wish = guest['well_wish'] if guest['well_wish'] else ""
            wish = st.text_area("Write your warm wishes for the couple...", value=current_wish)
            
            if st.button("Send Blessings", use_container_width=True):
                if wish:
                    update_guest_well_wish(guest['id'], wish)
                    st.success("Thank you for your blessings! 💕")
                    st.balloons()
                else:
                    st.warning("Please write a message before sending!")
    else:
        st.info("No invitation found. Please contact the wedding host for your invitation code.")

# ==================== MAIN ====================

def main():
    """Main application"""
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h2 style="color: #D4AF37;">💍 Shadi-Hub</h2>
            <p style="color: #8B6914; font-size: 12px;">Complete Wedding Ecosystem</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if 'user' in st.session_state and st.session_state.user:
            user = st.session_state.user
            st.markdown(f"**Welcome,**")
            st.markdown(f"**{user['name']}**")
            st.caption(f"Role: {user['role'].title()}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            # Login/Register in sidebar
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
            with tab1:
                login_form()
            with tab2:
                register_form()
    
    # Main content area
    user = get_current_user()
    
    if user:
        if user['role'] == 'host':
            host_dashboard()
        elif user['role'] == 'vendor':
            vendor_dashboard()
        elif user['role'] == 'guest':
            guest_dashboard()
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px;">
                <h1 style="font-size: 48px;">💍 Shadi-Hub</h1>
                <p style="font-size: 20px; color: #D4AF37;">Complete Wedding Management Ecosystem</p>
                <div style="height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 30px 0;"></div>
                <p>Login or Register to access your dashboard</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
