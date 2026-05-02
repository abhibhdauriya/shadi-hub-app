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

# ==================== USER CRUD ====================

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
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
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_login(email, password):
    conn = get_db_connection()
    hashed = hashlib.md5(password.encode()).hexdigest()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ? AND password = ?', 
        (email, hashed)
    ).fetchone()
    conn.close()
    return user

# ==================== WEDDING CRUD ====================

def get_wedding_by_host(host_id):
    conn = get_db_connection()
    wedding = conn.execute(
        'SELECT * FROM weddings WHERE host_id = ?', (host_id,)
    ).fetchone()
    conn.close()
    return wedding

def get_wedding_by_id(wedding_id):
    conn = get_db_connection()
    wedding = conn.execute(
        'SELECT * FROM weddings WHERE id = ?', (wedding_id,)
    ).fetchone()
    conn.close()
    return wedding

def create_or_update_wedding(host_id, couple_names, event_date, venue, venue_address, guest_count):
    """Create or update wedding for a host"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if wedding exists
    existing = conn.execute(
        'SELECT id FROM weddings WHERE host_id = ?', (host_id,)
    ).fetchone()
    
    if existing:
        # Update existing
        cursor.execute('''
            UPDATE weddings 
            SET couple_names = ?, event_date = ?, venue = ?, venue_address = ?, guest_count = ?
            WHERE host_id = ?
        ''', (couple_names, event_date, venue, venue_address, guest_count, host_id))
    else:
        # Insert new
        cursor.execute('''
            INSERT INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (host_id, couple_names, event_date, venue, venue_address, guest_count))
    
    conn.commit()
    conn.close()

# ==================== GUEST CRUD ====================

def get_all_guests(wedding_id):
    conn = get_db_connection()
    guests = conn.execute(
        'SELECT * FROM guests WHERE wedding_id = ? ORDER BY name', (wedding_id,)
    ).fetchall()
    conn.close()
    return guests

def get_guest_by_id(guest_id):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE id = ?', (guest_id,)).fetchone()
    conn.close()
    return guest

def get_guest_by_code(invitation_code):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE invitation_code = ?', (invitation_code,)).fetchone()
    conn.close()
    return guest

def add_guest(wedding_id, name, email, phone, category='Family'):
    conn = get_db_connection()
    cursor = conn.cursor()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    cursor.execute('''
        INSERT INTO guests (wedding_id, name, email, phone, category, invitation_code, rsvp_status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    ''', (wedding_id, name, email, phone, category, code))
    conn.commit()
    guest_id = cursor.lastrowid
    conn.close()
    return guest_id, code

def update_guest_rsvp(guest_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE guests SET rsvp_status = ? WHERE id = ?', (status, guest_id))
    conn.commit()
    conn.close()

def update_guest_well_wish(guest_id, well_wish):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE guests SET well_wish = ? WHERE id = ?', (well_wish, guest_id))
    conn.commit()
    conn.close()

def delete_guest(guest_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM guests WHERE id = ?', (guest_id,))
    conn.commit()
    conn.close()

def get_guest_rsvp_stats(wedding_id):
    conn = get_db_connection()
    confirmed = conn.execute(
        'SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = "confirmed"', (wedding_id,)
    ).fetchone()[0]
    pending = conn.execute(
        'SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = "pending"', (wedding_id,)
    ).fetchone()[0]
    declined = conn.execute(
        'SELECT COUNT(*) FROM guests WHERE wedding_id = ? AND rsvp_status = "declined"', (wedding_id,)
    ).fetchone()[0]
    total = confirmed + pending + declined
    conn.close()
    return {'confirmed': confirmed, 'pending': pending, 'declined': declined, 'total': total}

# ==================== VENDOR CRUD ====================

def get_vendor_by_user_id(user_id):
    conn = get_db_connection()
    vendor = conn.execute('SELECT * FROM vendors WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return vendor

def get_vendor_by_id(vendor_id):
    conn = get_db_connection()
    vendor = conn.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,)).fetchone()
    conn.close()
    return vendor

def get_all_vendors(category=None, price_range=None, location=None):
    conn = get_db_connection()
    query = 'SELECT * FROM vendors WHERE 1=1'
    params = []
    
    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)
    if price_range and price_range != 'All':
        query += ' AND price_range = ?'
        params.append(price_range)
    if location:
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    query += ' ORDER BY rating DESC'
    vendors = conn.execute(query, params).fetchall()
    conn.close()
    return vendors

def create_or_update_vendor(user_id, business_name, category, description, price_range, 
                            min_price, max_price, location, portfolio='[]'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    existing = conn.execute('SELECT id FROM vendors WHERE user_id = ?', (user_id,)).fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE vendors 
            SET business_name = ?, category = ?, description = ?, price_range = ?,
                min_price = ?, max_price = ?, location = ?, portfolio = ?
            WHERE user_id = ?
        ''', (business_name, category, description, price_range, min_price, max_price, location, portfolio, user_id))
    else:
        cursor.execute('''
            INSERT INTO vendors (user_id, business_name, category, description, price_range, 
                               min_price, max_price, location, portfolio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, business_name, category, description, price_range, min_price, max_price, location, portfolio))
    
    conn.commit()
    conn.close()

# ==================== TEAM MANAGEMENT (RBAC) ====================

def add_team_member(vendor_id, member_name, member_email, role, permissions):
    """Add team member for vendor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Convert permissions list to comma-separated string
    perms_str = ','.join(permissions) if permissions else ''
    cursor.execute('''
        INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions)
        VALUES (?, ?, ?, ?, ?)
    ''', (vendor_id, member_name, member_email, role, perms_str))
    conn.commit()
    member_id = cursor.lastrowid
    conn.close()
    return member_id

def get_team_members(vendor_id):
    conn = get_db_connection()
    members = conn.execute(
        'SELECT * FROM vendor_team WHERE vendor_id = ? ORDER BY joined_at DESC', (vendor_id,)
    ).fetchall()
    conn.close()
    return members

def delete_team_member(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vendor_team WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()

def check_member_permission(vendor_id, member_email, permission):
    """Check if a team member has specific permission"""
    conn = get_db_connection()
    member = conn.execute(
        'SELECT permissions FROM vendor_team WHERE vendor_id = ? AND member_email = ?', 
        (vendor_id, member_email)
    ).fetchone()
    conn.close()
    if member:
        permissions = member['permissions'].split(',') if member['permissions'] else []
        return permission in permissions
    return False

# ==================== PHOTO GALLERY ====================

def add_photo(wedding_id, photo_url, is_sneak_peek, uploaded_by):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wedding_photos (wedding_id, photo_url, is_sneak_peek, uploaded_by, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (wedding_id, photo_url, 1 if is_sneak_peek else 0, uploaded_by, datetime.now().isoformat()))
    conn.commit()
    photo_id = cursor.lastrowid
    conn.close()
    return photo_id

def get_photos(wedding_id, sneak_peek_only=False):
    conn = get_db_connection()
    if sneak_peek_only:
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

def delete_photo(photo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wedding_photos WHERE id = ?', (photo_id,))
    conn.commit()
    conn.close()

# ==================== BOOKINGS ====================

def create_booking(wedding_id, vendor_id, message, event_date, budget):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (wedding_id, vendor_id, message, event_date, budget, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    ''', (wedding_id, vendor_id, message, event_date, budget, datetime.now().isoformat()))
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()
    return booking_id

def get_bookings_for_vendor(vendor_id):
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.*, w.couple_names 
        FROM bookings b
        JOIN weddings w ON b.wedding_id = w.id
        WHERE b.vendor_id = ?
        ORDER BY b.created_at DESC
    ''', (vendor_id,)).fetchall()
    conn.close()
    return bookings

def update_booking_status(booking_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
    conn.commit()
    conn.close()

# ==================== DEMO DATA ====================

def seed_demo_data():
    """Seed all demo data into database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        return
    
    # Create Host User
    host_password = hashlib.md5("host123".encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        ("Rahul & Priya", "host@demo.com", host_password, "host")
    )
    host_id = cursor.lastrowid
    
    # Create Wedding for Host
    cursor.execute('''
        INSERT INTO weddings (host_id, couple_names, event_date, venue, venue_address, guest_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (host_id, "Rahul & Priya", "2024-12-15", "Grand Palace, Mumbai", "Marine Drive, South Mumbai", 150))
    wedding_id = cursor.lastrowid
    
    # Create Vendor User
    vendor_password = hashlib.md5("vendor123".encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        ("Dream Photography", "vendor@demo.com", vendor_password, "vendor")
    )
    vendor_user_id = cursor.lastrowid
    
    # Create Vendor Profile
    cursor.execute('''
        INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (vendor_user_id, "Dream Photography Studio", "photographer", "Award winning wedding photographers", 
          "premium", 50000, 200000, 4.9, "Mumbai"))
    vendor_id = cursor.lastrowid
    
    # Add Sample Team Members
    cursor.execute('''
        INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions)
        VALUES (?, ?, ?, ?, ?)
    ''', (vendor_id, "Raj Kumar", "raj@dreamphoto.com", "photographer", "upload_photos,view_clients"))
    
    cursor.execute('''
        INSERT INTO vendor_team (vendor_id, member_name, member_email, role, permissions)
        VALUES (?, ?, ?, ?, ?)
    ''', (vendor_id, "Neha Singh", "neha@dreamphoto.com", "editor", "upload_photos"))
    
    # Create More Vendors
    vendors_data = [
        (vendor_user_id, "Mehndi Art by Seema", "mehndi", "Bridal mehndi specialist", "mid-range", 10000, 50000, 4.7, "Delhi"),
        (vendor_user_id, "Grand Palace Hotel", "venue", "Luxury wedding venue", "luxury", 500000, 2000000, 4.8, "Mumbai"),
        (vendor_user_id, "Spice Caterers", "catering", "Exotic wedding cuisine", "premium", 500, 1500, 4.6, "Mumbai"),
        (vendor_user_id, "Magic Decorators", "decor", "Theme based decoration", "mid-range", 50000, 150000, 4.5, "Mumbai"),
    ]
    
    for v in vendors_data:
        cursor.execute('''
            INSERT INTO vendors (user_id, business_name, category, description, price_range, min_price, max_price, rating, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', v)
    
    # Create Sample Guests
    guests_data = [
        (wedding_id, "Amit Sharma", "amit@test.com", "9876543210", "Friend", "confirmed", "INV001", None),
        (wedding_id, "Neha Gupta", "neha@test.com", "9876543211", "Friend", "pending", "INV002", None),
        (wedding_id, "Rajesh Kumar", "rajesh@test.com", "9876543212", "Family", "confirmed", "INV003", None),
        (wedding_id, "Priya Singh", "priya@test.com", "9876543213", "Family", "pending", "INV004", None),
        (wedding_id, "Vikram Mehta", "vikram@test.com", "9876543214", "Colleague", "declined", "INV005", None),
    ]
    
    for g in guests_data:
        cursor.execute('''
            INSERT INTO guests (wedding_id, name, email, phone, category, rsvp_status, invitation_code, well_wish)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', g)
    
    # Create Guest User
    guest_password = hashlib.md5("guest123".encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        ("Amit Sharma", "guest@demo.com", guest_password, "guest")
    )
    
    conn.commit()
    conn.close()
    
    print("Demo data seeded successfully!")

# ==================== HELPER FUNCTIONS ====================

def get_wedding_id_by_host(host_id):
    """Get wedding ID for a host"""
    conn = get_db_connection()
    result = conn.execute('SELECT id FROM weddings WHERE host_id = ?', (host_id,)).fetchone()
    conn.close()
    return result['id'] if result else None

def get_host_id_by_wedding(wedding_id):
    """Get host ID for a wedding"""
    conn = get_db_connection()
    result = conn.execute('SELECT host_id FROM weddings WHERE id = ?', (wedding_id,)).fetchone()
    conn.close()
    return result['host_id'] if result else None

# ==================== INITIALIZATION ====================

def initialize_app():
    """Initialize database and seed demo data"""
    init_db()
    seed_demo_data()
    
if __name__ == "__main__":
    initialize_app()
    print("Database initialized successfully!")
