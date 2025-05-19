#!/bin/bash

# This script deploys the backend to Heroku

# Heroku app name
HEROKU_APP_NAME="registration-app-backend"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "Heroku CLI is not installed. Please install it first."
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
heroku whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "Not logged in to Heroku. Please login first."
    heroku login
fi

# Check if app exists
heroku apps:info --app $HEROKU_APP_NAME &> /dev/null
if [ $? -ne 0 ]; then
    echo "Creating Heroku app: $HEROKU_APP_NAME"
    heroku apps:create $HEROKU_APP_NAME
else
    echo "Heroku app $HEROKU_APP_NAME already exists."
fi

# Create Procfile if it doesn't exist
if [ ! -f "Procfile" ]; then
    echo "Creating Procfile..."
    echo "web: python production_server.py" > Procfile
fi

# Create runtime.txt if it doesn't exist
if [ ! -f "runtime.txt" ]; then
    echo "Creating runtime.txt..."
    echo "python-3.9.16" > runtime.txt
fi

# Set Heroku config variables
echo "Setting Heroku config variables..."
heroku config:set SUMSUB_APP_TOKEN="sbx:KLRZP8PRbxeNmlgfpMzyiDRY.Qqjq7MWF2nJAzjxvUR9zEK6BZkE04MqX" --app $HEROKU_APP_NAME
heroku config:set SUMSUB_SECRET_KEY="0YIkTYFr1Xex1402bqIn9Gw6658s0sq9" --app $HEROKU_APP_NAME
heroku config:set PORT="8080" --app $HEROKU_APP_NAME
heroku config:set HOST="0.0.0.0" --app $HEROKU_APP_NAME
heroku config:set USE_HTTPS="true" --app $HEROKU_APP_NAME

# Add PostgreSQL add-on
echo "Adding PostgreSQL add-on..."
heroku addons:create heroku-postgresql:hobby-dev --app $HEROKU_APP_NAME

# Deploy to Heroku
echo "Deploying to Heroku..."
git push heroku main

# Open the app in browser
echo "Opening app in browser..."
heroku open --app $HEROKU_APP_NAME

echo "Deployment completed!"
