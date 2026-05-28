# 2. Video Downloader

# 🔎  Create a program that:
#     1. Asks the user for a URL
#     2. Downloads the corresponding video in the lowest quality
#     Use a reliable library and no APIs.

import yt_dlp

def download_lowest_quality_video():
    url = input("Enter the URL of the video: ")

    ydl_opts = {
        'format': 'worst[ext=mp4]/worst',
        'outtmpl': '%(title)s.%(ext)s',
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
