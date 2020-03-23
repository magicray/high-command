import time
import json
import argparse

from . import Cmd, SQLite


def accept():
    sql = SQLite(args.db)
    sql('''create table if not exists paxos(
        key      text primary key,
        sequence integer,
        value    text)''')

    row = sql('select sequence, value from paxos where key=?', args.key)
    row = row.fetchone()
    sequence, value = row if row else (0, None)

    sql('delete from paxos where key=?', args.key)

    # Phase1 - Promise
    if not args.value and args.sequence > sequence:
        sql('insert into paxos values(?, ?, ?)',
            args.key, args.sequence, value)
        sql.commit()

        print(json.dumps(dict(sequence=sequence, value=value)))

    # Phase2 - Accept
    if args.value and args.sequence >= sequence:
        sql('insert into paxos values(?, ?, ?)',
            args.key, args.sequence, args.value)
        sql.commit()

        print(json.dumps('ok'))

    sql.rollback()


def propose():
    acceptors = [a.split(':') for a in args.acceptors.split(',')]

    sequence = int(time.time()*10**9)

    cmdstr = 'stdio.paxos --cmd accept --key {} --sequence {}'.format(
        args.key, sequence)

    count = 0
    seq, val = 0, None
    for ip, port, db in acceptors:  # Phase1 - Promise
        try:
            cmd = Cmd(ip, int(port), cmdstr + ' --db {}'.format(db))
            res = json.loads(cmd.stdout.readline())

            if res['sequence'] > seq and res['value']:
                seq, val = res['sequence'], res['value']

            count += 1
        except Exception:
            pass

    if count <= len(acceptors)/2:
        return

    value = val if val else args.value  # Value to be proposed

    count = 0
    for ip, port, db in acceptors:  # Phase2 - Accept
        try:
            cmd = Cmd(ip, int(port), cmdstr + ' --db {} --value {}'.format(
                                              db, value))
            if 'ok' == json.loads(cmd.stdout.readline()):
                count += 1
        except Exception:
            pass

    if count <= len(acceptors)/2:
        return

    print(value)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--db', dest='db')
    args.add_argument('--cmd', dest='cmd')
    args.add_argument('--key', dest='key')
    args.add_argument('--value', dest='value')
    args.add_argument('--sequence', dest='sequence', type=int)
    args.add_argument('--acceptors', dest='acceptors')
    args = args.parse_args()
    locals()[args.cmd]()
