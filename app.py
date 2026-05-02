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
    .price-tag {
        font-size: 20px;
        font-weight: bold;
        color: #D4AF37;
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
            invitation_sent INTEGER DEFAULT 0,
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
    
    # Products table
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
    vendors_data = [
        ("Mehndi Art by Seema", "mehndi", "Bridal mehndi specialist", "mid-range", 10000, 50000, 4.7, "Delhi", "919876543211"),
        ("Grand Palace Hotel", "venue", "Luxury wedding venue", "luxury", 500000, 2000000, 4.8, "Mumbai", "919876543212"),
        ("Spice Caterers", "catering", "Exotic wedding cuisine", "premium", 500, 1500, 4.6, "Mumbai", "919876543213"),
        ("Magic Decorators", "decor", "Theme based decoration", "mid-range", 50000, 150000, 4.5, "Mumbai", "919876543214"),
        ("Raj Makeup Studio", "makeup", "Bridal makeup specialist", "premium", 15000, 50000, 4.8, "Mumbai", "919876543215"),
    ]
    
    for v in vendors_data:
        cursor.execute('''INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location, whatsapp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (vendor_user_id,) + v)
    
    # Products
    products_data = [
        (1, "Royal Wedding Lehenga", "outfits", 45000, 55000, "Beautiful red bridal lehenga", "https://via.placeholder.com/300x300?text=Lehenga", 18),
        (1, "Designer Sherwani", "outfits", 35000, 45000, "Royal gold sherwani for groom", "https://via.placeholder.com/300x300?text=Sherwani", 22),
        (1, "Premium Gift Hamper", "gifts", 2500, 4000, "Luxury wedding gift set", "https://via.placeholder.com/300x300?text=Gift", 37),
        (1, "Wedding Decor Pack", "decor", 15000, 25000, "Complete decor setup", "https://via.placeholder.com/300x300?text=Decor", 40),
        (1, "Bridal Jewelry Set", "accessories", 12000, 20000, "Gold plated bridal set", "https://via.placeholder.com/300x300?text=Jewelry", 40),
    ]
    
    for p in products_data:
        cursor.execute('''INSERT INTO products (vendor_id, name, category, price, original_price, description, image_url, discount)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', p)
    
    # Guests
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
    
    # Sample Photos
    for i in range(1, 7):
        cursor.execute('''INSERT INTO wedding_photos (wedding_id, photo_url, caption, is_sneak_peek)
                       VALUES (?, ?, ?, ?)''',
                       (wedding_id, f"https://via.placeholder.com/400x300?text=Wedding+Photo+{i}", f"Beautiful moment {i}", 1 if i <= 3 else 0))
    
    conn.commit()
    conn.close()

# ==================== INVITATION GENERATOR ====================
def generate_invitation_card(guest_name, couple_names, event_date, venue, venue_address, output_path):
    """Generate beautiful wedding invitation"""
    try:
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
        
        # Fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 38)
            font_names = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 32)
            font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            font_title = font_names = font_text = ImageFont.load_default()
        
        # Draw text
        draw.text((400, 60), "✨ WEDDING INVITATION ✨", fill='#D4AF37', anchor="mm", font=font_title)
        draw.text((400, 130), couple_names, fill='#8B6914', anchor="mm", font=font_names)
        
        # Decorative line
        draw.line([(200, 170), (600, 170)], fill='#D4AF37', width=2)
        
        # Personalized message
        draw.text((400, 230), f"Dear {guest_name},", fill='#666666', anchor="mm", font=font_text)
        draw.text((400, 280), "You are cordially invited to celebrate", fill='#555555', anchor="mm", font=font_text)
        draw.text((400, 320), "the wedding of", fill='#555555', anchor="mm", font=font_text)
        
        # Details box
        box_y = 370
        draw.rectangle([150, box_y-15, 650, box_y+70], fill='#FFF8F0', outline='#D4AF37', width=1)
        draw.text((400, box_y), f"📅 {event_date}", fill='#D4AF37', anchor="mm", font=font_text)
        draw.text((400, box_y+35), f"📍 {venue}", fill='#D4AF37', anchor="mm", font=font_text)
        
        # Footer
        draw.line([(200, 530), (600, 530)], fill='#D4AF37', width=1)
        draw.text((400, 555), "🎉 Reception & Dinner to follow 🎉", fill='#8B6914', anchor="mm", font=font_text)
        
        # Save
        os.makedirs("invitations", exist_ok=True)
        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating invitation: {e}")
        return None

# ==================== DATABASE FUNCTIONS ====================
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

def get_guest_by_id(guest_id):
    conn = get_db_connection()
    guest = conn.execute("SELECT * FROM guests WHERE id = ?", (guest_id,)).fetchone()
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

def add_guest(wedding_id, name, email, phone, category):
    conn = get_db_connection()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    conn.execute('''INSERT INTO guests (wedding_id, name, email, phone, category, invitation_code, rsvp_status)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending')''',
                   (wedding_id, name, email, phone, category, code))
    conn.commit()
    conn.close()
    return code

def get_all_guests(wedding_id):
    conn = get_db_connection()
    guests = conn.execute("SELECT * FROM guests WHERE wedding_id = ? ORDER BY name", (wedding_id,)).fetchall()
    conn.close()
    return guests

def delete_guest(guest_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
    conn.commit()
    conn.close()

def add_team_member(vendor_id, member_name, member_email, role, permissions):
    conn = get_db_connection()
    perms_str = ','.join(permissions) if permissions else ''
    conn.execute('''INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions)
                   VALUES (?, ?, ?, ?, ?)''',
                   (vendor_id, member_name, member_email, role, perms_str))
    conn.commit()
    conn.close()

def get_team_members(vendor_id):
    conn = get_db_connection()
    members = conn.execute("SELECT * FROM vendor_team WHERE vendor_id = ?", (vendor_id,)).fetchall()
    conn.close()
    return members

def delete_team_member(member_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM vendor_team WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

def get_vendor_by_user_id(user_id):
    conn = get_db_connection()
    vendor = conn.execute("SELECT * FROM vendors WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return vendor

def get_guest_rsvp_stats(wedding_id):
    conn = get_db_connection()
    confirmed = conn.execute("SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = 'confirmed'", (wedding_id,)).fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = 'pending'", (wedding_id,)).fetchone()[0]
    declined = conn.execute("SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = 'declined'", (wedding_id,)).fetchone()[0]
    conn.close()
    return {'confirmed': confirmed, 'pending': pending, 'declined': declined, 'total': confirmed + pending + declined}

def create_or_update_wedding(host_id, couple_names, event_date, venue, venue_address, guest_count):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM weddings WHERE host_id = ?", (host_id,)).fetchone()
    
    if existing:
        conn.execute('''UPDATE weddings 
                       SET couple_names = ?, event_date = ?, venue = ?, venue_address = ?, guest_count = ?
                       WHERE host_id = ?''',
                       (couple_names, event_date, venue, venue_address, guest_count, host_id))
    else:
        conn.execute('''INSERT INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                       (host_id, couple_names, event_date, venue, venue_address, guest_count))
    conn.commit()
    conn.close()

# ==================== LOGIN PAGE ====================
def show_login():
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 56px;">💍 Shadi-Hub</h1>
        <p style="font-size: 20px; color: #D4AF37;">Your Complete Wedding Ecosystem</p>
        <p>Everything you need for your dream wedding - Vendors, Shopping, Invitations & More!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "🎭 Demo Access"])
        
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
            st.markdown("Click any button to login as demo user")
            
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
    
    with tab1:
        st.subheader("Wedding Details")
        col1, col2 = st.columns(2)
        with col1:
            couple = st.text_input("Couple Names", wedding['couple_names'] if wedding else "Rahul & Priya")
            venue = st.text_input("Venue", wedding['venue'] if wedding else "Grand Palace")
        with col2:
            if wedding and wedding['event_date']:
                event_date = st.date_input("Wedding Date", datetime.strptime(wedding['event_date'], '%Y-%m-%d').date())
            else:
                event_date = st.date_input("Wedding Date", datetime(2024, 12, 15))
            guest_count = st.number_input("Expected Guests", value=int(wedding['guest_count']) if wedding and wedding['guest_count'] else 150)
        
        venue_address = st.text_area("Venue Address", wedding['venue_address'] if wedding else "")
        
        if st.button("💾 Save Wedding Details"):
            create_or_update_wedding(user['id'], couple, str(event_date), venue, venue_address, guest_count)
            st.success("✅ Wedding details saved!")
            st.rerun()
    
    with tab2:
        st.subheader("Guest Management")
        
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
                    code = add_guest(wedding_id, guest_name, guest_email, guest_phone, guest_category)
                    st.success(f"✅ {guest_name} added! Invitation code: {code}")
                    st.rerun()
                elif not wedding_id:
                    st.warning("Please setup wedding details first in 'Wedding Info' tab")
                else:
                    st.warning("Please enter guest name")
        
        if wedding_id:
            guests = get_all_guests(wedding_id)
            if guests:
                guest_data = []
                for g in guests:
                    guest_data.append({
                        "Name": g['name'],
                        "Email": g['email'] or "-",
                        "Phone": g['phone'] or "-",
                        "RSVP": g['rsvp_status'].title(),
                        "ID": g['id']
                    })
                df = pd.DataFrame(guest_data)
                st.dataframe(df.drop(columns=['ID']), use_container_width=True)
                
                with st.expander("🗑️ Delete Guest"):
                    guest_names = {g['name']: g['id'] for g in guests}
                    selected_guest = st.selectbox("Select guest to delete", list(guest_names.keys()))
                    if st.button("Delete Guest", key="del_btn"):
                        delete_guest(guest_names[selected_guest])
                        st.success(f"Deleted {selected_guest}")
                        st.rerun()
            else:
                st.info("No guests added yet.")
        else:
            st.warning("Please setup wedding details first")
    
    with tab3:
        st.subheader("Digital Invitation Generator")
        if wedding and wedding_id:
            guests = get_all_guests(wedding_id)
            if guests:
                if st.button("🎨 Generate Invitations for ALL Guests", use_container_width=True):
                    os.makedirs("invitations", exist_ok=True)
                    progress_bar = st.progress(0)
                    for i, guest in enumerate(guests):
                        path = f"invitations/{guest['name']}.jpg"
                        generate_invitation_card(guest['name'], wedding['couple_names'], 
                                               wedding['event_date'], wedding['venue'], 
                                               wedding['venue_address'] or wedding['venue'], path)
                        progress_bar.progress((i + 1) / len(guests))
                    st.success(f"✅ Generated {len(guests)} invitations!")
                    st.balloons()
            else:
                st.warning("Please add guests first!")
        else:
            st.warning("Please setup wedding details first")
    
    with tab4:
        st.subheader("Find Wedding Vendors")
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Category", ["All", "photographer", "mehndi", "catering", "venue", "decor", "makeup"])
        with col2:
            price_filter = st.selectbox("Budget", ["All", "budget", "mid-range", "premium", "luxury"])
        with col3:
            location_filter = st.text_input("Location", placeholder="City name")
        
        vendors = get_all_vendors(
            None if category_filter == "All" else category_filter,
            None if price_filter == "All" else price_filter,
            location_filter if location_filter else None
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
            st.info("No vendors found")

# ==================== VENDOR DASHBOARD ====================
def vendor_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>📸 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    
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
                df = pd.DataFrame(team_data)
                st.dataframe(df.drop(columns=['ID']), use_container_width=True)
                
                with st.expander("🗑️ Remove Team Member"):
                    member_names = {m['member_name']: m['id'] for m in team}
                    selected_member = st.selectbox("Select member to remove", list(member_names.keys()))
                    if st.button("Remove Member"):
                        delete_team_member(member_names[selected_member])
                        st.success(f"Removed {selected_member}")
                        st.rerun()
            else:
                st.info("No team members yet.")
    
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
    user = st.session_state.user
    st.markdown(f"<h1>💌 Hello {user['name']}!</h1>", unsafe_allow_html=True)
    
    guest = get_guest_by_email(user['email'])
    
    if not guest:
        st.error("Guest profile not found!")
        return
    
    wedding = get_wedding_by_id(guest['wedding_id'])
    
    if not wedding
