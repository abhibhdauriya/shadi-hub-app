import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Shadi-Hub - Complete Wedding Ecosystem",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
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
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
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
    .wedding-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        margin: 20px 0;
        transition: transform 0.3s ease;
    }
    .wedding-card:hover {
        transform: translateY(-5px);
    }
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.15);
    }
    .whatsapp-btn {
        background: #25D366;
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
    }
    .gold-text {
        color: #D4AF37;
    }
    .price-tag {
        font-size: 20px;
        font-weight: bold;
        color: #D4AF37;
    }
    .rating-stars {
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE SETUP ====================
DB_PATH = 'shadi_hub.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('host', 'vendor', 'guest'))
        )
    ''')
    
    # Weddings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id INTEGER NOT NULL,
            couple_names TEXT NOT NULL,
            event_date TEXT NOT NULL,
            venue TEXT NOT NULL,
            venue_address TEXT,
            guest_count INTEGER DEFAULT 0,
            whatsapp_group TEXT,
            photo_gallery_link TEXT,
            FOREIGN KEY(host_id) REFERENCES users(id)
        )
    ''')
    
    # Guests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wedding_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            category TEXT,
            rsvp_status TEXT DEFAULT 'pending',
            invitation_code TEXT UNIQUE,
            well_wish TEXT,
            invitation_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY(wedding_id) REFERENCES weddings(id)
        )
    ''')
    
    # Vendors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price_range TEXT,
            min_price REAL,
            max_price REAL,
            rating REAL DEFAULT 0,
            location TEXT,
            image_url TEXT,
            whatsapp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Products table (Shopping)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            original_price REAL,
            description TEXT,
            image_url TEXT,
            discount INTEGER,
            FOREIGN KEY(vendor_id) REFERENCES vendors(id)
        )
    ''')
    
    # Vendor Team table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendor_team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            member_name TEXT NOT NULL,
            member_email TEXT NOT NULL,
            role TEXT NOT NULL,
            permissions TEXT,
            FOREIGN KEY(vendor_id) REFERENCES vendors(id)
        )
    ''')
    
    # Wedding Photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wedding_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wedding_id INTEGER NOT NULL,
            photo_url TEXT NOT NULL,
            caption TEXT,
            is_sneak_peek INTEGER DEFAULT 0,
            uploaded_by TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(wedding_id) REFERENCES weddings(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_demo_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Create Host
    host_pass = hashlib.md5("host123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Rahul & Priya", "host@demo.com", host_pass, "host"))
    host_id = cursor.lastrowid
    
    # Create Wedding
    cursor.execute('''INSERT INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count, whatsapp_group)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (host_id, "Rahul & Priya", "2024-12-15", "Grand Palace, Mumbai", "Marine Drive, Mumbai", 200, "https://chat.whatsapp.com/invite-link"))
    wedding_id = cursor.lastrowid
    
    # Create Vendor
    vendor_pass = hashlib.md5("vendor123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Dream Photography", "vendor@demo.com", vendor_pass, "vendor"))
    vendor_user_id = cursor.lastrowid
    
    cursor.execute('''INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location, whatsapp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (vendor_user_id, "Dream Photography Studio", "photographer", "Award winning wedding photographers", "premium", 50000, 200000, 4.9, "Mumbai", "919876543210"))
    
    # More Vendors
    vendors = [
        ("Mehndi Art by Seema", "mehndi", "Bridal mehndi specialist", "mid-range", 10000, 50000, 4.7, "Delhi", "919876543211"),
        ("Grand Palace Hotel", "venue", "Luxury wedding venue", "luxury", 500000, 2000000, 4.8, "Mumbai", "919876543212"),
        ("Spice Caterers", "catering", "Exotic wedding cuisine", "premium", 500, 1500, 4.6, "Mumbai", "919876543213"),
        ("Magic Decorators", "decor", "Theme based decoration", "mid-range", 50000, 150000, 4.5, "Mumbai", "919876543214"),
        ("Raj Makeup Studio", "makeup", "Bridal makeup specialist", "premium", 15000, 50000, 4.8, "Mumbai", "919876543215"),
    ]
    
    for v in vendors:
        cursor.execute('''INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location, whatsapp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (vendor_user_id,) + v)
    
    # Products (Shopping items)
    products = [
        ("Royal Wedding Lehenga", "outfits", 45000, 55000, "Beautiful red bridal lehenga", "https://via.placeholder.com/300x300?text=Lehenga", 18),
        ("Designer Sherwani", "outfits", 35000, 45000, "Royal gold sherwani for groom", "https://via.placeholder.com/300x300?text=Sherwani", 22),
        ("Premium Gift Hamper", "gifts", 2500, 4000, "Luxury wedding gift set", "https://via.placeholder.com/300x300?text=Gift", 37),
        ("Wedding Decor Pack", "decor", 15000, 25000, "Complete decor setup", "https://via.placeholder.com/300x300?text=Decor", 40),
        ("Bridal Jewelry Set", "accessories", 12000, 20000, "Gold plated bridal set", "https://via.placeholder.com/300x300?text=Jewelry", 40),
        ("Wedding Invitation Cards", "stationery", 500, 1000, "Premium invitation cards (100 pcs)", "https://via.placeholder.com/300x300?text=Cards", 50),
    ]
    
    for p in products:
        cursor.execute('''INSERT INTO products (vendor_id, name, category, price, original_price, description, image_url, discount)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (1,) + p)
    
    # Sample Guests
    guests_data = [
        (wedding_id, "Amit Sharma", "amit@guest.com", "9876543210", "Friend", "confirmed", "INV001", None, 0),
        (wedding_id, "Neha Gupta", "neha@guest.com", "9876543211", "Friend", "pending", "INV002", None, 0),
        (wedding_id, "Rajesh Kumar", "rajesh@guest.com", "9876543212", "Family", "confirmed", "INV003", None, 0),
        (wedding_id, "Priya Singh", "priya@guest.com", "9876543213", "Family", "pending", "INV004", None, 0),
        (wedding_id, "Vikram Mehta", "vikram@guest.com", "9876543214", "Colleague", "declined", "INV005", None, 0),
    ]
    
    for g in guests_data:
        cursor.execute('''INSERT INTO guests (wedding_id, name, email, phone, category, rsvp_status, invitation_code, well_wish, invitation_sent)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', g)
    
    # Guest User
    guest_pass = hashlib.md5("guest123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Amit Sharma", "guest@demo.com", guest_pass, "guest"))
    
    # Sample Wedding Photos
    for i in range(1, 7):
        cursor.execute('''INSERT INTO wedding_photos (wedding_id, photo_url, caption, is_sneak_peek)
                       VALUES (?, ?, ?, ?)''',
                       (wedding_id, f"https://via.placeholder.com/400x300?text=Wedding+Photo+{i}", f"Beautiful moment {i}", 1 if i <= 3 else 0))
    
    conn.commit()
    conn.close()

# ==================== INVITATION GENERATOR ====================
def generate_invitation_card(guest_name, couple_names, event_date, venue, venue_address, output_path):
    """Generate beautiful wedding invitation"""
    img = Image.new('RGB', (800, 600), color='#FFF8F0')
    draw = ImageDraw.Draw(img)
    
    # Gold borders
    for i in range(4):
        draw.rectangle([i*2, i*2, 800-i*2, 600-i*2], outline='#D4AF37', width=3)
    
    # Corner decorations
    corner = 45
    positions = [(10,10), (745,10), (10,545), (745,545)]
    for x, y in positions:
        draw.line([(x, y), (x+corner, y)], fill='#D4AF37', width=3)
        draw.line([(x, y), (x, y+corner)], fill='#D4AF37', width=3)
    
    # Floral corner accents
    for x, y in positions:
        draw.ellipse([x-5, y-5, x+10, y+10], fill='#D4AF37', outline='#D4AF37')
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 38)
        font_names = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 32)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_title = font_names = font_text = font_small = ImageFont.load_default()
    
    # Main design
    draw.text((400, 60), "✨ WEDDING INVITATION ✨", fill='#D4AF37', anchor="mm", font=font_title)
    draw.text((400, 130), couple_names, fill='#8B6914', anchor="mm", font=font_names)
    
    # Decorative line
    draw.line([(200, 170), (600, 170)], fill='#D4AF37', width=2)
    draw.ellipse([(195, 165), (205, 175)], fill='#D4AF37')
    draw.ellipse([(595, 165), (605, 175)], fill='#D4AF37')
    
    # Personalized
    draw.text((400, 230), f"Dear {guest_name},", fill='#666666', anchor="mm", font=font_text)
    draw.text((400, 280), "You are cordially invited to celebrate", fill='#555555', anchor="mm", font=font_text)
    draw.text((400, 320), "the wedding of", fill='#555555', anchor="mm", font=font_text)
    
    # Details box
    box_y = 370
    draw.rectangle([150, box_y-15, 650, box_y+70], fill='#FFF8F0', outline='#D4AF37', width=1)
    draw.text((400, box_y), f"📅 {event_date}", fill='#D4AF37', anchor="mm", font=font_text)
    draw.text((400, box_y+35), f"📍 {venue}", fill='#D4AF37', anchor="mm", font=font_text)
    draw.text((400, box_y+70), f"📌 {venue_address if venue_address else venue}", fill='#888888', anchor="mm", font=font_small)
    
    # Footer with decorative elements
    draw.line([(200, 530), (600, 530)], fill='#D4AF37', width=1)
    draw.text((400, 555), "🎉 Reception & Dinner to follow 🎉", fill='#8B6914', anchor="mm", font=font_text)
    
    # Save
    os.makedirs("invitations", exist_ok=True)
    img.save(output_path)
    return output_path

# ==================== AUTH FUNCTIONS ====================
def verify_login(email, password):
    conn = get_db_connection()
    hashed = hashlib.md5(password.encode()).hexdigest()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_guest_by_email(email):
    conn = get_db_connection()
    guest = conn.execute("SELECT * FROM guests WHERE email = ?", (email,)).fetchone()
    conn.close()
    return guest

def get_wedding_by_id(wedding_id):
    conn = get_db_connection()
    wedding = conn.execute("SELECT * FROM weddings WHERE id = ?", (wedding_id,)).fetchone()
    conn.close()
    return wedding

def get_wedding_by_host(host_id):
    conn = get_db_connection()
    wedding = conn.execute("SELECT * FROM weddings WHERE host_id = ?", (host_id,)).fetchone()
    conn.close()
    return wedding

def update_guest_rsvp(guest_id, status):
    conn = get_db_connection()
    conn.execute("UPDATE guests SET rsvp_status = ? WHERE id = ?", (status, guest_id))
    conn.commit()
    conn.close()

def update_guest_well_wish(guest_id, well_wish):
    conn = get_db_connection()
    conn.execute("UPDATE guests SET well_wish = ? WHERE id = ?", (well_wish, guest_id))
    conn.commit()
    conn.close()

def get_all_vendors(category=None, price_range=None, location=None):
    conn = get_db_connection()
    query = "SELECT * FROM vendors WHERE 1=1"
    params = []
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if price_range and price_range != "All":
        query += " AND price_range = ?"
        params.append(price_range)
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    query += " ORDER BY rating DESC"
    vendors = conn.execute(query, params).fetchall()
    conn.close()
    return vendors

def get_all_products(category=None):
    conn = get_db_connection()
    if category and category != "All":
        products = conn.execute("SELECT * FROM products WHERE category = ?", (category,)).fetchall()
    else:
        products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return products

def get_wedding_photos(wedding_id, sneak_peek_only=False):
    conn = get_db_connection()
    if sneak_peek_only:
        photos = conn.execute("SELECT * FROM wedding_photos WHERE wedding_id = ? AND is_sneak_peek = 1", (wedding_id,)).fetchall()
    else:
        photos = conn.execute("SELECT * FROM wedding_photos WHERE wedding_id = ?", (wedding_id,)).fetchall()
    conn.close()
    return photos

# ==================== LOGIN PAGE ====================
def login_page():
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 56px;">💍 Shadi-Hub</h1>
        <p style="font-size: 20px; color: #D4AF37;">Your Complete Wedding Ecosystem</p>
        <p>Everything you need for your dream wedding - Vendors, Shopping, Invitations & More!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Demo Access"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                if st.form_submit_button("Login", use_container_width=True):
                    user = verify_login(email, password)
                    if user:
                        st.session_state.user = dict(user)
                        st.success(f"Welcome {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
        
        with tab2:
            st.markdown("### 🎭 Demo Accounts")
            st.info("Click any button to login as demo user")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("💒 Wedding Host", use_container_width=True):
                    user = verify_login("host@demo.com", "host123")
                    if user:
                        st.session_state.user = dict(user)
                        st.rerun()
            with col_b:
                if st.button("📸 Vendor", use_container_width=True):
                    user = verify_login("vendor@demo.com", "vendor123")
                    if user:
                        st.session_state.user = dict(user)
                        st.rerun()
            with col_c:
                if st.button("💝 Guest", use_container_width=True):
                    user = verify_login("guest@demo.com", "guest123")
                    if user:
                        st.session_state.user = dict(user)
                        st.rerun()
            
            st.caption("Host: host@demo.com / host123")
            st.caption("Vendor: vendor@demo.com / vendor123")
            st.caption("Guest: guest@demo.com / guest123")

# ==================== HOST DASHBOARD ====================
def host_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>🌟 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    
    wedding = get_wedding_by_host(user['id'])
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Wedding Info", "👥 Guests", "🎨 Invitations", "🛍️ Vendors", "📸 Gallery"])
    
    with tab1:
        st.subheader("Wedding Details")
        col1, col2 = st.columns(2)
        with col1:
            couple = st.text_input("Couple Names", wedding['couple_names'] if wedding else "Rahul & Priya")
            venue = st.text_input("Venue", wedding['venue'] if wedding else "Grand Palace")
        with col2:
            date = st.date_input("Wedding Date", datetime.strptime(wedding['event_date'], '%Y-%m-%d').date() if wedding and wedding['event_date'] else datetime(2024, 12, 15))
            guest_count = st.number_input("Expected Guests", wedding['guest_count'] if wedding else 150)
        
        venue_address = st.text_area("Venue Address", wedding['venue_address'] if wedding else "")
        
        if st.button("Save Wedding Details"):
            st.success("Wedding details saved!")
    
    with tab2:
        st.subheader("Guest Management")
        with st.expander("Add New Guest"):
            name = st.text_input("Guest Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            if st.button("Add Guest"):
                st.success(f"Added {name}")
    
    with tab3:
        st.subheader("Invitation Generator")
        if st.button("Generate Invitations for All Guests"):
            st.success("Invitations generated!")
            st.balloons()
    
    with tab4:
        st.subheader("Vendor Marketplace")
        vendors = get_all_vendors()
        for vendor in vendors:
            st.markdown(f"**{vendor['business_name']}** - ⭐ {vendor['rating']}")
    
    with tab5:
        st.subheader("Wedding Gallery")
        st.info("Upload and manage wedding photos here")

# ==================== VENDOR DASHBOARD ====================
def vendor_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>📸 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👥 Team Management", "📅 Bookings"])
    
    with tab1:
        st.subheader("Add Team Member")
        with st.form("add_team"):
            name = st.text_input("Member Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["photographer", "editor", "assistant"])
            if st.form_submit_button("Add"):
                st.success(f"{name} added to team!")
    
    with tab2:
        st.info("Booking requests will appear here")

# ==================== GUEST DASHBOARD ====================
def guest_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>💌 Hello {user['name']}!</h1>", unsafe_allow_html=True)
    
    # Get guest and wedding details
    guest = get_guest_by_email(user['email'])
    
    if not guest:
        st.error("Guest profile not found!")
        return
    
    wedding = get_wedding_by_id(guest['wedding_id'])
    
    if not wedding:
        st.error("Wedding details not found!")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💌 My Invitation", "✅ RSVP", "🛍️ Wedding Shop", "📸 Gallery", "💝 Blessings"
    ])
    
    # ========== TAB 1: INVITATION ==========
    with tab1:
        st.markdown(f"""
        <div class="wedding-card">
            <h2 style="color: #D4AF37;">✨ You're Invited! ✨</h2>
            <h3>{wedding['couple_names']}</h3>
            <p>Request the pleasure of your company at their wedding celebration</p>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 20px;"></div>
            <p><b>📅 Date:</b> {wedding['event_date']}</p>
            <p><b>📍 Venue:</b> {wedding['venue']}</p>
            <p><b>📌 Address:</b> {wedding['venue_address'] or wedding['venue']}</p>
            <p><b>⏰ Time:</b> 7:00 PM onwards</p>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 20px;"></div>
            <p style="color: #D4AF37;">🎉 Reception & Dinner to follow 🎉</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate and download invitation button
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Download Invitation Card", use_container_width=True):
                invite_path = f"invitations/{user['name']}_invitation.jpg"
                generate_invitation_card(
                    user['name'], 
                    wedding['couple_names'],
                    wedding['event_date'],
                    wedding['venue'],
                    wedding['venue_address'],
                    invite_path
                )
                with open(invite_path, "rb") as f:
                    st.download_button(
                        label="💾 Save Invitation",
                        data=f,
                        file_name=f"{user['name']}_wedding_invitation.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
        
        with col2:
            # WhatsApp Share Button
            message = f"🎉 *Wedding Invitation* 🎉%0A%0A*{wedding['couple_names']}* are getting married!%0A%0A📅 Date: {wedding['event_date']}%0A📍 Venue: {wedding['venue']}%0A⏰ Time: 7:00 PM%0A%0AYou're cordially invited to celebrate with us! 🎊"
            whatsapp_url = f"https://wa.me/?text={message}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background:#25D366; color:white; border:none; border-radius:25px; padding:10px; width:100%; cursor:pointer;">📱 Share on WhatsApp</button></a>', unsafe_allow_html=True)
        
        with col3:
            if st.button("📤 Share Invitation", use_container_width=True):
                st.info("Copy the link to share with family!")
                st.code(f"https://shadi-hub.app/invite/{guest['invitation_code']}")
    
    # ========== TAB 2: RSVP ==========
    with tab2:
        st.subheader("Will You Attend?")
        
        current_status = guest['rsvp_status']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if current_status != "confirmed":
                if st.button("✅ Yes, I Will Attend", use_container_width=True):
                    update_guest_rsvp(guest['id'], "confirmed")
                    st.success("🎉 Thank you! We can't wait to celebrate with you!")
                    st.balloons()
                    st.rerun()
            else:
                st.success("✅ You are attending! We're excited to see you!")
        
        with col2:
            if current_status != "declined":
                if st.button("❌ Sorry, Cannot Attend", use_container_width=True):
                    update_guest_rsvp(guest['id'], "declined")
                    st.info("💝 We'll miss you! Photos will be shared after the event.")
                    st.rerun()
            else:
                st.info("❌ You've declined the invitation")
        
        if current_status == "pending":
            st.warning("⏳ Please let us know if you can attend by clicking one of the buttons above.")
        elif current_status == "confirmed":
            st.success("We look forward to celebrating with you! 🎉")
        elif current_status == "declined":
            st.info("We'll share memories with you after the event! 📸")
    
    # ========== TAB 3: WEDDING SHOP ==========
    with tab3:
        st.subheader("🛍️ Wedding Shop")
        st.markdown("<p>Shop for wedding essentials, gifts, and more!</p>", unsafe_allow_html=True)
        
        # Product categories
        categories = ["All", "outfits", "gifts", "decor", "accessories", "stationery"]
        selected_cat = st.selectbox("Browse Category", categories, format_func=lambda x: {"All": "All Items", "outfits": "👗 Outfits", "gifts": "🎁 Gifts", "decor": "🎀 Decor", "accessories": "💎 Accessories", "stationery": "📜 Stationery"}.get(x, x))
        
        products = get_all_products(None if selected_cat == "All" else selected_cat)
        
        if products:
            cols = st.columns(3)
            for idx, product in enumerate(products):
                with cols[idx % 3]:
                    discount_text = f"<span style='background:#D4AF37; color:white; padding:2px 8px; border-radius:20px; font-size:12px;'>-{product['discount']}% OFF</span>" if product['discount'] else ""
                    
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{product['image_url']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                        <h4 style="margin:10px 0 5px 0;">{product['name']}</h4>
                        <p style="color:#888; font-size:12px;">{product['description'][:60]}...</p>
                        <div>
                            <span class="price-tag">₹{product['price']:,.0f}</span>
                            <span style="text-decoration:line-through; color:#999; margin-left:8px;">₹{product['original_price']:,.0f}</span>
                            {discount_text}
                        </div>
                    </div>
                    <br>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🛒 Buy Now", key=f"buy_{product['id']}", use_container_width=True):
                        st.success(f"Added {product['name']} to cart! 🎁")
        else:
            st.info("No products found in this category.")
    
    # ========== TAB 4: GALLERY ==========
    with tab4:
        st.subheader("📸 Wedding Gallery")
        
        # View options
        view_option = st.radio("View", ["Sneak Peeks", "Full Gallery"], horizontal=True)
        
        if view_option == "Sneak Peeks":
            photos = get_wedding_photos(wedding['id'], sneak_peek_only=True)
            st.caption("Here's a glimpse of the celebrations!")
        else:
            photos = get_wedding_photos(wedding['id'], sneak_peek_only=False)
        
        if photos:
            cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with cols[idx % 3]:
                    st.image(photo['photo_url'], caption=photo['caption'] or "Wedding Moment", use_container_width=True)
        else:
            st.info("📸 Photos will appear here after the wedding!")
            
            # Sample gallery placeholder
            st.markdown("""
            <div style="background: #f8f8f8; border-radius: 15px; padding: 40px; text-align: center;">
                <p>🌟 Wedding moments will be shared here</p>
                <p>Stay tuned for beautiful memories!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== TAB 5: BLESSINGS ==========
    with tab5:
        st.subheader("💝 Leave Your Blessings")
        
        current_wish = guest['well_wish'] if guest['well_wish'] else ""
        well_wish = st.text_area("Write your heartfelt wishes for the couple...", value=current_wish, height=150, placeholder="Wishing you a lifetime of love and happiness...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💕 Send Blessings", use_container_width=True):
                if well_wish:
                    update_guest_well_wish(guest['id'],
