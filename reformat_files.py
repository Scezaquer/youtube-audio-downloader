import eyed3
from pydub import AudioSegment
from os import listdir
from re import split
import traceback
import music_tag

def reformat(originfile, destinfile):
    catched_up = False
    for filename in listdir(originfile):
        if not catched_up and filename != "ARCHSPIRE_-_Bleed_the_Future_Off_(getmp3.pro).mp3":
            continue
        else:
            catched_up = True

        print(filename)

        fmat = filename.split(".")[-1]
        formats = ["mp4", "m4a", "mp3", "ogg", "wav"]
        if fmat in formats: formats.remove(fmat)
        formats = [fmat] + formats
        new_filename = f"{destinfile}/{filename.split('.')[0]}.mp3"

        skip = False

        for x in formats:
            try:
                unformatted_audio = AudioSegment.from_file(f"{originfile}/{filename}", format=x)
                unformatted_audio.export(new_filename, format="mp3")
                break
            except Exception:
                print(f"Failed {x}")
                #print(traceback.format_exc())
                if x == formats[-1]:
                    skip = True
        
        if skip:
            print("CRITICAL FAILURE, SKIPPING")
            with open(f"error.txt", "a") as file:
                file.write(filename + "\n")
            continue
        
        old_audiofile = music_tag.load_file(f"{originfile}/{filename}")
        new_audiofile = music_tag.load_file(new_filename)
        title = old_audiofile["title"].first

        if title == None:
            title = filename.split('.')[0]
        
        if "-" in title:
            title = split(" - | -|- |-", title, maxsplit=1)
            new_audiofile["artist"] = title[0]
            new_audiofile["title"] = title[1]
        else:
            new_audiofile["title"] = old_audiofile["title"]
            new_audiofile["artist"] = old_audiofile["artist"]
            print(f"{title} NEEDS MANUAL CHANGE")

        new_audiofile["album"] = old_audiofile["album"]
        try:
            new_audiofile["artwork"] = old_audiofile["artwork"]
        except KeyError:
            #print(traceback.format_exc())
            print("KeyError")

        new_audiofile.save()

def format_artists(directory):
    for filename in listdir(directory):
        audiofile = music_tag.load_file(f"{directory}/{filename}")
        audiofile["title"] = audiofile["title"].first.lower().title()
        audiofile.save()

#reformat("reformat", "reformatted")
format_artists("C:/A40 de Aurélien/Phone/Music")
