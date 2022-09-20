# App Installation

MusicBingo is written in [Python 3](https://www.python.org/). It requires
Python v3.6 or higher. It is recommended to install the 64bit version if your
operating system is 64bit. If the 32bit version of Python is used, you will
find that the application will run out of memory at about 40 clips in a game.

Check if [PIP](https://pypi.org/project/pip/) has been installed:

    pip3 help

If this says command not found, you will need to install PIP. See
[PIP installation instructions](https://pip.pypa.io/en/stable/installing/).
Make sure to use Python v3 when installing PIP, otherwise it will install PIP
into the Python v2 installation directory.

If you still get a "file not found" or "not recognized as an internal or
external command" error for pip, you might need to add it to your PATH.

To avoid the Python libraries used by MusicBingo conflicting with other Python
libraries installed on your computer, it is recommended to use a virtual
environment for running MusicBingo.

As a one-time step, create a directory that contains the virtual Python
environment (in this example called "virt"):

    python -m venv virt

Before installing any libraries and before each time you want to run the app,
active the virtual environment.

On Unix:

    . ./virt/bin/activate

On Windows:

    virt\Scripts\activate

Note that this only activates in the current Unix shell / Windows command
prompt. You need to run the activate script every time you start a new
shell / command prompt.

Install all the required Python libraries:

    pip3 install -r requirements.txt

Install [ffmpeg](https://www.ffmpeg.org/) and make sure the ffmpeg executable is
in your PATH.

    ffmpeg -version

If you get a "file not found" or "not recognized as an internal or external
command" error for ffmpeg, you need to add it to your PATH.

If when you try to start MusicBingo you get an import error for tkinter, you
need to install Tkinter for Python 3.

On Debian / Ubuntu:

    sudo apt install python3-tk

On Centos:

    # note the "36" part refers to the version of Python installed and
    # might be different on your machine
    sudo yum -y install python36u-tkinter

On Windows, make sure the "tcl/tk and IDLE" optional feature is enabled when
installing Python. You can add tcl/tk to an existing install using the "Change"
option in:

    Control Panel -> Programs -> Programs and Features

For macOS see [https://www.python.org/download/mac/tcltk/]

MusicBingo has optional support for playing music files from within the app.
It allows playback of a clip by double-clicking on its title.

This feature requires either ffplay (which is part of ffmpeg) to be in the
PATH, or an additional library "pyaudio" needs to be installed.

Check if ffplay is available:

    ffplay -version

If that fails, you can try installing pyaudio:

    pip3 install pyaudio

On Linux you might need to install the Alsa development libraries:

    sudo apt-get install -y python3-dev libasound2-dev

When using Windows, the pyaudio library is not available as a
pre-compiled package. If you wish to use pyaudio, you might have to
install some [Visual Studio components](https://visualstudio.microsoft.com/downloads/)
so that pyaudio is able to compile itself during installation.

An alternative approach is to use
[Anaconda](https://www.anaconda.com/products/individual) or
[miniconda](https://docs.conda.io/en/latest/miniconda.html) which has pre-compiled
versions of pyaudio. In a conda shell:

    pip install -r requirements.txt
    conda install pyaudio

To check which MP3 libraries have been successfully installed and detected:

    python -m musicbingo.mp3


# Usage

## Running the application

Start the MusicBingo App

    python -m musicbingo

It will scan all of the clips in the "Clips" directory and show them in the
"Available Songs" window. You can use the "Add Selected Songs" and "Add 5 Random
Songs" buttons to add songs to the "Songs In This Game" window. For each Bingo
game you need at least 30 songs, ideally more than 40 songs.

Pressing the "Generate Bingo Game" will take the songs listed in the
"Songs In This Game" window, shuffle them and generate one MP3 file the
combines all of these clips. It will put a "5, 4, 3, 2, 1" count at the
beginning and a "swoosh" interstitial between clips.

After it has generated the MP3 file it will generate the Bingo cards, a track
listing and a list of when each card will win. All three of these are generated
as PDF files.

The PDF files and the MP3 file will be placed into a sub-directory of the
"Bingo Games" directory.

## Creating Music Clips

Starting from an existing directory of music (e.g. an album) MusicBingo.py
can generate a set of clips of these songs.

Starting from the directory containing musicbingo source code:

    python -m musicbingo --clip **directory**

Where **directory** is the name of the directory where the original music
files are located. For example:

    python -m musicbingo --clip "c:\Users\Alex\Music\Amazon MP3\Various"

Alternatively you can just start the MusicBingo application and use the
"Select Clip Source" menu item from the "File" menu.

You need to decide on the duration of the clips and the position in each song
that it will start each clip. 30 seconds seems to be reasonable duration for
each clip. The three start points that seem to generate the best results are
01:00, 00:30 and 01:30. Depending upon the album you will have to try a few
times to find out which one produces the best results.

From the "Available Songs" window, select all the songs you want to clip and
press the "Add Selected Songs" button.

Now press the "Generate clips" button, which will grab the selected part of
each song listed in the in the "Songs in This Game" window into a sub-directory
of the "NewClips" directory.

The slow part of the process is having to listen to each clip and re-grab them
if they are not correct. The easiest way is to click the "Remove All Songs"
button to clear the "Songs in This Game" window and then just add the one song
you are adjusting the clip start time.

You can listen to the clipped version of the song by double clicking on the
song title in the right hand song list window.

When are satisfied with the clips, move or copy them into a sub-directory of the
"Clips" directory.

## Creating Bingo Games

Start the MusicBingo App

    python -m musicbingo

It will scan all of the clips in the "Clips" directory and show them in the
"Available Songs" window. You can use the "Add Selected Songs" and "Add 5 Random
Songs" buttons to add songs to the "Songs In This Game" window. For each Bingo
game you need at least 30 songs, ideally more than 40 songs.

After you have selected sufficient songs, use the "Ticket Colour" dropdown to
select the colour theme, and "Number Of Tickets" to enter the number of bingo
cards you want in this game.

MusicBingo.py will automatically generate a unique ID for each bingo game and
show it in the "Game ID" text box. You can modify this name if you wish. This
ID is used as the name of the directory in the "Bingo Games" folder that will
be created when generating the game. Also each ticket will contain the ID of
the game.

Pressing the "Generate Bingo Game" will take the songs listed in the
"Songs In This Game" window, shuffle them and generate one MP3 file the
combines all of these clips. It will put a "5, 4, 3, 2, 1" count at the
beginning and a "swoosh" interstitial between clips.

After it has generated the MP3 file it will generate the Bingo cards, a track
listing and a list of when each card will win. All three of these are generated
as PDF files.

The PDF files and the MP3 file will be placed into a sub-directory of the
"Bingo Games" directory.

## Creating Musical Quiz

There is an experimental feature that allows MusicBingo to generate a music
quiz, where contestants are required to work out title and/or artist from a
short clip.

    python -m musicbingo --quiz

Up to 10 tracks can then be added to the "Songs In This Game" window. It will
put a spoken number before each clip and the "swoosh" interstitial.
