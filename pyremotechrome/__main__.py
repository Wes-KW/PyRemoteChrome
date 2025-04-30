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


from typing import Generator, Any
from os.path import dirname, realpath
from subprocess import Popen, PIPE
from pyremotechrome.config import Conf


c = Conf()
__ROOT__ = f"{dirname(realpath(__file__))}"
__PYTHON_EXEC__ = c.server.python_executable_path


def readline_from_server() -> Generator[list[str], Any, None]:
    """Start the server"""
    proc_args = [__PYTHON_EXEC__, f"{__ROOT__}/server/server.py"]
    proc = Popen(proc_args, stdout=PIPE, universal_newlines=True)
    for stdout in iter(proc.stdout.readlines, ""):
        yield stdout

    proc.stdout.close()
    code = proc.wait()
    if code:
        raise Exception("Server exited unexceptedly.")

if __name__ == "__main__":
    for line in readline_from_server():
        print(line, end="")
