#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import uuid
import urllib.parse
from http import HTTPStatus

# Configuration
PORT = 8000
SUMSUB_APP_TOKEN = "sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX"
SUMSUB_SECRET_KEY = "0YIkTYFr1Xex1402bqIn9Gw6658s0sq9"

# In-memory database
users = []

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/public")
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # API routes
        if path.startswith('/api/'):
            if path.startswith('/api/verification/token/'):
                user_id = path.split('/')[-1]
                self.handle_get_token(user_id)
                return
            elif path.startswith('/api/verification/status/'):
                user_id = path.split('/')[-1]
                self.handle_get_status(user_id)
                return
            elif path == '/api/health':
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
                return

        # Serve static files
        return super().do_GET()

    def do_POST(self):
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # API routes
        if path == '/api/users/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_data = json.loads(post_data.decode('utf-8'))

            # Validate user data
            if not self.validate_user_data(user_data):
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Invalid user data'
                }).encode())
                return

            # Check if email already exists
            if any(user['email'] == user_data['email'] for user in users):
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Email already registered'
                }).encode())
                return

            # Create new user
            user_id = str(uuid.uuid4())
            new_user = {
                'id': user_id,
                **user_data,
                'verificationStatus': 'pending',
                'verificationDetails': {
                    'applicantId': None,
                    'lastChecked': None
                }
            }

            # Save user
            users.append(new_user)

            # Return success response
            self.send_response(HTTPStatus.CREATED)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'userId': new_user['id'],
                    'firstName': new_user['firstName'],
                    'lastName': new_user['lastName'],
                    'email': new_user['email'],
                    'verificationStatus': new_user['verificationStatus']
                }
            }).encode())
            return

        # Not found
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Not found'}).encode())

    def handle_get_token(self, user_id):
        # Find user
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'User not found'
            }).encode())
            return

        # Return token
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'token': SUMSUB_APP_TOKEN
        }).encode())

    def handle_get_status(self, user_id):
        # Find user
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'User not found'
            }).encode())
            return

        # Return status
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'status': user['verificationStatus'],
            'lastChecked': user['verificationDetails']['lastChecked']
        }).encode())

    def validate_user_data(self, data):
        # Check required fields
        required_fields = ['firstName', 'lastName', 'dob', 'email', 'phoneNumber', 'street', 'city', 'postcode']
        for field in required_fields:
            if field not in data or not data[field]:
                return False

        # Validate email format
        if '@' not in data['email'] or '.' not in data['email']:
            return False

        # Validate phone number
        if not data['phoneNumber'].replace('+', '').replace('-', '').replace(' ', '').isdigit():
            return False

        return True

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

def run_server():
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
