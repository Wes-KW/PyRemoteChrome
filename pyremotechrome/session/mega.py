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


from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support.events import AbstractEventListener
from pyremotechrome.session import Base
from pyremotechrome.session.support.options import FFMpegOptions
from pyremotechrome.session.support.common import Vector
from pyremotechrome.util import Numbers


class _EventListener(AbstractEventListener):
    """DOCSTRING"""

    def __init__(self) -> None:
        super().__init__()

    def after_navigate_to(self, url: str, driver: Base) -> None:
        driver.hide_scrollbar()
        driver.reset_audio()

    def after_navigate_back(self, driver: Base) -> None:
        driver.hide_scrollbar()
        driver.reset_audio()

    def after_navigate_forward(self, driver: Base) -> None:
        driver.hide_scrollbar()
        driver.reset_audio()


class MegaBase(EventFiringWebDriver):

    url_rules: list[str]

    def __init__(
        self,
        id: str,
        scale: Numbers,
        data_dir: str,
        default_url: str,
        size: Vector,
        screen_size: Vector,
        user_agent: str,
        webdriver_exec: str,
        ffmpeg_options: FFMpegOptions,
        allow_rules: list[str] = [],
        deny_rules: list[str] = []
    ) -> None:

        """DOCSTRING"""
        super().__init__(
            Base(
                id,
                scale,
                data_dir,
                default_url,
                size,
                screen_size,
                user_agent,
                webdriver_exec,
                ffmpeg_options,
                allow_rules,
                deny_rules
            ),
            _EventListener()
        )

    def quit(self, clear_cache: bool = False) -> None:
        """Quit the browser"""
        super().wrapped_driver.quit(clear_cache)
