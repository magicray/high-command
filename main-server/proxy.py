import uuid
import asyncio
import logging
import argparse
import urllib.parse

from logging import critical as log


workers = dict()


async def server(reader, writer):
    peer = writer.get_extra_info('peername')

    cmd = await reader.readline()

    # worker
    if b'\n' == cmd:
        await reader.readline()  # Discard the next empty line
        uid = uuid.uuid4().hex
        workers[uid] = writer
        log('join%s workers(%d)', peer, len(workers))
        writer = None

    # client
    else:
        log('join%s cmd(%s)', peer, cmd)

        if len(workers):
            uid, w_writer = workers.popitem()
            workers[uid] = writer
            writer = w_writer

            http = False
            f = cmd.decode().split()
            if f[0].lower() in ('get', 'post'):
                if f[-1].lower().startswith('http/1.'):
                    http = True

            if http:
                workers[uid].write(b'HTTP/1.0 200 OK\n\n')
                writer.write(urllib.parse.unquote(f[1][1:]).encode() + b'\n')
            else:
                workers[uid].write(b'\n\n')
                writer.write(cmd)
        else:
            writer.close()
            return

    try:
        while True:
            buf = await reader.read()

            if writer is None:
                writer = workers[uid]

            if not buf:
                break

            writer.write(buf)
    finally:
        pass

    writer.write_eof()

    if uid in workers and writer == workers[uid]:
        workers.pop(uid)
        log('exit%s workers(%s)', peer, len(workers))
    else:
        log('exit%s cmd(%s)', peer, cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', dest='port', type=int)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(process)d : %(message)s')

    asyncio.gather(asyncio.start_server(server, '', args.port))
    asyncio.get_event_loop().run_forever()
