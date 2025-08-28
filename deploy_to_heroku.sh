#!/bin/bash

echo "===== Reddit Crawler Heroku Deployment ====="

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "Heroku CLI is not installed. Please install it from:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "Heroku CLI detected. Proceeding with deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Create Heroku app if app name is provided
read -p "Enter your Heroku app name (leave blank to use existing app): " app_name

if [ ! -z "$app_name" ]; then
    echo "Creating Heroku app: $app_name"
    heroku create "$app_name"
else
    echo "Using existing Heroku app..."
fi

# Set environment variables
echo "Setting up environment variables..."
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

read -p "Do you want to use PostgreSQL database? (y/n): " use_postgres

if [[ "$use_postgres" =~ ^[Yy]$ ]]; then
    echo "Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:hobby-dev
fi

# Generate a random secret key
random_key=$(openssl rand -hex 24)
echo "Setting SECRET_KEY environment variable..."
heroku config:set SECRET_KEY="$random_key"

# Push to Heroku
echo "Deploying to Heroku..."
git push heroku master

echo "===== Deployment Complete ====="
echo "Your app should now be available at:"
heroku open

echo "You can view logs with: heroku logs --tail"