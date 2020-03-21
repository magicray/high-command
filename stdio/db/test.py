import time
import json
import random
import argparse

from .. import Cmd


def main():
    keys = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

    for i in range(100):
        cmd = 'stdio.db --cmd put --db {}'.format(args.db)
        cmd = Cmd(args.ip, args.port, cmd)

        for j in range(10):
            cmd.stdin.write(json.dumps(dict(
                key=random.choice(keys),
                value=str(time.time()))))
            cmd.stdin.write('\n')

        cmd.stdin.write('\n')
        cmd.stdin.flush()

        print('count({}) result({})'.format(i, cmd.stdout.readline().strip()))


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--ip', dest='ip')
    args.add_argument('--port', dest='port', type=int)
    args.add_argument('--db', dest='db')
    args = args.parse_args()
    main()
