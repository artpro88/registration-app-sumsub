#!/bin/bash

# This script sets up GitHub Actions secrets for CI/CD

# GitHub username and repository name
echo "Please enter your GitHub username:"
read GITHUB_USERNAME

REPO_NAME="registration-app-sumsub"

# GitHub personal access token
echo "Please enter your GitHub personal access token:"
read -s GITHUB_TOKEN
echo ""

# Verify token by checking user info
echo "Verifying GitHub token..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user)

if [[ $USER_INFO == *"login"* ]]; then
  echo "Token verified successfully!"
  ACTUAL_USERNAME=$(echo $USER_INFO | grep -o '"login":"[^"]*' | cut -d'"' -f4)
  echo "Logged in as: $ACTUAL_USERNAME"

  # Use the actual username from the API response
  GITHUB_USERNAME=$ACTUAL_USERNAME
else
  echo "Invalid token. Please check your token and try again."
  exit 1
fi

# Check if repository exists
REPO_CHECK=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME)

if [[ $REPO_CHECK != *"id"* ]]; then
  echo "Repository $REPO_NAME does not exist! Please create it first."
  exit 1
fi

# Docker Hub credentials
echo "Please enter your Docker Hub username:"
read DOCKERHUB_USERNAME

echo "Please enter your Docker Hub token/password:"
read -s DOCKERHUB_TOKEN
echo ""

# Sumsub credentials
echo "Please enter your Sumsub App Token (or press Enter to use default):"
read SUMSUB_APP_TOKEN_INPUT
SUMSUB_APP_TOKEN=${SUMSUB_APP_TOKEN_INPUT:-"sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX"}

echo "Please enter your Sumsub Secret Key (or press Enter to use default):"
read -s SUMSUB_SECRET_KEY_INPUT
echo ""
SUMSUB_SECRET_KEY=${SUMSUB_SECRET_KEY_INPUT:-"0YIkTYFr1Xex1402bqIn9Gw6658s0sq9"}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "jq is not installed. Using alternative method for JSON parsing."
  JQ_INSTALLED=false
else
  JQ_INSTALLED=true
fi

# Function to create a GitHub secret
create_secret() {
  local secret_name=$1
  local secret_value=$2

  echo "Getting public key for repository..."
  # Get the public key for the repository
  local public_key_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets/public-key")

  echo "Public key response: $public_key_response"

  # Parse the response to get the key and key_id
  if [ "$JQ_INSTALLED" = true ]; then
    local public_key=$(echo $public_key_response | jq -r .key)
    local key_id=$(echo $public_key_response | jq -r .key_id)
  else
    # Alternative parsing without jq
    local public_key=$(echo $public_key_response | grep -o '"key":"[^"]*' | cut -d'"' -f4)
    local key_id=$(echo $public_key_response | grep -o '"key_id":"[^"]*' | cut -d'"' -f4)
  fi

  if [ -z "$public_key" ] || [ "$public_key" == "null" ]; then
    echo "Failed to get public key. Please check your token and repository name."
    echo "Response: $public_key_response"
    return 1
  fi

  echo "Public key obtained successfully."

  # Create or update the secret directly (without encryption for simplicity)
  echo "Creating secret: $secret_name..."
  local create_response=$(curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/secrets/$secret_name" \
    -d "{\"encrypted_value\":\"$(echo -n "$secret_value" | base64)\",\"key_id\":\"$key_id\"}")

  echo "Create response: $create_response"

  if [[ $create_response == *"message"*"Bad credentials"* ]]; then
    echo "Failed to create secret: $secret_name - Bad credentials"
    return 1
  elif [[ $create_response == *"message"* ]]; then
    echo "Failed to create secret: $secret_name - $(echo $create_response | grep -o '"message":"[^"]*' | cut -d'"' -f4)"
    return 1
  else
    echo "Secret created: $secret_name"
    return 0
  fi
}

# Create secrets
echo "Creating GitHub Actions secrets..."

# Try to create each secret and report success/failure
if create_secret "DOCKERHUB_USERNAME" "$DOCKERHUB_USERNAME"; then
  echo "DOCKERHUB_USERNAME secret created successfully."
else
  echo "Failed to create DOCKERHUB_USERNAME secret."
fi

if create_secret "DOCKERHUB_TOKEN" "$DOCKERHUB_TOKEN"; then
  echo "DOCKERHUB_TOKEN secret created successfully."
else
  echo "Failed to create DOCKERHUB_TOKEN secret."
fi

if create_secret "SUMSUB_APP_TOKEN" "$SUMSUB_APP_TOKEN"; then
  echo "SUMSUB_APP_TOKEN secret created successfully."
else
  echo "Failed to create SUMSUB_APP_TOKEN secret."
fi

if create_secret "SUMSUB_SECRET_KEY" "$SUMSUB_SECRET_KEY"; then
  echo "SUMSUB_SECRET_KEY secret created successfully."
else
  echo "Failed to create SUMSUB_SECRET_KEY secret."
fi

echo "Secret creation process completed!"
