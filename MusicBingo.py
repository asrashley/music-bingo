import codecs
import hashlib
import inspect
import datetime
import io
import json
import math
import os
import random
import re
import stat
import string
import subprocess
import sys
import threading
import traceback

from Tkinter import *
import tkMessageBox, Tkconstants, tkFileDialog
import ttk

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from pydub import AudioSegment

''''''
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

''''''

# These prime numbers are here to avoid having to generate a list of prime number on start-up/when required
primeNumbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277,1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871,1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161,2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473,2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999]

typeface = "Arial"

normalColour = "#343434"#f15725"
altColour = "#282828"#"#d83315"
bannerColour = "#222"

# This function converts the time in milliseconds to a MM:SS form
def convertTime(millis):
    x = millis / 1000

    seconds = int(x % 60)
    x /= 60
    minutes = x % 60

    seconds = int(seconds)

    if seconds < 10:
        seconds = "0"+str(seconds)
    else:
        seconds = str(seconds)

    return str(int(minutes)) + ":" + seconds

def combinations(total, select):
    """calculate combinations
    Calculates the number of combinations of selecting 'select' items
    from 'total' items
    """
    return math.factorial(total)/(math.factorial(select)*math.factorial(total-select))

# This class is used to generate 'Song' objects which are objects which possess a title,
# artist, songID (prime number), refID (for referring to the track in the list) and a filepath
# to the file
class Song(object):
    FEAT_RE = re.compile(r'[\[(](feat[.\w]*|ft\.?)[)\]]', re.IGNORECASE)
    DROP_RE = re.compile(r'\s*[\[(](clean|[\w\s]+ (edit|mix|remix)|edit|explicit|remastered[ \d]*|live|main title|mono|([\d\w"]+ single|album|single) version)[)\]]\s*', re.IGNORECASE)

    def __init__(self, title, artist, **kwargs):
        self.title = self.correctTitle(title.split('[')[0])
        self.artist = self.correctTitle(artist)
        self.songId = None
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
        #self.refId = refId
        #self.filepath = filepath
        #self.duration = duration

    def correctTitle(self, s):
        n = re.sub(self.DROP_RE, '', s)
        n = re.sub(self.FEAT_RE, 'ft.', n)
        return n

    def find(self, refId):
        if self.refId == refId:
            return self
        return None

    def marshall(self):
        rv = {}
        for k,v in self.__dict__.iteritems():
            if k == 'filepath' or k == 'refId':
                continue
            rv[k] = v
        return rv

    def __len__(self):
        return 1

    def __str__(self):
        return self.title + " - " + self.artist + " - ID=" + str(self.songId)

    def __key(self):
        return (self.title, self.artist, self.filepath, self.duration)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

class Directory(object):
    maxFileSize = 32 * 1024 * 1024
    cache_filename = 'songs.json'

    def __init__(self, refId, directory):
        if not os.path.isdir(directory):
            raise IOError('Directory {0} does not exist'.format(directory))
        self.refId = refId
        self.directory = directory
        self.songs = []
        self.subdirectories = []
        head, tail = os.path.split(directory)
        self.title = '[{0}]'.format(tail)
        self.artist=''
        folderList = os.listdir(directory)
        cache = {}
        print(directory)
        self.cache_hash = None
        try:
            cfn = os.path.join(self.directory, self.cache_filename)
            data = open(cfn, 'r').read()
            js = json.loads(data)
            sha = hashlib.sha256()
            sha.update(data)
            self.cache_hash = sha.hexdigest()
            for s in js:
                cache[s['filename']] = s
            del data
            del js
            del sha
        except IOError:
            pass
        for index, theFile in enumerate(folderList):
            absPath = os.path.join(directory, theFile)
            stats = os.stat(absPath)
            if stat.S_ISDIR(stats.st_mode):
                d = Directory(1000 * (self.refId + index), absPath)
                self.subdirectories.append(d)
            elif not stat.S_ISREG(stats.st_mode):
                continue
            if theFile.lower()[-4:] != ".mp3":
                continue
            if stats.st_size > self.maxFileSize:
                print('Skipping {file} as it is too large'.format(file=theFile))
                continue
            try:
                s = cache[theFile]
                s['filepath'] = os.path.join(directory, s['filename'])
                s['refId'] = self.refId + index + 1
                self.songs.append(Song(**s))
                continue
            except KeyError:
                pass
            try:
                #['albumartistsort', 'musicbrainz_albumstatus', 'lyricist', 'musicbrainz_workid', 'releasecountry', 'date', 'albumartist', 'musicbrainz_albumartistid', 'composer', 'catalognumber', 'encodedby', 'tracknumber', 'musicbrainz_albumid', 'album', 'asin', 'musicbrainz_artistid', 'mood', 'copyright', 'author', 'media', 'performer', 'length', 'acoustid_fingerprint', 'version', 'artistsort', 'titlesort', 'discsubtitle', 'website', 'musicip_fingerprint', 'conductor', 'musicbrainz_releasegroupid', 'compilation', 'barcode', 'performer:*', 'composersort', 'musicbrainz_discid', 'musicbrainz_albumtype', 'genre', 'isrc', 'discnumber', 'musicbrainz_trmid', 'acoustid_id', 'replaygain_*_gain', 'musicip_puid', 'originaldate', 'language', 'artist', 'title', 'bpm', 'musicbrainz_trackid', 'arranger', 'albumsort', 'replaygain_*_peak', 'organization', 'musicbrainz_releasetrackid']
                print(theFile)
                fn = io.BytesIO(open(absPath,'rb').read())
                mp3info = EasyID3(fn)
                artist = mp3info["artist"]
                title = mp3info["title"]
                if len(artist) == 0 or len(title) == 0:
                    print("File: " + theFile + " does not contain both title and artist info.")
                    continue
                metadata = {
                    "artist": artist[0],
                    "title": title[0],
                    "filepath": unicode(absPath),
                    "filename": unicode(theFile),
                }
                try:
                    metadata["album"] = unicode(mp3info["album"][0])
                except KeyError:
                    head, tail = os.path.split(directory)
                    metadata["album"] = tail if tail else head
                del mp3info
                fn.seek(0)
                seg = AudioSegment.from_mp3(fn)
                metadata["duration"] = len(seg) # in milliseconds
                del seg
                del fn
                # Need to use title[0] below as it returns a list not a string
                self.songs.append(Song(refId = self.refId + index + 1,  **metadata))
            except:
                print(sys.exc_info())
                print("Error inspecting file: " + theFile)
        if self.songs:
            self.save_cache()

    def find(self, refId):
        for s in self.songs:
            if s.refId == refId:
                return s
        for d in self.subdirectories:
            f = d.find(refId)
            if f is not None:
                return f
        return None

    def chooseRandomItem(self):
        d = self
        s = self
        while isinstance(s, Directory):
            d = s
            randomIndex = random.randint(0, len(d) - 1)
            s = d[randomIndex]
        return (d,s)

    def addToTreeView(self, view, parent=''):
        for d in self.subdirectories:
            item_id = view.insert(parent, 'end', str(d.refId), values=(d.title, ''), open=False)
            d.addToTreeView(view, item_id)
        for song in self.songs:
            view.insert(parent, 'end', str(song.refId), values=(song.title, song.artist))

    def totalLength(self):
        rv = len(self.songs)
        for s in self.subdirectories:
            rv += len(s)
        return rv

    def getSongs(self, id=None):
        rv = []
        for d in self.subdirectories:
            for s in d.getSongs(id):
                rv.append(s)
        for s in self.songs:
            if id is None or s.refId == id or self.refId == id:
                rv.append(s)
        return rv

    def sort(self, **kwargs):
        self.subdirectories.sort(**kwargs)
        for d in self.subdirectories:
            d.sort(**kwargs)
        self.songs.sort(**kwargs)

    def popById(self, refId):
        for s in self.songs:
            if s.refId == refId:
                self.songs.remove(s)
                return s
        for d in self.subdirectories:
            try:
                return d.popById(refId)
            except ValueError:
                pass
        raise ValueError("Song {0} not found".format(refId))

    def remove(self, song):
        try:
            self.songs.remove(song)
            return
        except ValueError:
            pass
        for d in self.subdirectories:
            try:
                d.remove(song)
                return
            except ValueError:
                pass
        raise ValueError("Song {0} not found".format(song.refId))

    def save_cache(self):
        songs = [s.marshall() for s in self.songs]
        js = json.dumps(songs, ensure_ascii=True)
        sha = hashlib.sha256()
        sha.update(js)
        if self.cache_hash != sha.hexdigest():
            cfn = os.path.join(self.directory, self.cache_filename)
            f = open(cfn, 'w')
            f.write(js)
            f.close()

    def __len__(self):
        return len(self.songs) + len(self.subdirectories)

    def __getitem__(self, index):
        subLen = len(self.subdirectories)
        if index < subLen:
            return self.subdirectories[index]
        return self.songs[index - subLen]

    def __repr__(self):
        return 'Directory({0}, {1}, {2})'.format(self.directory, str(self.subdirectories), str(self.songs))

# This class is used to generate 'BingoTicket' objects which are representations of a ticket with 15 songs.
class BingoTicket(object):
    NUM_SONGS = 15
    def __init__(self):
        self.cardId = 1
        self.cardTracks = []
        self.ticketNumber = None

# This class is used to generate 'Mp3Order' objects, these represent the order of the tracks within
# the final mp3. Currently, the majority of the variables are not used.
class Mp3Order(object):
    def __init__(self, items):
        self.items = items
        self.winPoint = None
        self.amountAtWinPoint = None
        self.amountAfterWinPoint = None
        self.winPoints = None

# This class is the GUI of the program and also contains all the functions used in generating
# the bingo tickets.
class MainApp(object):
    GAME_DIRECTORY = "./Bingo Games"
    GAME_PREFIX="Game-"
    GAME_TRACKS_FILENAME="gameTracks.json"

    TICKET_COLOURS = {
        "BLUE": {
            "boxNorColour":   HexColor(0xF0F8FF),
            "boxAltColour":   HexColor(0xDAEDFF),
            "boxTitleColour": HexColor(0xa4d7ff),
        },
        "RED": {
            "boxNorColour":   HexColor(0xFFF0F0),
            "boxAltColour":   HexColor(0xffdada),
            "boxTitleColour": HexColor(0xffa4a4),
        },
        "GREEN": {
            "boxNorColour":   HexColor(0xf0fff0),
            "boxAltColour":   HexColor(0xd9ffd9),
            "boxTitleColour": HexColor(0xa4ffa4),
        },
        "ORANGE": {
            "boxNorColour":   HexColor(0xfff7f0),
            "boxAltColour":   HexColor(0xffecd9),
            "boxTitleColour": HexColor(0xffd1a3),
        },
        "PURPLE": {
            "boxNorColour" :   HexColor(0xf8f0ff),
            "boxAltColour" :   HexColor(0xeed9ff),
            "boxTitleColour" : HexColor(0xd5a3ff),
        },
        "YELLOW": {
            "boxNorColour" :   HexColor(0xfffff0),
            "boxAltColour" :   HexColor(0xfeffd9),
            "boxTitleColour" : HexColor(0xfdffa3),
        },
        "GREY": {
            "boxNorColour" :   HexColor(0xf1f1f1),
            "boxAltColour" :   HexColor(0xd9d9d9),
            "boxTitleColour" : HexColor(0xbfbfbf),
        }
    }

    # Constructor to initialise the GUI and assign variable names etc.
    def __init__(self, master):
        self.appMaster = master
        self.resetProgram()
        self.generateBaseGameId()
        self.sortByTitle = True

        frame = Frame(master, bg=normalColour)
        frame.pack(side=TOP, fill=BOTH, expand=1)

        leftFrame = Frame(frame, bg=bannerColour)
        leftFrame.grid(row=0, column=0)

        midFrame = Frame(frame, bg=normalColour, padx=15)
        midFrame.grid(row=0, column=1)

        rightFrame = Frame(frame, bg=bannerColour)
        rightFrame.grid(row=0, column=2)

        self.allSongsLabelText = StringVar()
        allSongsLabel = Label(leftFrame, textvariable=self.allSongsLabelText, padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 16))
        allSongsLabel.grid(row=0, column=0)

        songListFrame = Frame(leftFrame)
        songListFrame.grid(row=1, column=0)

        columns = ('title', 'artist')

        songListScrollbar = Scrollbar(songListFrame)

        self.songListTree = ttk.Treeview(songListFrame,  columns=columns, height=20, yscrollcommand=songListScrollbar.set)
        self.songListTree.pack(side=LEFT)

        #self.songListTree['columns'] = ('title', 'artist')

        self.songListTree.column('#0', width=20, anchor='center')
        #self.songListTree.heading('#0', text='')
        self.songListTree.column('title', width=200, anchor='center')
        self.songListTree.heading('title', text='Title', command=self.sortListByTitle)
        self.songListTree.column('artist', width=200, anchor='center')
        self.songListTree.heading('artist', text='Artist', command=self.sortListByArtist)

        self.songsRemaining = "Songs Remaining = "

        self.songsRemainingLabel = Label(leftFrame, text=self.songsRemaining, padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 14))#, width=34)
        self.songsRemainingLabel.grid(row=3, column=0)

        self.songsInGame = "Songs In Game = "

        self.songsInGameLabel = Label(rightFrame, text=self.songsInGame, padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 14))#, width=34)
        self.songsInGameLabel.grid(row=3, column=0)

        self.addSongsToList()

        songListScrollbar.pack(side=LEFT, fill=Y)

        songListScrollbar.config(command=self.songListTree.yview)

        gameSongsLabel = Label(rightFrame, text="Songs In This Game:", padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 16))
        gameSongsLabel.grid(row=0, column=0)

        gameSongListFrame = Frame(rightFrame)
        gameSongListFrame.grid(row=1, column=0)

        gameSongListScrollbar = Scrollbar(gameSongListFrame)

        columns = ('title', 'artist')
        self.gameSongListTree = ttk.Treeview(gameSongListFrame,  columns=columns, show="headings", height=20, yscrollcommand=gameSongListScrollbar.set)
        self.gameSongListTree.pack(side=LEFT)

        self.gameSongListTree.column('title', width=200, anchor='center')
        self.gameSongListTree.heading('title', text='Title', command=self.sortGameListByTitle)
        self.gameSongListTree.column('artist', width=200, anchor='center')
        self.gameSongListTree.heading('artist', text='Artist', command=self.sortGameListByArtist)

        gameSongListScrollbar.pack(side=LEFT, fill=Y)
        gameSongListScrollbar.config(command=self.gameSongListTree.yview)

        self.selectSourceDirectoryButton = Button(midFrame, text="Select Directory", command=self.selectSourceDirectory, bg="#63ff5f")
        self.selectSourceDirectoryButton.grid(row=0 , column=0, pady=0)

        buttonGapPadding = Label(midFrame, height=2, bg=normalColour)
        buttonGapPadding.grid(row=1, column=0)

        self.addSongButton = Button(midFrame, text="Add Selected Songs", command=self.addToGame, bg="#63ff5f")
        self.addSongButton.grid(row=2, column=0, pady=10)

        self.addRandomSongsButton = Button(midFrame, text="Add 5 Random Songs", command=self.addRandomSongsToGame, bg="#18ff00")
        self.addRandomSongsButton.grid(row=3, column=0, pady=10)

        self.removeSongButton = Button(midFrame, text="Remove Selected Songs", command=self.removeFromGame, bg="#ff9090")
        self.removeSongButton.grid(row=4, column=0, pady=10)

        self.removeSongButton2 = Button(midFrame, text="Remove All Songs", command=self.removeAllFromGame, bg="#ff5151")
        self.removeSongButton2.grid(row=5, column=0, pady=10)

        self.previousGamesSize = Label(midFrame, font=(typeface, 16), text="Previous\ngames:\n0 songs", bg=altColour, fg="#FFF", padx=6)
        self.previousGamesSize.grid(row=6, column=0, pady=10)

        gameButtonFrame = Frame(frame, bg=altColour, pady=5)
        gameButtonFrame.grid(row=1, column=0, columnspan=3)

        colourLabel = Label(gameButtonFrame, font=(typeface, 16),
                            text="Ticket Colour:", bg=altColour, fg="#FFF",
                            padx=6)
        colourLabel.grid(row=0, column=1)
        self.colourBox_value = StringVar()
        self.colourBox = ttk.Combobox(gameButtonFrame,
                                      textvariable=self.colourBox_value,
                                      state='readonly', font=(typeface, 16),
                                      width=8, justify=CENTER)
        self.colourBox['values'] = ('BLUE', 'GREEN', 'RED', 'ORANGE', 'PURPLE', 'YELLOW', 'GREY')
        self.colourBox.current(0)
        self.colourBox.grid(row=0, column=2, sticky=E, padx=10)

        numberLabel = Label(gameButtonFrame, font=(typeface, 16), text="Game ID:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.grid(row=0, column=3, sticky=E, padx=10)

        self.gameNameEntry = Entry(gameButtonFrame, font=(typeface, 16), width=10, justify=CENTER)
        self.gameNameEntry.grid(row=0, column=4, sticky=W, padx=10)

        self.createGameId()

        #padding = Label(gameButtonFrame, width=6, bg=altColour, height=4)
        #padding.grid(row=0, column=5, sticky=E, padx=10)

        numberLabel = Label(gameButtonFrame, font=(typeface, 16), text="Number Of Tickets:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.grid(row=0, column=5, sticky=W, padx=10)

        self.ticketsNumberEntry = Entry(gameButtonFrame, font=(typeface, 16), width=5, justify=CENTER)
        self.ticketsNumberEntry.grid(row=0, column=6)
        self.ticketsNumberEntry.insert(0, "18")

        self.generateCardsButton = Button(gameButtonFrame, text="Generate Bingo Game", command=self.generateBingoGame, pady=0, font=(typeface, 18), bg="#00cc00")
        self.generateCardsButton.grid(row=0, column=7, padx=20)

        clipButtonFrame = Frame(gameButtonFrame, bg=altColour, pady=5)
        clipButtonFrame.grid(row=2, column=0, columnspan=8)

        self.selectClipDirectoryButton = Button(clipButtonFrame, text="Select destination", command=self.selectDestinationDirectory, bg="#63ff5f")
        self.selectClipDirectoryButton.grid(row=0 , column=0, pady=0)

        self.clipDestLabel = Label(clipButtonFrame, text=self.destinationDirectory, font=(typeface, 16), width=10, justify=CENTER)
        self.clipDestLabel.grid(row=0, column=1, padx=10)

        numberLabel = Label(clipButtonFrame, font=(typeface, 16), text="Start time:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.grid(row=0, column=2, sticky=W, padx=10)
        self.startTimeEntry = Entry(clipButtonFrame, font=(typeface, 16), width=5, justify=CENTER)
        self.startTimeEntry.grid(row=0, column=3)
        self.startTimeEntry.insert(0, "01:00")
        
        numberLabel = Label(clipButtonFrame, font=(typeface, 16), text="Duration:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.grid(row=0, column=4, sticky=W, padx=10)
        self.durationEntry = Entry(clipButtonFrame, font=(typeface, 16), width=5, justify=CENTER)
        self.durationEntry.grid(row=0, column=5)
        self.durationEntry.insert(0, "30")
        
        self.generateClipsButton = Button(clipButtonFrame, text="Generate clips", command=self.generateClips, pady=0, font=(typeface, 18), bg="#00cc00")
        self.generateClipsButton.grid(row=0, column=6, padx=20)

        self.bottomBanner = Label(gameButtonFrame, text="", bg=bannerColour, fg="#FFF", font=(typeface, 14))
        self.bottomBanner.grid(row=3, column=0, columnspan=6)
        self.progressVar = DoubleVar()
        self.progressbar = ttk.Progressbar(gameButtonFrame,
                                           orient=HORIZONTAL,
                                           mode="determinate",
                                           variable=self.progressVar,
                                           length=200,
                                           maximum=100.0)
        self.progressbar.grid(row=3, column=6, columnspan=2)

        self.updateCounts()
        self.sortListByTitle()
        self.gen_thread = None
        #gameButtonFrame.grid_remove();

    def createGameId(self):
        gameNumber = "1"
        directoryList = [x[0] for x in os.walk(self.GAME_DIRECTORY)]
        start = len(self.GAME_PREFIX)
        end = start + len(self.baseGameId)
        self.previousGameSongs = {}
        if len(directoryList) > 0:
            del directoryList[0]
            clashList = []
            for i in directoryList:
                base = os.path.basename(i)
                if base[start:end] == self.baseGameId:
                    self.loadPreviousGameTracks(i)
                    clashList.append(base[start:])
            if len(clashList) > 0:
                highestNumber = 0
                for i in clashList:
                    try:
                        number = int(i[len(self.baseGameId)+1:], 10)
                        if number > highestNumber:
                            highestNumber = number
                    except ValueError:
                        pass
                gameNumber = str(highestNumber + 1)
        self.gameId = self.baseGameId + "-" + gameNumber
        self.gameNameEntry.delete(0, len(self.gameNameEntry.get()))
        self.gameNameEntry.insert(0, self.gameId)
        numPrevSongs = len(self.previousGameSongs)
        p = '' if numPrevSongs==1 else 's'
        t = "Previous\nGames:\n{:d} song{:s}".format(numPrevSongs, p)
        self.previousGamesSize.config(text=t)

    def loadPreviousGameTracks(self, dirname):
        try:
            filename = os.path.join(dirname, self.GAME_TRACKS_FILENAME)
            f = open(filename, 'r')
            js = json.load(f)
            for song in js:
                song['filepath'] = os.path.join(dirname, song['filename'])
                s = Song(**song)
                self.previousGameSongs[hash(s)] = filename
        except IOError:
            pass
        
    def timecode(self, ms):
        secs = ms // 1000
        mins = secs // 60
        secs = secs % 60
        ms = (ms // 10) % 100
        return '{:d}:{:02d}.{:02d}'.format(mins, secs, ms)
        
    # This function is called after any addition or removal of songs to/from
    # the lists - it updates the counts at the bottom of each list
    def updateCounts(self):
        self.songsRemainingLabel.config(text='{0}{1:d}'.format(self.songsRemaining, self.songList.totalLength()))
        if len(self.gameSongList) < 30:
            boxColour = "#ff0000"
        elif len(self.gameSongList) < 45:
            boxColour = "#fffa20"
        else:
            boxColour = "#00c009"
        duration = sum([s.duration for s in self.gameSongList])
        txt = '{}{:d} ({:s})'.format(self.songsInGame, len(self.gameSongList), self.timecode(duration))
        self.songsInGameLabel.config(text=txt, fg=boxColour)

    # This function generates the first 3 values of a game ID based on the current date
    def generateBaseGameId(self):
        self.baseGameId = datetime.date.today()
        self.baseGameId = str(self.baseGameId)[2:]

    # This function resets the program back to its default state - with the left list populated
    # with all available songs, and nothing in the current game list
    def resetProgram(self):
        self.nextRefId = 0
        self.usedCardIds = []
        self.clipDirectory = './Clips'
        self.destinationDirectory = './NewClips'
        if len(sys.argv) > 1:
            self.clipDirectory = sys.argv[1]
        self.previousGameSongs = {}
        self.populateSongList()
        self.gameSongList = []

    def selectSourceDirectory(self):
        self.clipDirectory = tkFileDialog.askdirectory()
        self.removeSongsFromList()
        self.populateSongList()
        self.addSongsToList()
        self.updateCounts()

    def selectDestinationDirectory(self):
        self.destinationDirectory = tkFileDialog.askdirectory()
        self.clipDestLabel.config(text=self.destinationDirectory)

    # This function adds the selected song from the list to the game
    def addToGame(self):
        selections = list(self.songListTree.selection())
        focusElement = self.songListTree.focus()
        if not selections and not focusElement:
            return
        try:
            if not selections:
                selections = [focusElement]
            ids = set()
            for id in selections:
                for s in self.songList.getSongs(int(id)):
                    ids.add(str(s.refId))
            selections = ids # list(ids)
            #selections.sort()
            #print(selections)
            self.removeSongsFromGameList()
            for refId in selections:
                song = self.songList.find(int(refId))
                if song is None:
                    print("Song {0} Not Found.".format(refId))
                    continue
                self.gameSongList.append(song)
                #self.songList.remove(song)
                self.songListTree.delete(refId)
            self.addSongsToGameList()
        except:
            print(sys.exc_info())
            print("Couldn't Add To Game List For Unknown Reason.")
        self.updateCounts()

    # This function adds a random 5 (if available) songs to the game list
    def addRandomSongsToGame(self):
        songList = self.songList
        selections = list(self.songListTree.selection())
        if not selections:
            selections = self.songListTree.get_children()
        ids = set()
        for id in selections:
            for s in self.songList.getSongs(int(id)):
                if not self.previousGameSongs.has_key(hash(s)):
                    ids.add(str(s.refId))
        for s in self.gameSongList:
            try:
                ids.remove(str(s.refId))
            except KeyError:
                pass
        selections = list(ids)
        #selections.sort()
        #print(selections)
        maxCount = min(len(selections), 5)
        self.removeSongsFromGameList()
        try:
            for i in range(0, maxCount):
                randomIndex = random.randint(0, len(selections) - 1)
                refId = selections.pop(randomIndex)
                song = self.songList.find(int(refId))
                self.gameSongList.append(song)
                self.songListTree.delete(str(song.refId))
        except:
            print(sys.exc_info())
            print("Couldn't Add To Game List For Unknown Reason.")
        self.addSongsToGameList()
        self.updateCounts()

    # This function removes the selected song from the game and returns it to the main list
    def removeFromGame(self):
        selections = list(self.gameSongListTree.selection())
        focusElement = self.gameSongListTree.focus()
        if not selections and not focusElement:
            return
        if not selections:
            selections = [focusElement]
        try:
            self.removeSongsFromList()
            for refId in selections:
                song = self.songList.find(int(refId))
                if song is None:
                    print("Song {0} not found.".format(refId))
                    continue
                self.gameSongList.remove(song)
                self.gameSongListTree.delete(str(song.refId))
            self.addSongsToList()
        except:
            print(sys.exc_info())
            print("Couldn't Add To Game List For Unknown Reason.")
        self.updateCounts()

    # This function removes all of the songs from the game
    def removeAllFromGame(self):
        answer = 'yes'
        if len(self.gameSongList) > 1:
            questionMessage = "Are you sure you want to remove all "+str(len(self.gameSongList))+" songs from the game?"
            answer = tkMessageBox.askquestion("Are you sure?", questionMessage)
        if answer == 'yes':
            self.removeSongsFromGameList()
            self.removeSongsFromList()
            self.gameSongList = []
            self.addSongsToList()
            if self.sortByTitle:
                self.sortBothTitles()
            else:
                self.sortBothArtists()   
        self.updateCounts()     

    # This function takes the program's representation of the list of songs and adds them
    # all to the GUI list
    def addSongsToList(self):
        head, tail = os.path.split(self.clipDirectory)
        self.allSongsLabelText.set("Available Songs: {0}".format(tail))
        self.songList.addToTreeView(self.songListTree)
        for s in self.gameSongList:
            self.songListTree.delete(str(s.refId))

    # This function takes the program's representation of the list of songs and removes them
    # all from the GUI list
    def removeSongsFromList(self):
        children = self.songListTree.get_children()
        if children:
            self.songListTree.delete(*children)

    # This function takes the program's representation of the list of game songs and adds them
    # all to the game GUI list
    def addSongsToGameList(self):
        for song in self.gameSongList:
            self.gameSongListTree.insert('', 'end', str(song.refId), values=(song.title, song.artist))
        self.updateCounts()

    # This function takes the program's representation of the list of game songs and removes them
    # all from the game GUI list
    def removeSongsFromGameList(self):
        children = self.gameSongListTree.get_children()
        if children:
            self.gameSongListTree.delete(*children)
        self.updateCounts()

    # This function sorts the song list by artist and updates the GUI song list
    def sortListByArtist(self):
        self.removeSongsFromList()

        self.songList.sort(key=lambda x: x.artist, reverse=False)

        self.addSongsToList()

    # This function sorts the song list by title and updates the GUI song list
    def sortListByTitle(self):
        self.removeSongsFromList()

        self.songList.sort(key=lambda x: x.title, reverse=False)

        self.addSongsToList()

    # This function sorts the game song list by artist and updates the GUI song list
    def sortGameListByArtist(self):
        self.removeSongsFromGameList()

        self.gameSongList.sort(key=lambda x: x.artist, reverse=False)

        self.addSongsToGameList()

    # This function sorts the game song list by title and updates the GUI song list
    def sortGameListByTitle(self):
        self.removeSongsFromGameList()

        self.gameSongList.sort(key=lambda x: x.title, reverse=False)

        self.addSongsToGameList()

    # This function sorts both the song list and game song list by artist and updates the GUI
    def sortBothArtists(self):
        self.sortByTitle = False
        self.sortListByArtist()
        self.sortGameListByArtist()

    # This function sorts both the song list and game song list by title and updates the GUI
    def sortBothTitles(self):
        self.sortByTitle = True
        self.sortListByTitle()
        self.sortGameListByTitle()

    # This function retrieves a list of songs from the Clips folder, gets the Title/Artist data
    # and adds them to the song list
    def populateSongList(self):
        self.songList = Directory(1, self.clipDirectory)

    # This function is called on the creation of a game and assigns prime numbers to all of the songs
    # in the game for the generation of the tickets.
    def assignSongIds(self, gameList):
        nextPrimeIndex = 0
        for i in gameList:
            i.songId = primeNumbers[nextPrimeIndex]
            nextPrimeIndex = nextPrimeIndex + 1
            if nextPrimeIndex >= len(primeNumbers):
                print("Exceeded the {0} song limit.", len(primeNumbers))
                return False
        return True

    # This function generates a bingo ticket ensuring that it is unique
    def generateCard(self, songList, card, numberOfTracks):
        validCard = False
        pickedIndices = []
        while validCard == False:
            indexValid = False
            randomIndex = 0
            while indexValid == False:
                randomIndex = random.randint(0, len(songList)-1)
                indexValid = True
                for i in pickedIndices:
                    if randomIndex == i:
                        indexValid = False
            card.cardTracks.append(songList[randomIndex])
            card.cardId = card.cardId * songList[randomIndex].songId
            pickedIndices.append(randomIndex)
            if (len(card.cardTracks) == numberOfTracks):
                validCard = True
                for i in self.usedCardIds:
                    if i == card.cardId:
                        validCard = False
                        pickedIndices = []
                        card.cardTracks = []
                        card.cardId = 1
                        break
                if validCard == True:
                    self.usedCardIds.append(card.cardId)

    # This function generates a bingo ticket which is placed in the PDF
    def makeTableCard(self, elements, card):
        I = Image('./Extra-Files/logo_banner.jpg')
        I.drawHeight = 6.2*inch*I.drawHeight / I.drawWidth
        I.drawWidth = 6.2*inch

        s = Spacer(width=0, height=0.1*inch) 

        elements.append(I)
        elements.append(s)

        p = ParagraphStyle('test')
        p.textColor = 'black'
        p.alignment = TA_CENTER
        p.fontSize = 12
        p.leading = 12

        pGap = ParagraphStyle('test')
        pGap.textColor = 'black'
        pGap.alignment = TA_CENTER
        pGap.fontSize = 4
        pGap.leading = 4

        row1 = []

        for i in range(0,5):
            Ptitle = Paragraph(card.cardTracks[i].title, p)
            Pgap = Paragraph('', pGap)
            Partist = Paragraph('<b>' + card.cardTracks[i].artist + '</b>',p)

            row1.append([Ptitle, Pgap, Partist])

        row2 = []

        for i in range(5,10):
            Ptitle = Paragraph(card.cardTracks[i].title,p)
            Pgap = Paragraph('', pGap)
            Partist = Paragraph('<b>' + card.cardTracks[i].artist + '</b>',p)
            row2.append([Ptitle, Pgap, Partist])

        row3 = []

        for i in range(10,15):
            Ptitle = Paragraph(card.cardTracks[i].title,p)
            Pgap = Paragraph('', pGap)
            Partist = Paragraph('<b>' + card.cardTracks[i].artist + '</b>',p)
            row3.append([Ptitle, Pgap, Partist])

        data = [row1, row2, row3]
        columnWidth = 1.54*inch
        rowHeight = 1.0*inch

        t=Table(data, colWidths=(columnWidth, columnWidth, columnWidth, columnWidth, columnWidth),
                rowHeights=(rowHeight, rowHeight, rowHeight),
          style=[('BOX',(0,0),(-1,-1),2,colors.black),
                 ('GRID',(0,0),(-1,-1),0.5,colors.black),
                 ('VALIGN',(0,0),(-1,-1),'CENTER'),
                 ('BACKGROUND', (1, 0), (1, 0), self.boxNorColour),
                 ('BACKGROUND', (3, 0), (3, 0), self.boxNorColour),
                 ('BACKGROUND', (0, 1), (0, 1), self.boxNorColour),
                 ('BACKGROUND', (2, 1), (2, 1), self.boxNorColour),
                 ('BACKGROUND', (4, 1), (4, 1), self.boxNorColour),
                 ('BACKGROUND', (1, 2), (1, 2), self.boxNorColour),
                 ('BACKGROUND', (3, 2), (3, 2), self.boxNorColour),
                 ('PADDINGTOP', (0, 0), (-1, -1), 0),
                 ('PADDINGLEFT', (0, 0), (-1, -1), 0),
                 ('PADDINGRIGHT', (0, 0), (-1, -1), 0),
                 ('PADDINGBOTTOM', (0, 0), (-1, -1), 0),


                 ('BACKGROUND', (0, 0), (0, 0), self.boxAltColour),
                 ('BACKGROUND', (2, 0), (2, 0), self.boxAltColour),
                 ('BACKGROUND', (4, 0), (4, 0), self.boxAltColour),
                 ('BACKGROUND', (1, 1), (1, 1), self.boxAltColour),
                 ('BACKGROUND', (3, 1), (3, 1), self.boxAltColour),
                 ('BACKGROUND', (0, 2), (0, 2), self.boxAltColour),
                 ('BACKGROUND', (2, 2), (2, 2), self.boxAltColour),
                 ('BACKGROUND', (4, 2), (4, 2), self.boxAltColour),
        ])
         
        elements.append(t)

    # This function generates a PDF version of the track order in the game
    def generateTrackListing(self, trackOrder):
        doc = SimpleDocTemplate(self.directory+"/"+self.gameId+" Track Listing.pdf", pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements = []
        I = Image('./Extra-Files/logo_banner.jpg')
        I.drawHeight = 6.2*inch*I.drawHeight / I.drawWidth
        I.drawWidth = 6.2*inch

        elements.append(I)

        s = Spacer(width=0, height=0.05*inch)
        elements.append(s)

        pTitle = ParagraphStyle('test')
        pTitle.textColor = 'black'
        pTitle.alignment = TA_CENTER
        pTitle.fontSize = 18
        pTitle.leading = 18

        title = Paragraph('Track Listing For Game Number: <b>' + self.gameId + '</b>', pTitle)
        elements.append(title)

        p = ParagraphStyle('test')
        p.textColor = 'black'
        p.alignment = TA_CENTER
        p.fontSize = 10
        p.leading = 10

        s = Spacer(width=0, height=0.15*inch)
        elements.append(s)

        data = []

        orderPara = Paragraph('<b>Order</b>',p)
        titlePara = Paragraph('<b>Title</b>',p)
        artistPara = Paragraph('<b>Artist</b>',p)
        startPara = Paragraph('<b>Start Time</b>',p)
        gonePara = Paragraph('',p)

        data.append([orderPara,titlePara, artistPara, startPara, gonePara])

        #lines = orderString.split("\n")
        #lines = lines [0:len(lines)-1]

        #for i in lines:
        for index, song in enumerate(trackOrder):
            #line = i.split("/-/")
            orderNo = Paragraph('<b>' + str(index+1) + '</b>',p)
            titleField = Paragraph(song.title, p)
            artistField = Paragraph(song.artist, p)
            startField = Paragraph(song.startTime, p)
            endBox = Paragraph('',p)
            data.append([orderNo,titleField,artistField,startField,endBox])

        t=Table(data,
          style=[('BOX',(0,0),(-1,-1),1,colors.black),
                 ('GRID',(0,0),(-1,-1),0.5,colors.black),
                 ('VALIGN',(0,0),(-1,-1),'CENTER'),
                 ('BACKGROUND', (0, 0), (4, 0), self.boxTitleColour),
        ])

        t._argW[0] = 0.55*inch
        t._argW[1] = 3.1*inch
        t._argW[2] = 3.1*inch

        t._argW[3]=0.85*inch
        t._argW[4]=0.3*inch
         
        elements.append(t)

        doc.build(elements)

    def generateCardResults(self, tracks):
        doc = SimpleDocTemplate(self.directory+"/"+self.gameId+" Ticket Results.pdf", pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements = []
        I = Image('./Extra-Files/logo_banner.jpg')
        I.drawHeight = 6.2*inch*I.drawHeight / I.drawWidth
        I.drawWidth = 6.2*inch

        elements.append(I)

        s = Spacer(width=0, height=0.05*inch)
        elements.append(s)

        pTitle = ParagraphStyle('test')
        pTitle.textColor = 'black'
        pTitle.alignment = TA_CENTER
        pTitle.fontSize = 18
        pTitle.leading = 18

        title = Paragraph('Results For Game Number: <b>' + self.gameId + '</b>', pTitle)
        elements.append(title)

        p = ParagraphStyle('test')
        p.textColor = 'black'
        p.alignment = TA_CENTER
        p.fontSize = 10
        p.leading = 10

        s = Spacer(width=0, height=0.15*inch)
        elements.append(s)

        data = []

        numberPara = Paragraph('<b>Ticket Number</b>',p)
        winPara = Paragraph('<b>Wins after track</b>',p)
        gonePara = Paragraph('<b>Start Time</b>',p)
        data.append([numberPara, winPara, gonePara])
        #self.gameSongList
        cards = [c for c in self.cardList]
        cards.sort(key=lambda x: x.ticketNumber, reverse=False)
        for card in cards:
            theWinPoint = self.getWinPoint(self.songOrder, card)
            song = tracks[theWinPoint-1]
            ticketNumber = Paragraph('' + str(card.ticketNumber), p)
            theWinPoint = u'Track {0:d} - {1} ({2})'.format(theWinPoint, song.title, song.artist)
            win = Paragraph('' + theWinPoint, p)

            endBox = Paragraph(song.startTime, p)
            data.append([ticketNumber,win,endBox])

        t=Table(data,
          style=[('BOX',(0,0),(-1,-1),1,colors.black),
                 ('GRID',(0,0),(-1,-1),0.5,colors.black),
                 ('VALIGN',(0,0),(-1,-1),'CENTER'),
                 ('BACKGROUND', (0, 0), (4, 0), self.boxTitleColour),
        ])
        t._argW[0] = 0.75 * inch
        t._argW[1] = 5.5  * inch
        t._argW[2] = 0.8  * inch
        elements.append(t)

        doc.build(elements)

    # This function generates an 'amount' number of bingo tickets that will win
    # at the specified amount from the end
    def generateAtPoint(self, amount, fromEnd):

        count = 0

        newCard = None

        while count < amount:

            newCard = BingoTicket()

            self.generateCard(self.gameSongList, newCard, 15) # 15 per card

            theWinPoint = self.getWinPoint(self.songOrder, newCard)

            if theWinPoint != len(self.songOrder.items) - fromEnd:
                self.usedCardIds.remove(newCard.cardId)
            else:
                self.cardList.append(newCard)
                count = count + 1

    # This function generates one bingo ticket the specified amount from the end
    def generateOneAtPoint(self, fromEnd):

        newCard = None

        amount = 1

        count = 0

        while count < amount:

            newCard = BingoTicket()

            self.generateCard(self.gameSongList, newCard, 15) # 15 per card

            theWinPoint = self.getWinPoint(self.songOrder, newCard)

            if theWinPoint != len(self.songOrder.items) - fromEnd:
                self.usedCardIds.remove(newCard.cardId)
            else:
                count = count + 1

        return newCard

    # This function generates all the bingo tickets in the game
    def generateAllCards(self):
        self.progress['text'] = 'Calculating cards'
        self.progress['pct'] = 0.0
        self.progress['phase'] = (2,3)
        self.usedCardIds = [] # Could assign this from file (for printing more)
        numberOfCards = self.numberOfCards
        self.cardList = []
        tracksOnTickets = ""
        decayRate = 0.65
        numberOnLastSong = numberOfCards * decayRate
        numberOnSecondLast = (numberOfCards-numberOnLastSong) * decayRate
        numberOnThirdLast = (numberOfCards-numberOnLastSong-numberOnSecondLast) * decayRate
        numberOnFourthLast = (numberOfCards-numberOnLastSong-numberOnSecondLast-numberOnThirdLast) * decayRate
        numberOnLastSong = int(numberOnLastSong)
        numberOnSecondLast = int(numberOnSecondLast)
        numberOnThirdLast = int(numberOnThirdLast)
        numberOnFourthLast = int(numberOnFourthLast)
        if numberOnFourthLast == 0:
            numberOnFourthLast = 1
        amountLeft = numberOfCards - numberOnLastSong - numberOnSecondLast - numberOnThirdLast - numberOnFourthLast
        amountToGo = 4
        offset = 4
        if numberOnFourthLast == 1 or numberOnFourthLast == 0:
            offset = 3
            numberOnFourthLast = 0
            numberOnLastSong = numberOnLastSong + 1
        if amountLeft < amountToGo or amountLeft > amountToGo:
            numberOnLastSong = numberOnLastSong - (amountToGo-amountLeft)
        self.generateAtPoint(numberOnLastSong, 0)
        if numberOnSecondLast != 0:
            increment = (len(self.cardList) + numberOnSecondLast) / numberOnSecondLast
            startPoint = 0
            for i in range(0, numberOnSecondLast):
                randomPoint = random.randrange(int(math.ceil(startPoint)), int(math.ceil(startPoint+increment)), 1)
                if randomPoint >= numberOnLastSong + numberOnSecondLast:
                    randomPoint = numberOnLastSong + numberOnSecondLast - 1
                self.cardList.insert(randomPoint, self.generateOneAtPoint(1))
                startPoint = startPoint + increment
        if numberOnThirdLast != 0:
            increment = (len(self.cardList) + numberOnThirdLast) / numberOnThirdLast
            startPoint = 0
            for i in range(0, numberOnThirdLast):
                randomPoint = random.randrange(int(math.ceil(startPoint)), int(math.ceil(startPoint+increment)), 1)
                if randomPoint >= numberOnLastSong + numberOnThirdLast:
                    randomPoint = numberOnLastSong + numberOnThirdLast - 1
                self.cardList.insert(randomPoint, self.generateOneAtPoint(2))
                startPoint = startPoint + increment
        if numberOnFourthLast != 0:
            increment = (len(self.cardList) + numberOnFourthLast) / numberOnFourthLast
            startPoint = 0
            for i in range(0, numberOnFourthLast):
                randomPoint = random.randrange(int(math.ceil(startPoint)), int(math.ceil(startPoint+increment)), 1)
                if randomPoint >= numberOnLastSong + numberOnFourthLast:
                    randomPoint = numberOnLastSong + numberOnFourthLast - 1
                self.cardList.insert(randomPoint, self.generateOneAtPoint(3))
                startPoint = startPoint + increment
        goodCards = []
        for i in range(0, amountToGo):
            self.progress['pct'] = 100.0 * (float(i) / float(amountToGo))
            newCard = self.generateOneAtPoint(offset)
            goodCards.append(newCard)
            offset = offset + 1
        increment = numberOfCards / amountToGo
        startPoint = 0
        random.shuffle(goodCards)
        for i in goodCards:
            randomPoint = random.randrange(int(math.ceil(startPoint)), int(math.ceil(startPoint+increment)), 1)
            if randomPoint >= numberOfCards:
                randomPoint = numberOfCards - 1
            self.cardList.insert(randomPoint, i)
            startPoint = startPoint+increment
        ticketNumber = 1
        for i in self.cardList:
            i.ticketNumber = ticketNumber
            tracksOnTickets = tracksOnTickets + str(i.ticketNumber) + "/" + str(i.cardId) + "\n"
            ticketNumber = ticketNumber + 1
        self.pageOrder = True
        if self.pageOrder:
            noc3c = int(math.ceil(numberOfCards/3))
            noc3f = int(math.floor(numberOfCards/3))
            firstThird = self.cardList[0:noc3c]
            secondThird = self.cardList[noc3c: noc3c + noc3f]
            thirdThird = self.cardList[noc3c+noc3f : len(self.cardList)]
            self.cardList = []
            while len(firstThird) > 0:
                self.cardList.append(firstThird[0])
                del firstThird[0]
                if len(secondThird) > 0:
                    self.cardList.append(secondThird[0])
                    del secondThird[0]
                if len(thirdThird) > 0:
                    self.cardList.append(thirdThird[0])
                    del thirdThird[0]
        doc = SimpleDocTemplate(self.directory + "/" + self.gameId + " Bingo Tickets - (" + str(numberOfCards) + " Tickets).pdf", pagesize=A4)
        doc.topMargin = 0
        doc.bottomMargin = 0
        # container for the 'Flowable' objects
        elements = []
        page = 1
        numCards = len(self.cardList)
        for count, card in enumerate(self.cardList, start=1):
            self.progress['text'] = 'Card {index}/{numCards}'.format(index=count, numCards=numCards)
            self.progress['pct'] = 100.0 * float(count) / float(numCards)
            self.makeTableCard(elements, card)
            p = ParagraphStyle('test')
            p.textColor = 'black'
            p.alignment = TA_RIGHT
            p.fontSize = 12
            p.leading = 12
            idNumberPara = Paragraph(self.gameId+" / T"+str(card.ticketNumber) + " / P"+str(page), p)
            if count % 3 != 0:
                s = Spacer(width=0, height=0.01*inch)
                elements.append(s)
                elements.append(idNumberPara)
                s = Spacer(width=0, height=0.06*inch)
                elements.append(s)
                data = [[""]]
                columnWidth = 10.0*inch
                rowHeight = 0.00*inch
                t=Table(data, colWidths=(columnWidth),
                        rowHeights=(rowHeight),
                  style=[("LINEBELOW", (0,0), (-1,-1), 1, colors.black)])
                elements.append(t)
                s = Spacer(width=0, height=0.08*inch) 
                elements.append(s)
            else:
                s = Spacer(width=0, height=0.01*inch)
                elements.append(s)
                elements.append(idNumberPara)
                elements.append(PageBreak())
                page = page + 1
            count = count + 1

        # write the document to disk
        doc.build(elements)
        f = open(self.directory + "/ticketTracks", 'w')
        f.write(tracksOnTickets)
        f.close()

    # This function generates a random order of tracks for the game
    def getTrackOrder(self):

        newList = []

        listCopy = []

        for i in self.gameSongList:
            listCopy.append(i)

        while len(listCopy) > 0:

            randomIndex = random.randint(0, len(listCopy)-1)

            newList.append(listCopy[randomIndex])

            del listCopy[randomIndex]

        return newList

    # This function gets the point at which the given ticket will win, given the specified order
    def getWinPoint(self, order, ticket):
        lastSong = -1
        count = 1
        tracksCopy = []
        for i in ticket.cardTracks:
            tracksCopy.append(i)

        for i in order.items:
            if i in tracksCopy:
                lastSong = count
                tracksCopy.remove(i)

            count = count + 1

            if len(tracksCopy) == 0:
                break

        return lastSong

    def clean(self, s):
        return unicode(s).encode('ascii', 'ignore')

    # This function generate the mp3 for the game with the generated order of tracks
    def generateMp3(self):

        self.progress["phase"] = (1,3)
        bestCandidate = Mp3Order(self.getTrackOrder())
        self.songOrder = bestCandidate
        extra_files = os.path.join(os.getcwd(), 'Extra-Files')
        transition = AudioSegment.from_mp3(os.path.join(extra_files, 'TRANSITION.mp3'))
        transition = transition.normalize(headroom=0)
        combinedTrack = AudioSegment.from_mp3(os.path.join(extra_files, 'START.mp3'))
        combinedTrack = combinedTrack.normalize(headroom=0)
        trackOrder = []
        gameTracks = []
        numTracks = len(bestCandidate.items)
        for index, track in enumerate(bestCandidate.items, start=1):
            if index==1:
                trackLength = combinedTrack.__len__()
            else:
                trackLength = combinedTrack.__len__() + transition.__len__()
            nextTrack = AudioSegment.from_mp3(track.filepath)
            nextTrack = nextTrack.normalize(headroom=0)
            if index==1:
                combinedTrack = combinedTrack + nextTrack
            else:
                combinedTrack = combinedTrack + transition + nextTrack
            #orderString.append("{count:d}/-/{title}/-/{artist}/-/{length}".format(count=index, title=clean(track.title), artist=clean(track.artist), length=convertTime(trackLength)))
            s = Song(track.title, track.artist, refId=index, filepath=track.filepath)
            s.startTime = convertTime(trackLength)
            trackOrder.append(s)
            gt = track.marshall()
            gt["count"] = index
            #gt = dict(count=index, songId=track.songId, title=clean(track.title), artist=clean(track.artist), filepath=track.filepath)
            try:
                gt['album'] = track.album
            except AttributeError:
                pass
            gameTracks.append(gt)
            self.progress['text'] = 'Adding track {index}/{numTracks}'.format(index=index, numTracks=numTracks)
            self.progress['pct'] = 100.0 * float(index) / float(numTracks)

        f = open(os.path.join(self.directory, self.GAME_TRACKS_FILENAME), 'w')
        json.dump(gameTracks, f, sort_keys=True, indent=2)
        f.close()
        trackName = os.path.join(self.directory, self.gameId + " Game Audio.mp3")
        self.progress['text'] = 'Exporting MP3'
        combinedTrack.export(trackName, format="mp3", bitrate="192k")
        self.progress['text'] = 'MP3 Generated, creating track listing PDF'
        self.progress['pct'] = 100.0
        #self.generateTrackListing('\n'.join(orderString))
        self.generateTrackListing(trackOrder)
        self.progress['text'] = 'MP3 and Track listing PDF generated'
        return trackOrder

    # This function is called on pressing the generate game button to generate tickets and mp3
    def generateBingoGame(self):
        self.numberOfCards = self.ticketsNumberEntry.get()
        self.numberOfCards = int(self.numberOfCards.strip())
        numberOfCards = self.numberOfCards
        extra = ""
        min_cards = 15
        max_cards = combinations(len(self.gameSongList), BingoTicket.NUM_SONGS)
        min_songs = 17 # 17 songs allows 136 combinations

        if len(self.gameSongList) < 45:
            extra = " (at least 45 songs is recommended)"

        if numberOfCards > max_cards:
            self.bottomBanner.config(text='{songLen} only allows {max_cards} cards to be generated)'.format(songLen=len(self.gameSongList, max_cards=max_cards)))
            return

        if len(self.gameSongList) < min_songs or numberOfCards < min_cards or numberOfCards > max_cards:
            self.bottomBanner.config(text="You must select at least {min_songs} songs (at least 45 is better) and between {min_cards} and {max_cards} tickets for a bingo game to be generated.".format(min_songs=min_songs, min_cards=min_cards, max_cards=max_cards), fg="#F11")
            return
        answer = 'yes'
        
        questionMessage = "Are you sure you want to generate a bingo game with " + str(numberOfCards) + " tickets and the "+str(len(self.gameSongList))+" songs in the white box on the right? "+extra+"\n(The process will take a few minutes.)"
        answer = tkMessageBox.askquestion("Are you sure?", questionMessage)

        if answer != 'yes':
            return
        self.generateCardsButton.config(state=DISABLED)
        self.generateClipsButton.config(state=DISABLED)
        self.addSongButton.config(state=DISABLED)
        self.addRandomSongsButton.config(state=DISABLED)
        self.removeSongButton.config(state=DISABLED)
        self.removeSongButton2.config(state=DISABLED)
        colour = self.colourBox_value.get()
        try:
            palete = self.TICKET_COLOURS[colour]
        except KeyError:
            palete = self.TICKET_COLOURS["BLUE"]
        self.boxNorColour = palete["boxNorColour"]
        self.boxAltColour = palete["boxAltColour"]
        self.boxTitleColour = palete["boxTitleColour"]
        self.bottomBanner.config(text="Generating Bingo Game - {0}".format(self.gameId), fg="#0D0")
        self.gameId = self.gameNameEntry.get().strip()
        self.directory = os.path.join(os.getcwd(), self.GAME_DIRECTORY, self.GAME_PREFIX + self.gameId)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.assignSongIds(self.gameSongList)
        self.progress = {'text':'', 'pct': 0.0, 'phase': (1,3)}
        self.gen_thread = threading.Thread(target=self.generateBingoTicketsAndMp3)
        self.gen_thread.daemon = True
        self.gen_thread.start()
        self.pollProgress()

    def generateBingoTicketsAndMp3(self):
        if not self.assignSongIds(self.gameSongList):
            self.progress['text'] = 'Failed to assign song IDs - maybe not enough tracks in the game?'
            return
        self.progress['phase'] = (1,3)
        trackOrder = self.generateMp3()
        self.progress['phase'] = (2,3)
        self.generateAllCards()
        self.progress['phase'] = (3,3)
        self.generateCardResults(trackOrder)
        self.progress['text'] = "Finished Generating Bingo Game - {0}".format(self.gameId)
        self.progress['pct'] = 100.0

    def pollProgress(self):
        if not self.gen_thread:
            return
        pct = self.progress['pct'] / float(self.progress['phase'][1])
        pct += float(self.progress['phase'][0] - 1)/float(self.progress['phase'][1])
        self.progressVar.set(pct)
        self.bottomBanner.config(text=self.progress['text'])
        if self.gen_thread.is_alive():
            self.poll_id = self.appMaster.after(250, self.pollProgress)
            return
        self.generateCardsButton.config(state=NORMAL)
        self.generateClipsButton.config(state=NORMAL)
        self.addSongButton.config(state=NORMAL)
        self.addRandomSongsButton.config(state=NORMAL)
        self.removeSongButton.config(state=NORMAL)
        self.removeSongButton2.config(state=NORMAL)
        self.gen_thread.join()
        self.gen_thread = None
        self.createGameId()
        #self.removeSongsFromGameList()
        #self.removeSongsFromList()
        #self.gameSongList = []
        #self.addSongsToList()
        #if self.sortByTitle:
        #    self.sortBothTitles()
        #else:
        #    self.sortBothArtists()   
        self.progress = {'text':'', 'pct': 0.0, 'phase': (1,1)}

    def generateClips(self):
        if not self.gameSongList:
            return
        self.generateCardsButton.config(state=DISABLED)
        self.generateClipsButton.config(state=DISABLED)
        self.addSongButton.config(state=DISABLED)
        self.addRandomSongsButton.config(state=DISABLED)
        self.removeSongButton.config(state=DISABLED)
        self.removeSongButton2.config(state=DISABLED)
        self.progress = {'text':'', 'pct': 0.0, 'phase': (1,1)}
        self.gen_thread = threading.Thread(target=self.generateClipsThread)
        self.gen_thread.daemon = True
        self.gen_thread.start()
        self.pollProgress()

    def parseTime(self, tm):
        parts = tm.split(':')
        parts.reverse()
        secs = 0
        while parts:
            secs = (60*secs) + int(parts.pop(), 10)
        return secs

    def generateClipsThread(self):
        totalSongs = len(self.gameSongList)
        for index, song in enumerate(self.gameSongList):
            #print(song.title, song.artist, song.album)
            self.progress['text'] = u'{} ({:d}/{:d})'.format(self.clean(song.title), index, totalSongs)
            self.progress['pct'] = 100.0 * float(index) / float(totalSongs)
            try:
                self.generateClip(song)
            except:
                traceback.print_exc()
                #print(sys.exc_traceback)
                #print(sys.exc_value)
                print(r'Error generating clip: {}'.format(self.clean(song.title)))
        self.progress['pct'] = 100.0
        self.progress['text'] = 'Finished generating clips'

    def generateClip(self, song):
        head, tail = os.path.split(os.path.dirname(song.filepath))
        dirname = tail if tail else head
        destinationDirectory = os.path.join(self.destinationDirectory, dirname)
        if not os.path.exists(destinationDirectory):
            os.makedirs(destinationDirectory)
        start = self.parseTime(self.startTimeEntry.get()) * 1000
        end = start + self.parseTime(self.durationEntry.get()) * 1000
        src = AudioSegment.from_mp3(song.filepath)
        dst = src[start:end]
        tags = {
            "artist": self.clean(song.artist),
            "title": self.clean(song.title)
        }
        if song.album:
            tags["album"] = self.clean(song.album)
        destPath = os.path.join(destinationDirectory, song.filename)
        dst.export(destPath, format='mp3', bitrate='256k', tags=tags)
        del src
        del dst

root = Tk()
root.resizable(0,0)
root.wm_title("Music Bingo Game Generator")
#if os.path.exists("./Extra-Files/Icon.ico"):
#    root.iconbitmap('./Extra-Files/Icon.ico')

newObject = MainApp(root)
root.mainloop()
