# Copyright (c) 2024 Wes-KW
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import annotations
from io import TextIOWrapper
from pyvirtualdisplay import Display
from subprocess import Popen, STDOUT
from pyremotechrome.session.monitor.audio import Audio
from pyremotechrome.session.support.options import FFMpegOptions
from pyremotechrome.util import get_utc_timestr, Numbers


class BrowserDisplay(Display):

    width: Numbers
    height: Numbers
    scale: Numbers
    _sink_name: str
    _video_dir: str
    ffmpeg_options: FFMpegOptions
    _ffmpeg_process: Popen
    _log_dir: str
    _log_file: TextIOWrapper

    def __init__(self, width: Numbers, height: Numbers, scale: Numbers, log_dir: str, video_dir: str) -> None:
        """Initialize a monitor with display and audio output"""

        self.width = width
        self.height = height
        self.scale = scale
        self.audio_manager = None
        self._sink_name = ""
        self._video_dir = video_dir
        self._log_dir = log_dir
        self._log_file = None
        self.ffmpeg_options = None
        self._ffmpeg_process = None

        super().__init__(
            visible=False,
            size=(int(width * scale), int(height * scale)),
            bgcolor="black",
            extra_args=["-nocursor"]
        )

    def init_audio(self, browser_pid: int) -> None:
        """Set browser's sink input to the corresponding sink device"""
        self.audio_manager = Audio(browser_pid)
        self._sink_name = self.audio_manager.get_monitor()

    def init_ffmpeg(self, ffmpeg_options: FFMpegOptions) -> None:
        self.ffmpeg_options = ffmpeg_options

    def start_capturing(self, x: Numbers, y: Numbers, width: Numbers, height: Numbers) -> None:

        """Start capturing the screen"""
        if self._ffmpeg_process is not None:
            return
        if self.ffmpeg_options is None:
            return

        fg = self.ffmpeg_options
        frame_per_second = fg.frame_per_second
        queue_size_multiplier = fg.queue_size_multiplier
        queue_size = queue_size_multiplier * frame_per_second
        screen_id = self.env()["DISPLAY"]
        
        proc_args = [fg.ffmpeg_exec, "-probesize", str(fg.probesize)]

        proc_args.extend([
            "-video_size", f"{width}x{height}", "-framerate", str(fg.frame_per_second), "-f",
            "x11grab", "-thread_queue_size", str(queue_size), "-i", f"{screen_id}+{x},{y}",
            "-r", str(queue_size_multiplier)
        ])

        # audio
        proc_args.extend([
            "-itsoffset", str(fg.audio_itsoffset), "-f", "pulse", "-i", f"{self._sink_name}"
        ])

        # combine audio and image and separate output
        proc_args.extend([
            "-f", "hls", "-hls_time", str(fg.segment_time), "-reset_timestamps",
            "1", "-g", str(frame_per_second * fg.segment_time), "-sc_threshold", "0",
            "-force_key_frames", f"expr:gte(t,n_forced*{fg.segment_time})", "-vf",
            "drawbox=x=0:y=0:w=iw:h=6:color=white@1:t=fill", "-c:v", "libx264", "-preset",
            "ultrafast", "-b:v", str(fg.maxrate), "-maxrate", str(fg.maxrate), "-bufsize",
            str(fg.bufsize), "-pix_fmt", "yuv420p", "-crf", str(fg.constant_rate_factor), "-c:a",
            "aac", "-preset", "ultrafast", "-tune", "zerolatency", f"{self._video_dir}/.m3u8"
        ])

        self._log_file = open(f"{self._log_dir}/{get_utc_timestr('%d.%b.%Y__%H_%M_%S')}.log", "w")
        self._ffmpeg_process = Popen(proc_args, stdout=self._log_file, stderr=STDOUT)

    def stop_capturing(self) -> None:
        """DOCSTRING"""
        if self._ffmpeg_process is not None:
            self._ffmpeg_process.terminate()
            self._ffmpeg_process.wait()
            self._ffmpeg_process = None
            self._log_file.close()

    def restart_capturing(self, x: Numbers, y: Numbers, width: Numbers, height: Numbers) -> None:
        """DOCSTRING"""
        if self._ffmpeg_process is not None:
            self.stop_capturing()
            self.start_capturing(x, y, width, height)

    def __del__(self) -> None:
        self.stop_capturing()
        super().stop()
        self._log_file.close()
        del self.audio_manager
