import sqlite3
import os
import json
import datetime
import uuid

# Database file path
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        dob TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT NOT NULL,
        street TEXT NOT NULL,
        city TEXT NOT NULL,
        postcode TEXT NOT NULL,
        verification_status TEXT DEFAULT 'pending',
        applicant_id TEXT,
        verification_details TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # Create sessions table for authentication
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create audit_logs table for tracking important events
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_user(user_data):
    """Create a new user in the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
    if cursor.fetchone():
        conn.close()
        return None, "Email already registered"
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    now = datetime.datetime.now().isoformat()
    
    # Insert user data
    cursor.execute('''
    INSERT INTO users (
        id, first_name, last_name, dob, email, phone_number, 
        street, city, postcode, verification_status, 
        verification_details, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        user_data['firstName'],
        user_data['lastName'],
        user_data['dob'],
        user_data['email'],
        user_data['phoneNumber'],
        user_data['street'],
        user_data['city'],
        user_data['postcode'],
        'pending',
        json.dumps({"lastChecked": now}),
        now,
        now
    ))
    
    # Log the action
    log_action(cursor, None, "USER_CREATED", f"User {user_id} created", user_data.get('ip_address'))
    
    conn.commit()
    conn.close()
    
    return user_id, None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM users WHERE id = ?
    ''', (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_email(email):
    """Get user by email"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM users WHERE email = ?
    ''', (email,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def update_verification_status(user_id, status, applicant_id=None, details=None):
    """Update user verification status"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    verification_details = {"lastChecked": now}
    
    if details:
        verification_details.update(details)
    
    cursor.execute('''
    UPDATE users 
    SET verification_status = ?, 
        applicant_id = ?,
        verification_details = ?,
        updated_at = ?
    WHERE id = ?
    ''', (
        status,
        applicant_id,
        json.dumps(verification_details),
        now,
        user_id
    ))
    
    # Log the action
    log_action(cursor, user_id, "VERIFICATION_STATUS_UPDATED", f"Status updated to {status}")
    
    conn.commit()
    conn.close()
    
    return True

def create_session(user_id, token, expires_in=86400):
    """Create a new session for a user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    session_id = str(uuid.uuid4())
    now = datetime.datetime.now()
    expires_at = (now + datetime.timedelta(seconds=expires_in)).isoformat()
    
    cursor.execute('''
    INSERT INTO sessions (id, user_id, token, expires_at, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        session_id,
        user_id,
        token,
        expires_at,
        now.isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return session_id

def validate_session(token):
    """Validate a session token"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    
    cursor.execute('''
    SELECT user_id FROM sessions 
    WHERE token = ? AND expires_at > ?
    ''', (token, now))
    
    session = cursor.fetchone()
    conn.close()
    
    if session:
        return session['user_id']
    return None

def log_action(cursor, user_id, action, details, ip_address=None):
    """Log an action in the audit log"""
    log_id = str(uuid.uuid4())
    now = datetime.datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO audit_logs (id, user_id, action, details, ip_address, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        log_id,
        user_id,
        action,
        details,
        ip_address,
        now
    ))
    
    return log_id

# Initialize the database when the module is imported
init_db()
