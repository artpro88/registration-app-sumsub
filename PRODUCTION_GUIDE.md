# Production Deployment Guide for Registration App with Sumsub Integration

This guide provides detailed instructions for deploying the Registration App with Sumsub Integration to a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Server Setup](#server-setup)
4. [Database Setup](#database-setup)
5. [Sumsub Integration](#sumsub-integration)
6. [Security Considerations](#security-considerations)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Scaling Considerations](#scaling-considerations)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- A cloud provider account (AWS, GCP, Azure, DigitalOcean, etc.)
- Domain name for your application
- SSL certificate (Let's Encrypt or commercial)
- Sumsub account with API credentials
- Docker and Docker Compose installed on your local machine

## Architecture Overview

The production deployment consists of the following components:

1. **Web Server**: Nginx for serving static files and as a reverse proxy
2. **Application Server**: Python application server for handling API requests
3. **Database**: PostgreSQL for persistent storage
4. **Cache**: Redis for session storage and caching
5. **Load Balancer**: For distributing traffic across multiple application servers
6. **Monitoring**: Prometheus and Grafana for monitoring and alerting
7. **Logging**: ELK stack (Elasticsearch, Logstash, Kibana) for centralized logging

## Server Setup

### 1. Provision Servers

For a basic production setup, provision at least the following servers:

- 1 Load Balancer
- 2 Application Servers
- 1 Database Server
- 1 Monitoring Server

### 2. Install Docker and Docker Compose

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker repository
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package index again
sudo apt update

# Install Docker
sudo apt install -y docker-ce

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add your user to the docker group
sudo usermod -aG docker $USER
```

### 3. Configure SSL

Use Let's Encrypt to obtain SSL certificates:

```bash
# Install Certbot
sudo apt install -y certbot

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl directory
sudo mkdir -p /etc/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/nginx/ssl/server.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/nginx/ssl/server.key
```

### 4. Configure Nginx

Create a production Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://static.sumsub.com https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://cdnjs.cloudflare.com; connect-src 'self' https://api.sumsub.com;" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }
    }

    # API proxy
    location /api/ {
        proxy_pass http://app-servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Load balancing for application servers
upstream app-servers {
    server app1.internal:8080;
    server app2.internal:8080;
}
```

## Database Setup

### 1. Set Up PostgreSQL

```bash
# Create a docker-compose.yml file for the database
cat > docker-compose.yml << EOF
version: '3'

services:
  postgres:
    image: postgres:14
    restart: always
    environment:
      POSTGRES_USER: regapp
      POSTGRES_PASSWORD: your-secure-password
      POSTGRES_DB: registration
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U regapp"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
EOF

# Create database initialization scripts
mkdir -p init-scripts
cat > init-scripts/01-schema.sql << EOF
CREATE TABLE users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending',
    applicant_id VARCHAR(100),
    verification_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_applicant_id ON users(applicant_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
EOF

# Start the database
docker-compose up -d
```

## Sumsub Integration

### 1. Configure Sumsub Webhook

1. Log in to your Sumsub account
2. Go to Settings > Webhooks
3. Add a new webhook with the URL: `https://yourdomain.com/api/verification/webhook`
4. Generate a secret key for webhook signatures
5. Configure the webhook to receive the following events:
   - Applicant Created
   - Applicant Reviewed
   - Applicant Pending
   - Applicant Approved
   - Applicant Rejected

### 2. Update Environment Variables

Create a `.env.production` file with your Sumsub credentials:

```
SUMSUB_APP_TOKEN=sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX
SUMSUB_SECRET_KEY=0YIkTYFr1Xex1402bqIn9Gw6658s0sq9
SUMSUB_WEBHOOK_SECRET=your-webhook-secret
DB_HOST=db.internal
DB_PORT=5432
DB_NAME=registration
DB_USER=regapp
DB_PASSWORD=your-secure-password
REDIS_HOST=redis.internal
REDIS_PORT=6379
SECRET_KEY=your-secure-secret-key
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive environment variables to version control
2. **Database Security**:
   - Use strong passwords
   - Restrict network access to the database
   - Enable SSL for database connections
3. **API Security**:
   - Implement rate limiting
   - Use HTTPS for all communications
   - Validate all input data
   - Implement proper authentication and authorization
4. **Sumsub Integration**:
   - Verify webhook signatures
   - Use HTTPS for all API calls
   - Rotate API keys periodically

## Monitoring and Logging

1. **Application Monitoring**:
   - Set up Prometheus for metrics collection
   - Configure Grafana for visualization
   - Create dashboards for key metrics (response time, error rate, etc.)
2. **System Monitoring**:
   - Monitor CPU, memory, disk usage
   - Set up alerts for critical thresholds
3. **Logging**:
   - Centralize logs with ELK stack
   - Log all API requests and responses
   - Log all verification status changes
   - Implement structured logging

## Scaling Considerations

1. **Horizontal Scaling**:
   - Add more application servers behind the load balancer
   - Configure session affinity if needed
2. **Database Scaling**:
   - Implement read replicas for read-heavy workloads
   - Consider sharding for very large datasets
3. **Caching**:
   - Use Redis for caching frequently accessed data
   - Implement proper cache invalidation strategies

## Backup and Recovery

1. **Database Backups**:
   - Set up automated daily backups
   - Test restoration procedures regularly
   - Store backups in multiple locations
2. **Application Backups**:
   - Back up configuration files
   - Use version control for code
3. **Disaster Recovery**:
   - Document recovery procedures
   - Implement multi-region deployment for critical applications

## Troubleshooting

### Common Issues

1. **Webhook Not Working**:
   - Check webhook URL is correct
   - Verify webhook signature validation
   - Check server logs for errors
2. **Verification Status Not Updating**:
   - Check Sumsub API credentials
   - Verify webhook is configured correctly
   - Check database connectivity
3. **Performance Issues**:
   - Check server resource utilization
   - Look for slow database queries
   - Monitor application logs for errors

For additional help, contact support or refer to the documentation.
