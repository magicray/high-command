import os
import sys
import time
import hashlib
import argparse
from logging import critical as log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', dest='cmd')
    parser.add_argument('--file', dest='file')
    args = parser.parse_args()

    if 'read' == args.cmd:
        with open(os.path.join(os.getcwd(), args.file)) as fd:
            sys.stdout.write(fd.read())

    if 'ping' == args.cmd:
        print(time.strftime('%c'))

    if 'hash' == args.cmd:
        print(hashlib.md5(sys.stdin.readline().encode()).hexdigest())

    if 'echo' == args.cmd:
        for line in sys.stdin:
            print(line)

    if 'cleanup' == args.cmd:
        log('cleaning up....')
        for line in sys.stdin:
            print('{} {}'.format(time.strftime('%c'), line))

    if 'jobs' == args.cmd:
        print('stdio.tools --cmd cleanup | jobs.in | jobs.out')


if __name__ == '__main__':
    main()
