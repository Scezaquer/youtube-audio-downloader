import os
import re
from typing import List
import yt_dlp
import eyed3
import unicodedata
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# You need to set up OAuth 2.0 and get your credentials
# Visit https://console.developers.google.com/ to set up a project and get credentials
with open("api_key.txt", "r") as f:
    YOUTUBE_API_KEY = f.readline()

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*!()[\]{}]', '', filename)
    filename = re.sub(r'[\s_]+', '_', filename)
    filename = ''.join(ch for ch in filename if ord(ch) < 128)
    filename = ''.join(ch for ch in filename if unicodedata.category(ch)[0] != 'C')
    filename = filename.strip('_').strip()
    filename = filename[:255]
    if not filename:
        filename = "untitled"
    return filename

def get_playlist_video_ids(playlist_id: str) -> List[str]:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    video_ids = []
    next_page_token = None
    
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        
        pl_response = pl_request.execute()
        
        for item in pl_response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page_token = pl_response.get('nextPageToken')
        
        if not next_page_token:
            break
    
    return video_ids

def download_and_convert_to_mp3(video_id: str, output_dir: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',  # Add this to embed the thumbnail into the MP3 file
            }
        ],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'writethumbnail': True,  # Add this to download the thumbnail
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        original_title = info['title']
        channel = info['channel']
        sanitized_title = sanitize_filename(original_title)
        possible_filenames = [
            os.path.join(output_dir, f"{original_title}.mp3"),
            os.path.join(output_dir, f"{sanitized_title}.mp3"),
            os.path.join(ydl.prepare_filename(info)).rsplit('.', 1)[0] + '.mp3'
        ]
        
        for filename in possible_filenames:
            if os.path.exists(filename):
                new_filename = os.path.join(output_dir, f"{sanitized_title}.mp3")
                if filename != new_filename:
                    os.rename(filename, new_filename)
                return new_filename, original_title, channel
        
        raise FileNotFoundError(f"Could not find downloaded file for {original_title}")

def set_mp3_metadata(file_path: str, title: str, artist: str):
    audio_file = eyed3.load(file_path)
    if audio_file.tag is None:
        audio_file.initTag()
    
    audio_file.tag.title = title
    audio_file.tag.artist = artist
    audio_file.tag.album = title
    audio_file.tag.save()

def parse_title(title: str, channel: str) -> tuple:
    if " - " in title:
        artist, song_title = title.split(" - ", 1)
    else:
        artist, song_title = channel, title
    return artist.strip(), song_title.strip()

def download_playlist(playlist_id: str, use_history: bool = True):
    output_dir = "audio"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("download_memory", exist_ok=True)
    
    history_file = f"download_memory/{playlist_id}.txt"
    downloaded_ids = set()
    if use_history and os.path.exists(history_file):
        with open(history_file, "r") as f:
            downloaded_ids = set(f.read().splitlines())
    
    video_ids = get_playlist_video_ids(playlist_id)
    new_video_ids = [id for id in video_ids if id not in downloaded_ids]
    
    print(f"Downloading {len(new_video_ids)} new songs...")
    
    failed_downloads = []
    
    for video_id in new_video_ids:
        try:
            file_path, original_title, channel = download_and_convert_to_mp3(video_id, output_dir)
            artist, song_title = parse_title(original_title, channel)
            set_mp3_metadata(file_path, song_title, artist)
            
            with open(history_file, "a") as f:
                f.write(f"{video_id}\n")
            
            print(f"Successfully downloaded and tagged: {original_title}")
        except Exception as e:
            print(f"Failed to download {video_id}: {str(e)}")
            failed_downloads.append(video_id)
    
    if failed_downloads:
        with open("failed_to_download.txt", "a") as f:
            for video_id in failed_downloads:
                f.write(f"{video_id}\n")
        print(f"Failed to download {len(failed_downloads)} videos. Check failed_to_download.txt for details.")

if __name__ == "__main__":
    playlist_id = "PLHd5WXDxcD4C0jAxhtFCJoXbMIgG5EB27"
    download_playlist(playlist_id, use_history=True)