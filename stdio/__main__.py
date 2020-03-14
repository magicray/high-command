import os
import sys
import ssl
import time
import runpy
import signal
import socket
import select
import logging
import argparse
import mimetypes
import urllib.parse

from . import Cmd
from logging import critical as log


def logfile(filename):
    if not args.logs:
        return

    name = args.logs + '/' + filename
    os.dup2(os.open(name, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644), 2)


def server(conn, addr):
    sys.stdin = conn.makefile('r')
    sys.stdout = conn.makefile('w')

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

    print('HTTP/1.0 200 OK')

    if 1 == len(sys.argv) and '/' in sys.argv[0]:
        mime_type = mime.guess_type(sys.argv[0])[0]
        mime_type = mime_type if mime_type else 'application/octet-stream'
        print('Content-Type: {}\n'.format(mime_type))
        sys.stdout.flush()

        with open(os.path.join(os.getcwd(), sys.argv[0]), 'rb') as fd:
            length = 0
            while True:
                buf = fd.read(2**20)
                if not buf:
                    break

                conn.sendall(buf)
                length += len(buf)

            log('client%s file(%s) bytes(%d)', addr, sys.argv[0], length)
    else:
        print()
        sys.stdout.flush()
        logfile(sys.argv[0])
        runpy.run_module(sys.argv[0], run_name='__main__')
        sys.stdout.flush()


def jobs():
    cmd = Cmd('127.0.0.1', args.port, args.jobs)
    jobs = cmd.stdout.readlines()
    del(cmd)

    for job in jobs:
        if 0 == os.fork():
            cmd = [x.strip() for x in job.split('|')]

            sys.argv = cmd[0].split()
            logfile(sys.argv[0])

            if len(cmd) > 1 and cmd[1]:
                sys.stdin = open(os.path.join(os.getcwd(), cmd[1]), 'r')
            if len(cmd) > 2 and cmd[2]:
                sys.stdout = open(os.path.join(os.getcwd(), cmd[2]), 'w')

            runpy.run_module(sys.argv[0], run_name='__main__')

            sys.stdout.flush()
            sys.stdout.close()
            return


def main():
    logging.basicConfig(format='%(asctime)s %(process)d : %(message)s')
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    if args.logs and not os.path.isdir(args.logs):
        os.mkdir(args.logs)

    logfile(__loader__.name)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', args.port))
    sock.listen()

    next_timestamp = int(time.time() / 60) * 60 + 60
    while True:
        r, _, _ = select.select([sock], [], [], 1)

        if time.time() > next_timestamp:
            next_timestamp = int(time.time() / 60) * 60 + 60

            if 0 == os.fork():
                return jobs()

        if sock in r:
            conn, addr = sock.accept()

            if 0 == os.fork():
                sock.close()
                return server(ssl.wrap_socket(conn, None, 'ssl.cert', True),
                              addr)
            conn.close()


if __name__ == '__main__':
    # openssl req -x509 -nodes -subj / -sha256 --keyout ssl.key --out ssl.cert

    args = argparse.ArgumentParser()
    args.add_argument('--ip', dest='ip')
    args.add_argument('--cmd', dest='cmd')
    args.add_argument('--logs', dest='logs')
    args.add_argument('--port', dest='port', type=int)
    args.add_argument('--jobs', dest='jobs', default='stdio.tools --cmd jobs')
    args = args.parse_args()

    if args.ip and args.port and args.cmd:
        cmd = Cmd(args.ip, args.port, args.cmd)

        if not os.isatty(0):
            cmd.stdin.write(sys.stdin.read())

        while os.write(1, cmd.stdout.read().encode()):
            pass
    else:
        mime = mimetypes.MimeTypes()
        main()
