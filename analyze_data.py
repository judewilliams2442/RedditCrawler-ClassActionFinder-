import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime

def analyze_reddit_data(csv_file):
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return 1
    
    # Load the data
    print(f"Loading data from {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} posts.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return 1
    
    # Basic statistics
    print("\n=== Basic Statistics ===")
    print(f"Total posts: {len(df)}")
    
    # Check if required columns exist
    required_columns = ['title', 'score', 'num_comments', 'created_utc']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing required columns: {missing_columns}")
        print("Some analyses may not be available.")
    
    # Post scores analysis
    if 'score' in df.columns:
        print("\n=== Post Scores Analysis ===")
        print(f"Average score: {df['score'].mean():.2f}")
        print(f"Median score: {df['score'].median():.2f}")
        print(f"Highest score: {df['score'].max()} (Post: '{df.loc[df['score'].idxmax(), 'title']}')")
        
        # Plot score distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['score'], bins=20, alpha=0.7, color='blue')
        plt.title('Distribution of Post Scores')
        plt.xlabel('Score')
        plt.ylabel('Number of Posts')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        score_plot_file = 'score_distribution.png'
        plt.savefig(score_plot_file)
        print(f"Score distribution plot saved as '{score_plot_file}'")
    
    # Comments analysis
    if 'num_comments' in df.columns:
        print("\n=== Comments Analysis ===")
        print(f"Average comments per post: {df['num_comments'].mean():.2f}")
        print(f"Median comments per post: {df['num_comments'].median():.2f}")
        print(f"Most commented post: {df['num_comments'].max()} comments (Post: '{df.loc[df['num_comments'].idxmax(), 'title']}')")
        
        # Plot comments distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['num_comments'], bins=20, alpha=0.7, color='green')
        plt.title('Distribution of Comments per Post')
        plt.xlabel('Number of Comments')
        plt.ylabel('Number of Posts')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        comments_plot_file = 'comments_distribution.png'
        plt.savefig(comments_plot_file)
        print(f"Comments distribution plot saved as '{comments_plot_file}'")
    
    # Time analysis
    if 'created_utc' in df.columns:
        print("\n=== Time Analysis ===")
        try:
            # Convert UTC timestamps to datetime objects
            df['created_datetime'] = pd.to_datetime(df['created_utc'])
            
            # Get the day of week for each post
            df['day_of_week'] = df['created_datetime'].dt.day_name()
            
            # Count posts by day of week
            day_counts = df['day_of_week'].value_counts()
            
            # Reorder days of week
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = day_counts.reindex(days_order)
            
            print("Posts by day of week:")
            for day, count in day_counts.items():
                print(f"  {day}: {count}")
            
            # Plot posts by day of week
            plt.figure(figsize=(10, 6))
            day_counts.plot(kind='bar', color='purple')
            plt.title('Posts by Day of Week')
            plt.xlabel('Day of Week')
            plt.ylabel('Number of Posts')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            day_plot_file = 'posts_by_day.png'
            plt.savefig(day_plot_file)
            print(f"Posts by day plot saved as '{day_plot_file}'")
            
        except Exception as e:
            print(f"Error in time analysis: {e}")
    
    # Content length analysis
    if 'content' in df.columns:
        print("\n=== Content Analysis ===")
        # Calculate content length
        df['content_length'] = df['content'].astype(str).apply(len)
        
        print(f"Average content length: {df['content_length'].mean():.2f} characters")
        print(f"Median content length: {df['content_length'].median():.2f} characters")
        print(f"Longest post: {df['content_length'].max()} characters (Post: '{df.loc[df['content_length'].idxmax(), 'title']}')")
        
        # Plot content length distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['content_length'], bins=20, alpha=0.7, color='orange')
        plt.title('Distribution of Post Content Length')
        plt.xlabel('Content Length (characters)')
        plt.ylabel('Number of Posts')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        length_plot_file = 'content_length_distribution.png'
        plt.savefig(length_plot_file)
        print(f"Content length distribution plot saved as '{length_plot_file}'")
    
    # Correlation analysis
    if all(col in df.columns for col in ['score', 'num_comments', 'content_length']):
        print("\n=== Correlation Analysis ===")
        # Calculate correlation between score, comments, and content length
        correlation = df[['score', 'num_comments', 'content_length']].corr()
        print("Correlation matrix:")
        print(correlation)
        
        # Plot correlation heatmap
        plt.figure(figsize=(8, 6))
        plt.imshow(correlation, cmap='coolwarm', interpolation='none', vmin=-1, vmax=1)
        plt.colorbar()
        plt.xticks(range(len(correlation)), correlation.columns, rotation=45)
        plt.yticks(range(len(correlation)), correlation.columns)
        
        # Add correlation values to the heatmap
        for i in range(len(correlation)):
            for j in range(len(correlation)):
                plt.text(j, i, f"{correlation.iloc[i, j]:.2f}", 
                         ha="center", va="center", color="white" if abs(correlation.iloc[i, j]) > 0.5 else "black")
        
        plt.title('Correlation Between Post Metrics')
        plt.tight_layout()
        corr_plot_file = 'correlation_heatmap.png'
        plt.savefig(corr_plot_file)
        print(f"Correlation heatmap saved as '{corr_plot_file}'")
    
    print("\nAnalysis complete! Check the current directory for generated plots.")
    return 0

def main():
    # Default file name
    default_file = 'legaladvice_classaction_matches.csv'
    
    # Get file name from command line argument or use default
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = default_file
        print(f"No file specified, using default: {default_file}")
    
    return analyze_reddit_data(csv_file)

if __name__ == "__main__":
    sys.exit(main())