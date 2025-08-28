# Reddit Crawler Deployment Guide

This guide will help you deploy the Reddit Crawler application to various cloud platforms so that it can be accessed from the web.

## Prerequisites

Before deploying, make sure you have:

1. A GitHub account (for version control and deployment)
2. An account on your chosen cloud platform (Heroku, Render, PythonAnywhere, etc.)
3. Git installed on your local machine

## Preparing Your Application

The application has already been configured for web deployment with the following changes:

1. The Flask app now binds to `0.0.0.0` to accept connections from any IP
2. Port settings are read from environment variables (for cloud compatibility)
3. Debug mode is controlled via environment variables
4. A `Procfile` has been added for Heroku deployment
5. `gunicorn` has been added to requirements.txt as a production web server

## Deployment Options

### Option 1: Heroku

Heroku is one of the easiest platforms for deploying Flask applications.

1. **Create a Heroku account** at [heroku.com](https://heroku.com) if you don't have one

2. **Install the Heroku CLI** from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

3. **Login to Heroku** from your terminal:
   ```
   heroku login
   ```

4. **Initialize a Git repository** (if you haven't already):
   ```
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```

5. **Create a Heroku app**:
   ```
   heroku create your-app-name
   ```
   Replace `your-app-name` with a unique name for your application

6. **Deploy to Heroku**:
   ```
   git push heroku main
   ```
   (or `git push heroku master` depending on your branch name)

7. **Set environment variables** (if needed):
   ```
   heroku config:set FLASK_DEBUG=False
   ```

8. **Open your application**:
   ```
   heroku open
   ```

### Option 2: Render

Render is a newer cloud platform with a generous free tier.

1. **Create a Render account** at [render.com](https://render.com)

2. **Connect your GitHub repository** to Render

3. **Create a new Web Service**:
   - Select your repository
   - Choose a name for your service
   - Select "Python" as the environment
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `gunicorn app:app`
   - Choose the free plan

4. **Click "Create Web Service"**

### Option 3: PythonAnywhere

PythonAnywhere is specifically designed for Python web applications.

1. **Create a PythonAnywhere account** at [pythonanywhere.com](https://pythonanywhere.com)

2. **Upload your code**:
   - Use the Files tab to upload a zip of your project, or
   - Clone your Git repository using the Consoles tab

3. **Set up a virtual environment**:
   ```
   mkvirtualenv --python=/usr/bin/python3.9 myenv
   pip install -r requirements.txt
   ```

4. **Configure a new web app**:
   - Go to the Web tab and click "Add a new web app"
   - Choose "Manual configuration" and select Python 3.9
   - Set the path to your virtual environment
   - Configure the WSGI file to point to your Flask app

5. **Reload your web app**

## Important Considerations for Production

### Database Configuration

The current application uses SQLite, which is fine for small deployments. For larger deployments, consider:

- Using PostgreSQL or another production database
- Configuring the database URL via environment variables
- Implementing database migrations for updates

### Environment Variables

Set these environment variables on your hosting platform:

- `FLASK_DEBUG`: Set to "False" in production
- `SECRET_KEY`: Set to a strong random value for session security

### Reddit API Credentials

Make sure to set up your Reddit API credentials as environment variables if your application uses them.

## Troubleshooting

### Common Issues

1. **Application Error on Heroku**:
   - Check logs with `heroku logs --tail`
   - Ensure Procfile is correctly formatted
   - Verify all dependencies are in requirements.txt

2. **Database Issues**:
   - Ensure database initialization happens before the app starts
   - Check file permissions for SQLite database

3. **Port Binding Errors**:
   - Ensure your app is binding to the port provided by the environment

## Maintenance

After deployment, regularly:

1. Update dependencies to patch security vulnerabilities
2. Monitor application logs for errors
3. Back up your database

## Need Help?

If you encounter issues with deployment, consult the documentation for your chosen platform or seek help from their support channels.