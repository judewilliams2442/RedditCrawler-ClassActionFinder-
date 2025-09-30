from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
import requests
import os
import pandas as pd
import threading
import time
import io
import csv
import json
import uuid
import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from db import get_connection, init_db
from run_crawler import main as run_crawler_main
from ollama_summarizer import summarize_text


app = Flask(__name__)
# Use a strong secret key in production by setting the SECRET_KEY environment variable
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_reddit_crawler')

# Configure for production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'

# Global variable to store crawler results
crawler_results = []
crawler_running = False
crawler_complete = False
current_run_id = None

# Initialize database
init_db()

@app.route('/')
def index():
    # Get previous crawler runs from database
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM crawler_runs ORDER BY timestamp DESC LIMIT 10')
    previous_runs = cur.fetchall()
    conn.close()
    
    return render_template('index.html', previous_runs=previous_runs)

@app.route('/ollama-summarize', methods=['POST'])
def ollama_summarize():
    """
    API endpoint to summarize text using Ollama.
    
    Expects JSON with:
    - text: The Reddit post content to summarize
    - model: (optional) The Ollama model name, defaults to "llama3"
    
    Returns JSON with:
    - summary: The generated summary
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required parameter: text'}), 400
        
        text = data['text']
        model = data.get('model', 'llama3')  # Default to llama3 if not specified
        
        # Call the Ollama summarizer
        summary = summarize_text(text, model)
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    API endpoint to summarize text using Ollama with gemma3 model.
    
    Expects JSON with:
    - text: The text to summarize
    
    Returns JSON with:
    - summary: The generated summary
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'summary': 'Error: Missing required parameter: text'}), 400
        
        text = data['text']
        
        # Prepare the request to Ollama
        url = "http://localhost:11434/api/generate"
        prompt = f"Summarize this: {text}"
        
        payload = {
            "model": "gemma3",
            "prompt": prompt
        }
        
        # Send the request and handle streaming response
        response = requests.post(url, json=payload, stream=True)
        
        # Check if the request was successful
        if response.status_code != 200:
            return jsonify({'summary': f'Error: Ollama returned status code {response.status_code}'}), 500
        
        # Process the streaming response
        summary = ""
        for line in response.iter_lines():
            if line:
                # Parse the JSON response
                try:
                    json_response = json.loads(line.decode('utf-8'))
                    if 'response' in json_response:
                        summary += json_response['response']
                except json.JSONDecodeError:
                    continue
        
        return jsonify({'summary': summary})
    
    except requests.exceptions.ConnectionError:
        return jsonify({'summary': 'Error: Could not connect to Ollama. Make sure it is running on localhost:11434.'}), 503
    except Exception as e:
        return jsonify({'summary': f'Error: An unexpected error occurred: {str(e)}'}), 500

@app.route('/summarize-all', methods=['POST'])
def summarize_all():
    """
    API endpoint to summarize all posts from the current or specified run.
    """
    try:
        data = request.get_json()
        run_id = data.get('run_id') if data else None
        
        # If no run_id provided, use current run
        if not run_id:
            run_id = current_run_id
        
        # Get posts from database
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM crawler_results WHERE run_id = ?', (run_id,))
        results_data = cur.fetchall()
        conn.close()
        
        if not results_data:
            return jsonify({'summary': 'Error: No posts found to summarize'}), 400
        
        # Extract content from posts
        post_contents = []
        for row in results_data:
            # Use summary if available, otherwise use title
            content = row['summary'] if row['summary'] else row['title']
            if content and content.strip():
                post_contents.append(content)
        
        if not post_contents:
            return jsonify({'summary': 'Error: No content found in posts to summarize'}), 400
        
        # Concatenate all post contents
        full_text = "\n\n---\n\n".join(post_contents)
        
        # Prepare the request to Ollama
        url = "http://localhost:11434/api/generate"
        prompt = f"Provide a high-level summary of the key themes and common issues from the following Reddit posts:\n\n{full_text}"
        
        payload = {
            "model": "gemma3",
            "prompt": prompt
        }
        
        # Send the request and handle streaming response
        response = requests.post(url, json=payload, stream=True)
        
        # Check if the request was successful
        if response.status_code != 200:
            return jsonify({'summary': f'Error: Ollama returned status code {response.status_code}'}), 500
        
        # Process the streaming response
        summary = ""
        for line in response.iter_lines():
            if line:
                # Parse the JSON response
                try:
                    json_response = json.loads(line.decode('utf-8'))
                    if 'response' in json_response:
                        summary += json_response['response']
                except json.JSONDecodeError:
                    continue
        
        return jsonify({'summary': summary})
    
    except requests.exceptions.ConnectionError:
        return jsonify({'summary': 'Error: Could not connect to Ollama. Make sure it is running on localhost:11434.'}), 503
    except Exception as e:
        return jsonify({'summary': f'Error: An unexpected error occurred: {str(e)}'}), 500

@app.route('/run-crawler', methods=['POST'])
def run_crawler():
    global crawler_results, crawler_running, crawler_complete, current_run_id
    
    # Reset state
    crawler_results = []
    crawler_running = True
    crawler_complete = False
    
    # Generate a unique ID for this run
    current_run_id = str(uuid.uuid4())
    
    # Get parameters from form
    subreddit = request.form.get('subreddit', 'legaladvice')
    posts = int(request.form.get('posts', 20))
    keyword = request.form.get('keyword', '')
    
    # Store run information in session for later use
    session['current_run'] = {
        'id': current_run_id,
        'subreddit': subreddit,
        'posts': posts,
        'keyword': keyword,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # Start crawler in a background thread
    thread = threading.Thread(target=run_crawler_thread, args=(subreddit, posts, keyword, current_run_id))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('results'))

def run_crawler_thread(subreddit, posts, keyword, run_id):
    global crawler_results, crawler_running, crawler_complete
    
    # Prepare arguments for the crawler
    import sys
    original_argv = sys.argv.copy()
    
    # Build command line arguments
    sys.argv = ['run_crawler.py', '--subreddit', subreddit, '--posts', str(posts), '--print-only']
    
    # Add keyword if provided
    if keyword:
        sys.argv.extend(['--keyword', keyword])
    
    try:
        # Redirect stdout to capture output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Import and run the crawler
            from reddit_crawler import crawl_reddit, print_summarized_posts
            
            # Define keywords based on input
            filter_keywords = [keyword] if keyword else None
            
            # Run the crawler and get results
            posts_data = crawl_reddit(subreddit, posts, 5, 30, filter_keywords)
            
            # Store results in global variable
            crawler_results = posts_data
            
            # Save results to database
            conn = get_connection()
            cur = conn.cursor()
            
            # First, save the run information
            cur.execute(
                'INSERT INTO crawler_runs (id, timestamp, subreddit, posts_count, keyword, results_count) VALUES (?, ?, ?, ?, ?, ?)',
                (run_id, datetime.datetime.now().isoformat(), subreddit, posts, keyword, len(posts_data))
            )
            
            # Then save each result
            for post in posts_data:
                # Convert top_comments to JSON string if present
                top_comments_json = None
                if 'top_comments' in post and post['top_comments']:
                    top_comments_json = json.dumps(post['top_comments'])
                
                cur.execute(
                    'INSERT INTO crawler_results (run_id, title, url, score, author, created_utc, num_comments, summary, top_comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (run_id, post['title'], post['permalink'], post['score'], post['author'], post['created_utc'], 
                     post['num_comments'], post.get('summary', ''), top_comments_json)
                )
            
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error running crawler: {e}")
    finally:
        # Restore original argv
        sys.argv = original_argv
        crawler_running = False
        crawler_complete = True

@app.route('/results')
def results():
    run_id = request.args.get('run_id', current_run_id)
    
    # If a specific run_id is provided, load results from database
    if run_id and run_id != current_run_id:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM crawler_runs WHERE id = ?', (run_id,))
        run_info = cur.fetchone()
        
        if not run_info:
            conn.close()
            return redirect(url_for('index'))
        
        cur.execute('SELECT * FROM crawler_results WHERE run_id = ?', (run_id,))
        results_data = cur.fetchall()
        conn.close()
        
        # Convert database rows to dictionaries
        results_list = []
        for row in results_data:
            # Parse top_comments JSON if available
            top_comments = []
            try:
                if row['top_comments']:
                    top_comments = json.loads(row['top_comments'])
            except (json.JSONDecodeError, TypeError):
                pass
            
            results_list.append({
                'title': row['title'],
                'permalink': row['url'],
                'score': row['score'],
                'author': row['author'],
                'created_utc': row['created_utc'],
                'num_comments': row['num_comments'],
                'summary': row['summary'],
                'top_comments': top_comments
            })
        
        return render_template('results.html',
                              crawler_running=False,
                              crawler_complete=True,
                              results=results_list,
                              run_id=run_id,
                              subreddit=run_info['subreddit'],
                              keyword=run_info['keyword'],
                              timestamp=run_info['timestamp'],
                              is_cached=True)
    else:
        # Use current results
        return render_template('results.html', 
                              crawler_running=crawler_running,
                              crawler_complete=crawler_complete,
                              results=crawler_results,
                              subreddit=session.get('current_run', {}).get('subreddit', ''),
                              keyword=session.get('current_run', {}).get('keyword', ''),
                              is_cached=False)

@app.route('/status')
def status():
    return jsonify({
        'running': crawler_running,
        'complete': crawler_complete,
        'result_count': len(crawler_results)
    })

@app.route('/visualize/<run_id>')
def visualize(run_id):
    # Get run info and results from database
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM crawler_runs WHERE id = ?', (run_id,))
    run_info = cur.fetchone()
    
    if not run_info:
        conn.close()
        return redirect(url_for('index'))
    
    cur.execute('SELECT * FROM crawler_results WHERE run_id = ?', (run_id,))
    results_data = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert database rows to dictionaries
    results_list = []
    for row in results_data:
        # Parse top_comments JSON if available
        top_comments = []
        try:
            if row['top_comments']:
                top_comments = json.loads(row['top_comments'])
        except (json.JSONDecodeError, TypeError):
            pass
        
        results_list.append({
            'title': row['title'],
            'permalink': row['url'],
            'score': row['score'],
            'author': row['author'],
            'created_utc': row['created_utc'],
            'num_comments': row['num_comments'],
            'summary': row['summary'],
            'top_comments': top_comments
        })
    
    # Generate visualizations
    charts = generate_visualizations(results_list, run_info)
    
    return render_template('visualize.html',
                          run_info=run_info,
                          charts=charts,
                          result_count=len(results_list))

def generate_visualizations(results, run_info):
    charts = {}
    
    # Only generate charts if we have results
    if not results:
        return charts
    
    # 1. Score Distribution
    plt.figure(figsize=(10, 6))
    scores = [post['score'] for post in results]
    plt.hist(scores, bins=10, alpha=0.7, color='blue')
    plt.title('Distribution of Post Scores')
    plt.xlabel('Score')
    plt.ylabel('Number of Posts')
    plt.grid(True, alpha=0.3)
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    charts['score_distribution'] = base64_encode_image(buf)
    plt.close()
    
    # 2. Comments Distribution
    plt.figure(figsize=(10, 6))
    comments = [post['num_comments'] for post in results]
    plt.hist(comments, bins=10, alpha=0.7, color='green')
    plt.title('Distribution of Comments per Post')
    plt.xlabel('Number of Comments')
    plt.ylabel('Number of Posts')
    plt.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    charts['comments_distribution'] = base64_encode_image(buf)
    plt.close()
    
    # 3. Top Posts by Score
    plt.figure(figsize=(12, 8))
    top_posts = sorted(results, key=lambda x: x['score'], reverse=True)[:10]
    titles = [post['title'][:30] + '...' if len(post['title']) > 30 else post['title'] for post in top_posts]
    scores = [post['score'] for post in top_posts]
    
    y_pos = np.arange(len(titles))
    plt.barh(y_pos, scores, align='center', alpha=0.7, color='purple')
    plt.yticks(y_pos, titles)
    plt.xlabel('Score')
    plt.title('Top Posts by Score')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    charts['top_posts'] = base64_encode_image(buf)
    plt.close()
    
    return charts

def base64_encode_image(image_buffer):
    import base64
    return base64.b64encode(image_buffer.getvalue()).decode('utf-8')

@app.route('/download-csv')
def download_csv():
    run_id = request.args.get('run_id')
    results_to_download = []
    subreddit_name = ''
    
    if run_id:
        # Get cached results from database
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM crawler_runs WHERE id = ?', (run_id,))
        run = cur.fetchone()
        
        if run:
            subreddit_name = run['subreddit']
            cur.execute('SELECT * FROM crawler_results WHERE run_id = ?', (run_id,))
            results = cur.fetchall()
            
            for result in results:
                # Get top comments if available
                top_comments = []
                try:
                    if result['top_comments']:
                        top_comments = json.loads(result['top_comments'])
                except (json.JSONDecodeError, TypeError):
                    pass
                
                results_to_download.append({
                    'title': result['title'],
                    'permalink': result['url'],
                    'score': result['score'],
                    'author': result['author'],
                    'created_utc': result['created_utc'],
                    'num_comments': result['num_comments'],
                    'summary': result['summary'],
                    'top_comments': top_comments
                })
        conn.close()
    else:
        # Use current results
        if not crawler_results:
            return redirect(url_for('results'))
        
        results_to_download = crawler_results
        if 'current_run' in session:
            subreddit_name = session['current_run'].get('subreddit', '')
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Title', 'URL', 'Score', 'Author', 'Created', 'Comments', 'Summary', 'Top Comments'])
    
    # Write data
    for post in results_to_download:
        # Format top comments as a string
        top_comments_str = ''
        if 'top_comments' in post and post['top_comments']:
            if isinstance(post['top_comments'], list):
                if isinstance(post['top_comments'][0], str):
                    top_comments_str = '\n'.join(post['top_comments'])
                elif isinstance(post['top_comments'][0], dict):
                    comments_formatted = [f"u/{c.get('author', 'unknown')} (Score: {c.get('score', 0)}): {c.get('body', '')}" 
                                         for c in post['top_comments'][:3]]
                    top_comments_str = '\n'.join(comments_formatted)
        
        writer.writerow([
            post['title'],
            post.get('permalink', ''),
            post['score'],
            post['author'],
            post.get('created_utc', ''),
            post['num_comments'],
            post.get('summary', ''),
            top_comments_str
        ])
    
    # Prepare response
    output.seek(0)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reddit_crawler_{subreddit_name}_{timestamp}.csv" if subreddit_name else f"reddit_crawler_results_{timestamp}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Initialize the database
    init_db()
    
    # Update requirements.txt to include Flask and other dependencies
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    # Add required packages if not already present
    required_packages = {
        'flask': 'flask==2.3.3',
        'matplotlib': 'matplotlib',  # Use existing version or default
        'numpy': 'numpy',  # Use existing version or default
        'gunicorn': 'gunicorn==20.1.0'  # For production deployment
    }
    
    missing_packages = []
    for package, version in required_packages.items():
        if package not in requirements.lower():
            missing_packages.append(version)
    
    if missing_packages:
        with open('requirements.txt', 'a') as f:
            f.write('\n' + '\n'.join(missing_packages) + '\n')
    
    # Get port from environment variable (for Heroku/cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # In production, debug should be False
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run the app - bind to all IPs (0.0.0.0) for cloud deployment
    app.run(host='0.0.0.0', port=port, debug=debug)