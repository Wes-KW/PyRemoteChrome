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
This is an api server to control RemoteSession

// Use this as url_obj for debugging:
// url_obj = {"method": "GET", "url": url, "response": response}

TODO: Try using a json file for configuration
TODO: Try using a log file to log errors, and actions
"""

from __future__ import annotations
from os.path import realpath
from os.path import dirname
from json import dumps as json_dumps
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
from pyremotechrome.session.support.common import Result
from pyremotechrome.server.manager import Manager
from pyremotechrome.config import Conf
from pyremotechrome.util import get_value_in_dict


__ROOT__ = dirname(dirname(realpath(__file__)))
__ICON_PATH__ = f"{__ROOT__}/server/favicon.ico"
__WAVE_DIR__ = f"{__ROOT__}/wave/"

# load the following from config.json
c = Conf()

# Server
url = c.server.url
__SERVER_SCHEME__ = url.scheme
__SERVER_NAME__ = url.name
__SERVER_PORT__ = url.port

ips = set(url.ips)
ips.add(f"{url.name}:{url.port}")
__SERVER_NAMES__ = set(url.ips)

# Server Implementation
_sess: Manager


class ApiHandler(BaseHTTPRequestHandler):
    """Api server handler"""

    def __init__(self, *args, **kwargs):
        """DOCSTRING"""
        super().__init__(*args, **kwargs)

    def send_h(self, code: int, content_type: str) -> None:
        """DOCSTRING"""
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def url_check(self, url: str) -> None:
        """DOCSTRING"""
        parsed = urlparse(url)
        path = parsed.path
        scheme = parsed.scheme
        server = get_value_in_dict(parse_qs(parsed.query), "url")
        is_http = scheme == "http" or scheme == "https"
        if server is not None:
            parsed2 = urlparse(server[0])
            port = parsed2.port
            if port is None:
                port = 80
            server = f"{parsed2.hostname}:{port}"
        else:
            server = ""
        if any(server == servername for servername in __SERVER_NAMES__):
            # Prevent loading website recursively
            self.send_h(200, "application/json")
            response = Result(False, "RECURSIVE_LOAD_ERROR").to_dict()
            url_obj = {"response": response}
            message_str = json_dumps(url_obj)
            self.wfile.write(bytes(message_str, "utf8"))
        elif is_http and path == "/api":
            # Allow APIs
            self.send_h(200, "application/json")
            response = _sess.call_from_url(url).to_dict()
            url_obj = {"response": response}
            message_str = json_dumps(url_obj)
            self.wfile.write(bytes(message_str, "utf8"))

        elif is_http and path == "/favicon.ico":
            # Allow favicon.ico
            self.send_h(200, "image/x-icon")
            with open(__ICON_PATH__, 'rb') as f:
                self.wfile.write(f.read())

        else:
            # Deny permission to other files
            self.send_h(403, "text/plain")

    def get_url(self):
        """DOCSTRING"""
        return f"{__SERVER_SCHEME__}://{__SERVER_NAME__}:{__SERVER_PORT__}{self.path}"

    def do_GET(self):
        """DOCSTRING"""
        url = self.get_url()
        self.url_check(url)

    def do_POST(self):
        """DOCSTRING"""
        pass


if __name__ == "__main__":
    _sess = Manager()
    with HTTPServer(('', __SERVER_PORT__), ApiHandler) as server:
        server.serve_forever()
