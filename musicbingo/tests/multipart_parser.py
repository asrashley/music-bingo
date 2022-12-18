"""
Parser for HTTP multipart/mixed streams
"""
from enum import IntEnum
from typing import Dict, Generator, List

import requests

MultipartMixedParserGenerator = Generator[bytes, None, None]

class MultipartMixedParser:
    """
    Parser to a multipart/mixed stream
    """
    class State(IntEnum):
        """
        State of parsing
        """
        BOUNDARY = 0
        HEADERS = 1
        BODY = 2

    def __init__(self, boundary: bytes, source: requests.Response) -> None:
        self.source = source
        self.mid_boundary = b'--' + boundary
        self.end_boundary = b'--' + boundary + b'--'

    def parse(self) -> MultipartMixedParserGenerator:
        """
        Parse the stream
        """
        headers: Dict[str, str] = {}
        body: List[bytes] = []
        todo: int = 0
        state = self.State.BOUNDARY
        for data in self.source.iter_lines():
            if state == self.State.BOUNDARY:
                if data == b'':
                    continue
                if len(data) < len(self.mid_boundary):
                    return
                if data == self.end_boundary:
                    return
                if data != self.mid_boundary:
                    raise ValueError(b'Expected boundary: "' + self.mid_boundary +
                                     b'" but got "' + data + b'"')
                headers = {}
                state = self.State.HEADERS
            elif state == self.State.HEADERS:
                if data == b'':
                    state = self.State.BODY
                    todo = int(headers['Content-Length'], 10)
                    body = []
                    continue
                name, value = str(data, 'utf-8').split(':')
                headers[name] = value.strip()
            elif state == self.State.BODY:
                assert todo > 0
                body.append(data)
                todo -= len(data)
                if todo < 1:
                    yield b''.join(body)
                    todo = 0
                    state = self.State.BOUNDARY
