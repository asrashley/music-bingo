Music Bingo is a variation on normal bingo where the numbers are replaced
with songs which the players must listen out for. This program allows
users to generate their own games of Music Bingo using their own music
clips.

This is a fork of the original code, which is available here:

    https://davidwhite478.github.io/portfolio/

Installation
============
Install 'reportlab', 'pydub' and 'mutagen' libraries

    pip install reportlab
    pip install pydub
    pip install mutagen

If you get a "file not found" or "not recognized as an internal or external command"
error for pip, you need to install python-pip or add it to your PATH. 

Install ffmpeg [https://www.ffmpeg.org/]

Must also have ffmpeg installed and on the PATH.

Usage
=====

Creating Music Clips
--------------------

Starting from an existing directory of music (e.g. an album) MusicBingo.py
can generate a set of clips of these songs.

Starting from the directory containing MusicBingo.py

   python MusicBingo.py <directory>

Where <directory> is the name the directory where the original music files are
located. For example:

    python MusicBingo.py "c:\Users\Alex\Music\Amazon MP3\Various"

Alternatively you can just start the MusicBingo application and use the
"Select Directory" near the top of the app.

You need to decide on the duration of the clips and the position in each song
that it will start each clip. 30 seconds seems to be reasonable duration for
each clip. The three start points that seem to generate the best results are
00:00, 00:30 and 01:30. Depending upon the album you will have to try a few
times to find out which one produces the best results.

From the "Available Songs" window, select all the songs you want to clip and
press the "Add Selected Songs" button. The application will produce a clip
for each song in the "Songs in This Game" window.

Now press the "Generate clips" button, which will grab the selected part of
each song into a sub-directory of the "NewClips" directory.

The slow part of the process is having to listen to each clip and re-grab them
if they are not correct. The easiest way is to click the "Remove All Songs"
button to clear the "Songs in This Game" window and then just add the one song
you are adjusting the clip start time.

When are satisfied with the clips, move or copy them into a sub-directory of the
"Clips" directory.

Creating Bingo Games
--------------------
Start the MusicBingo App

    python MusicBingo.py

It will scan all of the clips in the "Clips" directory and show them in the
"Available Songs" window. You can use the "Add Selected Songs" and "Add 5 Random
Songs" buttons to add songs to the "Songs In This Game" window. For each Bingo game
you need at least 30 songs, ideally more than 40 songs.

After you have selected sufficient songs, use the "Ticket Colour" dropdown to select
the colour theme, and "Number Of Tickets" to enter the number of bingo cards you
want in this game.

Pressing the "Generate Bingo Game" will take the songs listed in the "Songs In This
Game" window, suffle them and generate one MP3 file the combines all of these clips.
It will put a "5, 4, 3, 2, 1" count at the beginning and a "swoosh" intersial between
clips.

After it has generated the MP3 file it will generate the bingo cards,
a track listing and a list of when each card will win. All three of these are generated
as PDF files.

The PDF files and the MP3 file will be placed into a sub-directory of the "Bingo Games"
directory. The name of the this directory is specified by the "Game ID" text box.
MusicBingo will automatically generate a unique name, but you can change that to something
else before pressing the "Generate Bingo Game" button.
