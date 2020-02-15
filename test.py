import sys
import hashlib
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', dest='cmd', default='ping')
    args = parser.parse_args()

    if 'ping' == args.cmd:
        print('ok')

    if 'hash' == args.cmd:
        print(hashlib.md5(sys.stdin.buffer.read()).hexdigest())

    elif 'echo' == args.cmd:
        for line in sys.stdin:
            print(line)


if __name__ == '__main__':
    main()
