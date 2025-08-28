@echo off
echo Setting up Reddit Crawler for r/legaladvice Class Action Posts...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or higher.
    echo Visit https://www.python.org/downloads/ to download Python.
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Setup complete! You can now run the crawler.
echo.

:menu
echo What would you like to do?
echo 1. Run crawler with default settings (r/legaladvice, 100 posts, 5 comments, 30 days, class action keywords)
echo 2. Run crawler with custom settings
echo 3. Exit

set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo Running crawler with default settings...
    python reddit_crawler.py
    goto end
)

if "%choice%"=="2" (
    echo Running crawler with custom settings...
    
    set /p subreddit=Enter subreddit name (default: legaladvice): 
    if "%subreddit%"=="" set subreddit=legaladvice
    
    set /p posts=Enter number of posts to fetch (default: 100): 
    if "%posts%"=="" set posts=100
    
    set /p comments=Enter number of comments per post (default: 5): 
    if "%comments%"=="" set comments=5
    
    set /p days=Enter number of days to limit posts (default: 30): 
    if "%days%"=="" set days=30
    
    set /p output=Enter output file name (default: legaladvice_classaction_matches.csv): 
    if "%output%"=="" set output=legaladvice_classaction_matches.csv
    
    set /p filter=Filter for class action keywords? (y/n, default: y): 
    if "%filter%"=="" set filter=y
    
    echo Running crawler for r/%subreddit% with %posts% posts and %comments% comments per post for the last %days% days...
    
    if "%filter%"=="y" (
        python run_crawler.py --subreddit %subreddit% --posts %posts% --comments %comments% --days %days% --output %output%
    ) else (
        python run_crawler.py --subreddit %subreddit% --posts %posts% --comments %comments% --days %days% --output %output% --no-filter
    )
    goto end
)

if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
)

echo Invalid choice. Please try again.
goto menu

:end
echo.
echo Crawler execution completed.
pause