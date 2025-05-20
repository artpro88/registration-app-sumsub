#!/bin/bash

# This script creates a GitHub repository and pushes the local code to it

# GitHub username and repository name
echo "Please enter your GitHub username:"
read GITHUB_USERNAME

REPO_NAME="registration-app-sumsub"

# Create a GitHub personal access token with 'repo' scope
# Visit: https://github.com/settings/tokens/new
echo "Please enter your GitHub personal access token:"
read -s GITHUB_TOKEN

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

# Check if repository already exists
REPO_CHECK=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME)

if [[ $REPO_CHECK == *"id"* ]]; then
  echo "Repository $REPO_NAME already exists!"
else
  # Create the repository
  echo "Creating GitHub repository: $REPO_NAME..."
  REPO_CREATION=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"Registration App with Sumsub Identity Verification\",\"private\":false,\"has_issues\":true,\"has_projects\":true,\"has_wiki\":true}")

  if [[ $REPO_CREATION == *"id"* ]]; then
    echo "Repository created successfully!"
  else
    echo "Failed to create repository. Error: $REPO_CREATION"
    exit 1
  fi
fi

# Add the remote repository
echo "Setting up Git remote..."

# Check if remote already exists
if git remote | grep -q "^origin$"; then
  echo "Remote 'origin' already exists. Updating URL..."
  git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
else
  echo "Adding remote 'origin'..."
  git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# If not on main branch, create and checkout main
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Not on main branch. Checking if main branch exists..."

  if git show-ref --verify --quiet refs/heads/main; then
    echo "Main branch exists. Checking out main..."
    git checkout main
  else
    echo "Creating and checking out main branch..."
    git checkout -b main
  fi
fi

# Set up credentials for push
echo "Setting up Git credentials..."
git config --local credential.helper store
echo "https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com" > ~/.git-credentials

# Push the code to GitHub
echo "Pushing code to GitHub..."
git push -u origin main

# Check if push was successful
if [ $? -ne 0 ]; then
  echo "Failed to push code to GitHub. Trying with force flag..."
  git push -u origin main --force

  if [ $? -ne 0 ]; then
    echo "Force push also failed. Please check your credentials and try again."
    # Clean up credentials
    rm ~/.git-credentials
    exit 1
  fi
fi

echo "Code pushed successfully to GitHub!"
echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

# Clean up credentials
rm ~/.git-credentials

echo "Done!"
