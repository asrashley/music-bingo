import os, sys, inspect

from Tkinter import *
import tkMessageBox, Tkconstants, tkFileDialog
import ttk
import random
from random import shuffle
import datetime

import math

import subprocess

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
class Song:

    def __init__(self, title, artist, refId, filepath):

        self.title = self.correctFeat(title.split('[')[0])
        self.artist = self.correctFeat(artist)
        self.songId = None
        self.refId = refId
        self.filepath = filepath

    def correctFeat(s):
        featWords = ["FT.","FT","FEAT", "FEAT."]
        correctFeat = "ft."
        s = s.split(" ")
        rv = ""
        first = True
        for i in s:
            if len(i) != 0:
                if not first:
                    rv += " "
                else:
                    first = False
                if i[0].isalpha():
                    if i.upper() in featWords:
                        rv += correctFeat
                    else:
                        rv += i[0].upper()
                        if 1 < len(i):
                            rv += i[1:len(i)]
                else:
                    firstLetter = 1
                    while firstLetter < len(i) and not i[firstLetter].isalpha():
                        firstLetter+=1
                    if firstLetter < len(i):
                        if i[firstLetter:len(i)].upper() in featWords:
                            rv += i[0:firstLetter]+correctFeat
                        else:
                            sr += i[0:firstLetter]+i[firstLetter].upper()
                            if firstLetter+1 < len(i):
                                rv += i[firstLetter+1:len(i)]
                    else:
                        rv += i
        return rv
        
    def __str__(self):
        return self.title + " - " + self.artist + " - ID=" + str(self.songId)

# This class is used to generate 'BingoTicket' objects which are representations of a ticket with
# 15 songs.
class BingoTicket:

    def __init__(self):

        self.cardId = 1
        self.cardTracks = []

        self.ticketNumber = None

# This class is used to generate 'Mp3Order' objects, these represent the order of the tracks within
# the final mp3. Currently, the majority of the variables are not used.
class Mp3Order:

    def __init__(self, list):

        self.list = list

        self.winPoint = None
        self.amountAtWinPoint = None

        self.amountAfterWinPoint = None

        self.winPoints = None

# This class is the GUI of the program and also contains all the functions used in generating
# the bingo tickets.
class MainApp:

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

        self.songListTree = ttk.Treeview(songListFrame,  columns=columns, show="headings", height=20, yscrollcommand=songListScrollbar.set)
        self.songListTree.pack(side=LEFT)

        self.songListTree['columns'] = ('title', 'artist')

        self.songListTree.column('title', width=200, anchor='center')
        self.songListTree.heading('title', text='Title')
        self.songListTree.column('artist', width=200, anchor='center')
        self.songListTree.heading('artist', text='Artist')

        self.songsRemaining = "Songs Remaining = "

        self.songsRemainingLabel = Label(leftFrame, text=self.songsRemaining, padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 14))#, width=34)
        self.songsRemainingLabel.grid(row=3, column=0)

        self.songsInGame = "Songs In Game = "

        self.songsInGameLabel = Label(rightFrame, text=self.songsInGame, padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 14))#, width=34)
        self.songsInGameLabel.grid(row=3, column=0)

        self.addSongsToList()

        songListScrollbar.pack(side=LEFT, fill=Y)

        songListScrollbar.config(command=self.songListTree.yview)


        ''''''

        gameSongsLabel = Label(rightFrame, text="Songs In This Game:", padx=5, bg=bannerColour, fg="#FFF", font=(typeface, 16))
        gameSongsLabel.grid(row=0, column=0)

        gameSongListFrame = Frame(rightFrame)
        gameSongListFrame.grid(row=1, column=0)

        gameSongListScrollbar = Scrollbar(gameSongListFrame)

        self.gameSongListTree = ttk.Treeview(gameSongListFrame,  columns=columns, show="headings", height=20, yscrollcommand=gameSongListScrollbar.set)
        self.gameSongListTree.pack(side=LEFT)

        self.gameSongListTree.column('title', width=200, anchor='center')
        self.gameSongListTree.heading('title', text='Title')
        self.gameSongListTree.column('artist', width=200, anchor='center')
        self.gameSongListTree.heading('artist', text='Artist')

        gameSongListScrollbar.pack(side=LEFT, fill=Y)

        gameSongListScrollbar.config(command=self.gameSongListTree.yview)

        ''''''

        self.selectDirectoryButton = Button(midFrame, text="Select Directory", command=self.selectDirectory, bg="#63ff5f")
        self.selectDirectoryButton.pack(side=TOP)

        buttonGapPadding = Label(midFrame, height=2, bg=normalColour)
        buttonGapPadding.pack(side=TOP)

        self.addSongButton = Button(midFrame, text="Add Selected Song To Game", command=self.addToGame, bg="#63ff5f")
        self.addSongButton.pack(side=TOP)

        buttonGapPadding = Label(midFrame, height=2, bg=normalColour)
        buttonGapPadding.pack(side=TOP)

        self.addRandomSongsButton = Button(midFrame, text="Add 5 Random Songs To Game", command=self.addRandomSongsToGame, bg="#18ff00")
        self.addRandomSongsButton.pack(side=TOP)

        buttonGapPadding2 = Label(midFrame, height=6, bg=normalColour)
        buttonGapPadding2.pack(side=TOP)

        self.removeSongButton = Button(midFrame, text="Remove Selected Song From Game", command=self.removeFromGame, bg="#ff9090")
        self.removeSongButton.pack(side=TOP)

        buttonGapPadding3 = Label(midFrame, height=2, bg=normalColour)
        buttonGapPadding3.pack(side=TOP)

        self.removeSongButton2 = Button(midFrame, text="Remove All Songs From Game", command=self.removeAllFromGame, bg="#ff5151")
        self.removeSongButton2.pack(side=TOP)

        buttonGapPadding4 = Label(midFrame, height=4, bg=normalColour)
        buttonGapPadding4.pack(side=TOP)

        self.sortArtistsButton = Button(midFrame, text="Sort Lists By Artist", command=self.sortBothArtists, bg="#f4ff45")
        self.sortArtistsButton.pack(side=TOP)

        self.sortTitlesButton = Button(midFrame, text="Sort Lists By Title", command=self.sortBothTitles, bg="#45aeff")
        self.sortTitlesButton.pack(side=TOP)    

        bottomFrame = Frame(master, bg=altColour, pady=5)
        bottomFrame.pack(side=TOP, fill=X)

        padding = Label(bottomFrame, width=4, bg=altColour)
        padding.pack(side=LEFT)

        numberLabel = Label(bottomFrame, font=(typeface, 16), text="Game ID:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.pack(side=LEFT)
        self.gameNameEntry = Entry(bottomFrame, font=(typeface, 16), width=10, justify=CENTER)
        self.gameNameEntry.pack(side=LEFT)#, fill=X, expand=1)
        self.createGameId()
        self.gameNameEntry.insert(0, self.gameId)

        padding = Label(bottomFrame, width=6, bg=altColour, height=4)
        padding.pack(side=LEFT)

        numberLabel = Label(bottomFrame, font=(typeface, 16), text="Number Of Tickets:", bg=altColour, fg="#FFF", padx=6)
        numberLabel.pack(side=LEFT)
        self.ticketsNumberEntry = Entry(bottomFrame, font=(typeface, 16), width=5, justify=CENTER)
        self.ticketsNumberEntry.pack(side=LEFT)#, fill=X, expand=1)

        self.ticketsNumberEntry.insert(0, "100")

        colourLabel = Label(bottomFrame, font=(typeface, 16), text="Ticket Colour:", bg=altColour, fg="#FFF", padx=6)
        colourLabel.pack(side=LEFT)

        self.colourBox_value = StringVar()
        self.colourBox = ttk.Combobox(bottomFrame, textvariable=self.colourBox_value,
                                state='readonly', font=(typeface, 16), width=8, justify=CENTER)
        self.colourBox['values'] = ('BLUE', 'GREEN', 'RED', 'ORANGE', 'PURPLE', 'YELLOW', 'GREY')
        self.colourBox.current(0)

        self.colourBox.pack(side=LEFT)

        padding = Label(bottomFrame, width=6, bg=altColour, height=4)
        padding.pack(side=LEFT)

        self.generateCardsButton = Button(bottomFrame, text="Generate Bingo Game", command=self.generateBingoTicketsAndMp3, pady=0, font=(typeface, 18), bg="#00cc00")
        self.generateCardsButton.pack(side=LEFT)

        self.bottomBanner = Label(master, text="Waiting...", bg=bannerColour, fg="#FFF", font=(typeface, 14))
        self.bottomBanner.pack(side=TOP, fill=X, expand=1)

        self.updateCounts()

        self.sortListByTitle()

    def createGameId(self):
        gameNumber = "1"
        directoryList = [x[0] for x in os.walk("./Bingo Games/")]
        if len(directoryList) > 0:
            del directoryList[0]
            clashList = []
            for i in directoryList:
                if i[27:35] == self.baseGameId:
                    clashList.append(i)
            if len(clashList) > 0:
                highestNumber = 0
                for i in clashList:
                    number = int(i[36:])
                    if number > highestNumber:
                        highestNumber = number

                gameNumber = str(highestNumber + 1)

        self.gameId = self.baseGameId + "-" + gameNumber
        
    # This function is called after any addition or removal of songs to/from the lists - it updates
    # the counts at the bottom of each list
    def updateCounts(self):

        self.songsRemainingLabel.config(text=self.songsRemaining+str(len(self.songList)))

        if len(self.gameSongList) < 30:
            boxColour = "#ff0000"
        elif len(self.gameSongList) < 45:
            boxColour = "#fffa20"
        else:
            boxColour = "#00c009"

        self.songsInGameLabel.config(text=self.songsInGame+str(len(self.gameSongList)), fg=boxColour)

        self.bottomBanner.config(text="Waiting...", fg="#FFF")

    # This function generates the first 3 values of a game ID based on the current date
    def generateBaseGameId(self):

        self.baseGameId = datetime.date.today()

        self.baseGameId = str(self.baseGameId)[2:]

    # This function resets the program back to its default state - with the left list populated
    # with all available songs, and nothing in the current game list
    def resetProgram(self):

        self.nextPrimeIndex = 0
        self.nextRefId = 0
        self.usedCardIds = []

        self.clipDirectory = './Clips'
        if len(sys.argv) > 1:
            self.clipDirectory = sys.argv[1]

        self.songList = []

        self.populateSongList(self.songList)

        self.gameSongList = []

    def selectDirectory(self):
        self.clipDirectory = tkFileDialog.askdirectory()
        self.removeSongsFromList()
        self.songList = []
        self.populateSongList(self.songList)
        self.addSongsToList()
        self.updateCounts()

    # This function adds the selected song from the list to the game
    def addToGame(self):
        try:
            focusElement = self.songListTree.focus()

            if len(focusElement) > 0:
                song = None

                for i in self.songList:
                    if i.refId == int(focusElement):
                        song = i
                        break

                if song is not None:
                    self.removeSongsFromGameList()
                    self.gameSongList.append(song)
                    self.addSongsToGameList()

                    self.removeSongsFromList()
                    self.songList.remove(song)
                    self.addSongsToList()

                    if self.sortByTitle:
                        self.sortGameListByTitle()
                    else:
                        self.sortGameListByArtist()

                else:
                    print("Song Not Found.")
        except:
            print("Couldn't Add To Game List For Unknown Reason.")

        self.updateCounts()

    # This function adds a random 5 (if available) songs to the game list
    def addRandomSongsToGame(self):

        if len(self.songList) < 5:
            maxCount = len(self.songList)
        else:
            maxCount = 5

        for i in range(0, maxCount):
            randomIndex = random.randint(0, len(self.songList)-1)

            self.removeSongsFromGameList()
            self.gameSongList.append(self.songList[randomIndex])
            self.addSongsToGameList()

            self.removeSongsFromList()
            self.songList.remove(self.songList[randomIndex])
            self.addSongsToList()

            if self.sortByTitle:
                self.sortGameListByTitle()
            else:
                self.sortGameListByArtist()

        self.updateCounts()

    # This function removes the selected song from the game and returns it to the main list
    def removeFromGame(self):
        try:
            focusElement = self.gameSongListTree.focus()

            if len(focusElement) > 0:
                song = None

                for i in self.gameSongList:
                    if i.refId == int(focusElement):
                        song = i
                        break

                if song is not None:

                    self.removeSongsFromList()
                    self.songList.append(song)
                    self.addSongsToList()

                    self.removeSongsFromGameList()
                    self.gameSongList.remove(song)
                    self.addSongsToGameList()

                    if self.sortByTitle:
                        self.sortListByTitle()
                    else:
                        self.sortListByArtist()

                else:
                    print("Song Not Found.")
        except:
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
            self.resetProgram()

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
        for song in self.songList:
            self.songListTree.insert('', 'end', str(song.refId), values=(song.title, song.artist))

    # This function takes the program's representation of the list of songs and removes them
    # all from the GUI list
    def removeSongsFromList(self):
        for song in self.songList:
            self.songListTree.delete(song.refId)

    # This function takes the program's representation of the list of game songs and adds them
    # all to the game GUI list
    def addSongsToGameList(self):
        for song in self.gameSongList:
            self.gameSongListTree.insert('', 'end', str(song.refId), values=(song.title, song.artist))

        self.updateCounts()

    # This function takes the program's representation of the list of game songs and removes them
    # all from the game GUI list
    def removeSongsFromGameList(self):
        for song in self.gameSongList:
            self.gameSongListTree.delete(song.refId)

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
        self.bottomBanner.config(text="Waiting...", fg="#FFF")

    # This function sorts both the song list and game song list by title and updates the GUI
    def sortBothTitles(self):
        self.sortByTitle = True
        self.sortListByTitle()
        self.sortGameListByTitle()
        self.bottomBanner.config(text="Waiting...", fg="#FFF")

    # This function retrieves a list of songs from the Clips folder, gets the Title/Artist data
    # and adds them to the song list
    def populateSongList(self, theList):

        if not os.path.isdir(self.clipDirectory):
            print('Directory {0} does not exist'.format(self.clipDirectory))
            return

        folderList = os.listdir(self.clipDirectory)

        for theFile in folderList:

            if theFile[-4:] == ".mp3":
                try:
                    absPath = os.path.join(self.clipDirectory, theFile)
                    mp3info = EasyID3(absPath)
                    artist = mp3info["artist"]
                    title = mp3info["title"]

                    # Need to use title[0] below as it returns a list not a string
                    if len(artist) > 0 and len(title) > 0:
                        theList.append(Song(title[0], artist[0], self.nextRefId, absPath))
                        self.nextRefId = self.nextRefId + 1

                    else:
                        print("File: " + theFile + " does not contain both title and artist info.")
                except:
                    print("File: " + theFile + " does not contain both title and artist info.")

    # This function is called on the creation of a game and assigns prime numbers to all of the songs
    # in the game for the generation of the tickets.
    def assignSongIds(self, gameList):

        self.nextPrimeIndex = 0

        for i in gameList:
            i.songId = primeNumbers[self.nextPrimeIndex]
            self.nextPrimeIndex = self.nextPrimeIndex + 1
            if self.nextPrimeIndex >= len(primeNumbers):
                print("Exceeded the 430 song limit.")
                break

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
            Ptitle = Paragraph('''<para align=center spaceb=3>''' + card.cardTracks[i].title,p)
            Pgap = Paragraph('''<para align=center spaceb=0>''', pGap)
            Partist = Paragraph('''<para align=center spaceb=3><b>''' + card.cardTracks[i].artist + '''</b>''',p)

            row1.append([Ptitle, Pgap, Partist])

        row2 = []

        for i in range(5,10):
            Ptitle = Paragraph('''<para align=center spaceb=3>''' + card.cardTracks[i].title,p)
            Pgap = Paragraph('''<para align=center spaceb=0>''', pGap)
            Partist = Paragraph('''<para align=center spaceb=3><b>''' + card.cardTracks[i].artist + '''</b>''',p)
            row2.append([Ptitle, Pgap, Partist])

        row3 = []

        for i in range(10,15):
            Ptitle = Paragraph('''<para align=center spaceb=3>''' + card.cardTracks[i].title,p)
            Pgap = Paragraph('''<para align=center spaceb=0>''', pGap)
            Partist = Paragraph('''<para align=center spaceb=3><b>''' + card.cardTracks[i].artist + '''</b>''',p)
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
    def generateTrackListing(self, orderString):

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

        title = Paragraph('''<para align=center spaceb=3>Track Listing For Game Number: <b>''' + self.gameId + '''</b>''', pTitle)
        elements.append(title)

        p = ParagraphStyle('test')
        p.textColor = 'black'
        p.alignment = TA_CENTER
        p.fontSize = 10
        p.leading = 10

        s = Spacer(width=0, height=0.15*inch)
        elements.append(s)

        data = []

        orderPara = Paragraph('''<para align=center spaceb=3><b>Order</b>''',p)
        titlePara = Paragraph('''<para align=center spaceb=3><b>Title</b>''',p)
        artistPara = Paragraph('''<para align=center spaceb=3><b>Artist</b>''',p)
        startPara = Paragraph('''<para align=center spaceb=3><b>Start Time</b>''',p)
        gonePara = Paragraph('''<para align=center spaceb=3> ''',p)

        data.append([orderPara,titlePara, artistPara, startPara, gonePara])

        lines = orderString.split("\n")
        lines = lines [0:len(lines)-1]

        for i in lines:
            line = i.split("/-/")

            orderNo = Paragraph('''<para align=center spaceb=3><b>''' + line[0] + '''</b>''',p)
            titleField = Paragraph('''<para align=center spaceb=3>''' + line[1],p)
            artistField = Paragraph('''<para align=center spaceb=3>''' + line[2],p)
            startField = Paragraph('''<para align=center spaceb=3>''' + line[3],p)

            endBox = Paragraph('''<para align=center spaceb=3> ''',p)

            data.append([orderNo,titleField,artistField,startField,endBox])

        boxTitleColour = HexColor(0xa4d7ff)

        t=Table(data,
          style=[('BOX',(0,0),(-1,-1),1,colors.black),
                 ('GRID',(0,0),(-1,-1),0.5,colors.black),
                 ('VALIGN',(0,0),(-1,-1),'CENTER'),

                 ('BACKGROUND', (0, 0), (4, 0), boxTitleColour),
                 
        ])

        t._argW[0] = 0.55*inch
        t._argW[1] = 3.1*inch
        t._argW[2] = 3.1*inch

        t._argW[3]=0.85*inch
        t._argW[4]=0.3*inch
         
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

            if theWinPoint != len(self.songOrder.list) - fromEnd:
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

            if theWinPoint != len(self.songOrder.list) - fromEnd:
                self.usedCardIds.remove(newCard.cardId)
            else:
                count = count + 1

        return newCard

    # This function generates all the bingo tickets in the game
    def generateAllCards(self):

        self.usedCardIds = [] # Could assign this from file (for printing more)

        numberOfCards = self.numberOfCards

        self.cardList = []

        tracksOnTickets = ""

        decayRate = 0.65

        numberOnLastSong = numberOfCards * decayRate

        numberOnSecondLast = (numberOfCards-numberOnLastSong) * decayRate

        numberOnThirdLast = (numberOfCards-numberOnLastSong-numberOnSecondLast) * decayRate

        numberOnFourthLast = (numberOfCards-numberOnLastSong-numberOnSecondLast-numberOnThirdLast) * decayRate

        print(str(numberOnLastSong))
        print(str(numberOnSecondLast))
        print(str(numberOnThirdLast))
        print(str(numberOnFourthLast))

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
            newCard = self.generateOneAtPoint(offset)
            goodCards.append(newCard)

            offset = offset + 1

        increment = numberOfCards / amountToGo

        startPoint = 0

        shuffle(goodCards)

        for i in goodCards:

            randomPoint = random.randrange(int(math.ceil(startPoint)), int(math.ceil(startPoint+increment)), 1)

            if randomPoint >= numberOfCards:
                randomPoint = numberOfCards - 1

            self.cardList.insert(randomPoint, i)
            startPoint = startPoint+increment

        print(str(len(self.cardList)))
        print(str(numberOfCards))

        ticketNumber = 1

        for i in self.cardList:
            i.ticketNumber = ticketNumber
            
            tracksOnTickets = tracksOnTickets + str(i.ticketNumber) + "/" + str(i.cardId) + "\n"

            ticketNumber = ticketNumber + 1

        self.pageOrder = True

        if self.pageOrder:
            noc3c = int(math.ceil(numberOfCards/3))
            noc3f = int(math.floor(numberOfCards/3))
            print(noc3c,noc3f)
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

        count = 1

        page = 1

        for card in self.cardList:
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

                #t._argW[3]=1.5*inch
                 
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

        print("Number Of Tracks In Game: " + str(len(self.gameSongList)))
        print("Number Of Cards Made: " + str(len(self.cardList)))

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

        for i in order.list:
            if i in tracksCopy:
                lastSong = count
                tracksCopy.remove(i)

            count = count + 1

            if len(tracksCopy) == 0:
                break

        return lastSong

    # This function generate the mp3 for the game with the generated order of tracks
    def generateMp3(self):
        def clean(s):
            return unicode(s).encode('ascii', 'ignore')

        bestCandidate = Mp3Order(self.getTrackOrder())

        self.songOrder = bestCandidate

        transition = AudioSegment.from_mp3("./Extra-Files/TRANSITION.mp3")

        transition = transition.normalize(headroom=0)

        combinedTrack = AudioSegment.from_mp3("./Extra-Files/START.mp3")

        combinedTrack = combinedTrack.normalize(headroom=0)

        starting = True

        orderString = ""
        count = 0

        gameTracksString = ""

        for track in bestCandidate.list:

            if starting:
                trackLength = combinedTrack.__len__()
            else:
                trackLength = combinedTrack.__len__() + transition.__len__()

            nextTrack = AudioSegment.from_mp3(track.filepath)

            nextTrack = nextTrack.normalize(headroom=0)

            if starting:
                combinedTrack = combinedTrack + nextTrack
                starting = False
            else:
                combinedTrack = combinedTrack + transition + nextTrack

            count = count + 1

            orderString = orderString + str(count) + "/-/" + clean(track.title) + "/-/" + clean(track.artist) + "/-/" + convertTime(trackLength) + "\n"

            gameTracksString = gameTracksString + str(count) + "/#/" + clean(track.songId) + "/#/" + clean(track.title) + "/#/" + clean(track.artist) + "\n"


        f = open(self.directory + "/gameTracks", 'w')
        f.write(gameTracksString)
        f.close()

        trackName = self.directory + "/" + self.gameId + " Game Audio.mp3"
        combinedTrack.export(trackName, format="mp3")
        print("MP3 Generated.")

        self.generateTrackListing(orderString)

    # This function is called on pressing the generate game button to generate tickets and mp3
    def generateBingoTicketsAndMp3(self):

        self.bottomBanner.config(text="Waiting...", fg="#FFF")

        self.numberOfCards = self.ticketsNumberEntry.get()

        self.numberOfCards = int(self.numberOfCards.strip())

        numberOfCards = self.numberOfCards

        extra = ""

        max_cards = combinations(len(self.gameSongList), 15)
        min_songs = 17 # 17 songs allows 136 combinations

        if len(self.gameSongList) < 45:
            extra = " (at least 45 songs is recommended)"

        if numberOfCards > max_cards:
            extra = ' ('+len(self.gameSongList)+' only allows '+max_cards+' cards to be generated)'
        if len(self.gameSongList) >= min_songs and numberOfCards >= 15 and numberOfCards <= max_cards:

            answer = 'yes'

            questionMessage = "Are you sure you want to generate a bingo game with " + str(numberOfCards) + " tickets and the "+str(len(self.gameSongList))+" songs in the white box on the right? "+extra+"\n(The process will take a few minutes - The program may appear to freeze during this time, but it is nothing to worry about.)"
            answer = tkMessageBox.askquestion("Are you sure?", questionMessage)

            if answer == 'yes':

                self.generateCardsButton.config(state=DISABLED)

                self.addSongButton.config(state=DISABLED)

                self.addRandomSongsButton.config(state=DISABLED)

                self.removeSongButton.config(state=DISABLED)

                self.removeSongButton2.config(state=DISABLED)

                colour = self.colourBox_value.get()

                if colour == "BLUE":
                    # Blue Colours
                    self.boxNorColour = HexColor(0xF0F8FF)
                    self.boxAltColour = HexColor(0xDAEDFF)
                    self.boxTitleColour = HexColor(0xa4d7ff)
                elif colour == "RED":
                    # Red Colours
                    self.boxNorColour = HexColor(0xFFF0F0)
                    self.boxAltColour = HexColor(0xffdada)
                    self.boxTitleColour = HexColor(0xffa4a4)
                elif colour == "GREEN":
                    # Green Colours
                    self.boxNorColour = HexColor(0xf0fff0)
                    self.boxAltColour = HexColor(0xd9ffd9)
                    self.boxTitleColour = HexColor(0xa4ffa4)
                elif colour == "ORANGE":
                    # Orange Colours
                    self.boxNorColour = HexColor(0xfff7f0)
                    self.boxAltColour = HexColor(0xffecd9)
                    self.boxTitleColour = HexColor(0xffd1a3)
                elif colour == "PURPLE":
                    # Purple Colours
                    self.boxNorColour = HexColor(0xf8f0ff)
                    self.boxAltColour = HexColor(0xeed9ff)
                    self.boxTitleColour = HexColor(0xd5a3ff)
                elif colour == "YELLOW":
                    # Yellow Colours
                    self.boxNorColour = HexColor(0xfffff0)
                    self.boxAltColour = HexColor(0xfeffd9)
                    self.boxTitleColour = HexColor(0xfdffa3)
                elif colour == "GREY":
                    # Grey Colours
                    self.boxNorColour = HexColor(0xf1f1f1)
                    self.boxAltColour = HexColor(0xd9d9d9)
                    self.boxTitleColour = HexColor(0xbfbfbf)
                else:
                    # Defaults To Blue Colours
                    self.boxNorColour = HexColor(0xF0F8FF)
                    self.boxAltColour = HexColor(0xDAEDFF)
                    self.boxTitleColour = HexColor(0xa4d7ff)

                print("Generating MP3 and Bingo Tickets")
                
                self.gameId = self.gameNameEntry.get().strip()

                self.directory = "./Bingo Games/"+"Bingo Game - " + self.gameId

                if not os.path.exists(self.directory):
                    os.makedirs(self.directory)


                self.assignSongIds(self.gameSongList)

                self.bottomBanner.config(text="Something went wrong. Please Try Again...?", fg="#F00")

                self.generateMp3()
                self.generateAllCards()

                self.generateCardsButton.config(state=NORMAL)

                self.addSongButton.config(state=NORMAL)

                self.addRandomSongsButton.config(state=NORMAL)

                self.removeSongButton.config(state=NORMAL)

                self.removeSongButton2.config(state=NORMAL)

                self.bottomBanner.config(text="Finished Generating Bingo Game - Number = " + self.gameId, fg="#0D0")
                self.createGameId()

                #windowsDirectory = self.directory[2:]
                #[firstHalf, secondHalf] = windowsDirectory.split("/")
                #windowsDirectory = firstHalf + "\\" + secondHalf
                #subprocess.Popen('explorer "{0}"'.format(windowsDirectory))
        else:
            self.bottomBanner.config(text="You must select at least 30 songs (at least 45 is better) and between 50 and 400 tickets for a bingo game to be generated.", fg="#F11")

root = Tk()
root.resizable(0,0)
root.wm_title("Music Bingo Game Generator")
#if os.path.exists("./Extra-Files/Icon.ico"):
#    root.iconbitmap('./Extra-Files/Icon.ico')

newObject = MainApp(root)
root.mainloop()
