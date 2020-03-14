import ssl
import socket


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
