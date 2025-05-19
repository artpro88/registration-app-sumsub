# Deployment Guide for Registration App with Sumsub Integration

This guide provides instructions for deploying the Registration App with Sumsub Integration to a production environment.

## Prerequisites

- Docker and Docker Compose
- Domain name (for production deployment)
- SSL certificate (for production deployment)
- Sumsub account with API credentials

## Deployment Options

### 1. Local Deployment with Docker Compose

For testing or development purposes, you can deploy the application locally using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd registration-app

# Create required directories
mkdir -p data logs nginx/ssl

# Generate self-signed SSL certificate for local testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/server.key -out nginx/ssl/server.crt \
  -subj "/CN=localhost"

# Update environment variables in .env.production
# (Replace with your actual values)
cp .env.production .env

# Build and start the containers
docker-compose up -d

# Check the logs
docker-compose logs -f
```

The application will be available at:
- HTTP: http://localhost:80 (redirects to HTTPS)
- HTTPS: https://localhost:443

### 2. Production Deployment on Cloud Provider

For production deployment, follow these steps:

#### 2.1. Set Up Server

1. Provision a server with your preferred cloud provider (AWS, GCP, Azure, DigitalOcean, etc.)
2. Install Docker and Docker Compose:

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

#### 2.2. Configure Domain and SSL

1. Point your domain to your server's IP address using DNS settings
2. Obtain SSL certificate (using Let's Encrypt or your preferred provider)

For Let's Encrypt:

```bash
# Install Certbot
sudo apt install -y certbot

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/server.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/server.key
```

#### 2.3. Deploy the Application

1. Clone the repository to your server
2. Configure environment variables:

```bash
# Copy and edit the environment file
cp .env.production .env

# Update the following variables:
# - SECRET_KEY (generate a strong random key)
# - ADMIN_KEY (for accessing metrics)
# - SUMSUB_APP_TOKEN (from your Sumsub account)
# - SUMSUB_SECRET_KEY (from your Sumsub account)
```

3. Update Nginx configuration:

```bash
# Edit nginx/conf.d/default.conf
# Replace 'localhost' with your domain name
```

4. Start the application:

```bash
# Build and start the containers
docker-compose up -d

# Check the logs
docker-compose logs -f
```

### 3. Deployment on Kubernetes

For larger scale deployments, you can use Kubernetes:

1. Create Kubernetes configuration files (not included in this guide)
2. Deploy using kubectl or a CI/CD pipeline

## Sumsub Webhook Configuration

To receive verification status updates from Sumsub:

1. Log in to your Sumsub account
2. Go to Settings > Webhooks
3. Add a new webhook with the URL: `https://yourdomain.com/api/verification/webhook`
4. Select the events you want to receive (at minimum, select verification status changes)
5. Save the webhook configuration

## Monitoring and Maintenance

### Monitoring

Access the monitoring endpoints:

- Health check: `https://yourdomain.com/api/health`
- Metrics: `https://yourdomain.com/api/metrics` (requires ADMIN_KEY header)

### Logs

View logs:

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f
```

### Database Backup

Backup the SQLite database:

```bash
# Stop the application
docker-compose stop

# Backup the database
cp data/users.db data/users.db.backup

# Restart the application
docker-compose start
```

### Updates

To update the application:

```bash
# Pull the latest changes
git pull

# Rebuild and restart the containers
docker-compose down
docker-compose up -d
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive environment variables to version control
2. **Regular Updates**: Keep all components updated with security patches
3. **Firewall**: Configure firewall to only allow necessary ports (80, 443)
4. **Monitoring**: Regularly check logs for suspicious activity
5. **Backups**: Regularly backup the database and configuration

## Troubleshooting

### Common Issues

1. **Application not starting**: Check Docker logs for errors
2. **Database errors**: Ensure the data directory has proper permissions
3. **SSL issues**: Verify certificate paths and permissions
4. **Webhook not working**: Check Sumsub webhook configuration and server logs

For additional help, contact support or refer to the documentation.
