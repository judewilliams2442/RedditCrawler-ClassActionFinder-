# Reddit Crawler Dashboard

A simple web dashboard built with Flask that runs the Reddit crawler to identify potential class action lawsuit cases from subreddits like r/legaladvice.

## Features

- Web interface to run the Reddit crawler
- Configurable parameters (subreddit, number of posts, keyword filter)
- Results display with post titles, URLs, and summaries
- CSV export functionality
- Real-time status updates during crawler execution

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

1. Start the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

## Usage

1. On the homepage, configure your crawler settings:
   - **Subreddit**: The subreddit to crawl (default: legaladvice)
   - **Number of Posts**: How many posts to fetch (default: 20)
   - **Keyword Filter**: Optional keyword to filter posts by

2. Click the "Run Crawler" button to start the crawler

3. Wait for the crawler to complete (this may take a few moments)

4. View the results on the results page

5. Optionally download the results as a CSV file

## How It Works

The dashboard is a Flask web application that integrates with the existing Reddit crawler. When you click "Run Crawler", the application:

1. Starts the crawler in a background thread
2. Displays a loading indicator while the crawler runs
3. Automatically refreshes the page when the crawler completes
4. Displays the results in a user-friendly format

## Troubleshooting

- If you encounter any issues with the Reddit API, make sure your API credentials in `reddit_crawler.py` are valid
- If the crawler seems to hang, try reducing the number of posts to fetch
- For any other issues, check the console output for error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.