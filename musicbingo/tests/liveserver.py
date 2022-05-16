"""
Used for running tests against an HTTP server rather than
the Flask test client.

Based upon
https://raw.githubusercontent.com/jarus/flask-testing/master/flask_testing/utils.py
"""

import multiprocessing
import os
import socket
import time
from typing import ContextManager
import unittest
from urllib.parse import urlparse

class IntValueType:
    """
    Type hint for multiprocessing.Value when used to store an int
    """
    def __setattr__(self, name: str, value: int) -> None:
        ...

    def __getattr__(self, name: str) -> int:
        ...

    # pylint: disable=no-self-use
    def get_lock(self) -> ContextManager[None]:
        """
        Lock multiprocessing.Value so that this process has exclusive access
        """

class LiveServerTestCase(unittest.TestCase):
    """
    Base class for testing using a live HTTP server
    """
    LIVESERVER_TIMEOUT: int = 5

    def create_app(self):
        """
        Create your Flask app here, with any
        configuration you need.
        """
        raise NotImplementedError

    # pylint: disable=arguments-differ
    def __call__(self, result=None):
        """
        Does the required setup, doing it here means you don't have to
        call super.setUp in subclasses.
        """

        # pylint: disable=attribute-defined-outside-init
        self._port_value = multiprocessing.Value('i', 0)

        try:
            self._spawn_live_server()
            super().__call__(result)
        finally:
            self._post_teardown()
            self._terminate_live_server()

    def get_server_url(self):
        """
        Return the url of the test server
        """
        return f'http://localhost:{self._port_value.value}'

    def _spawn_live_server(self):
        # pylint: disable=attribute-defined-outside-init
        self._process = None
        # port_value = self._port_value

        self._process = multiprocessing.Process(
            target=self.worker, args=(self._port_value,)
        )

        self._process.start()

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time)
            if elapsed_time > self.LIVESERVER_TIMEOUT:
                raise RuntimeError(
                    f"Failed to start the server after {self.LIVESERVER_TIMEOUT} seconds."
                )

            if self._can_ping_server():
                break
            time.sleep(0.25)

    def worker(self, port_value: IntValueType):
        """
        Thread that it used to start the Flask app
        """

        # Get the app
        app = self.create_app()
        # self._configured_port = self.app.config.get('LIVESERVER_PORT', 5000)

        # We need to create a context in order for extensions to catch up
        # pylint: disable=attribute-defined-outside-init
        self._ctx = app.test_request_context()
        self._ctx.push()

        with port_value.get_lock():
            port = port_value.value
        # Based on solution: http://stackoverflow.com/a/27598916
        if port == 0:
            # Chose a random available port by binding to port 0
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', 0))
            sock.listen()
            # Tells the underlying WERKZEUG server to use the socket we just created
            os.environ['WERKZEUG_SERVER_FD'] = str(sock.fileno())
            (_, port) = sock.getsockname()
            with port_value.get_lock():
                port_value.value = port
        app.run(port=port, use_reloader=False, debug=True)

    def _can_ping_server(self):
        host, port = self._get_server_address()
        if port == 0:
            # Port specified by the user was 0, and the OS has not yet assigned
            # the proper port.
            return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            success = True
        except socket.error:
            success = False
        finally:
            sock.close()

        return success

    def _get_server_address(self):
        """
        Gets the server address used to test the connection with a socket.
        Respects both the LIVESERVER_PORT config value and overriding
        get_server_url()
        """
        parts = urlparse(self.get_server_url())

        host = parts.hostname
        port = parts.port

        if port is None:
            if parts.scheme == 'http':
                port = 80
            elif parts.scheme == 'https':
                port = 443
            else:
                raise RuntimeError(
                    f"Unsupported server url scheme: {parts.scheme}"
                )

        return host, port

    def _post_teardown(self):
        if getattr(self, '_ctx', None) is not None:
            self._ctx.pop()
            del self._ctx

    def _terminate_live_server(self):
        if self._process:
            self._process.terminate()

    def assert200(self, response):
        """
        Assert that the response has an HTTP 200 status code
        """
        self.assertEqual(response.status_code, 200)

    # pylint: disable=invalid-name
    def assertNoCache(self, response):
        """
        Assert that "do not cache" headers were set in response
        """
        cache_control = response.headers['Cache-Control']
        self.assertIn('max-age=0', cache_control)
        self.assertIn('no-cache', cache_control)
        self.assertIn('no-store', cache_control)
        self.assertIn('must-revalidate', cache_control)
