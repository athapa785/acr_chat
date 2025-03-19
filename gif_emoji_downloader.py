import os
import time
import requests
import json

# Replace with your own Giphy API key
GIPHY_API_KEY = 'VEMKHpyQ9lu0KSXbsDUYA3XVcvSXwHDg'

def download_gifs(query, limit, download_dir):
    """Download reaction GIFs from Giphy."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    gifs_downloaded = 0
    offset = 0
    per_request = 50  # Giphygif allows up to 50 per request
    while gifs_downloaded < limit:
        params = {
            'api_key': GIPHY_API_KEY,
            'q': query,
            'limit': min(per_request, limit - gifs_downloaded),
            'offset': offset
        }
        response = requests.get("https://api.giphy.com/v1/gifs/search", params=params)
        if response.status_code != 200:
            print("Failed to fetch GIFs:", response.text)
            break
        data = response.json()
        results = data.get('data', [])
        if not results:
            break
        for gif in results:
            gif_url = gif.get('images', {}).get('original', {}).get('url')
            gif_id = gif.get('id')
            if gif_url and gif_id:
                try:
                    r = requests.get(gif_url, stream=True)
                    if r.status_code == 200:
                        gif_filename = os.path.join(download_dir, f"{gif_id}.gif")
                        with open(gif_filename, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                        gifs_downloaded += 1
                        print(f"Downloaded {gif_filename} ({gifs_downloaded}/{limit})")
                    else:
                        print("Failed to download gif:", gif_url)
                except Exception as e:
                    print("Error downloading gif:", e)
            else:
                print("Missing gif URL or ID")
        offset += len(results)
        time.sleep(0.2)  # Pause briefly to avoid hitting rate limits

def download_emojis(download_dir, limit=1000):
    """
    Download emoji images from the Twemoji CDN.
    
    For demonstration purposes, we use a small curated list of emoji hex codes.
    In a production system, you might load a full list of the most popular emoji codes.
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    # Sample list of popular emoji hex codes (Twemoji uses hex codes in lowercase)
    popular_emojis = [
        '1f600', '1f601', '1f602', '1f603', '1f604', '1f605', '1f606', '1f923',
        '1f609', '1f60a', '1f60b', '1f60e', '1f60d', '1f618', '1f617', '263a',
        '1f61a', '1f619', '1f60f', '1f636', '1f611', '1f62c', '1f615', '1f62a',
        '1f624', '1f625', '1f622', '1f62d', '1f631', '1f628', '1f630', '1f620'
    ]
    # Repeat the list to reach the desired limit (this is just for demonstration)
    emojis_to_download = (popular_emojis * ((limit // len(popular_emojis)) + 1))[:limit]
    
    for code in emojis_to_download:
        url = f"https://twemoji.maxcdn.com/v/latest/72x72/{code}.png"
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                filename = os.path.join(download_dir, f"{code}.png")
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded emoji {code} to {filename}")
            else:
                print(f"Failed to download emoji {code}: HTTP {r.status_code}")
        except Exception as e:
            print(f"Error downloading emoji {code}: {e}")

def categorize_files(base_directory):
    """
    Categorize downloaded files into 'gifs' and 'emojis' based on file extension.
    Returns a dictionary mapping category names to lists of file paths.
    """
    categories = {}
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext == 'gif':
                categories.setdefault('gifs', []).append(os.path.join(root, file))
            elif ext in ['png', 'jpg', 'jpeg']:
                categories.setdefault('emojis', []).append(os.path.join(root, file))
    return categories

def main():
    gif_download_dir = "downloaded_gifs"
    emoji_download_dir = "downloaded_emojis"
    
    print("Downloading 1000 reaction GIFs from Giphy...")
    download_gifs("reaction", 1000, gif_download_dir)
    
    print("\nDownloading 1000 emoji images from Twemoji CDN...")
    download_emojis(emoji_download_dir, limit=1000)
    
    print("\nCategorizing downloaded files...")
    categories = categorize_files(".")
    print(json.dumps(categories, indent=2))
    
if __name__ == "__main__":
    main()