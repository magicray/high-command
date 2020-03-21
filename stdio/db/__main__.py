import sys
import time
import json
import argparse

from logging import critical as log

from . import SQLite
from .. import Cmd


def init():
    sql = SQLite(args.db)
    sql('''create table if not exists kv(
        seq   integer primary key autoincrement,
        term  integer,
        ts    integer,
        key   text,
        value text)''')
    sql('create unique index if not exists key on kv(key)')


def read():
    sql = SQLite(args.db)

    rows = sql('''select seq, term, ts, key, value
                  from kv where seq >= ? order by seq
               ''', args.seq)

    byte_count = 0
    record_count = 0
    for r in rows:
        rec = json.dumps([r[0], r[1], r[2], r[3], r[4]])

        byte_count += len(rec)
        record_count += 1

        print(rec)

    sys.stdout.flush()

    log('read(%s) record(%d) bytes(%d)', args.db, record_count, byte_count)


def sync():
    sql = SQLite(args.db)

    row = sql('select max(seq) from kv').fetchone()
    seq = row[0] if row and row[0] else -1

    cmd = Cmd(args.ip, args.port,
              'stdio.db --cmd read --db {} --seq {}'.format(args.src, seq+1))

    byte_count = 0
    record_count = 0
    for line in cmd.stdout.readlines():
        try:
            seq, term, ts, key, value = json.loads(line)
        except Exception:
            break

        byte_count += len(line)
        record_count += 1

        sql('delete from kv where key=?', key)
        sql('insert into kv values(?, ?, ?, ?, ?)', seq, term, ts, key, value)

    seq = sql('select max(seq) from kv').fetchone()[0]
    sql.commit()

    print(seq)
    sys.stdout.flush()

    log('sync(%s) src(%s) record(%d) bytes(%d)',
        args.db, args.src, record_count, byte_count)


def put():
    dblist = [d.strip() for d in args.db.split(',')]

    db = dblist.pop(0)
    sql = SQLite(db)

    records = list()
    while True:
        try:
            records.append(json.loads(sys.stdin.readline()))
        except Exception:
            break

    ts = int(time.strftime('%Y%m%d%H%M%S'))
    row = sql('select seq, term from kv order by seq desc limit 1').fetchone()
    seq, term = row if row else (0, 0)

    row_count = 0
    for rec in records:
        row_count += 1

        sql('delete from kv where key=?', rec['key'])
        sql('insert into kv values(null, ?, ?, ?, ?)',
            term, ts, rec['key'], rec['value'])

    row = sql('select seq, term from kv order by seq desc limit 1').fetchone()
    final_seq = row[0]
    assert(seq+row_count == final_seq and term == row[1])
    sql.commit()

    log('put(%s) begin(%d) end(%d) rec(%d)', db, seq, final_seq, row_count)

    success_count = 0
    replica_count = len(dblist)
    for i in range(replica_count):
        d = dblist.pop(int(time.time()*10**6) % len(dblist))

        ip, port, d = d.split(':')
        cmd = 'stdio.db --cmd sync --db {} --src {} --ip {} --port {}'.format(
              d, db, ip, port)
        try:
            seq = int(Cmd(ip, int(port), cmd).stdout.readline().strip())
            log('ip(%s:%d) db(%s) seq(%d)', ip, int(port), d, seq)

            if seq >= final_seq:
                success_count += 1

            if success_count >= int(replica_count/2):
                break
        except Exception as e:
            log('exception(%s)', e)

    print(row_count)
    sys.stdout.flush()


def get():
    sql = SQLite('tmp')

    result = list()
    for key in sorted([k.strip() for k in args.keys.split(',')]):
        row = sql('select seq, value from kv where key=?', key).fetchone()
        if row:
            result.append((key, row[0], row[1]))
        else:
            result.append((key, 0, ''))

    del(sql)

    for r in result:
        print('{} {} {}'.format(*r))


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--cmd', dest='cmd')
    args.add_argument('--ip', dest='ip')
    args.add_argument('--port', dest='port', type=int)
    args.add_argument('--db', dest='db')
    args.add_argument('--src', dest='src')
    args.add_argument('--seq', dest='seq', type=int)
    args.add_argument('--keys', dest='keys')
    args = args.parse_args()
    locals()[args.cmd]()
