import argparse
import sys
from reddit_crawler import crawl_reddit, print_summarized_posts, save_to_csv, filter_class_action_posts

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Reddit Crawler for r/legaladvice Class Action Posts')
    
    # Add arguments
    parser.add_argument('--subreddit', type=str, default='legaladvice',
                        help='Subreddit to crawl (default: legaladvice)')
    parser.add_argument('--posts', type=int, default=100,
                        help='Number of posts to fetch (default: 100)')
    parser.add_argument('--comments', type=int, default=5,
                        help='Number of comments to fetch per post (default: 5)')
    parser.add_argument('--days', type=int, default=30,
                        help='Limit to posts from the last N days (default: 30)')
    parser.add_argument('--output', type=str, default='legaladvice_classaction_matches.csv',
                        help='Output CSV file name (default: legaladvice_classaction_matches.csv)')
    parser.add_argument('--print-only', action='store_true',
                        help='Only print to console, do not save to CSV')
    parser.add_argument('--no-filter', action='store_true',
                        help='Disable filtering for class action keywords')
    parser.add_argument('--keyword', help='Specify a single keyword to filter by')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Define keywords for potential class action lawsuits
    class_action_keywords = [
        "class action", "anyone else", "same issue", "same problem", "illegal",
        "wage theft", "false advertising", "scam", "unsafe", "defective"
    ]
    
    # Print configuration
    print(f"Crawling r/{args.subreddit}...")
    print(f"Fetching posts from the last {args.days} days")
    print(f"Looking for {args.posts} posts with {args.comments} comments each")
    
    # Determine filter keywords based on --no-filter flag and --keyword option
    filter_keywords = None if args.no_filter else class_action_keywords
    
    # If a specific keyword is provided, use only that keyword
    if args.keyword:
        filter_keywords = [args.keyword]
        print(f"Filtering for posts with keyword: {args.keyword}")
    elif not args.no_filter:
        print(f"Filtering for potential class action posts with keywords: {', '.join(class_action_keywords)}")
    
    try:
        # Crawl Reddit
        posts_data = crawl_reddit(args.subreddit, args.posts, args.comments, args.days, filter_keywords)
        
        # Print summarized posts
        print_summarized_posts(posts_data)
        
        # Save to CSV if not print-only
        if not args.print_only:
            save_to_csv(posts_data, args.output)
            print(f"Data saved to {args.output}")
        
        return 0  # Success
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1  # Error

if __name__ == "__main__":
    sys.exit(main())