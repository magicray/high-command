import uuid
import asyncio
import logging
import argparse

from logging import critical as log


workers = dict()


async def server(reader, writer):
    peer = writer.get_extra_info('peername')

    cmd = await reader.readline()

    # worker
    if b'\n' == cmd:
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

    if writer == workers[uid]:
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
