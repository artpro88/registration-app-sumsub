#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import urllib.parse
import time
import ssl
import threading
import uuid
from http import HTTPStatus

# Import our modules
import database
import security
import sumsub
import monitoring

# Configuration
PORT = int(os.environ.get('PORT', 8080))
USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
HOST = os.environ.get('HOST', '')

# Create logs directory
os.makedirs('logs', exist_ok=True)

class ProductionRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/public")
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Start timing the request
        start_time = time.time()

        # Get client IP
        client_ip = security.get_client_ip(self.headers)

        # Check rate limit
        if not security.check_rate_limit(client_ip):
            self.send_response(HTTPStatus.TOO_MANY_REQUESTS)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'Rate limit exceeded. Please try again later.'
            }).encode())

            # Log rate limit
            monitoring.log_request('GET', self.path, 429, (time.time() - start_time) * 1000, client_ip)
            return

        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # API routes
        if path.startswith('/api/'):
            # Check authentication for protected routes
            if path.startswith('/api/verification/') and not path.startswith('/api/verification/webhook'):
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    self.send_response(HTTPStatus.UNAUTHORIZED)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': 'Authentication required'
                    }).encode())

                    # Log unauthorized access
                    monitoring.log_request('GET', self.path, 401, (time.time() - start_time) * 1000, client_ip)
                    return

                token = auth_header[7:]  # Remove 'Bearer ' prefix
                user_id = security.validate_token(token)

                if not user_id:
                    self.send_response(HTTPStatus.UNAUTHORIZED)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': 'Invalid or expired token'
                    }).encode())

                    # Log invalid token
                    monitoring.log_request('GET', self.path, 401, (time.time() - start_time) * 1000, client_ip)
                    return

            # Handle API routes
            if path.startswith('/api/verification/token/'):
                user_id = path.split('/')[-1]
                self.handle_get_token(user_id)
            elif path.startswith('/api/verification/status/'):
                user_id = path.split('/')[-1]
                self.handle_get_status(user_id)
            elif path == '/api/health':
                self.handle_health_check()
            elif path == '/api/metrics' and self.headers.get('X-Admin-Key') == os.environ.get('ADMIN_KEY'):
                self.handle_metrics()
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'API endpoint not found'
                }).encode())

            # Log API request
            monitoring.log_request('GET', self.path, self.send_response, (time.time() - start_time) * 1000, client_ip)
            return

        # Serve static files
        try:
            super().do_GET()
            # Log successful static file request
            monitoring.log_request('GET', self.path, 200, (time.time() - start_time) * 1000, client_ip)
        except Exception as e:
            monitoring.log_error(e, {'path': self.path, 'method': 'GET'})
            monitoring.log_request('GET', self.path, 500, (time.time() - start_time) * 1000, client_ip)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Server Error")

    def do_POST(self):
        # Start timing the request
        start_time = time.time()

        # Get client IP
        client_ip = security.get_client_ip(self.headers)

        # Check rate limit
        if not security.check_rate_limit(client_ip):
            self.send_response(HTTPStatus.TOO_MANY_REQUESTS)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'Rate limit exceeded. Please try again later.'
            }).encode())

            # Log rate limit
            monitoring.log_request('POST', self.path, 429, (time.time() - start_time) * 1000, client_ip)
            return

        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        # API routes
        print(f"POST request to: {path}")
        if path == '/api/users/register':
            self.handle_register(post_data, client_ip)
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

        # Log API request
        monitoring.log_request('POST', self.path, self.send_response, (time.time() - start_time) * 1000, client_ip)

    def handle_register(self, post_data, client_ip):
        try:
            print(f"Received registration request: {post_data.decode('utf-8')}")
            user_data = json.loads(post_data.decode('utf-8'))

            # For demo purposes, we'll create a simple in-memory user
            # In a real app, this would be stored in the database
            user_id = str(uuid.uuid4())

            # Generate a simple token
            token = f"{user_id}_{int(time.time())}"

            # Print registration data for debugging
            print(f"Created user with ID: {user_id}")
            print(f"User data: {user_data}")

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

            # For demo purposes, we'll use the Sumsub app token directly
            # In a real app, this would be generated through the Sumsub API
            token = "sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX"

            # Return token
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'token': token
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

            # For demo purposes, we'll return a random status
            # In a real app, this would be fetched from the database
            statuses = ['pending', 'verified', 'rejected']
            import random
            status = random.choice(statuses)

            # Return status
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'status': status,
                'lastChecked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
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
            # Verify webhook signature
            signature = self.headers.get('X-Payload-Digest')

            success, error = sumsub.handle_webhook(post_data, signature)

            if not success:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': error
                }).encode())
                return

            # Return success
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Webhook processed successfully'
            }).encode())
        except Exception as e:
            monitoring.log_error(e, {'path': self.path, 'method': 'POST'})
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'An error occurred while processing webhook'
            }).encode())

    def handle_health_check(self):
        # Check database health
        db_health = monitoring.monitor_database()

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'ok',
            'database': db_health,
            'uptime': time.time() - monitoring.metrics['start_time']
        }).encode())

    def handle_metrics(self):
        # Get metrics
        metrics = monitoring.get_metrics()

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(metrics).encode())

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Key')

def run_server():
    server_class = socketserver.ThreadingTCPServer
    server_class.allow_reuse_address = True
    httpd = server_class((HOST, PORT), ProductionRequestHandler)

    # Use HTTPS if enabled
    if USE_HTTPS:
        httpd.socket = security.create_ssl_context().wrap_socket(httpd.socket, server_side=True)
        protocol = "HTTPS"
    else:
        protocol = "HTTP"

    print(f"Starting {protocol} server on port {PORT}...")

    # Start monitoring in background
    monitoring.start_monitoring()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Server stopped.")

if __name__ == "__main__":
    run_server()
