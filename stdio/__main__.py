import os
import sys
import ssl
import runpy
import socket
import logging
import argparse
import urllib.parse

from . import connect
from logging import critical as log


def logfile(filename):
    if not args.logdir:
        return

    name = args.logdir + '/' + filename
    os.dup2(os.open(name, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644), 2)


def server(addr):
    line = urllib.parse.unquote(sys.stdin.readline())
    sys.argv = line.split()[1:-1]
    sys.argv[0] = sys.argv[0][1:]

    os.environ['METHOD'] = line[0].strip().upper()
    while True:
        hdr = sys.stdin.readline().strip()
        if not hdr:
            break
        k, v = hdr.split(':', 1)
        os.environ[k.strip().upper()] = v.strip()

    log('from%s cmd(%s)', addr, ' '.join(sys.argv))

    logfile(sys.argv[0])

    print('HTTP/1.0 200 OK\n')
    sys.stdout.flush()
    runpy.run_module(sys.argv[0], run_name='__main__')
    sys.stdout.flush()


def main():
    # openssl req -x509 -newkey rsa:2048 -keyout ssl.key -nodes
    #             -subj / -out ssl.cert -sha256 -days 1000

    logging.basicConfig(format='%(asctime)s %(process)d : %(message)s')

    if args.logdir and not os.path.isdir(args.logdir):
        os.mkdir(args.logdir)

    logfile(__loader__.name)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((args.ip, args.port))
    sock.listen()

    while True:
        conn, addr = sock.accept()

        if 0 == os.fork():
            break

        conn.close()

    sock.close()
    conn = ssl.wrap_socket(conn, certfile='ssl.key', server_side=True)
    sys.stdin = conn.makefile('r')
    sys.stdout = conn.makefile('w')
    server(addr)


def cmd(ip, port, cmd):
    sock = connect(ip, port, cmd)

    sock.sendall(sys.stdin.read().encode())

    while True:
        buf = sock.recv(2**16)
        if not buf:
            break

        os.write(1, buf)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--ip', dest='ip', default='')
    args.add_argument('--cmd', dest='cmd')
    args.add_argument('--port', dest='port', type=int)
    args.add_argument('--logdir', dest='logdir', default='')
    args = args.parse_args()

    if args.cmd:
        cmd(args.ip, args.port, args.cmd)
    else:
        main()
