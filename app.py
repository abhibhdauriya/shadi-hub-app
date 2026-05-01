import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Shadi-Hub", page_icon="💍", layout="wide")

# ---------- CUSTOM CSS ----------
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
    }
    div[data-testid="stMetricValue"] {
        color: #D4AF37;
    }
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('shadi_hub.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, 
        name TEXT, role TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS weddings (
        id INTEGER PRIMARY KEY, host_id INTEGER, couple_names TEXT, 
        event_date TEXT, venue TEXT, guest_count INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY, wedding_id INTEGER, name TEXT, 
        email TEXT, phone TEXT, rsvp_status TEXT, invitation_code TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY, user_id INTEGER, business_name TEXT, 
        category TEXT, price_range TEXT, rating REAL, location TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS vendor_team (
        id INTEGER PRIMARY KEY, vendor_id INTEGER, member_email TEXT, 
        member_name TEXT, role TEXT, permissions TEXT)''')
    
    # Demo users
    c.execute("SELECT * FROM users WHERE email='host@demo.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (1, 'host@demo.com', ?, 'Rahul & Priya', 'host')",
                  (hashlib.md5('host123'.encode()).hexdigest(),))
        c.execute("INSERT INTO users VALUES (2, 'vendor@demo.com', ?, 'Dream Photography', 'vendor')",
                  (hashlib.md5('vendor123'.encode()).hexdigest(),))
        c.execute("INSERT INTO users VALUES (3, 'guest@demo.com', ?, 'Amit Kumar', 'guest')",
                  (hashlib.md5('guest123'.encode()).hexdigest(),))
        c.execute("INSERT INTO weddings VALUES (1, 1, 'Rahul & Priya', '2024-12-15', 'Grand Palace, Mumbai', 200)")
        c.execute("INSERT INTO vendors VALUES (1, 2, 'Dream Photography', 'photographer', 'premium', 4.8, 'Mumbai')")
        c.execute("INSERT INTO vendors VALUES (2, 2, 'Mehndi Art', 'mehndi', 'mid-range', 4.5, 'Delhi')")
    
    conn.commit()
    conn.close()

# ---------- INVITATION GENERATOR ----------
def generate_invitation(guest_name, couple_names, event_date, venue, output_path):
    img = Image.new('RGB', (800, 600), color='#FFF5E6')
    draw = ImageDraw.Draw(img)
    
    # Gold border
    for i in range(5):
        draw.rectangle([i*2, i*2, 800-i*2, 600-i*2], outline='#D4AF37', width=2)
    
    # Text
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 36)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28)
        font_detail = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_title = font_name = font_detail = ImageFont.load_default()
    
    draw.text((400, 80), "✨ WEDDING INVITATION ✨", fill='#D4AF37', anchor="mm", font=font_title)
    draw.text((400, 140), couple_names, fill='#8B6914', anchor="mm", font=font_title)
    draw.text((400, 220), f"Dear {guest_name},", fill='#666', anchor="mm", font=font_name)
    draw.text((400, 280), "You are cordially invited", fill='#666', anchor="mm", font=font_detail)
    draw.text((400, 340), f"📅 {event_date}  |  📍 {venue}", fill='#666', anchor="mm", font=font_detail)
    
    img.save(output_path)
    return output_path

# ---------- LOGIN ----------
def login():
    st.markdown("<h1 style='text-align:center;'>💍 Shadi-Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#D4AF37;'>Complete Wedding Ecosystem</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
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
                st.error("Use: host@demo.com / host123")
        
        st.markdown("---")
        st.code("Host: host@demo.com / host123\nVendor: vendor@demo.com / vendor123\nGuest: guest@demo.com / guest123")

# ---------- HOST DASHBOARD ----------
def host_dashboard():
    st.markdown(f"<h1>🌟 Welcome, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏠 Wedding Info", "👥 Guests", "🎨 Invitations"])
    
    with tab1:
        couple = st.text_input("Couple Names", "Rahul & Priya")
        date = st.date_input("Wedding Date", datetime(2024, 12, 15))
        venue = st.text_input("Venue", "Grand Palace, Mumbai")
        if st.button("Save"):
            st.success("Saved!")
    
    with tab2:
        with st.expander("➕ Add Guest"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            if st.button("Add"):
                conn = sqlite3.connect('shadi_hub.db')
                c = conn.cursor()
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                c.execute("INSERT INTO guests (wedding_id, name, email, rsvp_status, invitation_code) VALUES (1, ?, ?, 'pending', ?)",
                         (name, email, code))
                conn.commit()
                conn.close()
                st.success(f"Added {name}!")
                st.rerun()
        
        conn = sqlite3.connect('shadi_hub.db')
        guests = pd.read_sql_query("SELECT name, email, rsvp_status FROM guests WHERE wedding_id=1", conn)
        conn.close()
        if not guests.empty:
            st.dataframe(guests, use_container_width=True)
            st.metric("Total Guests", len(guests))
    
    with tab3:
        conn = sqlite3.connect('shadi_hub.db')
        wedding = pd.read_sql_query("SELECT couple_names, event_date, venue FROM weddings WHERE id=1", conn)
        guests_list = pd.read_sql_query("SELECT name FROM guests WHERE wedding_id=1", conn)
        conn.close()
        
        if not wedding.empty and not guests_list.empty:
            if st.button("🎨 Generate Invitations for ALL Guests"):
                os.makedirs("invitations", exist_ok=True)
                progress = st.progress(0)
                for i, guest in enumerate(guests_list['name'].tolist()):
                    path = f"invitations/{guest}.jpg"
                    generate_invitation(guest, wedding.iloc[0]['couple_names'], 
                                       wedding.iloc[0]['event_date'], wedding.iloc[0]['venue'], path)
                    progress.progress((i+1)/len(guests_list))
                st.success(f"Generated {len(guests_list)} invitations!")
                st.balloons()

# ---------- VENDOR DASHBOARD ----------
def vendor_dashboard():
    st.markdown(f"<h1>📸 {st.session_state.user_name}</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ Add Team Member"):
        name = st.text_input("Member Name")
        email = st.text_input("Email")
        role = st.selectbox("Role", ["photographer", "editor", "assistant"])
        if st.button("Add to Team"):
            conn = sqlite3.connect('shadi_hub.db')
            c = conn.cursor()
            c.execute("INSERT INTO vendor_team (vendor_id, member_email, member_name, role, permissions) VALUES (1, ?, ?, ?, '[]')",
                     (email, name, role))
            conn.commit()
            conn.close()
            st.success(f"{name} added!")
    
    conn = sqlite3.connect('shadi_hub.db')
    team = pd.read_sql_query("SELECT member_name, role FROM vendor_team WHERE vendor_id=1", conn)
    conn.close()
    if not team.empty:
        st.dataframe(team, use_container_width=True)

# ---------- GUEST VIEW ----------
def guest_view():
    st.markdown(f"<h1>💌 Dear {st.session_state.user_name},</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('shadi_hub.db')
    wedding = pd.read_sql_query("SELECT couple_names, event_date, venue FROM weddings WHERE id=1", conn)
    conn.close()
    
    if not wedding.empty:
        st.markdown(f"""
        <div style="background:white;padding:40px;border-radius:20px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h2 style="color:#D4AF37;">✨ You're Invited! ✨</h2>
            <h3>{wedding.iloc[0]['couple_names']}</h3>
            <p>📅 {wedding.iloc[0]['event_date']}</p>
            <p>📍 {wedding.iloc[0]['venue']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Will Attend"):
            st.success("Thank you! 🎉")
            st.balloons()

# ---------- MAIN ----------
def main():
    init_db()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
    else:
        with st.sidebar:
            st.markdown(f"**{st.session_state.user_name}**")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        
        if st.session_state.user_role == 'host':
            host_dashboard()
        elif st.session_state.user_role == 'vendor':
            vendor_dashboard()
        else:
            guest_view()

if __name__ == "__main__":
    main()
