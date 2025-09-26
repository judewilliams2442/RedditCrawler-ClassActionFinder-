# Setting Up Reddit API Credentials

The Reddit Crawler application requires Reddit API credentials to function properly. When you run the application, you may see an error message like:

```
Error running crawler: Required configuration setting 'client_id' missing.
This setting can be provided in a praw.ini file, as a keyword argument to the Reddit class constructor, or as an environment variable.
```

This document explains how to set up the necessary credentials.

## Option 1: Environment Variables (Recommended)

The application is configured to read Reddit API credentials from the following environment variables:

- `REDDIT_CLIENT_ID` - Your Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Your Reddit API client secret
- `REDDIT_USER_AGENT` - A user agent string (e.g., "RedditCrawler:v1.0 (by u/yourusername)")

### Setting Environment Variables

#### Windows

1. Open Command Prompt or PowerShell
2. Set the environment variables:

```
setx REDDIT_CLIENT_ID "your_client_id"
setx REDDIT_CLIENT_SECRET "your_client_secret"
setx REDDIT_USER_AGENT "RedditCrawler:v1.0 (by u/yourusername)"
```

3. Close and reopen your command prompt or terminal

#### macOS/Linux

1. Open Terminal
2. Set the environment variables:

```
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="RedditCrawler:v1.0 (by u/yourusername)"
```

3. To make these permanent, add these lines to your `~/.bashrc`, `~/.zshrc`, or equivalent shell configuration file

## Option 2: Using praw.ini File

Alternatively, you can create a `praw.ini` file in your project directory with the following content:

```ini
[DEFAULT]
client_id=your_client_id
client_secret=your_client_secret
user_agent=RedditCrawler:v1.0 (by u/yourusername)
```

## Getting Reddit API Credentials

To obtain your Reddit API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App" at the bottom
3. Fill in the required information:
   - Name: RedditCrawler (or any name you prefer)
   - Select "script" as the application type
   - Description: A script to crawl Reddit (or any description)
   - About URL: (can be left blank)
   - Redirect URI: http://localhost:8080 (or any valid URL, it won't be used)
4. Click "Create app"
5. Note your client ID (the string under the app name) and client secret

## Troubleshooting

If you continue to experience issues after setting up your credentials:

1. Verify that the environment variables are correctly set by printing them in your terminal/command prompt
2. Check that you've entered the correct client ID and client secret
3. Ensure you're using a valid user agent string
4. If using a `praw.ini` file, verify it's in the correct location and has the proper format

For more information, refer to the [PRAW documentation](https://praw.readthedocs.io/en/stable/getting_started/authentication.html).