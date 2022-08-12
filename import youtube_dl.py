import youtube_dl
import eyed3
import requests
import logging
from pydub import AudioSegment
from os import remove
from re import split, finditer

def download_ytvid_as_mp3(vid_id):
    #Download video
    url = f"https://www.youtube.com/watch?v={vid_id}"
    video_info = youtube_dl.YoutubeDL().extract_info(url = url,download=False)
    ext = video_info["ext"]
    extensions = ["webm", "mp4", "m4a", "mp3"]
    if ext in extensions: extensions.remove(ext)
    extensions = [ext] + extensions

    for x in extensions:
        try:
            filename = f"audio/{video_info['title']}.{x}"
            options={
                'format':'bestaudio/best',
                'keepvideo':False,
                'outtmpl':filename,
                'ext':x,
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([video_info['webpage_url']])
            print("Download complete... {}".format(filename))

            #Turn file into mp3
            unformatted_audio = AudioSegment.from_file(filename, format=x)

            remove(filename)
            filename = f"audio/{video_info['title']}.mp3"
            unformatted_audio.export(filename, format="mp3")

            tag(filename, video_info)
            return

        except:
            print(f"Failed {x}")
            try: remove(f"audio/{video_info['title']}.{ext}")
            except: pass
    print("COULD NOT DOWNLOAD, MOVING TO NEXT")

def tag(filepath, video_info):
    """
    Tag an mp3 file with all the appropriate info, including downloaded album art.
    """
    audiofile = eyed3.load(filepath)

    title = video_info["title"]
    if "-" in title:
        title = split(" - | -|- |-", title, maxsplit=1)
        audiofile.tag.artist = title[0]
        audiofile.tag.title = title[1]
    
    else:
        audiofile.tag.artist = video_info["uploader"]
        audiofile.tag.title = video_info["title"]

    # Get album art image
    thumbnail_url = f"http://img.youtube.com/vi/{video_info['id']}/0.jpg"
    print(thumbnail_url)
    image_data = requests.get(thumbnail_url).content
    audiofile.tag.images.set(
        3,# 3 means 'front cover'
        image_data,
        "image/jpeg"
    )

    audiofile.tag.save()

def download_playlist(url, excluding=[], starting=None, until=None):
    """
    url : str (url of the playlist)
    excluding: list[str] (ids of video to exclude)
    starting: str (id of first video to download)
    until: str (id of the last video to download)
    
    Downloads an entire youtube playlist using the specified url, with possibility to exclude some
    and specify start/end
    """

    playlist_id = url[-34:]
    ids = []
    # Scraping and extracting the video
    # links from the given playlist url
    page = requests.get(url).text
    res = [(_.start(), _.end()) for _ in finditer(f'\"url\"\:\"\/watch\?v\=.................list\={playlist_id}', page)]
    for x in res:
        ids.append(page[x[0]+16:x[0]+27])
    
    #Youtube doesn't load every video at once so we need this to go through entire long playlists
    last_id = ""
    while last_id != ids[-1]:
        last_id = ids[-1]
        page = requests.get(f"https://www.youtube.com/watch?v={last_id}&list={playlist_id}").text
        res = [(_.start(), _.end()) for _ in finditer(f'\"url\"\:\"\/watch\?v\=.................list\={playlist_id}', page)]
        for x in res:
            if page[x[0]+16:x[0]+27] not in ids:
                ids.append(page[x[0]+16:x[0]+27])
    
    start = 0 if starting is None else ids.index(starting)
    end = len(ids) if until is None else ids.index(until)
    ids = ids[start:end]
    for x in excluding:
        ids.remove(x)
    print(ids, len(ids))

    for x in ids:
        download_ytvid_as_mp3(x)

url = "https://www.youtube.com/playlist?list=PLHd5WXDxcD4C0jAxhtFCJoXbMIgG5EB27"
download_playlist(url, ["T23AY5gYhpE"], "pK98oaV3bII", "-AFdwoyNT24")