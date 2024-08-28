import youtube_dl
import eyed3
# from eyed3.id3.frames import ImageFrame
# from urllib import request
import requests
# import logging
from pydub import AudioSegment
from os import remove, mkdir, path  # , rename
from re import split, finditer
import traceback


def download_ytvid_as_mp3(vid_id):
    # Download video
    url = f"https://www.youtube.com/watch?v={vid_id}"
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(url=url,
                                                         download=False)
    except Exception:
        print(traceback.format_exc())
        return False
    # ext = video_info["ext"]
    extensions = ["m4a", "webm", "mp4", "mp3"]
    # if ext in extensions: extensions.remove(ext)
    # extensions = [ext] + extensions

    for x in extensions:
        try:
            song_name = "".join(c for c in video_info['title'] if c not in
                                ["'", "/", "\\", "|", '"', ".", "@", "$", "%",
                                 "&", ":", "*", "?", "<", ">", "|", "~", "`",
                                 "#", "^", "+", "=", "{", "}", "[", "]", ";",
                                 "!"])
            filename = f"audio/{song_name}.{x}"
            options = {
                'format': 'bestaudio/best',
                'keepvideo': False,
                'outtmpl': filename,
                'ext': x,
                'nopart': True,
                'fragment_retries': 10,
                'retries': 10,
                'age_limit': 18,
                'writethumbnail': False
            }
            try:
                with youtube_dl.YoutubeDL(options) as ydl:
                    ydl.download([video_info['webpage_url']])
            except: print(traceback.format_exc())

            print("Download complete... {}".format(filename))

            # Turn file into mp3
            unformatted_audio = AudioSegment.from_file(filename, format=x)

            remove(filename)
            filename = f"audio/{song_name}.mp3"
            unformatted_audio.export(filename, format="mp3")

            tag(filename, video_info, song_name)
            return True

        except:
            print(f"Failed {x}")
            remove(filename)
            print(traceback.format_exc())
    print("COULD NOT DOWNLOAD, MOVING TO NEXT")
    """with open("failed_to_download.txt", "a") as file:
        file.write(video_info['title'] + "\n")"""
    return False


def tag(filepath, video_info, song_name):
    """
    Tag an mp3 file with all the appropriate info, including downloaded album 
    art.
    """
    audiofile = eyed3.load(filepath)
    if (audiofile.tag is None):
        audiofile.initTag()

    title = video_info["title"]
    artist = ""
    if "-" in title:
        title = split(" - | -|- |-", title, maxsplit=1)
        artist = title[0]
        audiofile.tag.title = title[1]

    else:
        artist = video_info["uploader"]
        audiofile.tag.title = video_info["title"]

    if artist.endswith(" - Topic"):
        artist = artist[:-8]
    artist = artist.lower()
    artist = artist.title()

    audiofile.tag.artist = artist

    """# Get album art image
    thumbnail_url = f"http://img.youtube.com/vi/{video_info['id']}/0.jpg"
    print(thumbnail_url)
    \"""image_data = request.urlopen(thumbnail_url).read()
    type = ""
    for x in ['webp', 'jpg', 'png', 'jpeg']:
        try: 
            image_data = open(f'audio/{song_name}.{x}', 'rb').read()
            #remove(f'audio/{song_name}.{x}')
            break
        except: print(f"failed audio/{song_name}.{x}")\"""
    audiofile.tag.images.set(type_=3,
                             img_data=None,
                             mime_type=None,
                             description=u"cover",
                             mg_url=f"http://img.youtube.com/vi/{video_info['id']}/0.jpg")
    \"""audiofile.tag.images.set(
        3,# 3 means 'front cover'
        image_data,
        "image/jpeg",
        u"cover"
    )\"""
    """
    audiofile.tag.save()


def get_playlist_ids(url, playlist_id):
    ids = []
    # Scraping and extracting the video
    # links from the given playlist url
    page = requests.get(url).text
    res = [(_.start(), _.end()) for _ in 
           finditer(f'\"url\"\:\"\/watch\?v\=.................list\={playlist_id}', page)]
    for x in res:
        ids.append(page[x[0]+16:x[0]+27])

    # Youtube doesn't load every video at once so we need this to go through entire long playlists
    last_id = ""
    while last_id != ids[-1]:
        last_id = ids[-1]
        page = requests.get(f"https://www.youtube.com/watch?v={last_id}&list={playlist_id}").text
        res = [(_.start(), _.end()) for _ in finditer(f'\"url\"\:\"\/watch\?v\=.................list\={playlist_id}', page)]
        for x in res:
            if page[x[0]+16:x[0]+27] not in ids:
                ids.append(page[x[0]+16:x[0]+27])

    return ids


def download_playlist(playlist_id,
                      use_history=True,
                      excluding=[],
                      starting=None,
                      until=None):
    """
    url : str (url of the playlist)
    use_history : bool (If set to True, the function will only download
    everything it hasn't previously downloaded)
    excluding: list[str] (ids of video to exclude)
    starting: str (id of first video to download)
    until: str (id of the last video to download)

    Downloads an entire youtube playlist using the specified url, with
    possibility to exclude some and specify start/end
    """

    # Creates the necessary directories if they don't exist already
    if not path.exists("audio"):
        mkdir("audio")
    if not path.exists("download_memory"):
        mkdir("download_memory")
    if not path.exists("reformat"):
        mkdir("reformat")
    if not path.exists("reformatted"):
        mkdir("reformatted")

    url = "https://www.youtube.com/playlist?list=" + playlist_id

    ids = get_playlist_ids(url, playlist_id)

    start = 0 if starting is None else ids.index(starting)
    end = len(ids) if until is None else ids.index(until)
    ids = ids[start:end+1]
    for x in excluding:
        if x in ids:
            ids.remove(x)

    ids = set(ids)

    # Don't re-download previously downloaded songs
    history = {}
    try:
        with open(f"download_memory/{playlist_id}.txt", "r") as file:
            history = set(file.read().split("\n"))
    except FileNotFoundError:
        pass

    for x in history:
        if x in ids:
            ids.remove(x)
        # else: print(f"Here! {x}")

    print(f"Downloading {len(ids)} videos")

    for x in ids:
        d = download_ytvid_as_mp3(x)
        save_download(playlist_id, [x])
        print("\n")


def save_download(playlist_id, ids):
    with open(f"download_memory/{playlist_id}.txt", "a") as file:
        for x in ids:
            file.write(x + "\n")


def mark_playlist_as_downloaded(playlist_id):
    # Marks the entire playlist as having been already downloaded without
    # installing anything
    url = "https://www.youtube.com/playlist?list=" + playlist_id
    ids = get_playlist_ids(url, playlist_id)
    with open(f"download_memory/{playlist_id}.txt", "w") as file:
        for x in ids:
            file.write(x + "\n")


playlist_id = "PLHd5WXDxcD4C0jAxhtFCJoXbMIgG5EB27"
# mark_playlist_as_downloaded(playlist_id)
# download_playlist(url, use_history=True, excluding=["T23AY5gYhpE"],
# starting="WTKrJ-nEy40", until="-AFdwoyNT24")
download_playlist(playlist_id, use_history=False)
