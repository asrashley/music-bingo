"""
Used for running tests against an HTTP server rather than
the Flask test client.

Based upon
https://raw.githubusercontent.com/jarus/flask-testing/master/flask_testing/utils.py
"""

import multiprocessing
import socket
import socketserver
import time
import unittest
from urllib.parse import urlparse

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
        return 'http://localhost:%s' % self._port_value.value

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
                    "Failed to start the server after %d seconds. " % self.LIVESERVER_TIMEOUT
                )

            if self._can_ping_server():
                break

    def worker(self, port_value: multiprocessing.Value):
        """
        Thread that it used to start the Flask app
        """
        # Based on solution: http://stackoverflow.com/a/27598916
        # Monkey-patch the server_bind so we can determine the port bound by Flask.
        # This handles the case where the port specified is `0`, which means that
        # the OS chooses the port. This is the only known way (currently) of getting
        # the port out of Flask once we call `run`.
        original_socket_bind = socketserver.TCPServer.server_bind
        def socket_bind_wrapper(self):
            original_socket_bind(self)

            # Get the port and save it into the port_value, so the parent process
            # can read it.
            (_, port) = self.socket.getsockname()
            port_value.value = port
            socketserver.TCPServer.server_bind = original_socket_bind

        # Get the app
        app = self.create_app()
        # self._configured_port = self.app.config.get('LIVESERVER_PORT', 5000)

        # We need to create a context in order for extensions to catch up
        # pylint: disable=attribute-defined-outside-init
        self._ctx = app.test_request_context()
        self._ctx.push()

        socketserver.TCPServer.server_bind = socket_bind_wrapper # type: ignore
        app.run(port=port_value.value, use_reloader=False, debug=True)

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
                    "Unsupported server url scheme: %s" % parts.scheme
                )

        return host, port

    def _post_teardown(self):
        if getattr(self, '_ctx', None) is not None:
            self._ctx.pop()
            del self._ctx

    def _terminate_live_server(self):
        if self._process:
            self._process.terminate()
