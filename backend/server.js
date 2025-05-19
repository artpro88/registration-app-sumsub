import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

// Get the directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from .env file
const envFile = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
const env = {};
envFile.split('\n').forEach(line => {
  const [key, value] = line.split('=');
  if (key && value) {
    env[key.trim()] = value.trim();
  }
});

// Sumsub API configuration
const SUMSUB_APP_TOKEN = env.SUMSUB_APP_TOKEN;
const SUMSUB_SECRET_KEY = env.SUMSUB_SECRET_KEY;
const SUMSUB_BASE_URL = 'https://api.sumsub.com';

// In-memory database for users
const users = [];

// Create HTTP server
const server = http.createServer((req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    res.end();
    return;
  }

  // Parse URL
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;

  // Serve static files
  if (req.method === 'GET' && (pathname === '/' || pathname === '/index.html')) {
    serveFile(res, path.join(__dirname, '../frontend/public/index.html'), 'text/html');
    return;
  }

  if (req.method === 'GET' && pathname === '/styles.css') {
    serveFile(res, path.join(__dirname, '../frontend/public/styles.css'), 'text/css');
    return;
  }

  if (req.method === 'GET' && pathname === '/demo.html') {
    serveFile(res, path.join(__dirname, '../frontend/public/demo.html'), 'text/html');
    return;
  }

  // API routes
  if (pathname === '/api/users/register' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const userData = JSON.parse(body);

        // Validate user data
        if (!validateUserData(userData)) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ success: false, message: 'Invalid user data' }));
          return;
        }

        // Check if email already exists
        if (users.some(user => user.email === userData.email)) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ success: false, message: 'Email already registered' }));
          return;
        }

        // Create new user
        const userId = crypto.randomUUID();
        const newUser = {
          id: userId,
          ...userData,
          verificationStatus: 'pending',
          verificationDetails: {
            applicantId: null,
            lastChecked: new Date().toISOString()
          },
          createdAt: new Date().toISOString()
        };

        // Save user
        users.push(newUser);

        // Return success response
        res.statusCode = 201;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({
          success: true,
          message: 'User registered successfully',
          data: {
            userId: newUser.id,
            firstName: newUser.firstName,
            lastName: newUser.lastName,
            email: newUser.email,
            verificationStatus: newUser.verificationStatus
          }
        }));
      } catch (error) {
        console.error('Registration error:', error);
        res.statusCode = 500;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({
          success: false,
          message: 'An error occurred during registration'
        }));
      }
    });
    return;
  }

  if (pathname.startsWith('/api/verification/token/') && req.method === 'GET') {
    const userId = pathname.split('/').pop();

    // Find user
    const user = users.find(u => u.id === userId);
    if (!user) {
      res.statusCode = 404;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ success: false, message: 'User not found' }));
      return;
    }

    // Generate access token
    const accessToken = SUMSUB_APP_TOKEN;

    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      success: true,
      token: accessToken
    }));
    return;
  }

  if (pathname.startsWith('/api/verification/status/') && req.method === 'GET') {
    const userId = pathname.split('/').pop();

    // Find user
    const user = users.find(u => u.id === userId);
    if (!user) {
      res.statusCode = 404;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ success: false, message: 'User not found' }));
      return;
    }

    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      success: true,
      status: user.verificationStatus,
      lastChecked: user.verificationDetails.lastChecked
    }));
    return;
  }

  // Health check route
  if (pathname === '/health' && req.method === 'GET') {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  // Not found
  res.statusCode = 404;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ message: 'Not found' }));
});

// Serve static file
function serveFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.statusCode = 500;
      res.setHeader('Content-Type', 'text/plain');
      res.end('Internal Server Error');
      return;
    }

    res.statusCode = 200;
    res.setHeader('Content-Type', contentType);
    res.end(data);
  });
}

// Validate user data
function validateUserData(data) {
  // Check required fields
  const requiredFields = ['firstName', 'lastName', 'dob', 'email', 'phoneNumber', 'street', 'city', 'postcode'];
  for (const field of requiredFields) {
    if (!data[field]) {
      return false;
    }
  }

  // Validate email format
  const emailRegex = /\S+@\S+\.\S+/;
  if (!emailRegex.test(data.email)) {
    return false;
  }

  // Validate phone number
  const phoneRegex = /^\+?[0-9\s\-()]{8,20}$/;
  if (!phoneRegex.test(data.phoneNumber)) {
    return false;
  }

  // Validate age (18+)
  const dob = new Date(data.dob);
  const today = new Date();
  const eighteenYearsAgo = new Date(
    today.getFullYear() - 18,
    today.getMonth(),
    today.getDate()
  );

  if (dob > eighteenYearsAgo) {
    return false;
  }

  return true;
}

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
