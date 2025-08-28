@echo off
echo ===== Reddit Crawler Heroku Deployment =====

REM Check if Heroku CLI is installed
heroku --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Heroku CLI is not installed. Please install it from:
    echo https://devcenter.heroku.com/articles/heroku-cli
    exit /b 1
)

echo Heroku CLI detected. Proceeding with deployment...

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
)

REM Create Heroku app if app name is provided
set /p app_name=Enter your Heroku app name (leave blank to use existing app): 

if not "%app_name%"=="" (
    echo Creating Heroku app: %app_name%
    heroku create %app_name%
) else (
    echo Using existing Heroku app...
)

REM Set environment variables
echo Setting up environment variables...
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

echo Do you want to use PostgreSQL database? (y/n)
set /p use_postgres=

if /i "%use_postgres%"=="y" (
    echo Adding PostgreSQL addon...
    heroku addons:create heroku-postgresql:hobby-dev
)

REM Generate a random secret key
set "random_key=%RANDOM%%RANDOM%%RANDOM%%RANDOM%"
echo Setting SECRET_KEY environment variable...
heroku config:set SECRET_KEY=%random_key%

REM Push to Heroku
echo Deploying to Heroku...
git push heroku master

echo ===== Deployment Complete =====
echo Your app should now be available at:
heroku open

echo You can view logs with: heroku logs --tail