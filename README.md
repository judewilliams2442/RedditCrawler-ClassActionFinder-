# Reddit Crawler for r/legaladvice Class Action Posts

This is a Python script that crawls the r/legaladvice subreddit, fetches posts that might indicate potential class action lawsuits, and generates summaries of the content using natural language processing techniques.

## Features

- Fetches recent posts from r/legaladvice subreddit
- Filters posts that might indicate potential class action lawsuits using keywords
- Extracts post details (title, author, score, creation time, URL, etc.)
- Collects top comments for each post
- Generates summaries of post content using extractive summarization
- Limits results to posts from the last 30 days
- Saves the data to a CSV file for further analysis
- Includes tools for data visualization and analysis

## Requirements

- Python 3.7 or higher
- Required Python packages (listed in `requirements.txt`)

## Setup

1. Clone or download this repository

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a Reddit API application:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App" at the bottom
   - Fill in the required information:
     - Name: ClashRoyaleCrawler (or any name you prefer)
     - Select "script" as the application type
     - Description: A script to crawl r/ClashRoyale (or any description)
     - About URL: (can be left blank)
     - Redirect URI: http://localhost:8080 (or any valid URL, it won't be used)
   - Click "Create app"
   - Note your client ID (the string under the app name) and client secret

4. Update the Reddit API credentials in `reddit_crawler.py` if needed:
   - Replace the existing client ID with your client ID
   - Replace the existing client secret with your client secret
   - Replace the existing user agent with your Reddit username

## Usage

### Option 1: Using the Batch File (Windows)

For Windows users, we've included a convenient batch file that helps you set up and run the crawler:

1. Double-click `setup_and_run.bat`
2. Follow the on-screen instructions to install dependencies and run the crawler
3. Choose between default settings or customize the crawler parameters

### Option 2: Using the Command-Line Interface

The `run_crawler.py` script provides a command-line interface with various options:

```
python run_crawler.py [options]
```

Options:
- `--subreddit SUBREDDIT`: Subreddit to crawl (default: legaladvice)
- `--posts POSTS`: Number of posts to fetch (default: 100)
- `--comments COMMENTS`: Number of comments to fetch per post (default: 5)
- `--days DAYS`: Limit to posts from the last N days (default: 30)
- `--output OUTPUT`: Output CSV file name (default: legaladvice_classaction_matches.csv)
- `--print-only`: Only print to console, do not save to CSV
- `--no-filter`: Disable filtering for class action keywords

Examples:
```
# Crawl r/legaladvice with default settings (filtering for class action keywords)
python run_crawler.py

# Crawl r/legaladvice with 200 posts and 10 comments each
python run_crawler.py --posts 200 --comments 10

# Crawl r/legaladvice for the last 60 days
python run_crawler.py --days 60

# Crawl r/legaladvice without filtering for class action keywords
python run_crawler.py --no-filter

# Crawl r/legaladvice and save to a custom file
python run_crawler.py --output my_legaladvice_data.csv

# Crawl r/legaladvice but only print to console (don't save to CSV)
python run_crawler.py --print-only
```

### Option 3: Using the Main Script Directly

Run the main script with Python:

```
python reddit_crawler.py
```

The script will:
1. Fetch up to 100 recent posts from r/legaladvice (excluding stickied posts)
2. Filter posts containing keywords related to potential class action lawsuits
3. Extract post details and top 5 comments for each post
4. Generate summaries for posts with sufficient text content
5. Print the summarized posts and comments to the console
6. Save all the data to a CSV file named `legaladvice_classaction_matches.csv`

## Analyzing the Data

After crawling Reddit and saving the data to a CSV file, you can use the included analysis script to generate visualizations and statistics:

```
python analyze_data.py [csv_file]
```

If you don't specify a CSV file, it will use the default `legaladvice_classaction_matches.csv`.

The analysis script will generate:

1. **Basic Statistics**:
   - Total number of posts
   - Average, median, and highest scores
   - Average, median, and maximum number of comments
   - Average, median, and maximum content length

2. **Visualizations** (saved as PNG files):
   - Score distribution histogram
   - Comments distribution histogram
   - Posts by day of week bar chart
   - Content length distribution histogram
   - Correlation heatmap between post metrics

Example output:
```
Loading data from legaladvice_classaction_matches.csv...
Loaded 15 posts.

=== Basic Statistics ===
Total posts: 15

=== Post Scores Analysis ===
Average score: 125.30
Median score: 78.50
Highest score: 524 (Post: 'Employer not paying overtime - is this wage theft?')
Score distribution plot saved as 'score_distribution.png'

...

Analysis complete! Check the current directory for generated plots.
```

## Customization

You can modify the following parameters in the `main()` function of `reddit_crawler.py`:

- `subreddit_name`: Change to crawl a different subreddit
- `post_limit`: Change the number of posts to fetch
- `comment_limit`: Change the number of top comments to fetch per post
- `days_limit`: Change the time period for posts to fetch
- `class_action_keywords`: Modify the list of keywords to filter posts

## How the Summarization Works

The script uses extractive summarization based on the TextRank algorithm:

1. The text is split into sentences
2. A similarity matrix is created based on cosine similarity between sentences
3. A graph is constructed where nodes are sentences and edges represent similarity
4. The PageRank algorithm ranks sentences by importance
5. The top N sentences are selected and arranged in their original order

This approach extracts the most important sentences from the original text to create a concise summary.

## Project Structure

```
├── reddit_crawler.py    # Main crawler script
├── run_crawler.py       # Command-line interface
├── analyze_data.py      # Data analysis and visualization script
├── setup_and_run.bat    # Windows batch file for easy setup and running
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).