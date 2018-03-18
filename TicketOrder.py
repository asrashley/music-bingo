'''
This command line program takes 1 argument (a game ID number) from the Bingo Games folder,
and returns a list of all the points in which each of the generated tickets will win.
'''

import os
import sys

listOfTickets = []

class TicketWin:

    def __init__(self, winPoint, ticketNumber):
        self.winPoint = winPoint
        self.ticketNumber = ticketNumber

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

def checkWin(ticketId, directory, lines):
    ticketTracks = primes(ticketId)

    lastSong = "INVALID"

    if os.path.exists(directory):
        fileLines = lines

        for i in fileLines:
            if len(i) > 4:
                [orderNo, songId, title, artist] = i.split("/#/")

                if int(songId) in ticketTracks:
                    lastSong = orderNo
                    ticketTracks.remove(int(songId))

        if len(ticketTracks) == 0 and lastSong != "INVALID":
            return int(lastSong)
        else:
            return 0

    else:
        print("Game doesn't exist")
        return -1

gameNumber = sys.argv[1]
path = "./Bingo Games/Bingo Game - "+gameNumber

f = open(path + "/ticketTracks")
ticketFileLines = f.read()
f.close()


ticketFileLines = ticketFileLines.split("\n")
ticketFileLines = ticketFileLines[0:len(ticketFileLines)-1]

f = open(path + "/gameTracks", 'r')
fileLines = f.read()
f.close()

fileLines = fileLines.split("\n")

winningPoints = []

for i in range(0,len(fileLines)):
    winningPoints.append(0)

for line in ticketFileLines:
    [ticketNum, ticketId] = line.split("/")
    winPoint = checkWin(int(ticketId), path, fileLines)

    listOfTickets.append(TicketWin(winPoint,ticketNum))

    winningPoints[winPoint] = winningPoints[winPoint] + 1

print(winningPoints)
place = 0

count = 0

for i in winningPoints:
    if i > 0:
        place = count
        break
    count = count + 1

#print("First Win After " + str(place) + " tracks have played.")

listOfTickets.sort(key=lambda x: x.winPoint, reverse=False)

bestWinnerTickets = []

lastWinPoint = 0

for i in winningPoints:
    if i > 0:
        print("Winners at song " + str(listOfTickets[0].winPoint) + ":")
        start = True
        for j in range(0, i):
            if not start:
                print(",",end="")
            print(str(listOfTickets[0].ticketNumber),end="")
            del listOfTickets[0]
            start = False
        print("")