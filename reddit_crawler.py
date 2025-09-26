import praw
import pandas as pd
import datetime
import os
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Function to summarize text using extractive summarization
def generate_summary(text, num_sentences=5):
    # If text is too short, return it as is
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    
    # Create similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stop_words)
    
    # Create graph and use pagerank algorithm to rank sentences
    sentence_similarity_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(sentence_similarity_graph)
    
    # Sort sentences by score and select top ones
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    
    # Get the top n sentences as summary
    summary_sentences = [ranked_sentences[i][1] for i in range(min(num_sentences, len(ranked_sentences)))]
    
    # Sort the selected sentences based on their original order
    summary_sentences.sort(key=lambda sentence: sentences.index(sentence))
    
    # Join the selected sentences
    summary = ' '.join(summary_sentences)
    
    return summary

# Function to calculate similarity between sentences
def sentence_similarity(sent1, sent2, stop_words):
    sent1 = [w.lower() for w in sent1.split() if w.lower() not in stop_words]
    sent2 = [w.lower() for w in sent2.split() if w.lower() not in stop_words]
    
    # If both sentences are empty, they are identical
    if len(sent1) == 0 or len(sent2) == 0:
        return 0.0
    
    # Create a set of all unique words
    all_words = list(set(sent1 + sent2))
    
    # Create word vectors
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
    
    # Build the vectors
    for w in sent1:
        vector1[all_words.index(w)] += 1
    
    for w in sent2:
        vector2[all_words.index(w)] += 1
    
    # Calculate cosine similarity
    return 1 - cosine_distance(vector1, vector2)

# Function to crawl Reddit
def crawl_reddit(subreddit_name, post_limit=10, comment_limit=5, days_limit=30, filter_keywords=None):
    # Initialize Reddit API client
    # Note: You need to create a Reddit app and get these credentials
    # Visit https://www.reddit.com/prefs/apps to create an app
    # This will automatically use credentials from praw.ini
    reddit = praw.Reddit()   
    
    # Access the subreddit
    subreddit = reddit.subreddit(subreddit_name)
    
    # Calculate the cutoff date for posts (default: 30 days ago)
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_limit)
    cutoff_timestamp = cutoff_date.timestamp()
    
    # Create a list to store post data
    posts_data = []
    matches_found = 0
    
    # Get new posts from the subreddit
    posts_processed = 0
    for post in subreddit.new(limit=post_limit*2):  # Fetch more posts to account for filtering
        posts_processed += 1
        print(f"Processing post {posts_processed}: {post.title[:50]}...")
        
        # Skip stickied posts and posts older than the cutoff date
        if post.stickied or post.created_utc < cutoff_timestamp:
            print("  Skipping: Stickied or too old")
            continue
            
        # If filter keywords are provided, check if any keyword is in the title or selftext
        if filter_keywords:
            title_lower = post.title.lower()
            selftext_lower = post.selftext.lower() if hasattr(post, 'selftext') else ''
            
            # Check if any keyword is in the title or selftext
            matched_keywords = [keyword for keyword in filter_keywords if keyword.lower() in title_lower or keyword.lower() in selftext_lower]
            if matched_keywords:
                matches_found += 1
                print(f"  MATCH FOUND! Keywords: {', '.join(matched_keywords)}")
                print(f"  Title: {post.title}")
                print(f"  URL: https://www.reddit.com{post.permalink}")
            else:
                print(f"  No keyword matches found, skipping")
                continue  # Skip this post if no keywords match
        
        # Get post details
        post_data = {
            'title': post.title,
            'score': post.score,
            'id': post.id,
            'url': post.url,
            'created_utc': datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            'author': str(post.author),
            'num_comments': post.num_comments,
            'permalink': f'https://www.reddit.com{post.permalink}',
        }
        
        # Get post content
        if hasattr(post, 'selftext') and post.selftext:
            post_data['content'] = post.selftext
            # Generate summary if content is long enough
            if len(post.selftext.split()) > 50:  # Only summarize if more than 50 words
                post_data['summary'] = generate_summary(post.selftext)
            else:
                post_data['summary'] = post.selftext
        else:
            post_data['content'] = '[No text content]'
            post_data['summary'] = '[No text content]'
        
        # Get top comments
        post_data['top_comments'] = []
        post.comment_sort = 'top'
        post.comments.replace_more(limit=0)  # Skip 'load more comments' links
        for comment in post.comments[:comment_limit]:
            comment_data = {
                'author': str(comment.author),
                'score': comment.score,
                'body': comment.body,
                'created_utc': datetime.datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            }
            post_data['top_comments'].append(comment_data)
        
        posts_data.append(post_data)
    
    print(f"\nCrawling complete. Found {matches_found} posts matching the filter criteria out of {posts_processed} processed posts.")
    return posts_data

# Function to save results to CSV
def save_to_csv(posts_data, filename='clash_royale_posts.csv'):
    # Create a DataFrame from the posts data
    df = pd.DataFrame(posts_data)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')
    
# Function to filter posts for potential class action lawsuits
def filter_class_action_posts(posts_data, keywords):
    filtered_posts = []
    
    for post in posts_data:
        title_lower = post['title'].lower()
        content_lower = post['content'].lower()
        
        # Check if any keyword is in the title or content
        if any(keyword.lower() in title_lower or keyword.lower() in content_lower for keyword in keywords):
            filtered_posts.append(post)
    
    return filtered_posts

# Function to print summarized posts
def print_summarized_posts(posts_data):
    for i, post in enumerate(posts_data, 1):
        print(f"\n{'-'*80}\n")
        print(f"{i}. {post['title']} (Score: {post['score']})")
        print(f"Posted by u/{post['author']} on {post['created_utc']}")
        print(f"URL: {post['permalink']}")
        print("\nSummary:")
        print(post['summary'])
        print("\nTop Comments:")
        for j, comment in enumerate(post['top_comments'], 1):
            print(f"  {j}. u/{comment['author']} (Score: {comment['score']}): {comment['body'][:100]}..." if len(comment['body']) > 100 else f"  {j}. u/{comment['author']} (Score: {comment['score']}): {comment['body']}")

# Main function
def main():
    subreddit_name = 'legaladvice'
    post_limit = 100  # Number of posts to crawl (increased to get more potential matches)
    comment_limit = 5  # Number of top comments to get per post
    days_limit = 30  # Limit to posts from the last 30 days
    
    # Keywords for potential class action lawsuits
    class_action_keywords = [
        "class action", "anyone else", "same issue", "same problem",
        "illegal", "wage theft", "false advertising", "scam", "unsafe", "defective"
    ]
    
    print(f"Crawling r/{subreddit_name} for potential class action posts...")
    posts_data = crawl_reddit(subreddit_name, post_limit, comment_limit, days_limit, class_action_keywords)
    
    # Print summarized posts
    print_summarized_posts(posts_data)
    
    # Save data to CSV
    save_to_csv(posts_data, 'legaladvice_classaction_matches.csv')

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()