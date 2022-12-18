"""
Implementation of the MP3Engine interface to doesn't really
generate an MP3 file
"""
from musicbingo.mp3.editor import MP3Editor, MP3File, MP3FileWriter
from musicbingo.progress import Progress


class MockEditor(MP3Editor):
    """
    Mock MP3Editor implementation
    """

    def _generate(self, destination: MP3FileWriter,
                  progress: Progress) -> None:
        """generate output file, combining all input files"""
        assert destination._metadata is not None
        num_files = float(len(destination._files))
        for index, mp3file in enumerate(destination._files, 1):
            progress.pct = 100.0 * index / num_files
            progress.text = f'Adding {mp3file.filename.name}'
            if progress.abort:
                return
        progress.pct = 100.0

    def play(self, mp3file: MP3File, progress: Progress) -> None:
        """
        play the specified mp3 file
        """
        progress.text = str(mp3file.filename)
        progress.pct = 100.0
