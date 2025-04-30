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



from typing import Any
from os.path import expanduser
from json import load as json_load

class _Dict(object):

    def __init__(self, *args, **kwargs) -> None:
        """DOCSTRING"""
        for key in kwargs:
            value = kwargs[key]
            self.__setattr__(key, value)

        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError("None key arguments must be dictionary")

            for key in arg:
                value = arg[key]
                self.__setattr__(key, value)

    def __setattr__(self, key: Any, value: Any, depth: int = 0) -> None:
        """DOCSTRING"""
        if isinstance(value, dict):
            self.__setattr__(key, _Dict(value), depth + 1)
        else:
            super().__setattr__(key, value)



class Conf(_Dict):
    
    def __init__(self) -> None:
        conf_path = expanduser(f"~/.config/pyremotechrome/pyremotechrome.json")
        with open(conf_path) as f:
            parsed = json_load(f)
            super().__init__(parsed)
