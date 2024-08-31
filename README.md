# YouTube Playlist Downloader

This Python script allows you to download and convert YouTube playlist videos to MP3 format, complete with proper metadata tagging.

## Features

- Downloads all videos from a specified YouTube playlist
- Converts videos to high-quality MP3 files
- Embeds video thumbnails into MP3 files
- Sets appropriate metadata (title, artist, album) for each MP3 file
- Sanitizes filenames to ensure compatibility across different operating systems
- Keeps track of downloaded videos to avoid duplicates in subsequent runs
- Handles download failures gracefully

## Requirements

- Python 3.6+
- Required Python packages (install via `pip install -r requirements.txt`):
  - yt-dlp
  - eyed3
  - google-api-python-client

## Setup

1. Clone this repository or download the script.

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up OAuth 2.0 credentials:
   - Visit https://console.developers.google.com/
   - Create a new project (or select an existing one)
   - Enable the YouTube Data API v3
   - Create credentials (API Key)
   - Save your API key in a file named `api_key.txt` in the same directory as the script

## Usage

1. Open the script and set the `playlist_id` variable to the ID of the YouTube playlist you want to download. You can find the playlist ID in the URL of the playlist page (e.g., `PLHd5WXDxcD4C0jAxhtFCJoXbMIgG5EB27`).

2. Run the script:
   ```
   python youtube_playlist_downloader.py
   ```

3. The script will download all videos in the playlist, convert them to MP3, and save them in an `audio` directory.

## How it works

1. The script retrieves all video IDs from the specified playlist using the YouTube Data API.
2. For each video:
   - It downloads the best quality audio stream
   - Converts the audio to MP3 format
   - Embeds the video thumbnail into the MP3 file
   - Parses the video title to determine artist and song title
   - Sets the MP3 metadata (title, artist, album)
   - Sanitizes the filename to ensure compatibility
3. The script keeps track of downloaded videos to avoid duplicates in future runs.
4. Any failed downloads are logged in `failed_to_download.txt` for later review.

## Customization

- You can modify the `ydl_opts` dictionary in the `download_and_convert_to_mp3` function to change download options (e.g., audio quality, output template).
- Adjust the `sanitize_filename` function if you need different filename sanitization rules.
- Modify the `parse_title` function if you need a different logic for extracting artist and song title from video titles.

## Notes

- This script respects YouTube's terms of service and the copyrights of content creators. Ensure you have the right to download and use the content.
- Downloading copyrighted material without permission may be illegal in your country.

## Troubleshooting

- If you encounter any issues with downloading or API access, ensure your `api_key.txt` file contains a valid YouTube Data API key.
- For persistent download failures, check your internet connection and whether the videos are available in your region.
- If metadata tagging isn't working correctly, ensure you have the latest version of the `eyed3` library.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/Scezaquer/youtube-audio-downloader/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)