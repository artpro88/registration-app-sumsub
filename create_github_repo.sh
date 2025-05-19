#!/bin/bash

# This script creates a GitHub repository and pushes the local code to it

# GitHub username and repository name
GITHUB_USERNAME="ArturProlisko"
REPO_NAME="registration-app-sumsub"

# Create a GitHub personal access token with 'repo' scope
# Visit: https://github.com/settings/tokens/new
echo "Please enter your GitHub personal access token:"
read -s GITHUB_TOKEN

# Create the repository
echo "Creating GitHub repository: $REPO_NAME..."
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"Registration App with Sumsub Identity Verification\",\"private\":false,\"has_issues\":true,\"has_projects\":true,\"has_wiki\":true}"

# Check if repository was created successfully
if [ $? -ne 0 ]; then
  echo "Failed to create repository. Please check your token and try again."
  exit 1
fi

echo "Repository created successfully!"

# Add the remote repository
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Set up credentials for push
git config --local credential.helper store
echo "https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com" > ~/.git-credentials

# Push the code to GitHub
echo "Pushing code to GitHub..."
git push -u origin main

# Check if push was successful
if [ $? -ne 0 ]; then
  echo "Failed to push code to GitHub. Please check your credentials and try again."
  exit 1
fi

echo "Code pushed successfully to GitHub!"
echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

# Clean up credentials
rm ~/.git-credentials

echo "Done!"
