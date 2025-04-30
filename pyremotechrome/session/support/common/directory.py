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
from os import makedirs
from os.path import exists
from shutil import rmtree

class Directory():
    
    root: str
    directory: dict[str, str]

    def __init__(self, root: str, create: bool = True) -> None:
        """Initialize a directory"""
        self.root = root
        self.directory = {}
        if create:
            self._create_dir(root)

    def _create_dir(self, directory: str) -> None:
        """Create directory recursively
        
        Preconditions:
            - key in self.dir
        """
        if not exists(directory):
            makedirs(directory)

    def set_dir(self, key: str, relative_path: str, create: bool = True) -> str:
        """Create a directory with the key and return the relative and absolute path."""
        self.directory[key] = relative_path
        if create:
            self._create_dir(self.get_abs_dir(key))

        return self.get_dir(key), self.get_abs_dir(key)

    def get_dir(self, key: str) -> str:
        """DOCSTRING"""
        return self.directory[key]

    def get_abs_dir(self, key: str) -> str:
        """Return absolute path specified by key"""
        return f"{self.root}/{self.directory[key]}"

    def remove_dir(self) -> None:
        """Remove the whole data dir"""
        if exists(self.root):
            rmtree(self.root)
