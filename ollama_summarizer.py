import requests
import json

def summarize_text(text, model="llama3"):
    """
    Send text to a locally running Ollama model and return a summary.
    
    Args:
        text (str): The Reddit post content to summarize
        model (str, optional): The Ollama model name. Defaults to "llama3".
        
    Returns:
        str: The generated summary from Ollama or an error message
    """
    try:
        # Prepare the request
        url = "http://localhost:11434/api/generate"
        prompt = f"You are talking to an experienced attorney. Summarize the following Reddit posts and explain if they can come together in some sort of possible class action case. Additionally, if any one case has the potential to be a class action, highlight that and make it known.:\n\n{text}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        # Send the request with stream=False to get a single complete response
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code != 200:
            return f"Error: Ollama returned status code {response.status_code}"
        
        # Process the non-streaming response
        json_response = response.json()
        summary = json_response.get('response', '')
        
        return summary
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure it is running on localhost:11434."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"