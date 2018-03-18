from tkinter import *
from tkinter import ttk

import os

# Object representation of a ticket mapping its number to its prime number ID
class Ticket:

    def __init__(self, ticketNumber, ticketId):

        self.ticketNumber = ticketNumber
        self.ticketId = ticketId

# GUI Class
class MainApp:

    def __init__(self, master):

        self.appMaster = master

        frame = Frame(master, bg=normalColour)
        frame.pack(side=TOP, fill=BOTH, expand=1)

        gameIdLabel = Label(frame, bg=normalColour, text="Game ID Number:", font=(typeface, 18),pady=10)
        gameIdLabel.grid(row=0,column=0)

        self.gameIdEntry = Entry(frame, font=(typeface, 18), width=12, justify=LEFT)
        self.gameIdEntry.grid(row=0,column=1)

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

        path = "./Bingo Games/Bingo Game - "+gameId

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
                f = open(path + "/gameTracks", 'r')
                gameTracksLines = f.read()
                f.close()

                gameTracksLines = gameTracksLines.split("\n")

                [winPoint, title, artist] = checkWin(int(theTicket.ticketId), path, gameTracksLines)

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



# This function returns the point and track in which the ticket will win
def checkWin(ticketId, directory, lines):
    ticketTracks = primes(ticketId)

    lastSong = "INVALID"

    lastArtist = ""

    lastTitle = ""

    if os.path.exists(directory):
        fileLines = lines

        for i in fileLines:
            if len(i) > 4:
                [orderNo, songId, title, artist] = i.split("/#/")

                if int(songId) in ticketTracks:
                    lastSong = orderNo
                    lastTitle = title
                    lastArtist = artist
                    ticketTracks.remove(int(songId))

        if len(ticketTracks) == 0 and lastSong != "INVALID":
            return [int(lastSong),lastTitle,lastArtist]
        else:
            return [0, "", ""]

# This function calculates the prime factors of the prime ticket ID. This will tell exactly what
# tracks were on the ticket
def primes(n):
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
if os.path.exists("./Extra-Files/Icon.ico"):
    root.iconbitmap('./Extra-Files/Icon.ico')

typeface = "Arial"

normalColour = "#ff7200"
altColour = "#d83315"

bannerColour = "#222"

newObject = MainApp(root)
root.mainloop()