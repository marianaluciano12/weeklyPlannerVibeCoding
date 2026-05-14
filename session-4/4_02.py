# 2. Create a python program that asks the user for a URL and downloads the corresponding video in the lowest quality. Use a reliable library and no APIs.
""" 
    Make a program that:
        1. Asks the user for a URL
        2. Downloads the corresponding video in the lowest quality
"""

import yt_dlp

def download_lowest_quality_video():
    url = input("Enter the URL of the video: ")
    
    # Configure yt-dlp options for the lowest quality video
    ydl_opts = {
        'format': 'worst[ext=mp4]/worst', # Get worst quality mp4, or just worst overall
        'outtmpl': '%(title)s.%(ext)s',   # Save as title.extension
    }
    
    print(f"Attempting to download video from: {url}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("\nDownload completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred during download: {e}")

if __name__ == "__main__":
    download_lowest_quality_video()
