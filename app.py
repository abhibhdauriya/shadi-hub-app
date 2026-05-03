import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Shadi-Hub", page_icon="💍", layout="wide")

# ========== DATABASE SETUP ==========
DB_PATH = 'shadi_hub.db'

def get_db():
    return sqlite3.connect(DB_PATH)

def setup_database():
    conn = get_db()
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # Weddings
    c.execute('''CREATE TABLE IF NOT EXISTS weddings (
        id INTEGER PRIMARY KEY, host_id INTEGER, couple_names TEXT, event_date TEXT, venue TEXT)''')
    
    # Guests
    c.execute('''CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY, wedding_id INTEGER, name TEXT, email TEXT, rsvp_status TEXT, invitation_code TEXT)''')
    
    # Vendors
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY, user_id INTEGER, business_name TEXT, category TEXT, rating REAL, location TEXT)''')
    
    # Products
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT)''')
    
    # Demo data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Host
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Rahul & Priya", "host@demo.com", hashlib.md5("host123".encode()).hexdigest(), "host"))
        host_id = c.lastrowid
        
        # Wedding
        c.execute("INSERT INTO weddings (host_id, couple_names, event_date, venue) VALUES (?, ?, ?, ?)",
                  (host_id, "Rahul & Priya", "2024-12-15", "Grand Palace, Mumbai"))
        wedding_id = c.lastrowid
        
        # Guests
        c.execute("INSERT INTO guests (wedding_id, name, email, rsvp_status, invitation_code) VALUES (?, ?, ?, ?, ?)",
                  (wedding_id, "Amit Sharma", "guest@demo.com", "pending", "INV001"))
        
        # Vendor
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Dream Photography", "vendor@demo.com", hashlib.md5("vendor123".encode()).hexdigest(), "vendor"))
        vendor_id = c.lastrowid
        
        c.execute("INSERT INTO vendors (user_id, business_name, category, rating, location) VALUES (?, ?, ?, ?, ?)",
                  (vendor_id, "Dream Photography", "photographer", 4.9, "Mumbai"))
        
        # Products
        products = [("Royal Lehenga", 45000, "outfits"), ("Designer Sherwani", 35000, "outfits"), ("Gift Hamper", 2500, "gifts")]
        for p in products:
            c.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", p)
    
    conn.commit()
    conn.close()

# ========== INVITATION GENERATOR ==========
def make_invitation(guest_name, couple, date, venue, output_path):
    img = Image.new('RGB', (800, 600), color='#FFF8F0')
    draw = ImageDraw.Draw(img)
    
    # Border
    for i in range(3):
        draw.rectangle([i*3, i*3, 800-i*3, 600-i*3], outline='#D4AF37', width=2)
    
    # Fonts
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36)
        font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28)
    except:
        font_big = font_mid = ImageFont.load_default()
    
    # Text
    draw.text((400, 80), "WEDDING INVITATION", fill='#D4AF37', anchor="mm", font=font_big)
    draw.text((400, 160), couple, fill='#8B6914', anchor="mm", font=font_big)
    draw.text((400, 260), f"Dear {guest_name},", fill='#666', anchor="mm", font=font_mid)
    draw.text((400, 330), "You are cordially invited", fill='#666', anchor="mm", font=font_mid)
    draw.text((400, 400), f"Date: {date}", fill='#D4AF37', anchor="mm", font=font_mid)
    draw.text((400, 460), f"Venue: {venue}", fill='#D4AF37', anchor="mm", font=font_mid)
    
    os.makedirs("invitations", exist_ok=True)
    img.save(output_path)
    return output_path

# ========== AUTH FUNCTIONS ==========
def login_user(email, password):
    conn = get_db()
    hashed = hashlib.md5(password.encode()).hexdigest()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
    conn.close()
    return user

# ========== GUEST FUNCTIONS ==========
def get_guest(email):
    conn = get_db()
    guest = conn.execute("SELECT * FROM guests WHERE email=?", (email,)).fetchone()
    conn.close()
    return guest

def get_wedding(wedding_id):
    conn = get_db()
    wedding = conn.execute("SELECT * FROM weddings WHERE id=?", (wedding_id,)).fetchone()
    conn.close()
    return wedding

def update_rsvp(guest_id, status):
    conn = get_db()
    conn.execute("UPDATE guests SET rsvp_status=? WHERE id=?", (status, guest_id))
    conn.commit()
    conn.close()

def update_wish(guest_id, wish):
    conn = get_db()
    conn.execute("UPDATE guests SET well_wish=? WHERE id=?", (wish, guest_id))
    conn.commit()
    conn.close()

def get_products(category=None):
    conn = get_db()
    if category and category != "All":
        products = conn.execute("SELECT * FROM products WHERE category=?", (category,)).fetchall()
    else:
        products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return products

# ========== VENDOR FUNCTIONS ==========
def get_vendor(user_id):
    conn = get_db()
    vendor = conn.execute("SELECT * FROM vendors WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return vendor

def add_team_member(vendor_id, name, email, role):
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS vendor_team (id INTEGER PRIMARY KEY, vendor_id INTEGER, name TEXT, email TEXT, role TEXT)")
    conn.execute("INSERT INTO vendor_team (vendor_id, name, email, role) VALUES (?, ?, ?, ?)", (vendor_id, name, email, role))
    conn.commit()
    conn.close()

def get_team(vendor_id):
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS vendor_team (id INTEGER PRIMARY KEY, vendor_id INTEGER, name TEXT, email TEXT, role TEXT)")
    team = conn.execute("SELECT * FROM vendor_team WHERE vendor_id=?", (vendor_id,)).fetchall()
    conn.close()
    return team

# ========== HOST FUNCTIONS ==========
def get_wedding_by_host(host_id):
    conn = get_db()
    wedding = conn.execute("SELECT * FROM weddings WHERE host_id=?", (host_id,)).fetchone()
    conn.close()
    return wedding

def get_all_guests(wedding_id):
    conn = get_db()
    guests = conn.execute("SELECT * FROM guests WHERE wedding_id=?", (wedding_id,)).fetchall()
    conn.close()
    return guests

def add_new_guest(wedding_id, name, email):
    conn = get_db()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    conn.execute("INSERT INTO guests (wedding_id, name, email, rsvp_status, invitation_code) VALUES (?, ?, ?, 'pending', ?)",
                 (wedding_id, name, email, code))
    conn.commit()
    conn.close()
    return code

def update_wedding(host_id, couple, date, venue):
    conn = get_db()
    conn.execute("UPDATE weddings SET couple_names=?, event_date=?, venue=? WHERE host_id=?", (couple, date, venue, host_id))
    conn.commit()
    conn.close()

# ========== LOGIN UI ==========
def show_login():
    st.markdown("""
    <div style="text-align:center; padding:50px">
        <h1 style="color:#D4AF37; font-size:48px;">💍 Shadi-Hub</h1>
        <p style="font-size:18px;">Complete Wedding Ecosystem</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                user = login_user(email, password)
                if user:
                    st.session_state['user'] = {
                        'id': user[0],
                        'name': user[1],
                        'email': user[2],
                        'role': user[4]
                    }
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.markdown("---")
        st.markdown("### Demo Accounts")
        if st.button("💒 Login as Host"):
            user = login_user("host@demo.com", "host123")
            if user:
                st.session_state['user'] = {'id': user[0], 'name': user[1], 'email': user[2], 'role': user[4]}
                st.rerun()
        if st.button("📸 Login as Vendor"):
            user = login_user("vendor@demo.com", "vendor123")
            if user:
                st.session_state['user'] = {'id': user[0], 'name': user[1], 'email': user[2], 'role': user[4]}
                st.rerun()
        if st.button("💝 Login as Guest"):
            user = login_user("guest@demo.com", "guest123")
            if user:
                st.session_state['user'] = {'id': user[0], 'name': user[1], 'email': user[2], 'role': user[4]}
                st.rerun()

# ========== GUEST UI ==========
def guest_ui():
    user = st.session_state['user']
    st.markdown(f"<h1>💌 Hello {user['name']}!</h1>", unsafe_allow_html=True)
    
    guest = get_guest(user['email'])
    if not guest:
        st.error("Guest not found")
        return
    
    wedding = get_wedding(guest[1])
    if not wedding:
        st.error("Wedding not found")
        return
    
    tab1, tab2, tab3 = st.tabs(["💌 Invitation", "✅ RSVP", "🛍️ Shop"])
    
    with tab1:
        st.markdown(f"""
        <div style="background:white; border-radius:20px; padding:30px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h2 style="color:#D4AF37;">✨ You're Invited! ✨</h2>
            <h3>{wedding[2]}</h3>
            <p>Request the pleasure of your company</p>
            <hr>
            <p><b>📅 Date:</b> {wedding[3]}</p>
            <p><b>📍 Venue:</b> {wedding[4]}</p>
            <p><b>⏰ Time:</b> 7:00 PM</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 Download Invitation Card"):
            path = f"invitations/{user['name']}.jpg"
            make_invitation(user['name'], wedding[2], wedding[3], wedding[4], path)
            with open(path, "rb") as f:
                st.download_button("💾 Save to Device", f, file_name="invitation.jpg")
        
        if st.button("📱 Share on WhatsApp"):
            msg = f"Wedding Invitation! {wedding[2]} on {wedding[3]} at {wedding[4]}"
            st.markdown(f'<a href="https://wa.me/?text={msg.replace(" ", "%20")}" target="_blank">Click to Share</a>', unsafe_allow_html=True)
    
    with tab2:
        current = guest[4]
        if current == "confirmed":
            st.success("✅ You are attending the wedding!")
        elif current == "declined":
            st.info("❌ You have declined the invitation")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Will Attend", use_container_width=True):
                    update_rsvp(guest[0], "confirmed")
                    st.success("Thank you! 🎉")
                    st.balloons()
                    st.rerun()
            with col2:
                if st.button("❌ Cannot Attend", use_container_width=True):
                    update_rsvp(guest[0], "declined")
                    st.success("We'll miss you! 💝")
                    st.rerun()
    
    with tab3:
        st.subheader("Wedding Shop")
        cat = st.selectbox("Category", ["All", "outfits", "gifts"])
        products = get_products(cat)
        for p in products:
            with st.container():
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"**{p[1]}**")
                    st.caption(p[3])
                with col2:
                    st.write(f"₹{p[2]:,.0f}")
                    if st.button("Buy", key=f"buy_{p[0]}"):
                        st.success("Added to cart! 🎁")
                st.divider()

# ========== VENDOR UI ==========
def vendor_ui():
    user = st.session_state['user']
    st.markdown(f"<h1>📸 Welcome {user['name']}!</h1>", unsafe_allow_html=True)
    
    vendor = get_vendor(user['id'])
    if not vendor:
        st.error("Vendor profile not found")
        return
    
    tab1, tab2 = st.tabs(["👥 Team", "📅 Bookings"])
    
    with tab1:
        with st.form("add_member"):
            name = st.text_input("Member Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["photographer", "editor", "assistant"])
            if st.form_submit_button("Add Team Member"):
                if name:
                    add_team_member(vendor[0], name, email, role)
                    st.success(f"Added {name}!")
                    st.rerun()
        
        team = get_team(vendor[0])
        if team:
            st.subheader("Team Members")
            for m in team:
                st.write(f"👤 {m[2]} - {m[4]}")
    
    with tab2:
        st.info("Booking requests will appear here")
        st.metric("Pending Requests", "0")

# ========== HOST UI ==========
def host_ui():
    user = st.session_state['user']
    st.markdown(f"<h1>🌟 Welcome {user['name']}!</h1>", unsafe_allow_html=True)
    
    wedding = get_wedding_by_host(user['id'])
    
    tab1, tab2 = st.tabs(["🏠 Wedding Info", "👥 Guests"])
    
    with tab1:
        if wedding:
            couple = st.text_input("Couple Names", wedding[2])
            date = st.date_input("Wedding Date", datetime.strptime(wedding[3], '%Y-%m-%d').date())
            venue = st.text_input("Venue", wedding[4])
        else:
            couple = st.text_input("Couple Names", "Rahul & Priya")
            date = st.date_input("Wedding Date", datetime(2024, 12, 15))
            venue = st.text_input("Venue", "Grand Palace")
        
        if st.button("Save Wedding Details"):
            update_wedding(user['id'], couple, str(date), venue)
            st.success("Saved!")
            st.rerun()
    
    with tab2:
        with st.expander("Add New Guest"):
            name = st.text_input("Guest Name")
            email = st.text_input("Email")
            if st.button("Add Guest"):
                if name and wedding:
                    code = add_new_guest(wedding[0], name, email)
                    st.success(f"Added {name}! Code: {code}")
                    st.rerun()
        
        if wedding:
            guests = get_all_guests(wedding[0])
            if guests:
                data = [{"Name": g[2], "Email": g[3], "RSVP": g[4]} for g in guests]
                st.dataframe(pd.DataFrame(data), use_container_width=True)

# ========== MAIN ==========
def main():
    setup_database()
    
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    
    with st.sidebar:
        st.markdown("### 💍 Shadi-Hub")
        if st.session_state['user']:
            st.write(f"Welcome **{st.session_state['user']['name']}**")
            st.write(f"Role: {st.session_state['user']['role'].title()}")
            if st.button("🚪 Logout"):
                st.session_state['user'] = None
                st.rerun()
    
    if st.session_state['user'] is None:
        show_login()
    else:
        role = st.session_state['user']['role']
        if role == 'guest':
            guest_ui()
        elif role == 'vendor':
            vendor_ui()
        elif role == 'host':
            host_ui()

if __name__ == "__main__":
    main()
