#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import urllib.parse
import time
import uuid
import random
from http import HTTPStatus

# Configuration
PORT = 8080
HOST = ''

# In-memory database for users and their verification status
users = {}
verification_statuses = {}

class SimpleRequestHandler(http.server.SimpleHTTPRequestHandler):
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
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'API endpoint not found: {path}'
                }).encode())
                return

        # Serve static files
        return super().do_GET()

    def do_POST(self):
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        print(f"POST request to: {path}")

        # API routes
        if path == '/api/users/register':
            self.handle_register(post_data)
        elif path == '/api/verification/webhook':
            self.handle_webhook(post_data)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'API endpoint not found: {path}'
            }).encode())

    def handle_register(self, post_data):
        try:
            print(f"Received registration request: {post_data.decode('utf-8')}")
            user_data = json.loads(post_data.decode('utf-8'))

            # Create a simple user ID
            user_id = str(uuid.uuid4())

            # Generate a simple token
            token = f"{user_id}_{int(time.time())}"

            # Store user data in memory
            users[user_id] = {
                'id': user_id,
                'firstName': user_data['firstName'],
                'lastName': user_data['lastName'],
                'email': user_data['email'],
                'phoneNumber': user_data['phoneNumber'],
                'dob': user_data['dob'],
                'street': user_data['street'],
                'city': user_data['city'],
                'postcode': user_data['postcode'],
                'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }

            # Initialize verification status
            verification_statuses[user_id] = {
                'status': 'pending',
                'applicantId': None,
                'lastChecked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }

            print(f"Created user with ID: {user_id}")

            # Return success response
            self.send_response(HTTPStatus.CREATED)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'userId': user_id,
                    'token': token,
                    'firstName': user_data['firstName'],
                    'lastName': user_data['lastName'],
                    'email': user_data['email'],
                    'verificationStatus': 'pending'
                }
            }).encode())
        except Exception as e:
            print(f"Registration error: {str(e)}")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'An error occurred during registration: {str(e)}'
            }).encode())

    def handle_get_token(self, user_id):
        try:
            print(f"Generating token for user: {user_id}")

            # Check if user exists
            if user_id not in users:
                # For demo purposes, create a user if it doesn't exist
                users[user_id] = {
                    'id': user_id,
                    'firstName': 'Test',
                    'lastName': 'User',
                    'email': f'test_{user_id}@example.com',
                    'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                verification_statuses[user_id] = {
                    'status': 'pending',
                    'applicantId': None,
                    'lastChecked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                print(f"Created test user with ID: {user_id}")

            # Use the Sumsub app token directly - in a real app, this would be generated through the Sumsub API
            # The token is valid for 24 hours, so it won't expire during normal usage
            token = "sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX"

            # Store the token with the user for future reference
            if 'tokens' not in users[user_id]:
                users[user_id]['tokens'] = []

            # Add token with expiration time (24 hours from now)
            expiration_time = time.time() + 86400  # 24 hours in seconds
            users[user_id]['tokens'].append({
                'token': token,
                'expires_at': expiration_time
            })

            print(f"Generated token for user {user_id}: {token[:10]}... (expires in 24 hours)")

            # Return token
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'token': token,
                'expiresAt': expiration_time
            }).encode())
        except Exception as e:
            print(f"Token generation error: {str(e)}")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'An error occurred while generating access token: {str(e)}'
            }).encode())

    def handle_get_status(self, user_id):
        try:
            print(f"Getting status for user: {user_id}")

            # Check if user exists
            if user_id not in verification_statuses:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'User not found'
                }).encode())
                return

            # Get verification status
            status_data = verification_statuses[user_id]

            # Return status
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'status': status_data['status'],
                'lastChecked': status_data['lastChecked']
            }).encode())
        except Exception as e:
            print(f"Status check error: {str(e)}")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'An error occurred while getting verification status: {str(e)}'
            }).encode())

    def handle_webhook(self, post_data):
        try:
            print(f"Received webhook: {post_data.decode('utf-8')}")
            webhook_data = json.loads(post_data.decode('utf-8'))

            # Extract data from webhook
            applicant_id = webhook_data.get('applicantId')
            review_status = webhook_data.get('reviewStatus')
            review_result = webhook_data.get('reviewResult', {})

            if not applicant_id:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Missing applicant ID'
                }).encode())
                return

            # Find user by applicant ID (in a real app, this would be a database lookup)
            user_id = None
            for uid, status in verification_statuses.items():
                if status.get('applicantId') == applicant_id:
                    user_id = uid
                    break

            if not user_id:
                # For demo purposes, let's create a fake user ID
                user_id = str(uuid.uuid4())
                users[user_id] = {
                    'id': user_id,
                    'firstName': 'Webhook',
                    'lastName': 'User',
                    'email': f'webhook_{user_id}@example.com',
                    'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                verification_statuses[user_id] = {
                    'status': 'pending',
                    'applicantId': applicant_id,
                    'lastChecked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }

            # Map Sumsub status to our status
            if review_status == 'completed':
                status = 'verified' if review_result.get('reviewAnswer') == 'GREEN' else 'rejected'
            else:
                status = 'pending'

            # Update verification status
            verification_statuses[user_id] = {
                'status': status,
                'applicantId': applicant_id,
                'lastChecked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'reviewStatus': review_status,
                'reviewResult': review_result
            }

            print(f"Updated verification status for user {user_id} to {status}")

            # Return success
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Webhook processed successfully'
            }).encode())
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'An error occurred while processing webhook: {str(e)}'
            }).encode())

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Payload-Digest')

def run_server():
    server_class = socketserver.ThreadingTCPServer
    server_class.allow_reuse_address = True
    httpd = server_class((HOST, PORT), SimpleRequestHandler)

    print(f"Starting HTTP server on port {PORT}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Server stopped.")

if __name__ == "__main__":
    run_server()
