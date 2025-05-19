import unittest
import json
import sys
import os

# Add parent directory to path to import server module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import server module
from simple_server import SimpleRequestHandler

class MockRequest:
    def __init__(self, method='GET', path='/'):
        self.method = method
        self.path = path
        self.headers = {}

class MockResponse:
    def __init__(self):
        self.status_code = None
        self.headers = {}
        self.body = None
        
    def send_response(self, status_code):
        self.status_code = status_code
        
    def send_header(self, name, value):
        self.headers[name] = value
        
    def end_headers(self):
        pass
        
    def write(self, body):
        self.body = body

class TestSimpleServer(unittest.TestCase):
    def test_health_check(self):
        # Create mock request and response
        request = MockRequest(method='GET', path='/api/health')
        response = MockResponse()
        
        # Create handler
        handler = SimpleRequestHandler(request, ('127.0.0.1', 8080), None)
        
        # Override methods
        handler.send_response = response.send_response
        handler.send_header = response.send_header
        handler.end_headers = response.end_headers
        handler.wfile = type('obj', (object,), {'write': response.write})
        
        # Call handler
        handler.do_GET()
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        
        # Parse body
        body = json.loads(response.body.decode('utf-8'))
        self.assertEqual(body['status'], 'ok')
        
    def test_user_registration(self):
        # Create test user data
        user_data = {
            'firstName': 'Test',
            'lastName': 'User',
            'dob': '1990-01-01',
            'phoneNumber': '+1234567890',
            'email': 'test@example.com',
            'street': '123 Test St',
            'city': 'Test City',
            'postcode': '12345'
        }
        
        # Create mock request and response
        request = MockRequest(method='POST', path='/api/users/register')
        response = MockResponse()
        
        # Create handler
        handler = SimpleRequestHandler(request, ('127.0.0.1', 8080), None)
        
        # Override methods
        handler.send_response = response.send_response
        handler.send_header = response.send_header
        handler.end_headers = response.end_headers
        handler.wfile = type('obj', (object,), {'write': response.write})
        handler.rfile = type('obj', (object,), {
            'read': lambda size: json.dumps(user_data).encode('utf-8')
        })
        
        # Call handler
        handler.do_POST()
        
        # Check response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        
        # Parse body
        body = json.loads(response.body.decode('utf-8'))
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], 'User registered successfully')
        self.assertEqual(body['data']['firstName'], 'Test')
        self.assertEqual(body['data']['lastName'], 'User')
        self.assertEqual(body['data']['email'], 'test@example.com')
        self.assertEqual(body['data']['verificationStatus'], 'pending')

if __name__ == '__main__':
    unittest.main()
