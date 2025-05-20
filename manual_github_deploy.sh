#!/bin/bash

# This script helps you manually deploy to GitHub

# Get GitHub username
echo "Please enter your GitHub username:"
read GITHUB_USERNAME

# Repository name
REPO_NAME="registration-app-sumsub"

# Add the remote repository
echo "Setting up Git remote..."
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

# Push the code to GitHub
echo "Ready to push code to GitHub."
echo "Please enter your GitHub password or personal access token when prompted."
echo "Press Enter to continue..."
read

echo "Pushing code to GitHub..."
git push -u origin main

# Check if push was successful
if [ $? -ne 0 ]; then
  echo "Failed to push code to GitHub. Please check your credentials and try again."
  exit 1
fi

echo "Code pushed successfully to GitHub!"
echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

echo "Done!"
