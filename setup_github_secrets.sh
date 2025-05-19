#!/bin/bash

# This script sets up GitHub Actions secrets for CI/CD

# GitHub username and repository name
GITHUB_USERNAME="ArturProlisko"
REPO_NAME="registration-app-sumsub"

# GitHub personal access token
echo "Please enter your GitHub personal access token:"
read -s GITHUB_TOKEN

# Docker Hub credentials
echo "Please enter your Docker Hub username:"
read DOCKERHUB_USERNAME

echo "Please enter your Docker Hub token/password:"
read -s DOCKERHUB_TOKEN

# Sumsub credentials
echo "Please enter your Sumsub App Token:"
read SUMSUB_APP_TOKEN

echo "Please enter your Sumsub Secret Key:"
read -s SUMSUB_SECRET_KEY

# Function to create a GitHub secret
create_secret() {
  local secret_name=$1
  local secret_value=$2
  
  # Get the public key for the repository
  local public_key_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets/public-key")
  
  local public_key=$(echo $public_key_response | jq -r .key)
  local key_id=$(echo $public_key_response | jq -r .key_id)
  
  if [ -z "$public_key" ] || [ "$public_key" == "null" ]; then
    echo "Failed to get public key. Please check your token and repository name."
    return 1
  fi
  
  # Encrypt the secret value
  local encrypted_value=$(echo -n "$secret_value" | openssl base64 -A | openssl enc -base64 -A)
  
  # Create or update the secret
  curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets/$secret_name" \
    -d "{\"encrypted_value\":\"$encrypted_value\",\"key_id\":\"$key_id\"}"
  
  if [ $? -ne 0 ]; then
    echo "Failed to create secret: $secret_name"
    return 1
  fi
  
  echo "Secret created: $secret_name"
  return 0
}

# Create secrets
echo "Creating GitHub Actions secrets..."

create_secret "DOCKERHUB_USERNAME" "$DOCKERHUB_USERNAME"
create_secret "DOCKERHUB_TOKEN" "$DOCKERHUB_TOKEN"
create_secret "SUMSUB_APP_TOKEN" "$SUMSUB_APP_TOKEN"
create_secret "SUMSUB_SECRET_KEY" "$SUMSUB_SECRET_KEY"

echo "Secrets created successfully!"
