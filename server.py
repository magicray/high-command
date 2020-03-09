import os
import sys
import runpy
import socket
import logging
import argparse
import urllib.parse

from logging import critical as log


def logfile(logdir, filename):
    name = logdir + '/' + filename
    os.dup2(os.open(name, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644), 2)


def server(addr, logdir):
    line = urllib.parse.unquote(sys.stdin.buffer.readline().decode())
    sys.argv = line.split()[1:-1]
    sys.argv[0] = sys.argv[0][1:]

    while True:
        hdr = sys.stdin.buffer.readline().decode().strip()
        if not hdr:
            break
        k, v = hdr.split(':', 1)
        os.environ[k.strip().upper()] = v.strip()

    log('from%s cmd(%s)', addr, ' '.join(sys.argv))

    logfile(logdir, sys.argv[0])

    print('HTTP/1.0 200 OK\n\n')
    runpy.run_module(sys.argv[0], run_name='__main__')
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='ip', default='')
    parser.add_argument('--port', dest='port', type=int)
    parser.add_argument('--logdir', dest='logdir', default='.')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(process)d : %(message)s')

    if not os.path.isdir(args.logdir):
        os.mkdir(args.logdir)

    logfile(args.logdir, 'main-server')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((args.ip, args.port))
    sock.listen()

    while True:
        conn, addr = sock.accept()

        if 0 == os.fork():
            break

        conn.close()

    sock.close()
    os.dup2(conn.fileno(), 0)
    os.dup2(conn.fileno(), 1)
    server(addr, args.logdir)


if __name__ == '__main__':
    main()
