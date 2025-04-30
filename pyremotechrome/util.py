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
from re import search
from base64 import b64decode, b64encode
from typing import Any
from typing import Union
from datetime import datetime
from pytz import timezone
from urllib.parse import urlparse


Numbers = Union[float, int]


def get_utc_timestamp() -> float:
    """DOCSTRING"""
    return datetime.now(timezone("UTC")).timestamp()


def get_utc_timestr(format: str = "%d/%b/%Y %H.%M.%S") -> str:
    return datetime.now(timezone("UTC")).strftime(format)


def print_exception(e: Union[Exception, str]) -> None:
    """DOCTSTRING"""
    
    if isinstance(e, Exception):
        e = str(e)

    timestr = get_utc_timestr()
    print(f"127.0.0.1 - - [{timestr}] ERROR: {e.capitalize()}")


def get_value_in_dict(map: dict, key: Any) -> Any:
    """
    Return the value of a key in a dictionary.
    In the key is not found, return None.
    """

    if key in map:
        return map[key]
    else:
        return None


def get_absolute_path(origin: str, relative_path: str) -> str:
    """DOCSTRING"""
    org_parsed = urlparse(origin)
    rel_parsed = urlparse(relative_path)
    if rel_parsed.scheme == "http" or rel_parsed.scheme == "https":
        return relative_path
    elif relative_path.startswith("//"):
        return f"{org_parsed.scheme}:{relative_path}"
    elif relative_path.startswith("/"):
        origin_host = org_parsed.hostname
        if org_parsed.port is not None:
            origin_host += f":{org_parsed.port}"
        return f"{org_parsed.scheme}://{origin_host}{relative_path}"
    else:
        origin_host = org_parsed.hostname
        if org_parsed.port is not None:
            origin_host += f":{org_parsed.port}"

        origin_path = org_parsed.path
        if not origin_path.endswith("/"):
            origin_path_obj = origin_path.split("/")
            origin_path_obj.pop()
            origin_path = "/" + "/".join(origin_path_obj) + "/"

        return f"{org_parsed.scheme}://{origin_host}{origin_path}{relative_path}"


def filter_rules(arg: str, allow_rules: list[str], deny_rules: list[str], suppress: bool = False) -> None:
    """DOCSTRING"""
    filter_arg = ""
    for rule in allow_rules:
        if search(rule, arg) is not None:
            filter_arg = arg
            break

    for rule in deny_rules:
        if search(rule, arg) is not None:
            filter_arg = ""
            break

    if filter_arg == "" and not suppress:
        raise Exception("ARGUMENT_DENIED")

def btoa(decoded: str) -> str:
    """Encode ASCII string"""
    return b64encode(decoded.encode("utf-8")).decode('utf-8')

def atob(encoded: str) -> str:
    """Decode base64 string"""
    return b64decode(encoded).decode("utf-8")
