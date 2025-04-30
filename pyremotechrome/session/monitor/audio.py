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


"""
sessaudio is used to manage session's audio

Ensure the following are installed on your device:
    * pulseaudio

NOTE: Run pulsemixer after installed
NOTE: Selenium pid can be obtained by `driver.service.process.pid`.
"""

from __future__ import annotations
from typing import Optional, Callable
from subprocess import run, PIPE
from psutil import Process


class _Tree:

    root: Optional[str]
    children: list[_Tree]
    parent: Optional[_Tree]

    def __init__(self, root: Optional[str]) -> None:
        """DOCSTRING"""
        self.root = root
        self.children = []
        self.parent = None

    def is_empty(self) -> bool:
        """DOCSTRING"""
        return self.root is None

    def __str__(self, d: int = 0) -> str:
        """DOCSTRING"""
        if self.is_empty():
            return ""
        else:
            str_so_far = d * "\t" + self.root
            for subtree in self.children:
                str_so_far += "\n" + subtree.__str__(d + 1)

            return str_so_far

    def append(self, subtree: _Tree) -> None:
        """DOCSTRING"""
        subtree.parent = self
        self.children.append(subtree)

    def find(self, method: Callable = str.__contains__, args: str = "") -> _Tree:
        """DOCSTRING"""
        if self.is_empty():
            return _Tree(None)
        elif method(self.root, args):
            return self
        else:
            for subtree in self.children:
                found = subtree.find(method, args)
                if not found.is_empty():
                    return found

            return _Tree(None)

    def find_all(self, method: Callable = str.__contains__, args: str = "") -> list[_Tree]:
        """DOCSTRING"""
        trees = []
        if self.is_empty():
            pass
        elif method(self.root, args):
            trees.append(self)
        else:
            for subtree in self.children:
                trees.extend(subtree.find_all(method, args))

        return trees


class Audio:
    """DOCSTRING"""

    _pid: int
    _module_index: int

    def __init__(self, pid: int) -> None:
        """DOCSTRING"""
        self._pid = pid
        self._module_index = self._create_sink()

    def _parse(self, lines: list[str], contained: str = "") -> _Tree:
        """DOCSTRING"""
        top = _Tree("top")
        started = False
        for line in lines:
            if contained in line:
                started = True
            if not started:
                continue
            if line.strip() == "":
                continue

            d = 0
            while line[d:] != line.lstrip('\t'):
                d += 1

            curr_tree = top
            while d != 0:
                curr_tree = curr_tree.children[len(curr_tree.children) - 1]
                d -= 1

            curr_tree.append(_Tree(line.lstrip('\t')))

        return top

    def _get_sink_inputs(self) -> _Tree:
        """DOCSTRING"""
        decoded = run(["pacmd", "list-sink-inputs"], stdout=PIPE).stdout.decode()
        lines = decoded.splitlines()
        top = self._parse(lines, "sink input(s)")
        return top

    def _extract_node_by_pid(self, pid: int) -> _Tree:
        """DOCSTRING"""
        top = self._get_sink_inputs()
        node = top.find(args = f'application.process.id = "{pid}"')
        if not node.is_empty():
            return node
        else:
            try:
                p = Process(pid)
                for child in p.children():
                    found = self._extract_node_by_pid(child.pid)
                    if not found.is_empty():
                        return found

            except Exception:
                pass

            return _Tree(None)

    def _extract_nodes_by_pid(self, pid: int) -> list[_Tree]:
        """DOCSTRING"""
        top = self._get_sink_inputs()
        first_node = self._extract_node_by_pid(pid)
        if first_node.is_empty():
            return []

        pid_str = first_node.root
        return top.find_all(args = pid_str)

    def _get_sink_info_by_pid(self, pid: int) -> list[dict[str, str]]:
        """DOCSTRING"""
        nodes = self._extract_nodes_by_pid(pid)
        result = []
        for node in nodes:
            if node.parent is None:
                continue
            if node.parent.parent is None:
                continue

            top = node.parent.parent
            sink_node = top.find(args="sink")
            if sink_node.is_empty():
                continue

            map = {}
            sink_input_id_str = top.root.lstrip()
            sink_input_id_list = sink_input_id_str.lstrip().split(":")
            sink_input_id_list.pop(0)
            sink_input_id = "".join(sink_input_id_list).strip()
            map["sink-input-id"] = sink_input_id

            sink_id_str = sink_node.root
            sink_id_list = sink_id_str.split(" ")
            map["sink-id"] = sink_id_list[1]
            map["sink-name"] = sink_id_list[2][1:-1]
            result.append(map)

        return result

    def _create_sink(self) -> int:
        """DOCSTRING"""
        decoded = run(["pactl", "load-module", "module-null-sink", f"sink_name={str(self._pid)}"], stdout=PIPE).stdout.decode()
        for line in decoded.splitlines():
            if line.isdigit():
                return int(line)

        return -1

    def _move_sink(self, sink_input_id: str) -> None:
        """DOCSTRING"""
        run(["pacmd", "move-sink-input", sink_input_id, str(self._pid)], stdout=PIPE)

    def get_monitor(self) -> str:
        """DOCSTRING"""
        infos = self._get_sink_info_by_pid(self._pid)
        for info in infos:
            if info["sink-name"] != str(self._pid):
                self._move_sink(info["sink-input-id"])

        return f"{self._pid}.monitor"

    def __del__(self) -> None:
        """Destructor"""
        if self._module_index != -1:
            run(["pactl", "unload-module", str(self._module_index)])
