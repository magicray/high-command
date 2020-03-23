import ssl
import socket
import sqlite3
import urllib.request


class Cmd():
    def __init__(self, ip, port, cmd):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock = ssl.wrap_socket(self._sock)
        self._sock.connect((ip, port))

        self.stdin = self._sock.makefile('w')
        self.stdout = self._sock.makefile('r')

        self.stdin.write('cmd /{} http/1.0\n\n'.format(cmd))
        self.stdin.flush()

        for line in self.stdout:
            if not line.strip():
                break

    def __del__(self):
        self._sock.close()


def fetch(ip, port, filename):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = 'https://{}:{}/{}'.format(ip, port, filename)
    return urllib.request.urlopen(url, context=ctx).read()


class SQLite():
    def __init__(self, name):
        self.conn = None
        self.path = name + '.sqlite3'

    def __call__(self, query, *params):
        if self.conn is None:
            self.conn = sqlite3.connect(self.path)

        return self.conn.execute(query, params)

    def commit(self):
        if self.conn:
            self.conn.commit()
            self.rollback()

    def rollback(self):
        if self.conn:
            self.conn.rollback()
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.rollback()
