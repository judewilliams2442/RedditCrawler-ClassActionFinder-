import requests
import json
from ollama_summarizer import summarize_text

def test_ollama_api():
    """
    Test the Ollama Summarizer directly.
    """
    print("Testing Ollama Summarizer...")
    
    # Sample Reddit post content
    test_text = """
    I recently purchased a smartphone from TechGiant, and within two weeks, the battery started swelling and the phone became unusable. 
    When I contacted customer service, they told me this was a known issue affecting thousands of customers with this model, 
    but they're refusing to issue a recall or offer free replacements. Instead, they're charging a $200 "repair fee" even though 
    this is clearly a manufacturing defect. I've found online forums with hundreds of people experiencing the same issue. 
    Is there any legal recourse for all of us affected by this defect?
    """
    
    # Test direct function call
    print("\n1. Testing direct function call:")
    summary = summarize_text(test_text)
    print(f"Summary result: {summary}")
    
    # Test the Flask API endpoint
    print("\n2. Testing Flask API endpoint:")
    try:
        response = requests.post(
            "http://localhost:5000/ollama-summarize",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"API response: {result}")
        else:
            print(f"API error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Flask server. Make sure it's running on localhost:5000")

if __name__ == "__main__":
    test_ollama_api()