from Tkinter import *
import ttk

from collections import namedtuple
import json
import os
import sys

# Object representation of a ticket mapping its number to its prime number ID
class Ticket:

    def __init__(self, ticketNumber, ticketId):

        self.ticketNumber = ticketNumber
        self.ticketId = ticketId

# GUI Class
class MainApp:

    def __init__(self, master, gameID=''):

        self.appMaster = master

        frame = Frame(master, bg=normalColour)
        frame.pack(side=TOP, fill=BOTH, expand=1)

        gameIdLabel = Label(frame, bg=normalColour, text="Game ID Number:", font=(typeface, 18),pady=10)
        gameIdLabel.grid(row=0,column=0)

        self.gameIdEntry = Entry(frame, font=(typeface, 18), width=12, justify=LEFT)
        self.gameIdEntry.grid(row=0,column=1)
        self.gameIdEntry.insert(0, gameID)

        ticketNumberLabel = Label(frame, bg=normalColour, text="Ticket Number:", font=(typeface, 18),pady=10)
        ticketNumberLabel.grid(row=1,column=0)

        self.ticketNumberEntry = Entry(frame, font=(typeface, 18), width=12, justify=LEFT)
        self.ticketNumberEntry.grid(row=1,column=1)

        checkWinButton = Button(master, text="Check Win", command=self.findWinPoint, font=(typeface, 18), width=10, bg="#00e516")
        checkWinButton.pack(side=TOP, fill=X)

        self.ticketStatusWindow = Text(master, bg="#111", fg="#FFF", height=4, width=30,  font=(typeface, 16))
        self.ticketStatusWindow.pack(side=TOP,fill=X)

        self.ticketStatusWindow.config(state=DISABLED)

    # This function will find the winning point of the ticket given in box
    def findWinPoint(self):

        self.ticketStatusWindow.config(state=NORMAL)
        self.ticketStatusWindow.delete(0.0, END)

        gameId = self.gameIdEntry.get()
        gameId = gameId.strip()

        path = "./Bingo Games/Game-%s"%gameId
        if not os.path.exists(path):
            path = "./Bingo Games/Bingo Game - %s"%gameId

        if os.path.exists(path):

            f = open(path + "/ticketTracks")
            ticketFileLines = f.read()
            f.close()

            ticketFileLines = ticketFileLines.split("\n")
            ticketFileLines = ticketFileLines[0:len(ticketFileLines)-1]

            ticketList = []

            for line in ticketFileLines:
                [ticketNum, ticketId] = line.split("/")
                ticketList.append(Ticket(ticketNum, ticketId))


            ticketNumber = self.ticketNumberEntry.get()
            ticketNumber = ticketNumber.strip()

            theTicket = None

            for ticket in ticketList:
                if ticketNumber == ticket.ticketNumber:
                    theTicket = ticket
                    break

            if theTicket != None:
                with open(path + "/gameTracks.json", 'rt') as f:
                    gameTracks = json.load(f)
                Song = namedtuple('Song', ['song_id', 'title', 'artist', 'count', 'duration',
                                           'filename', 'album'])
                for idx in range(len(gameTracks)):
                    try:
                        gameTracks[idx]['song_id'] = gameTracks[idx]['songId']
                        del gameTracks[idx]['songId']
                    except KeyError:
                        pass
                gameTracks = map(lambda s: Song(**s), gameTracks)

                winPoint, title, artist = self.checkWin(int(theTicket.ticketId), path, gameTracks)

                self.ticketStatusWindow.config(fg=normalColour)

                self.ticketStatusWindow.insert(END,"In Game Number " + gameId +":\n")
                self.ticketStatusWindow.insert(END,"Ticket "+ticketNumber+" will win at song " + str(winPoint)+".")
                self.ticketStatusWindow.insert(END,"\n("+title+" - " +artist+")")

            else:
                if len(ticketNumber) > 0:
                    self.ticketStatusWindow.config(fg="#F00")
                    self.ticketStatusWindow.insert(END, "Ticket "+ticketNumber+" does not exist\nwith Game ID Number " + gameId+"!")
                else:
                    self.ticketStatusWindow.config(fg="#00f6ff")
                    self.ticketStatusWindow.insert(END, "You must enter a Ticket Number!")
        else:
            self.ticketStatusWindow.config(fg="#F00")
            if len(gameId) > 0:
                self.ticketStatusWindow.insert(END, "Game ID Number " + gameId + "\ndoes not exist!")
            else:
                self.ticketStatusWindow.insert(END, "You must enter a Game ID Number\nand Ticket Number!")

        self.ticketStatusWindow.config(state=DISABLED)

    def checkWin(self, ticketId, directory, lines):
        """returns the point and track in which the ticket will win"""
        ticketTracks = self.primes(ticketId)
        lastSong = "INVALID"
        lastArtist = ""
        lastTitle = ""
        if os.path.exists(directory):
            fileLines = lines
            for i in fileLines:
                if int(i.song_id) in ticketTracks:
                    lastSong = i.count
                    lastTitle = i.title
                    lastArtist = i.artist
                    ticketTracks.remove(int(i.song_id))

        if len(ticketTracks) == 0 and lastSong != "INVALID":
            return [int(lastSong),lastTitle,lastArtist]
        else:
            return [0, "", ""]

    def primes(self, n):
        """calculates the prime factors of the prime ticket ID. This will tell exactly what
        tracks were on the ticket"""
        primfac = []
        d = 2
        while d*d <= n:
            while (n % d) == 0:
                primfac.append(d)  # supposing you want multiple factors repeated
                n //= d
            d += 1
        if n > 1:
           primfac.append(n)
        return primfac

root = Tk()
root.resizable(0,0)
root.wm_title("Music Bingo - Ticket Checker")
#if os.path.exists("./Extra-Files/Icon.ico"):
#    root.iconbitmap('./Extra-Files/Icon.ico')

typeface = "Arial"

normalColour = "#ff7200"
altColour = "#d83315"

bannerColour = "#222"

if len(sys.argv) > 1:
    newObject = MainApp(root, sys.argv[1])
else:
    newObject = MainApp(root)
root.mainloop()
