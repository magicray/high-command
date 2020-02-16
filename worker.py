import os
import sys
import runpy
import socket
import argparse


def worker(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(b'\n\n')

    os.dup2(sock.fileno(), 0)
    os.dup2(sock.fileno(), 1)

    sys.argv = sys.stdin.readline().strip().split()
    runpy.run_module(sys.argv[0], run_name='__main__')

    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='ip', default=None)
    parser.add_argument('--port', dest='port', type=int)
    args = parser.parse_args()

    worker(args.ip, args.port)
