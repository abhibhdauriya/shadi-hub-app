import sqlite3
import hashlib
from datetime import datetime
import random
import string

def get_db_connection():
    conn = sqlite3.connect('wedding_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
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
            portfolio TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
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
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
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
    
    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wedding_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            message TEXT,
            event_date TEXT,
            budget REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(wedding_id) REFERENCES weddings(id),
            FOREIGN KEY(vendor_id) REFERENCES vendors(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# CRUD Operations
def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_user(name, email, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, hashed_password, role)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_wedding(host_id):
    conn = get_db_connection()
    wedding = conn.execute(
        'SELECT * FROM weddings WHERE host_id = ?', (host_id,)
    ).fetchone()
    conn.close()
    return wedding

def update_wedding(host_id, details):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count)
        VALUES (?, ?, ?, ?, ?, COALESCE((SELECT guest_count FROM weddings WHERE host_id=?), 0))
    ''', (*details, host_id))
    conn.commit()
    conn.close()

def get_all_guests(wedding_id):
    conn = get_db_connection()
    guests = conn.execute(
        'SELECT * FROM guests WHERE wedding_id = ? ORDER BY name', (wedding_id,)
    ).fetchall()
    conn.close()
    return guests

def add_guest(wedding_id, name, email, phone, category='Family'):
    conn = get_db_connection()
    cursor = conn.cursor()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    cursor.execute(
        'INSERT INTO guests (wedding_id, name, email, phone, category, invitation_code) VALUES (?, ?, ?, ?, ?, ?)',
        (wedding_id, name, email, phone, category, code)
    )
    conn.commit()
    conn.close()
    return code

def update_guest_status(guest_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE guests SET rsvp_status = ? WHERE id = ?', (status, guest_id))
    conn.commit()
    conn.close()

def delete_guest(guest_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM guests WHERE id = ?', (guest_id,))
    conn.commit()
    conn.close()

def get_all_vendors(filters=None):
    conn = get_db_connection()
    query = 'SELECT * FROM vendors WHERE 1=1'
    params = []
    if filters:
        if filters.get('category'):
            query += ' AND category = ?'
            params.append(filters['category'])
        if filters.get('location'):
            query += ' AND location LIKE ?'
            params.append(f'%{filters["location"]}%')
    vendors = conn.execute(query, params).fetchall()
    conn.close()
    return vendors

def get_vendor_by_id(vendor_id):
    conn = get_db_connection()
    vendor = conn.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,)).fetchone()
    conn.close()
    return vendor

def add_team_member(vendor_id, name, email, role, permissions):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions) VALUES (?, ?, ?, ?, ?)',
        (vendor_id, name, email, role, ','.join(permissions))
    )
    conn.commit()
    conn.close()

def get_team_members(vendor_id):
    conn = get_db_connection()
    members = conn.execute(
        'SELECT * FROM vendor_team WHERE vendor_id = ?', (vendor_id,)
    ).fetchall()
    conn.close()
    return members

def add_photo(wedding_id, url, is_sneak_peek, uploaded_by):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO wedding_photos (wedding_id, photo_url, is_sneak_peek, uploaded_by) VALUES (?, ?, ?, ?)',
        (wedding_id, url, is_sneak_peek, uploaded_by)
    )
    conn.commit()
    conn.close()

def get_photos(wedding_id, is_sneak_peek_only=False):
    conn = get_db_connection()
    if is_sneak_peek_only:
        photos = conn.execute(
            'SELECT * FROM wedding_photos WHERE wedding_id = ? AND is_sneak_peek = 1 ORDER BY uploaded_at DESC',
            (wedding_id,)
        ).fetchall()
    else:
        photos = conn.execute(
            'SELECT * FROM wedding_photos WHERE wedding_id = ? ORDER BY uploaded_at DESC',
            (wedding_id,)
        ).fetchall()
    conn.close()
    return photos

def seed_demo_data():
    # Demo Host
    host_id = create_user("Priya Sharma", "priya@example.com", "123456", "host")
    if host_id:
        update_wedding(host_id, ("Priya & Rohan", "2024-12-25", "Taj Hotel", "Mumbai"))
    
    # Demo Vendor
    vendor_id = create_user("Raj Photography", "raj@example.com", "123456", "vendor")
    if vendor_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vendors (user_id, business_name, category, description, price_range, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vendor_id, "Raj Photography", "Photography", "Best wedding photographers", "₹50k-₹2L", "Mumbai"))
        conn.commit()
        conn.close()
    
    # Demo Guest
    guest_id = create_user("Amit Guest", "amit@example.com", "123456", "guest")
