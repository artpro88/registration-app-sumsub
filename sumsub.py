import hmac
import hashlib
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import database

# Sumsub API configuration
SUMSUB_APP_TOKEN = "sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX"
SUMSUB_SECRET_KEY = "0YIkTYFr1Xex1402bqIn9Gw6658s0sq9"
SUMSUB_BASE_URL = "https://api.sumsub.com"

def generate_signature(method, url, timestamp, body=""):
    """Generate signature for Sumsub API request"""
    string_to_sign = str(timestamp) + method + url + body
    signature = hmac.new(
        SUMSUB_SECRET_KEY.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def make_request(method, url, body=None):
    """Make a request to Sumsub API"""
    timestamp = int(time.time())
    full_url = SUMSUB_BASE_URL + url
    
    body_str = ""
    if body:
        body_str = json.dumps(body)
    
    signature = generate_signature(method, url, timestamp, body_str)
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-App-Token': SUMSUB_APP_TOKEN,
        'X-App-Access-Sig': signature,
        'X-App-Access-Ts': str(timestamp)
    }
    
    request = urllib.request.Request(
        full_url,
        data=body_str.encode('utf-8') if body else None,
        headers=headers,
        method=method
    )
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return {'error': error_json}
        except:
            return {'error': error_body}

def create_applicant(user_id, user_data):
    """Create a new applicant in Sumsub"""
    url = "/resources/applicants"
    
    # Format date of birth as YYYY-MM-DD
    dob_parts = user_data['dob'].split('-')
    if len(dob_parts) == 3:
        dob = user_data['dob']
    else:
        # Handle different date formats
        dob = user_data['dob']
    
    body = {
        "externalUserId": user_id,
        "email": user_data['email'],
        "phone": user_data['phone_number'],
        "firstName": user_data['first_name'],
        "lastName": user_data['last_name'],
        "dob": dob,
        "country": "GBR",  # Default to UK
        "requiredIdDocs": {
            "docSets": [
                {
                    "idDocSetType": "IDENTITY",
                    "types": ["PASSPORT", "ID_CARD", "DRIVERS"]
                },
                {
                    "idDocSetType": "SELFIE",
                    "types": ["SELFIE"]
                }
            ]
        }
    }
    
    response = make_request("POST", url, body)
    
    if 'error' in response:
        return None, response['error']
    
    # Update user with applicant ID
    database.update_verification_status(
        user_id, 
        'pending', 
        response['id'], 
        {'applicantId': response['id']}
    )
    
    return response['id'], None

def generate_access_token(user_id, applicant_id=None):
    """Generate access token for Sumsub Web SDK"""
    # If no applicant ID provided, try to create one
    if not applicant_id:
        user = database.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Check if user already has an applicant ID
        if user.get('applicant_id'):
            applicant_id = user['applicant_id']
        else:
            # Create a new applicant
            applicant_id, error = create_applicant(user_id, user)
            if error:
                return None, error
    
    # Generate access token
    url = f"/resources/accessTokens?userId={applicant_id}&ttlInSecs=3600"
    
    response = make_request("POST", url)
    
    if 'error' in response:
        return None, response['error']
    
    return response['token'], None

def get_applicant_status(applicant_id):
    """Get applicant status from Sumsub"""
    url = f"/resources/applicants/{applicant_id}/status"
    
    response = make_request("GET", url)
    
    if 'error' in response:
        return None, response['error']
    
    # Map Sumsub status to our status
    review_status = response.get('reviewStatus')
    review_result = response.get('reviewResult', {})
    
    if review_status == 'completed':
        status = 'verified' if review_result.get('reviewAnswer') == 'GREEN' else 'rejected'
    else:
        status = 'pending'
    
    return status, None

def verify_webhook_signature(request_body, signature_header):
    """Verify Sumsub webhook signature"""
    if not signature_header:
        return False
    
    # Calculate expected signature
    expected_signature = hmac.new(
        SUMSUB_SECRET_KEY.encode('utf-8'),
        request_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(signature_header, expected_signature)

def handle_webhook(request_body, signature_header):
    """Handle Sumsub webhook"""
    # Verify signature
    if not verify_webhook_signature(request_body, signature_header):
        return False, "Invalid signature"
    
    try:
        data = json.loads(request_body.decode('utf-8'))
        
        # Extract relevant information
        applicant_id = data.get('applicantId')
        review_status = data.get('reviewStatus')
        review_result = data.get('reviewResult', {})
        
        if not applicant_id:
            return False, "Missing applicant ID"
        
        # Find user by applicant ID
        conn = database.sqlite3.connect(database.DB_FILE)
        conn.row_factory = database.sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE applicant_id = ?", (applicant_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found for this applicant"
        
        user_id = user['id']
        
        # Map Sumsub status to our status
        if review_status == 'completed':
            status = 'verified' if review_result.get('reviewAnswer') == 'GREEN' else 'rejected'
        else:
            status = 'pending'
        
        # Update user verification status
        details = {
            'reviewStatus': review_status,
            'reviewResult': review_result
        }
        
        if review_result.get('moderationComment'):
            details['rejectionReason'] = review_result['moderationComment']
        
        database.update_verification_status(user_id, status, applicant_id, details)
        
        # Log the webhook event
        database.log_action(cursor, user_id, "WEBHOOK_RECEIVED", 
                           f"Status updated to {status} via webhook")
        
        conn.commit()
        conn.close()
        
        return True, None
    except Exception as e:
        return False, str(e)
