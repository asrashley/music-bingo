"""
Implementation of the MP3Engine interface using ffmpeg and ffplay
"""
import math
import subprocess
import time
import socketserver
import threading
from typing import Iterable, List, Optional, Tuple, cast

import psutil # type: ignore

from musicbingo.duration import Duration
from musicbingo.mp3.editor import MP3Editor, MP3File, MP3FileWriter
from musicbingo.progress import Progress


class ProgressRequestHandler(socketserver.DatagramRequestHandler):
    """
    Class that handles one progress message from ffmpeg.
    Each event contains one or more lines of key-value pairs, where each
    pair is separated by an equals.
    """

    def handle(self):
        server = cast(ProgressUDPServer, self.server)
        for line in str(self.request[0], 'ascii').splitlines():
            line = line.split('=')
            # 'out_time_ms' is actually in microseconds and was renamed
            # to 'out_time_us'. See https://trac.ffmpeg.org/ticket/7345
            if len(line) == 2 and line[0] in ['out_time_us', 'out_time_ms']:
                pos = int(line[1], 10) / 1000.0
                server.progress.pct = 100.0 * pos / float(self.server.total_duration)


class ProgressUDPServer(socketserver.UDPServer):
    """
    UDP server that will receive progress messages from ffmpeg
    """

    def __init__(self, server_address: Tuple[str, int], progress: Progress,
                 total_duration: int):
        super().__init__(server_address, ProgressRequestHandler)
        self.progress = progress
        self.total_duration = total_duration


class FfmpegEditor(MP3Editor):
    """MP3Editor implementation using ffmpeg"""

    def _generate(self, destination: MP3FileWriter,
                  progress: Progress) -> None:
        """generate output file, combining all input files"""
        assert destination._metadata is not None
        num_files = len(destination._files)
        if num_files == 0:
            print('no files to encode')
            return
        args: List[str] = ['ffmpeg', '-hide_banner']
        if not self.debug:
            args += ['-loglevel', 'panic', '-v', 'quiet']
        concat = self.append_input_files(args, destination._files)
        progress.text = f'Encoding MP3 file "{destination.filename.name}"'
        mdata = [f'title={destination._metadata.title}']
        if destination._metadata.artist:
            mdata.append(f'artist={destination._metadata.artist}')
        if destination._metadata.album:
            mdata.append(f'album={destination._metadata.album}')
        if num_files > 1:
            args += [
                '-filter_complex',
                self.build_filter_argument(destination, concat)
            ]
            if destination.headroom is not None:
                args[-1] += ';' + self.build_headroom_filter(destination.headroom, 'outa', 'outb')
                args += ['-map', '[outb]']
            else:
                args += ['-map', '[outa]']
        elif destination.headroom is not None:
            args += ['-af', f'loudnorm=tp=-{destination.headroom}']
        for item in mdata:
            args += ['-metadata', item]
        args += [
            '-ab', f'{destination._metadata.bitrate}k',
            '-ac', str(destination._metadata.channels),
            '-ar', str(destination._metadata.sample_rate),
            '-acodec', 'mp3',
            '-threads', '0',
            '-f', 'mp3',
            '-y', str(destination.filename),
        ]
        if self.debug:
            print(args)
        dest_dir = destination.filename.parent
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        self.run_command_with_progress(args, progress, duration=int(destination.duration))

    @staticmethod
    def append_input_files(args: List[str], files: Iterable[MP3File]) -> bool:
        """
        Append each file to the ffmpeg command arguments
        """
        concat = True
        for mp3file in files:
            if mp3file.start is not None and mp3file.start > 0:
                args += ['-ss', str(mp3file.start / 1000.0)]
            if mp3file.end is not None:
                if mp3file.start is None:
                    duration = mp3file.end
                else:
                    duration = mp3file.end - mp3file.start
                if mp3file.metadata is None or duration != int(mp3file.metadata.duration):
                    args += ["-t", str(duration / 1000.0)]
            args.append('-i')
            args.append(str(mp3file.filename))
            if mp3file.overlap > 0:
                concat = False
        return concat

    def build_filter_argument(self, destination: MP3FileWriter, concat: bool) -> str:
        """
        generate the value for the "-filter_complex" ffmpeg command line option.
        """
        filter_complex: List[str] = []
        num_files = len(destination._files)
        for index, mp3file in enumerate(destination._files):
            if concat:
                filter_complex.append(f'[{index}:a]')
                continue
            if index == 0:
                continue
            first = 'a{0}'.format(index - 1) # pylint: disable=consider-using-f-string
            second = str(index)
            if index == 1:
                first = '0'
            dest = f'a{index}'
            if index == (num_files - 1):
                dest = 'outa'
            if mp3file.overlap < 100:
                num_samples = destination._metadata.sample_rate // 10
            else:
                num_samples = mp3file.overlap * destination._metadata.sample_rate // 1000
            if mp3file.headroom is not None:
                third = f'n{index}'
                filter_complex.append(
                    self.build_headroom_filter(mp3file.headroom, second, third))
                second = third
            crossfade = f'acrossfade=ns={num_samples}:c1=tri:c2=tri'
            filter_complex.append(f'[{first}][{second}]{crossfade}[{dest}]')
        if concat:
            filter_complex.append(f'concat=n={num_files}:v=0:a=1[outa]')
            return ''.join(filter_complex)
        return ';'.join(filter_complex)

    @staticmethod
    def build_headroom_filter(headroom: int, input_pad: str, output_pad: str) -> str:
        """
        generate the ffmpeg filter argument for loudness adjustment
        """
        pct = min(math.floor(math.pow(10, -headroom / 10.0) * 100.0), 100.0) / 100.0
        # TODO: provide an option to select the loudness / dynamic range algorithm
        return f'[{input_pad}]dynaudnorm=p={pct}[{output_pad}]'

    def run_command_with_progress(self, args: List[str], progress: Progress,
                                  duration: int) -> None:
        """
        Start a new thread to monitor progress and start a process running
        specified command and wait for it to complete.
        Can be terminated by setting progress.abort to True
        """
        progress_srv = ProgressUDPServer(
            ('localhost', 0), progress, duration)
        progress_thread = threading.Thread(target=progress_srv.serve_forever, daemon=True)
        args.insert(1, '-progress')
        args.insert(
            2,
            f'udp://{progress_srv.server_address[0]}:{progress_srv.server_address[1]}')
        try:
            progress_thread.start()
            self.run_command(args, progress)
        finally:
            progress_srv.shutdown()
            progress_thread.join()

    def run_command(self, args: List[str], progress: Progress, start: int = 0,
                    duration: Optional[int] = None) -> None:
        """
        Start a new process running specified command and wait for it to complete.
        :duration: If not None, the progress percentage will be updated based upon
        the amount of time the process has been running.
        Can be terminated by setting progress.abort to True
        """
        progress.pct = 0.0
        start_time = time.time()

        with subprocess.Popen(args, shell=False) as proc:
            done = False
            rcode: Optional[int] = None
            while not done and not progress.abort:
                if duration is not None:
                    elapsed = min(duration, 1000.0 * (time.time() - start_time))
                    progress.pct = 100.0 * elapsed / float(duration)
                    progress.pct_text = Duration(int(elapsed) + start).format()
                if rcode is None:
                    rcode = proc.poll()
                if rcode is not None:
                    try:
                        proc.wait(0.25)
                        done = True
                    except subprocess.TimeoutExpired:
                        pass
                else:
                    time.sleep(0.25)
            if progress.abort and not done:
                self.kill_process(proc.pid)
                proc.wait()
        progress.pct = 100.0

    def play(self, mp3file: MP3File, progress: Progress) -> None:
        """play the specified mp3 file"""
        args: List[str] = ['ffplay', '-nodisp', '-autoexit', '-hide_banner',
                           '-loglevel', 'panic', '-v', 'quiet']
        duration = int(mp3file.metadata.duration)
        start: int = 0
        if mp3file.start is not None:
            start = mp3file.start
            assert isinstance(start, int)
            duration -= mp3file.start
            args += ['-ss', str(mp3file.start / 1000.0)]
        if mp3file.end is not None:
            duration = mp3file.end
            if mp3file.start is not None:
                duration -= mp3file.start
            args += ['-t', str(duration / 1000.0)]
        args += ['-i', str(mp3file.filename)]
        assert isinstance(start, int)
        self.run_command(args, progress, duration=duration, start=start)

    @staticmethod
    def kill_process(proc_pid: int) -> None:
        """
        Kill a process and all of its children
        """
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
