import os
import requests
import json
from pathlib import Path

# Giphy API key
API_KEY = "GlVGYHkr3WSBnllca54iNt0yFbjz7L65"

def download_trending_gifs():
    """Download trending GIFs from Giphy."""
    url = f"https://api.giphy.com/v1/gifs/trending?api_key={API_KEY}&limit=10&rating=g"
    response = requests.get(url)
    data = response.json()
    
    if data["data"]:
        for gif in data["data"]:
            gif_url = gif["images"]["downsized"]["url"]  # Using downsized version for smaller file size
            gif_id = gif["id"]
            gif_response = requests.get(gif_url)
            
            # Save the GIF
            output_path = f"resources/gifs/{gif_id}.gif"
            with open(output_path, "wb") as f:
                f.write(gif_response.content)
            print(f"Downloaded: {gif_id}")

def main():
    # Create directories if they don't exist
    os.makedirs("resources/gifs", exist_ok=True)
    
    # Download trending GIFs
    download_trending_gifs()

if __name__ == "__main__":
    main() 