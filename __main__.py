import sys
import socket
import select
import argparse


def cmd(ip, port, cmd):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    sock.sendall(cmd.encode() + b'\n')

    fd_list = [sock, 0]
    while fd_list and sock:
        readable, _, error = select.select(fd_list, [], [], 0.01)

        if sock in readable:
            buf = sock.recv(2**16)
            if not buf:
                fd_list = None
            else:
                print(buf)

        if 0 in readable:
            buf = sys.stdin.buffer.read()
            if not buf:
                fd_list.remove(0)
                sock.shutdown(socket.SHUT_WR)
            else:
                sock.sendall(buf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='ip', default=None)
    parser.add_argument('--port', dest='port', type=int)
    parser.add_argument('--cmd', dest='cmd')
    args = parser.parse_args()

    cmd(args.ip, args.port, args.cmd)
