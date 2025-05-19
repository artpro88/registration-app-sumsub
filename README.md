# Registration App with Sumsub Identity Verification

A complete registration system with Sumsub identity verification integration.

## Overview

This application provides a user registration system with integrated identity verification using Sumsub. It includes:

- User registration form with validation
- Identity verification using Sumsub WebSDK
- Verification status tracking
- Webhook handling for status updates
- Production-ready deployment configuration

## Features

- **User Registration**: Collect user information with client-side and server-side validation
- **Identity Verification**: Seamless integration with Sumsub WebSDK
- **Status Tracking**: Real-time verification status updates
- **Webhook Handling**: Process verification status updates from Sumsub
- **Security**: HTTPS, authentication, input validation, and more
- **Monitoring**: Prometheus and Grafana for metrics
- **Logging**: ELK stack for centralized logging
- **Backup**: Automated database backups

## Project Structure

```
registration-app/
├── backend/                # Backend code
├── database/               # Database schema and migrations
├── docker-compose.yml      # Development Docker Compose
├── docker-compose.production.yml  # Production Docker Compose
├── Dockerfile              # Development Dockerfile
├── Dockerfile.production   # Production Dockerfile
├── frontend/               # Frontend code
│   └── public/             # Static files
├── logging/                # Logging configuration
├── monitoring/             # Monitoring configuration
├── nginx/                  # Nginx configuration
├── scripts/                # Utility scripts
├── .env.example            # Example environment variables
├── .env.production         # Production environment variables
├── DEPLOYMENT.md           # Deployment guide
├── PRODUCTION_GUIDE.md     # Production guide
└── README.md               # This file
```

## Quick Start

### Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd registration-app
   ```

2. Run the simple server:
   ```bash
   python3 simple_server.py
   ```

3. Open the application in your browser:
   ```
   http://localhost:8080/simple.html
   ```

### Production Environment

For production deployment, follow these steps:

1. Set up environment variables:
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your configuration
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. Access the application:
   ```
   https://yourdomain.com
   ```

For detailed deployment instructions, see [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md).

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for production deployment)
- Sumsub account with API credentials

## Architecture

The application consists of the following components:

- **Frontend**: HTML, CSS, and JavaScript with Bootstrap for styling
- **Backend**: Python application server
- **Database**: PostgreSQL for data storage
- **Cache**: Redis for session storage and caching
- **Web Server**: Nginx for serving static files and as a reverse proxy
- **Monitoring**: Prometheus and Grafana for metrics
- **Logging**: ELK stack for centralized logging

## API Endpoints

### User Routes

- `POST /api/users/register` - Register a new user
- `GET /api/verification/token/:userId` - Generate Sumsub access token
- `GET /api/verification/status/:userId` - Get verification status
- `POST /api/verification/webhook` - Webhook handler for Sumsub status updates

## Sumsub Integration

This application integrates with Sumsub Web SDK for identity verification. The integration flow is as follows:

1. User submits registration form
2. Backend creates a Sumsub applicant and generates an access token
3. Frontend initializes Sumsub Web SDK with the access token
4. User completes the verification process in the SDK
5. Sumsub sends status updates via webhook
6. Application displays verification status to the user

## Security Considerations

- All API endpoints are protected with authentication
- HTTPS is used for all communications
- Input validation is performed on both client and server
- Rate limiting is implemented to prevent abuse
- Webhook signatures are verified
- Database credentials are stored securely

## Monitoring and Logging

- **Prometheus**: Collects metrics from all services
- **Grafana**: Visualizes metrics and provides dashboards
- **ELK Stack**: Centralizes logs from all services
- **Health Checks**: Regular health checks for all services
- **Alerts**: Configurable alerts for critical issues

## GDPR Compliance

- User consent is obtained before collecting personal data
- Personal data is only used for the stated purpose
- Users can request access to or deletion of their data
- Data is securely stored and transmitted

## License

This project is licensed under the MIT License - see the LICENSE file for details.
