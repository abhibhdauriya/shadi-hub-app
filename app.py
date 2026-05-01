import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Shadi-Hub", page_icon="💍", layout="wide")

# -------------------- CUSTOM CSS --------------------
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
        background: #D4AF37;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background: #C5A028;
        transform: scale(1.02);
        transition: 0.3s;
    }
    .card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .gold-text {
        color: #D4AF37;
    }
    hr {
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- DATABASE --------------------
def init_db():
    """Initialize database with tables and demo data"""
    conn = sqlite3.connect('shadi_hub.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        name TEXT,
        role TEXT
    )''')
    
    # Weddings table
    c.execute('''CREATE TABLE IF NOT EXISTS weddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INTEGER,
        couple_names TEXT,
        event_date TEXT,
        venue TEXT,
        venue_address TEXT,
        guest_count INTEGER
    )''')
    
    # Guests table
    c.execute('''CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wedding_id INTEGER,
        name TEXT,
        email TEXT,
        phone TEXT,
        category TEXT,
        rsvp_status TEXT,
        invitation_code TEXT
    )''')
    
    # Vendors table
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        business_name TEXT,
        category TEXT,
        price_range TEXT,
        rating REAL,
        location TEXT,
        description TEXT
    )''')
    
    # Vendor team table
    c.execute('''CREATE TABLE IF NOT EXISTS vendor_team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        member_name TEXT,
        member_email TEXT,
        member_role TEXT,
        permissions TEXT
    )''')
    
    # Photos table
    c.execute('''CREATE TABLE IF NOT EXISTS wedding_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wedding_id INTEGER,
        photo_url TEXT,
        caption TEXT,
        is_sneak_peek INTEGER,
        uploaded_by TEXT
    )''')
    
    # Insert demo data
    c.execute("SELECT * FROM users WHERE email='host@demo.com'")
    if not c.fetchone():
        # Demo users
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                  ('host@demo.com', hashlib.md5('host123'.encode()).hexdigest(), 'Rahul & Priya', 'host'))
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                  ('vendor@demo.com', hashlib.md5('vendor123'.encode()).hexdigest(), 'Dream Photography', 'vendor'))
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                  ('guest@demo.com', hashlib.md5('guest123'.encode()).hexdigest(), 'Amit Sharma', 'guest'))
        
        # Demo wedding
        c.execute("INSERT INTO weddings (host_id, couple_names, event_date, venue, guest_count) VALUES (1, 'Rahul & Priya', '2024-12-15', 'Grand Palace, Mumbai', 150)")
        
        # Demo vendors
        vendors = [
            (2, 'Dream Photography Studio', 'photographer', 'premium', 4.9, 'Mumbai', 'Award winning wedding photographers'),
            (2, 'Mehndi Art by Seema', 'mehndi', 'mid-range', 4.7, 'Delhi', 'Bridal mehndi specialists'),
            (2, 'Grand Palace Hotel', 'venue', 'luxury', 4.8, 'Mumbai', 'Luxury wedding venue'),
            (2, 'Spice Caterers', 'catering', 'premium', 4.6, 'Mumbai', 'Exotic wedding cuisine'),
            (2, 'Magic Decorators', 'decor', 'mid-range', 4.5, 'Mumbai', 'Theme based decoration')
        ]
        for v in vendors:
            c.execute("INSERT INTO vendors (user_id, business_name, category, price_range, rating, location, description) VALUES (?, ?, ?, ?, ?, ?, ?)", v)
        
        # Demo guests
        guests_data = [
            (1, 'Amit Kumar', 'amit@test.com', '9876543210', 'Friend', 'confirmed', 'INV001'),
            (1, 'Neha Singh', 'neha@test.com', '9876543211', 'Friend', 'pending', 'INV002'),
            (1, 'Rajesh Sharma', 'rajesh@test.com', '9876543212', 'Family', 'confirmed', 'INV003'),
            (1, 'Priya Patel', 'priya@test.com', '9876543213', 'Family', 'pending', 'INV004'),
            (1, 'Vikram Mehta', 'vikram@test.com', '9876543214', 'Colleague', 'declined', 'INV005')
        ]
        for g in guests_data:
            c.execute("INSERT INTO guests (wedding_id, name, email, phone, category, rsvp_status, invitation_code) VALUES (?, ?, ?, ?, ?, ?, ?)", g)
    
    conn.commit()
    conn.close()

# -------------------- INVITATION GENERATOR --------------------
def generate_invitation(guest_name, couple_names, event_date, venue, output_path):
    """Generate beautiful wedding invitation"""
    # Create image
    img = Image.new('RGB', (800, 600), color='#FFF8F0')
    draw = ImageDraw.Draw(img)
    
    # Gold border
    for i in range(4):
        draw.rectangle([i*2, i*2, 800-i*2, 600-i*2], outline='#D4AF37', width=2)
    
    # Corner decorations
    corner = 40
    positions = [(10,10), (750,10), (10,550), (750,550)]
    for x, y in positions:
        draw.line([(x, y), (x+corner, y)], fill='#D4AF37', width=3)
        draw.line([(x, y), (x, y+corner)], fill='#D4AF37', width=3)
    
    # Try to load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 38)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_title = font_name = font_text = ImageFont.load_default()
    
    # Draw text
    draw.text((400, 80), "✨ WEDDING INVITATION ✨", fill='#D4AF37', anchor="mm", font=font_title)
    draw.text((400, 160), couple_names, fill='#8B6914', anchor="mm", font=font_title)
    
    # Decorative line
    draw.line([(250, 200), (550, 200)], fill='#D4AF37', width=2)
    
    # Personalized message
    draw.text((400, 260), f"Dear {guest_name},", fill='#666666', anchor="mm", font=font_name)
    draw.text((400, 320), "You are cordially invited to celebrate", fill='#666666', anchor="mm", font=font_text)
    draw.text((400, 360), "the wedding ceremony of", fill='#666666', anchor="mm", font=font_text)
    
    # Event details
    draw.text((400, 430), f"📅 {event_date}", fill='#D4AF37', anchor="mm", font=font_text)
    draw.text((400, 470), f"📍 {venue}", fill='#D4AF37', anchor="mm", font=font_text)
    
    # Footer
    draw.text((400, 550), "🎉 Reception to follow 🎉", fill='#8B6914', anchor="mm", font=font_text)
    
    # Save
    img.save(output_path)
    return output_path

# -------------------- LOGIN PAGE --------------------
def show_login():
    st.markdown("<h1 style='text-align: center;'>💍 Shadi-Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 18px;'>Complete Wedding Management Ecosystem</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("### ✨ Login to Your Account")
            
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            if st.button("🔐 Login"):
                if email and password:
                    conn = sqlite3.connect('shadi_hub.db')
                    c = conn.cursor()
                    hashed = hashlib.md5(password.encode()).hexdigest()
                    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed))
                    user = c.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_name = user[3]
                        st.session_state.user_role = user[4]
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password!")
                else:
                    st.warning("Please enter email and password")
            
            st.markdown("---")
            st.markdown("### 🎭 Demo Accounts")
            st.code("""
Host:   host@demo.com   / host123
Vendor: vendor@demo.com / vendor123
Guest:  guest@demo.com  / guest123
            """)

# -------------------- HOST DASHBOARD --------------------
def host_dashboard():
    st.markdown(f"<h1>🌟 Welcome, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #D4AF37;'>Manage your wedding from here</p>", unsafe_allow_html=True)
    
    # Stats
    conn = sqlite3.connect('shadi_hub.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM guests WHERE wedding_id=1")
    total_guests = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM guests WHERE wedding_id=1 AND rsvp_status='confirmed'")
    confirmed = c.fetchone()[0]
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Guests", total_guests)
    with col2:
        st.metric("✅ Confirmed", confirmed)
    with col3:
        st.metric("⏳ Pending", total_guests - confirmed)
    with col4:
        st.metric("📸 Vendors", 5)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Wedding Info", "👥 Guest Manager", "🎨 Invitations", "🛍️ Find Vendors"])
    
    # TAB 1: Wedding Info
    with tab1:
        st.subheader("Wedding Details")
        
        conn = sqlite3.connect('shadi_hub.db')
        c = conn.cursor()
        c.execute("SELECT couple_names, event_date, venue, venue_address, guest_count FROM weddings WHERE id=1")
        current = c.fetchone()
        conn.close()
        
        col1, col2 = st.columns(2)
        with col1:
            if current:
                couple = st.text_input("Couple Names", current[0])
                venue = st.text_input("Venue Name", current[2])
            else:
                couple = st.text_input("Couple Names", "Rahul & Priya")
                venue = st.text_input("Venue Name", "Grand Palace")
        
        with col2:
            if current:
                event_date = st.date_input("Wedding Date", datetime.strptime(current[1], '%Y-%m-%d'))
                guest_count = st.number_input("Expected Guests", 50, 1000, current[4])
            else:
                event_date = st.date_input("Wedding Date", datetime(2024, 12, 15))
                guest_count = st.number_input("Expected Guests", 50, 1000, 150)
        
        venue_address = st.text_area("Venue Address", "Marine Drive, South Mumbai")
        
        if st.button("💾 Save Wedding Details"):
            conn = sqlite3.connect('shadi_hub.db')
            c = conn.cursor()
            c.execute("""UPDATE weddings SET couple_names=?, event_date=?, venue=?, venue_address=?, guest_count=? WHERE id=1""",
                     (couple, str(event_date), venue, venue_address, guest_count))
            conn.commit()
            conn.close()
            st.success("✅ Wedding details saved successfully!")
    
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
                if guest_name:
                    conn = sqlite3.connect('shadi_hub.db')
                    c = conn.cursor()
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    c.execute("""INSERT INTO guests (wedding_id, name, email, phone, category, rsvp_status, invitation_code) 
                              VALUES (1, ?, ?, ?, ?, 'pending', ?)""",
                              (guest_name, guest_email, guest_phone, guest_category, code))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {guest_name} added to guest list!")
                    st.rerun()
        
        # Guest list
        conn = sqlite3.connect('shadi_hub.db')
        c = conn.cursor()
        c.execute("SELECT name, email, phone, category, rsvp_status FROM guests WHERE wedding_id=1 ORDER BY name")
        guests = c.fetchall()
        conn.close()
        
        if guests:
            for guest in guests:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1])
                with col1:
                    st.write(f"**{guest[0]}**")
                with col2:
                    st.write(guest[1])
                with col3:
                    st.write(guest[2] if guest[2] else "-")
                with col4:
                    status_color = "🟢" if guest[4] == "confirmed" else "🟡" if guest[4] == "pending" else "🔴"
                    st.write(f"{status_color} {guest[4]}")
                with col5:
                    st.write(guest[3])
                st.divider()
        else:
            st.info("No guests added yet. Use the form above to add guests.")
    
    # TAB 3: Invitations
    with tab3:
        st.subheader("Digital Invitation Generator")
        
        conn = sqlite3.connect('shadi_hub.db')
        c = conn.cursor()
        c.execute("SELECT couple_names, event_date, venue FROM weddings WHERE id=1")
        wedding = c.fetchone()
        c.execute("SELECT name FROM guests WHERE wedding_id=1")
        guests_list = c.fetchall()
        conn.close()
        
        if wedding and guests_list:
            st.markdown("### 🎨 Invitation Templates")
            st.caption("Classic Gold Theme - Elegant Wedding Design")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate for Single Guest", use_container_width=True):
                    guest_options = [g[0] for g in guests_list]
                    selected_guest = st.selectbox("Select Guest", guest_options)
                    if selected_guest:
                        os.makedirs("invitations", exist_ok=True)
                        path = f"invitations/{selected_guest}.jpg"
                        generate_invitation(selected_guest, wedding[0], wedding[1], wedding[2], path)
                        st.image(path, use_container_width=True)
                        st.success(f"✅ Invitation generated for {selected_guest}")
            
            with col2:
                if st.button("🎨 Generate for ALL Guests", use_container_width=True):
                    os.makedirs("invitations", exist_ok=True)
                    progress_bar = st.progress(0)
                    for i, guest in enumerate(guests_list):
                        path = f"invitations/{guest[0]}.jpg"
                        generate_invitation(guest[0], wedding[0], wedding[1], wedding[2], path)
                        progress_bar.progress((i + 1) / len(guests_list))
                    st.success(f"✅ Generated {len(guests_list)} invitations!")
                    st.balloons()
        else:
            st.warning("Please add guests first in Guest Manager tab!")
    
    # TAB 4: Find Vendors
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
        
        # Fetch vendors
        conn = sqlite3.connect('shadi_hub.db')
        c = conn.cursor()
        query = "SELECT business_name, category, price_range, rating, location, description FROM vendors WHERE 1=1"
        if category_filter != "All":
            query += f" AND category='{category_filter}'"
        if price_filter != "All":
            query += f" AND price_range='{price_filter}'"
        if location_filter:
            query += f" AND location LIKE '%{location_filter}%'"
        
        c.execute(query)
        vendors = c.fetchall()
        conn.close()
        
        if vendors:
            for vendor in vendors:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**{vendor[0]}**")
                        st.caption(f"⭐ {vendor[3]}/5.0 • {vendor[1].title()}")
                    with col2:
                        st.write(f"💰 {vendor[2].title()}")
                        st.write(f"📍 {vendor[4]}")
                    with col3:
                        if st.button("💝 Contact", key=vendor[0]):
                            st.success(f"Inquiry sent to {vendor[0]}!")
                    st.divider()
        else:
            st.info("No vendors found with selected filters.")

# -------------------- VENDOR DASHBOARD --------------------
def vendor_dashboard():
    st.markdown(f"<h1>📸 Welcome, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #D4AF37;'>Manage your photography business</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👥 Team Management", "📅 Booking Requests"])
    
    # TAB 1: Team Management
    with tab1:
        st.subheader("Add Team Member")
        
        with st.form("add_team_form"):
            col1, col2 = st.columns(2)
            with col1:
                member_name = st.text_input("Full Name")
                member_email = st.text_input("Email Address")
            with col2:
                member_role = st.selectbox("Role", ["Photographer", "Editor", "Assistant", "Videographer"])
                permissions = st.multiselect("Permissions", ["Upload Photos", "Edit Schedule", "View Clients", "Edit Profile"])
            
            if st.form_submit_button("➕ Add Team Member"):
                if member_name and member_email:
                    conn = sqlite3.connect('shadi_hub.db')
                    c = conn.cursor()
                    c.execute("""INSERT INTO vendor_team (vendor_id, member_name, member_email, member_role, permissions) 
                              VALUES (1, ?, ?, ?, ?)""",
                              (member_name, member_email, member_role, str(permissions)))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {member_name} added as {member_role}!")
                    st.balloons()
        
        # Display team
        st.markdown("### 👥 Current Team Members")
        
        conn = sqlite3.connect('shadi_hub.db')
        c = conn.cursor()
        c.execute("SELECT member_name, member_email, member_role, permissions FROM vendor_team WHERE vendor_id=1")
        team = c.fetchall()
        conn.close()
        
        if team:
            for member in team:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.markdown(f"**{member[0]}**")
                    with col2:
                        st.write(member[1])
                    with col3:
                        st.write(f"🎭 {member[2]}")
                    st.divider()
        else:
            st.info("No team members yet. Add your first team member above!")
    
    # TAB 2: Bookings
    with tab2:
        st.subheader("Booking Requests")
        st.info("📌 New booking inquiries will appear here")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Pending", "2")
        with col2:
            st.metric("✅ Confirmed", "3")
        with col3:
            st.metric("🎉 Completed", "5")

# -------------------- GUEST VIEW --------------------
def guest_view():
    st.markdown(f"<h1>💌 Hello {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('shadi_hub.db')
    c = conn.cursor()
    c.execute("SELECT couple_names, event_date, venue, venue_address FROM weddings WHERE id=1")
    wedding = c.fetchone()
    conn.close()
    
    if wedding:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h2 style="color: #D4AF37;">✨ You're Invited! ✨</h2>
            <h3 style="color: #8B6914;">{wedding[0]}</h3>
            <p style="font-size: 18px; margin: 20px 0;">Request the pleasure of your company at their wedding celebration</p>
            <hr>
            <p><b>📅 Date:</b> {wedding[1]}</p>
            <p><b>📍 Venue:</b> {wedding[2]}</p>
            <p><b>📌 Address:</b> {wedding[3]}</p>
            <p><b>⏰ Time:</b> 7:00 PM onwards</p>
            <hr>
            <p style="color: #D4AF37;">🎉 Dinner & Reception to follow 🎉</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Will Attend", use_container_width=True):
                st.success("🎉 Thank you! We can't wait to celebrate with you!")
                st.balloons()
        with col2:
            if st.button("❌ Cannot Attend", use_container_width=True):
                st.info("💝 We'll miss you! Photos will be shared after the event.")
        
        st.markdown("---")
        st.markdown("### 💝 Leave Your Blessings")
        wish = st.text_area("Write your warm wishes for the couple...")
        if st.button("Send Blessings", use_container_width=True):
            if wish:
                st.success("Thank you for your blessings! 💕")
                st.balloons()
            else:
                st.warning("Please write a message before sending!")

# -------------------- MAIN APP --------------------
def main():
    # Initialize database
    init_db()
    
    # Check login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <h3 style="color: #D4AF37;">💍 Shadi-Hub</h3>
                <p>Welcome,<br><b>{st.session_state.user_name}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Role-based menu
            if st.session_state.user_role == 'host':
                st.markdown("### 🏠 Menu")
            elif st.session_state.user_role == 'vendor':
                st.markdown("### 📸 Menu")
            else:
                st.markdown("### 💌 Menu")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Show appropriate dashboard
        if st.session_state.user_role == 'host':
            host_dashboard()
        elif st.session_state.user_role == 'vendor':
            vendor_dashboard()
        else:
            guest_view()

if __name__ == "__main__":
    main()
