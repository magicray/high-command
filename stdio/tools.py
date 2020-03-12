import os
import sys
import time
import hashlib
import argparse


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


if __name__ == '__main__':
    main()
