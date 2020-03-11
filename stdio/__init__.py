import ssl
import socket


def connect(ip, port, cmd):
    sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    sock.connect((ip, port))

    sock.sendall('cmd /{} http/1.0\n\n'.format(cmd).encode())
    assert('HTTP/1.0 200 OK\n\n' == sock.recv(17).decode())

    return sock
