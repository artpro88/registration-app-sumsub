import hashlib
import hmac
import base64
import os
import time
import uuid
import json
import ssl
import database

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-for-development')
TOKEN_EXPIRY = 86400  # 24 hours in seconds
RATE_LIMIT_WINDOW = 60  # 1 minute in seconds
RATE_LIMIT_MAX_REQUESTS = 60  # Maximum requests per minute

# Rate limiting storage (IP -> {count, timestamp})
rate_limits = {}

def generate_token(user_id):
    """Generate a secure authentication token"""
    # Create a unique token
    token_base = f"{user_id}:{uuid.uuid4()}:{int(time.time())}"
    
    # Sign the token with HMAC
    signature = hmac.new(
        SECRET_KEY.encode(),
        token_base.encode(),
        hashlib.sha256
    ).digest()
    
    # Combine and encode as base64
    token = base64.urlsafe_b64encode(
        f"{token_base}:{base64.b64encode(signature).decode()}".encode()
    ).decode()
    
    # Store the token in the database
    database.create_session(user_id, token)
    
    return token

def validate_token(token):
    """Validate an authentication token"""
    try:
        # Decode the token
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        token_parts = decoded.split(':')
        
        if len(token_parts) < 4:
            return None
        
        user_id = token_parts[0]
        timestamp = int(token_parts[2])
        provided_signature = base64.b64decode(token_parts[3])
        
        # Check if token has expired
        if int(time.time()) - timestamp > TOKEN_EXPIRY:
            return None
        
        # Verify the signature
        token_base = ':'.join(token_parts[:3])
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            token_base.encode(),
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(provided_signature, expected_signature):
            return None
        
        # Validate in database
        return database.validate_session(token)
    except Exception:
        return None

def check_rate_limit(ip_address):
    """Check if the request exceeds rate limits"""
    now = int(time.time())
    
    # Get or initialize rate limit data for this IP
    if ip_address not in rate_limits:
        rate_limits[ip_address] = {'count': 0, 'timestamp': now}
    
    # Reset count if window has passed
    if now - rate_limits[ip_address]['timestamp'] > RATE_LIMIT_WINDOW:
        rate_limits[ip_address] = {'count': 0, 'timestamp': now}
    
    # Increment count
    rate_limits[ip_address]['count'] += 1
    
    # Check if limit exceeded
    if rate_limits[ip_address]['count'] > RATE_LIMIT_MAX_REQUESTS:
        return False
    
    return True

def get_client_ip(headers):
    """Extract client IP from headers"""
    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0].strip()
    return headers.get('X-Real-IP', 'unknown')

def create_ssl_context():
    """Create SSL context for HTTPS"""
    # In production, you would use real certificates
    # For development, we'll create self-signed certificates
    cert_file = "server.crt"
    key_file = "server.key"
    
    # Check if certificates exist, if not create them
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        # This is for development only
        os.system(f'openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 '
                  f'-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" '
                  f'-keyout {key_file} -out {cert_file}')
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    
    return context

def hash_password(password, salt=None):
    """Hash a password for storage"""
    if salt is None:
        salt = os.urandom(32)
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    return {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'key': base64.b64encode(key).decode('utf-8')
    }

def verify_password(stored_password, provided_password):
    """Verify a password against its hash"""
    salt = base64.b64decode(stored_password['salt'])
    stored_key = base64.b64decode(stored_password['key'])
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000
    )
    
    return hmac.compare_digest(key, stored_key)

def sanitize_input(data):
    """Sanitize user input to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        return data.replace('<', '&lt;').replace('>', '&gt;')
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data
