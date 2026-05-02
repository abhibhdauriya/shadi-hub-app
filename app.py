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
    .stApp { background: linear-gradient(135deg, #FFF5E6 0%, #FFFFFF 100%); }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Georgia', serif; }
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37, #C5A028);
        color: white; border: none; border-radius: 25px;
        padding: 10px 25px; font-weight: bold; width: 100%;
    }
    .stButton > button:hover { transform: scale(1.02); }
    .wedding-card {
        background: white; border-radius: 20px; padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; margin: 20px 0;
    }
    .product-card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
    }
    .price-tag { font-size: 20px; font-weight: bold; color: #D4AF37; }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE SETUP ====================
DB_PATH = 'shadi_hub.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, role TEXT CHECK(role IN ('host', 'vendor', 'guest'))
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS weddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INTEGER NOT NULL, couple_names TEXT NOT NULL,
        event_date TEXT NOT NULL, venue TEXT NOT NULL,
        venue_address TEXT, guest_count INTEGER DEFAULT 0,
        FOREIGN KEY(host_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wedding_id INTEGER NOT NULL, name TEXT NOT NULL,
        email TEXT, phone TEXT, category TEXT,
        rsvp_status TEXT DEFAULT 'pending',
        invitation_code TEXT UNIQUE, well_wish TEXT,
        FOREIGN KEY(wedding_id) REFERENCES weddings(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, business_name TEXT NOT NULL,
        category TEXT NOT NULL, description TEXT,
        price_range TEXT, min_price REAL, max_price REAL,
        rating REAL DEFAULT 0, location TEXT, whatsapp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER, name TEXT NOT NULL,
        category TEXT, price REAL, original_price REAL,
        description TEXT, image_url TEXT, discount INTEGER
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendor_team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL, member_name TEXT NOT NULL,
        member_email TEXT NOT NULL, role TEXT NOT NULL,
        permissions TEXT, FOREIGN KEY(vendor_id) REFERENCES vendors(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS wedding_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wedding_id INTEGER NOT NULL, photo_url TEXT NOT NULL,
        caption TEXT, is_sneak_peek INTEGER DEFAULT 0,
        uploaded_by TEXT, uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(wedding_id) REFERENCES weddings(id)
    )''')
    
    conn.commit()
    conn.close()

def seed_demo_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Host
    host_pass = hashlib.md5("host123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Rahul & Priya", "host@demo.com", host_pass, "host"))
    host_id = cursor.lastrowid
    
    # Wedding
    cursor.execute('''INSERT INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                   (host_id, "Rahul & Priya", "2024-12-15", "Grand Palace, Mumbai", "Marine Drive, Mumbai", 200))
    wedding_id = cursor.lastrowid
    
    # Vendor
    vendor_pass = hashlib.md5("vendor123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Dream Photography", "vendor@demo.com", vendor_pass, "vendor"))
    vendor_user_id = cursor.lastrowid
    
    cursor.execute('''INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location, whatsapp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (vendor_user_id, "Dream Photography Studio", "photographer", "Award winning wedding photographers", "premium", 50000, 200000, 4.9, "Mumbai", "919876543210"))
    
    # More vendors
    vendors_data = [
        ("Mehndi Art by Seema", "mehndi", "Bridal mehndi specialist", "mid-range", 10000, 50000, 4.7, "Delhi", "919876543211"),
        ("Grand Palace Hotel", "venue", "Luxury wedding venue", "luxury", 500000, 2000000, 4.8, "Mumbai", "919876543212"),
        ("Spice Caterers", "catering", "Exotic wedding cuisine", "premium", 500, 1500, 4.6, "Mumbai", "919876543213"),
        ("Magic Decorators", "decor", "Theme based decoration", "mid-range", 50000, 150000, 4.5, "Mumbai", "919876543214"),
    ]
    
    for v in vendors_data:
        cursor.execute('''INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location, whatsapp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (vendor_user_id,) + v)
    
    # Products
    products_data = [
        ("Royal Wedding Lehenga", "outfits", 45000, 55000, "Beautiful red bridal lehenga", 18),
        ("Designer Sherwani", "outfits", 35000, 45000, "Royal gold sherwani for groom", 22),
        ("Premium Gift Hamper", "gifts", 2500, 4000, "Luxury wedding gift set", 37),
        ("Wedding Decor Pack", "decor", 15000, 25000, "Complete decor setup", 40),
        ("Bridal Jewelry Set", "accessories", 12000, 20000, "Gold plated bridal set", 40),
    ]
    
    for p in products_data:
        cursor.execute('''INSERT INTO products (vendor_id, name, category, price, original_price, description, image_url, discount)
                       VALUES (1, ?, ?, ?, ?, ?, ?, ?)''',
                       (p[0], p[1], p[2], p[3], p[4], "https://via.placeholder.com/300x300", p[5]))
    
    # Guests
    guests_data = [
        ("Amit Sharma", "amit@guest.com", "9876543210", "Friend", "confirmed", "INV001"),
        ("Neha Gupta", "neha@guest.com", "9876543211", "Friend", "pending", "INV002"),
        ("Rajesh Kumar", "rajesh@guest.com", "9876543212", "Family", "confirmed", "INV003"),
        ("Priya Singh", "priya@guest.com", "9876543213", "Family", "pending", "INV004"),
    ]
    
    for g in guests_data:
        cursor.execute('''INSERT INTO guests (wedding_id, name, email, phone, category, rsvp_status, invitation_code)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (wedding_id,) + g)
    
    # Guest user
    guest_pass = hashlib.md5("guest123".encode()).hexdigest()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Amit Sharma", "guest@demo.com", guest_pass, "guest"))
    
    conn.commit()
    conn.close()

# ==================== INVITATION GENERATOR ====================
def generate_invitation_card(guest_name, couple_names, event_date, venue, venue_address, output_path):
    try:
        img = Image.new('RGB', (800, 600), color='#FFF8F0')
        draw = ImageDraw.Draw(img)
        
        for i in range(4):
            draw.rectangle([i*2, i*2, 800-i*2, 600-i*2], outline='#D4AF37', width=3)
        
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 38)
            font_names = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 32)
            font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except:
            font_title = font_names = font_text = ImageFont.load_default()
        
        draw.text((400, 60), "WEDDING INVITATION", fill='#D4AF37', anchor="mm", font=font_title)
        draw.text((400, 130), couple_names, fill='#8B6914', anchor="mm", font=font_names)
        draw.text((400, 230), f"Dear {guest_name},", fill='#666666', anchor="mm", font=font_text)
        draw.text((400, 280), "You are cordially invited to celebrate", fill='#555555', anchor="mm", font=font_text)
        draw.text((400, 350), f"Date: {event_date}", fill='#D4AF37', anchor="mm", font=font_text)
        draw.text((400, 400), f"Venue: {venue}", fill='#D4AF37', anchor="mm", font=font_text)
        draw.text((400, 550), "Reception to follow", fill='#8B6914', anchor="mm", font=font_text)
        
        os.makedirs("invitations", exist_ok=True)
        img.save(output_path)
        return output_path
    except Exception as e:
        return None

# ==================== DATABASE FUNCTIONS ====================
def verify_login(email, password):
    conn = get_db_connection()
    hashed = hashlib.md5(password.encode()).hexdigest()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed)).fetchone()
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

def get_vendor_by_user_id(user_id):
    conn = get_db_connection()
    vendor = conn.execute("SELECT * FROM vendors WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return vendor

def add_team_member(vendor_id, member_name, member_email, role, permissions):
    conn = get_db_connection()
    perms_str = ','.join(permissions) if permissions else ''
    conn.execute('''INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions)
                   VALUES (?, ?, ?, ?, ?)''', (vendor_id, member_name, member_email, role, perms_str))
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

# ==================== LOGIN PAGE ====================
def show_login():
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 56px;">💍 Shadi-Hub</h1>
        <p style="font-size: 20px; color: #D4AF37;">Your Complete Wedding Ecosystem</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "🎭 Demo Access"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    user = verify_login(email, password)
                    if user:
                        st.session_state.user = dict(user)
                        st.success(f"Welcome {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
        
        with tab2:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("💒 Host", use_container_width=True):
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

# ==================== GUEST DASHBOARD ====================
def guest_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>💌 Hello {user['name']}!</h1>", unsafe_allow_html=True)
    
    guest = get_guest_by_email(user['email'])
    
    if guest is None:
        st.error("Guest profile not found!")
        return
    
    wedding = get_wedding_by_id(guest['wedding_id'])
    
    if wedding is None:
        st.error("Wedding details not found!")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💌 Invitation", "✅ RSVP", "🛍️ Shop", "💝 Blessings"])
    
    with tab1:
        st.markdown(f"""
        <div class="wedding-card">
            <h2>✨ You're Invited! ✨</h2>
            <h3>{wedding['couple_names']}</h3>
            <p>Request the pleasure of your company</p>
            <hr>
            <p><b>📅 Date:</b> {wedding['event_date']}</p>
            <p><b>📍 Venue:</b> {wedding['venue']}</p>
            <p><b>⏰ Time:</b> 7:00 PM onwards</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Download Invitation", use_container_width=True):
                path = f"invitations/{user['name']}.jpg"
                generate_invitation_card(user['name'], wedding['couple_names'], 
                                       wedding['event_date'], wedding['venue'],
                                       wedding['venue_address'] or wedding['venue'], path)
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button("💾 Save", f, file_name="invitation.jpg", use_container_width=True)
        
        with col2:
            msg = f"Wedding Invitation! {wedding['couple_names']} on {wedding['event_date']} at {wedding['venue']}"
            whatsapp_url = f"https://wa.me/?text={msg.replace(' ', '%20')}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background:#25D366; color:white; border:none; border-radius:25px; padding:10px; width:100%;">📱 Share on WhatsApp</button></a>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Will You Attend?")
        current = guest['rsvp_status']
        
        col1, col2 = st.columns(2)
        with col1:
            if current != "confirmed":
                if st.button("✅ Yes, I Will Attend", use_container_width=True):
                    update_guest_rsvp(guest['id'], "confirmed")
                    st.success("Thank you! 🎉")
                    st.balloons()
                    st.rerun()
            else:
                st.success("✅ You are attending!")
        
        with col2:
            if current != "declined":
                if st.button("❌ Cannot Attend", use_container_width=True):
                    update_guest_rsvp(guest['id'], "declined")
                    st.info("We'll miss you! 💝")
                    st.rerun()
            else:
                st.info("❌ You declined")
    
    with tab3:
        st.subheader("Wedding Shop")
        categories = ["All", "outfits", "gifts", "decor", "accessories"]
        selected_cat = st.selectbox("Category", categories)
        products = get_all_products(None if selected_cat == "All" else selected_cat)
        
        if products:
            cols = st.columns(3)
            for idx, p in enumerate(products):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="product-card">
                        <h4>{p['name']}</h4>
                        <p class="price-tag">₹{p['price']:,.0f}</p>
                        <p style="font-size:12px;">{p['description'][:50]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Buy Now", key=f"buy_{p['id']}"):
                        st.success("Added to cart! 🎁")
    
    with tab4:
        st.subheader("Leave Your Blessings")
        current_wish = guest['well_wish'] if guest['well_wish'] else ""
        wish = st.text_area("Write your wishes...", value=current_wish, height=100)
        if st.button("Send Blessings", use_container_width=True):
            if wish:
                update_guest_well_wish(guest['id'], wish)
                st.success("Thank you for your blessings! 💕")
                st.balloons()

# ==================== HOST DASHBOARD ====================
def host_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>🌟 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    st.info("Host Dashboard - Manage your wedding here")
    
    tab1, tab2 = st.tabs(["🏠 Wedding Info", "👥 Guests"])
    
    with tab1:
        wedding = get_wedding_by_host(user['id'])
        if wedding:
            st.write(f"**Couple:** {wedding['couple_names']}")
            st.write(f"**Date:** {wedding['event_date']}")
            st.write(f"**Venue:** {wedding['venue']}")
    
    with tab2:
        if wedding:
            guests = get_db_connection().execute("SELECT name, email, rsvp_status FROM guests WHERE wedding_id=?", (wedding['id'],)).fetchall()
            if guests:
                df = pd.DataFrame([dict(g) for g in guests])
                st.dataframe(df, use_container_width=True)

# ==================== VENDOR DASHBOARD ====================
def vendor_dashboard():
    user = st.session_state.user
    st.markdown(f"<h1>📸 Welcome, {user['name']}!</h1>", unsafe_allow_html=True)
    
    vendor = get_vendor_by_user_id(user['id'])
    
    with st.form("add_team"):
        st.subheader("Add Team Member")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Member Name")
            email = st.text_input("Email")
        with col2:
            role = st.selectbox("Role", ["photographer", "editor", "assistant"])
            perms = st.multiselect("Permissions", ["upload_photos", "edit_schedule"])
        
        if st.form_submit_button("Add Member"):
            if vendor and name:
                add_team_member(vendor['id'], name, email, role, perms)
                st.success(f"Added {name}!")
                st.rerun()
    
    if vendor:
        team = get_team_members(vendor['id'])
        if team:
            st.subheader("Team Members")
            for m in team:
                st.write(f"👤 {m['member_name']} - {m['role']}")

# ==================== MAIN ====================
def main():
    # Initialize
    init_db()
    seed_demo_data()
    
    # Session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 💍 Shadi-Hub")
        
        if st.session_state.user:
            st.markdown(f"Welcome, **{st.session_state.user['name']}**")
            st.markdown(f"Role: {st.session_state.user['role'].title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            show_login()
    
    # Main content
    if st.session_state.user:
        role = st.session_state.user['role']
        if role == 'host':
            host_dashboard()
        elif role == 'vendor':
            vendor_dashboard()
        elif role == 'guest':
            guest_dashboard()
    else:
        st.info("👈 Please login from the sidebar")

if __name__ == "__main__":
    main()
